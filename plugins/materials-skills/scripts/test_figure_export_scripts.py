from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIGURE_SCRIPTS = Path(__file__).parents[1] / "skills" / "materials-figure" / "scripts"
sys.path.insert(0, str(FIGURE_SCRIPTS))

from materials_plot_style import (  # noqa: E402
    add_panel_label,
    apply_publication_style,
    finalize_figure,
    is_dark,
    make_evidence_heatmap,
    make_ftir_overlay,
    make_mechanism_schematic,
    make_performance_bar,
    make_xrd_overlay,
    save_pub,
    style_dark_image_ax,
)
import qa_figure_export as qa  # noqa: E402


def _result(results, name):
    return next(result for result in results if result["check"] == name)


def _package(tmp_path: Path, source_name: str = "measurements/custom-panel.dat") -> Path:
    figure_dir = tmp_path / "figure-package"
    figure_dir.mkdir()
    source = figure_dir / source_name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("value\n1\n", encoding="utf-8")
    (figure_dir / "figure_storyboard.yaml").write_text(
        "panels:\n  - id: A\n    source: " + source_name + "\n",
        encoding="utf-8",
    )
    apply_publication_style(font_size=8, axes_linewidth=1)
    figure, axes = plt.subplots()
    axes.plot([0, 1], [0, 1])
    axes.set_xlabel("Stress (MPa)")
    axes.set_ylabel("Strength (MPa)")
    save_pub(figure, str(figure_dir / "figure"), dpi=300)
    return figure_dir


def test_save_pub_then_qa_pass(tmp_path):
    results = qa.run_checks(_package(tmp_path), 300)
    assert all(result["status"] == "pass" for result in results), results


def test_corrupt_pdf_fails(tmp_path):
    figure_dir = _package(tmp_path)
    (figure_dir / "figure.pdf").write_bytes(b"%PDF-1.7\n")
    result = _result(qa.run_checks(figure_dir, 300), "pdf_signature")
    assert result["status"] == "fail"


def test_corrupt_raster_fails(tmp_path):
    figure_dir = _package(tmp_path)
    (figure_dir / "figure.png").write_bytes(b"\x89PNG\r\n\x1a\nbroken")
    (figure_dir / "figure.tiff").write_bytes(b"II*\x00\x08\x00\x00\x00\x00")
    results = qa.run_checks(figure_dir, 300)
    assert _result(results, "png_integrity")["status"] == "fail"
    assert _result(results, "tiff_integrity")["status"] == "fail"


def test_empty_source_fails(tmp_path):
    figure_dir = _package(tmp_path, "empty/source.csv")
    (figure_dir / "empty/source.csv").write_text(" \n\t\n", encoding="utf-8")
    result = _result(qa.run_checks(figure_dir, 300), "source_data_anchor")
    assert result["status"] == "fail"


def test_empty_storyboard_source_fails_even_with_other_files(tmp_path):
    figure_dir = _package(tmp_path)
    (figure_dir / "figure_storyboard.yaml").write_text(
        "panels:\n  - id: A\n    source: ''\n", encoding="utf-8"
    )
    result = _result(qa.run_checks(figure_dir, 300), "source_data_anchor")
    assert result["status"] == "fail"


def test_public_api_helpers_import_and_run(tmp_path):
    assert is_dark("#000000") is True
    figure, axes = plt.subplots(2, 4, figsize=(8, 4))
    assert add_panel_label(axes[0, 0], "a") is not None
    assert style_dark_image_ax(axes[0, 1]) is axes[0, 1]
    assert make_xrd_overlay(
        axes[0, 2], [{"two_theta": [10, 20], "intensity": [1, 2]}], ["xrd"]
    )
    assert make_ftir_overlay(
        axes[0, 3], [{"wavenumber": [1000, 2000], "absorbance": [1, 2]}], ["ftir"]
    )
    assert make_performance_bar(axes[1, 0], ["A", "B"], ["strength"], [[1, 2]])
    make_mechanism_schematic(
        axes[1, 1],
        [{"label": "A", "position": (0.2, 0.2)}, {"label": "B", "position": (0.8, 0.2)}],
        [{"from": "A", "to": "B"}],
    )
    make_evidence_heatmap(axes[1, 2], np.array([[1, 2], [2, 3]]), ["x", "y"], ["m", "n"])
    saved = finalize_figure(figure, tmp_path / "api" / "figure", formats=["png"], close=False)
    assert Path(saved[0]).is_file()
    plt.close(figure)
