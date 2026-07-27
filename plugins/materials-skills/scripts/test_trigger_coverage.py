"""Regression checks for high-signal trigger aliases restored by fragment diet."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"


def _triggers(skill: str, axis: str, value: str) -> set[str]:
    manifest = yaml.safe_load(
        (SKILLS_ROOT / skill / "manifest.yaml").read_text(encoding="utf-8")
    )
    return set(manifest["axes"][axis]["values"][value]["triggers"])


@pytest.mark.parametrize(
    ("skill", "axis", "value", "expected"),
    [
        ("materials-research", "task", "experiment-design", {"DOE", "RSM", "Taguchi"}),
        ("materials-doe", "design_mode", "response-surface", {"RSM"}),
        ("materials-figure", "backend", "python", {"pyplot", "seaborn"}),
        ("materials-figure", "domain", "ceramics", {"alumina"}),
        ("materials-reader", "source_format", "scanned-pdf", {"OCR"}),
        ("materials-reader", "source_format", "doi-arxiv", {"doi.org"}),
        ("materials-reader", "output_type", "evidence-chain-audit", {"claim-evidence"}),
        ("materials-writing", "paper_type", "review-paper", {"literature review"}),
        ("materials-writing", "journal_family", "RMPD", {"JRE", "pavement"}),
    ],
)
def test_high_signal_trigger_aliases_are_present(
    skill: str, axis: str, value: str, expected: set[str]
) -> None:
    assert expected <= _triggers(skill, axis, value)
