#!/usr/bin/env python3
"""Materials-science publication plotting style and figure helpers.

The public constants and helpers documented in ``references/api.md`` live in
this executable module. Import from a plot.py next to this skill or copy the
module into a figure package:

    from materials_plot_style import (
        PALETTE_MATERIALS, DEFAULT_COLORS_MATERIALS,
        apply_publication_style, save_pub,
    )

    apply_publication_style(font_size=8, axes_linewidth=1)
    ... plot ...
    save_pub(fig, "figure")   # figure.svg + .pdf + .png + .tiff
"""

from __future__ import annotations

PALETTE_MATERIALS = {
    # Material-system semantic colors
    "asphalt_dark":    "#3A3A3A",   # dark gray for asphalt/binder
    "asphalt_light":   "#7A7A7A",   # light gray for aged asphalt
    "cement_gray":     "#B8B8B8",   # cement/concrete
    "ceramics_orange": "#D48A5C",   # warm orange for ceramics
    "ceramics_red":    "#B64342",   # strong red for ceramic emphasis
    "metals_blue":     "#4A7BA6",   # cool blue for metals
    "metals_silver":   "#A8A8B0",   # silver/steel gray
    "polymers_green":  "#5B9A5B",   # green for polymers
    "polymers_teal":   "#42949E",   # teal for polymer composites
    # Evidence-level semantic colors
    "measured":        "#2E6DA4",   # measured data (primary blue)
    "inferred":        "#8B8B8B",   # inferred/indirect evidence
    "literature":      "#C49A6C",   # literature values
    # Performance delta colors
    "improvement":     "#2E9E44",   # green for improvement
    "degradation":     "#E53935",   # red for degradation
    "neutral":         "#767676",   # gray for no change
    # Characterization technique colors
    "xrd_blue":        "#3775BA",   # XRD patterns
    "ftir_red":        "#B64342",   # FTIR spectra
    "sem_gray":        "#4D4D4D",   # SEM/TEM images
    "thermal_orange":  "#E07C3E",   # TGA/DSC curves
    # Neutrals
    "neutral_light":   "#CFCECE",
    "neutral_mid":     "#767676",
    "neutral_dark":    "#4D4D4D",
    "neutral_black":   "#272727",
    # Accent colors
    "gold":            "#FFD700",
    "teal":            "#42949E",
    "violet":          "#9A4D8E",
}

# Series order for comparing material systems or characterization techniques.
# Reserve green/red for performance delta, not primary series identity.
DEFAULT_COLORS_MATERIALS = [
    PALETTE_MATERIALS["measured"],
    PALETTE_MATERIALS["ceramics_orange"],
    PALETTE_MATERIALS["polymers_green"],
    PALETTE_MATERIALS["metals_blue"],
    PALETTE_MATERIALS["thermal_orange"],
    PALETTE_MATERIALS["neutral_light"],
]

PALETTE_CHARACTERIZATION = {
    "xrd_primary":       "#3775BA",
    "xrd_secondary":     "#7AA6D4",
    "ftir_primary":      "#B64342",
    "ftir_secondary":    "#E09A9A",
    "sem_primary":       "#4D4D4D",
    "sem_secondary":     "#8B8B8B",
    "thermal_primary":   "#E07C3E",
    "thermal_secondary": "#F0B87C",
    "rheology":          "#9A4D8E",
    "fluorescence":      "#2E9E44",
}

PALETTE_PERFORMANCE = {
    "baseline":     "#767676",   # baseline/reference
    "optimized":    "#2E6DA4",   # optimized material
    "improvement":  "#2E9E44",   # improvement marker
    "degradation":  "#E53935",   # degradation marker
    "target":       "#FFD700",   # target/specification line
    "uncertainty":  "#CFCECE",   # uncertainty band
}

# Journal-safe font stacks (figure-production-spec.md, publisher defaults).
JOURNAL_SAFE_FONTS = ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]

__all__ = [
    "PALETTE_MATERIALS",
    "DEFAULT_COLORS_MATERIALS",
    "PALETTE_CHARACTERIZATION",
    "PALETTE_PERFORMANCE",
    "JOURNAL_SAFE_FONTS",
    "apply_publication_style",
    "save_pub",
    "is_dark",
    "add_panel_label",
    "style_dark_image_ax",
    "make_xrd_overlay",
    "make_ftir_overlay",
    "make_performance_bar",
    "make_mechanism_schematic",
    "make_evidence_heatmap",
    "finalize_figure",
]


def apply_publication_style(font_size: float = 16, axes_linewidth: float = 2.5,
                            use_tex: bool = False) -> None:
    """Apply materials-science publication rcParams. Call once before plotting.

    Presets:
    - Large multi-panel figures: font_size=24, axes_linewidth=3
    - Compact single figures:    font_size=15, axes_linewidth=2
    - Dense journal-width panels: font_size=8, axes_linewidth=1
    """
    import matplotlib.pyplot as plt

    # MANDATORY: editable SVG text and TrueType PDF text
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = JOURNAL_SAFE_FONTS
    plt.rcParams["svg.fonttype"] = "none"   # keep text as <text> nodes, not paths
    plt.rcParams["pdf.fonttype"] = 42       # TrueType text in PDF
    # Layout & style
    plt.rcParams["font.size"] = font_size
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["legend.frameon"] = False
    if use_tex:
        plt.rcParams["text.usetex"] = True


def save_pub(fig, filename: str, dpi: int = 600) -> list[str]:
    """Export the journal bundle: SVG (primary) + PDF + PNG + TIFF.

    Raster exports use `dpi` (>=300 for photos, 600 for combination art per
    figure-production-spec.md). Returns the list of written paths.
    """
    written = []
    for ext, kwargs in (
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": dpi}),
        ("tiff", {"dpi": dpi}),
    ):
        path = f"{filename}.{ext}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        written.append(path)
    return written


def is_dark(hex_color: str, threshold: int = 128) -> bool:
    """Return True if hex color is dark (use white text on it)."""
    c = hex_color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < threshold


def add_panel_label(ax, label: str, x: float = -0.06, y: float = 1.02,
                    fontsize: float = 14, color: str = "black",
                    fontweight: str = "bold"):
    """Place a publication-style panel label near the axes top-left edge."""
    return ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=fontsize,
        fontweight=fontweight,
        color=color,
        ha="left",
        va="bottom",
    )


def style_dark_image_ax(ax, facecolor: str = "black"):
    """Prepare an axes for microscopy or rendering plates."""
    ax.set_facecolor(facecolor)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _overlay_arrays(pattern: dict, x_key: str, y_key: str):
    import numpy as np

    if x_key not in pattern or y_key not in pattern:
        raise ValueError(f"each series must contain {x_key!r} and {y_key!r}")
    x_values = np.asarray(pattern[x_key])
    y_values = np.asarray(pattern[y_key])
    if x_values.ndim != 1 or y_values.ndim != 1:
        raise ValueError("series values must be one-dimensional")
    if len(x_values) != len(y_values):
        raise ValueError(f"{x_key} and {y_key} must have equal lengths")
    if len(x_values) == 0:
        raise ValueError("series values must not be empty")
    return x_values, y_values


def make_xrd_overlay(ax, patterns, labels, colors=None,
                     two_theta_range=None, normalize=True,
                     ylabel="Intensity (a.u.)", xlabel="2theta (deg)"):
    """Plot one or more XRD patterns and return the created line objects."""
    from numpy import asarray

    if len(patterns) != len(labels):
        raise ValueError("patterns and labels must have equal lengths")
    if colors is None:
        colors = [PALETTE_CHARACTERIZATION["xrd_primary"],
                  PALETTE_CHARACTERIZATION["xrd_secondary"]]
    if not colors:
        raise ValueError("colors must not be empty")

    lines = []
    for index, (pattern, label) in enumerate(zip(patterns, labels)):
        two_theta, intensity = _overlay_arrays(pattern, "two_theta", "intensity")
        if normalize:
            maximum = float(asarray(intensity).max())
            if maximum == 0:
                raise ValueError("cannot normalize an all-zero XRD pattern")
            intensity = intensity / maximum
        if two_theta_range is not None:
            low, high = two_theta_range
            mask = (two_theta >= low) & (two_theta <= high)
            two_theta = two_theta[mask]
            intensity = intensity[mask]
        line, = ax.plot(
            two_theta,
            intensity,
            color=colors[index % len(colors)],
            lw=1.5,
            label=label,
        )
        lines.append(line)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if lines:
        ax.legend()
    return lines


def make_ftir_overlay(ax, spectra, labels, colors=None,
                      wavenumber_range=None, normalize=True,
                      ylabel="Absorbance (a.u.)", xlabel="Wavenumber (cm-1)"):
    """Plot one or more FTIR spectra and return the created line objects."""
    from numpy import asarray

    if len(spectra) != len(labels):
        raise ValueError("spectra and labels must have equal lengths")
    if colors is None:
        colors = [PALETTE_CHARACTERIZATION["ftir_primary"],
                  PALETTE_CHARACTERIZATION["ftir_secondary"]]
    if not colors:
        raise ValueError("colors must not be empty")

    lines = []
    for index, (spectrum, label) in enumerate(zip(spectra, labels)):
        wavenumber, absorbance = _overlay_arrays(
            spectrum, "wavenumber", "absorbance"
        )
        if normalize:
            maximum = float(asarray(absorbance).max())
            if maximum == 0:
                raise ValueError("cannot normalize an all-zero FTIR spectrum")
            absorbance = absorbance / maximum
        if wavenumber_range is not None:
            low, high = wavenumber_range
            mask = (wavenumber >= low) & (wavenumber <= high)
            wavenumber = wavenumber[mask]
            absorbance = absorbance[mask]
        line, = ax.plot(
            wavenumber,
            absorbance,
            color=colors[index % len(colors)],
            lw=1.5,
            label=label,
        )
        lines.append(line)

    ax.invert_xaxis()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if lines:
        ax.legend()
    return lines


def make_performance_bar(ax, materials, properties, values, errors=None,
                         colors=None, ylabel=None, xlabel=None,
                         annotate=False, bar_width=0.8):
    """Draw grouped material-performance bars and return bar containers."""
    import numpy as np

    if not properties:
        raise ValueError("properties must not be empty")
    if len(values) != len(properties):
        raise ValueError("values must contain one array per property")
    if bar_width <= 0:
        raise ValueError("bar_width must be positive")
    if colors is None:
        colors = DEFAULT_COLORS_MATERIALS
    if not colors:
        raise ValueError("colors must not be empty")

    n_materials = len(materials)
    n_properties = len(properties)
    x = np.arange(n_materials)
    width = bar_width / n_properties
    containers = []
    for index, (prop_values, prop_name) in enumerate(zip(values, properties)):
        prop_values = np.asarray(prop_values)
        if prop_values.ndim != 1 or len(prop_values) != n_materials:
            raise ValueError(
                "each values array must have one value per material"
            )
        error_kw = {}
        if errors is not None:
            if len(errors) != len(properties):
                raise ValueError("errors must contain one array per property")
            error_values = np.asarray(errors[index])
            if error_values.ndim != 1 or len(error_values) != n_materials:
                raise ValueError(
                    "each errors array must have one value per material"
                )
            error_kw = {
                "yerr": error_values,
                "elinewidth": 2,
                "capthick": 2,
                "capsize": 6,
            }
        offset = (index - (n_properties - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            prop_values,
            width=width,
            label=prop_name,
            color=colors[index % len(colors)],
            edgecolor="black",
            linewidth=1.5,
            **error_kw,
        )
        containers.append(bars)
        if annotate:
            for bar, value in zip(bars, prop_values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{value:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(materials)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.legend()
    return containers


def make_mechanism_schematic(ax, components, connections, layout="horizontal"):
    """Draw a component-and-connection mechanism schematic."""
    import matplotlib.patches as mpatches

    if layout not in {"horizontal", "vertical"}:
        raise ValueError("layout must be 'horizontal' or 'vertical'")
    component_by_label = {}
    for component in components:
        label = component["label"]
        if label in component_by_label:
            raise ValueError(f"duplicate component label: {label}")
        component_by_label[label] = component
        x, y = component["position"]
        color = component.get("color", PALETTE_MATERIALS["neutral_light"])
        rect = mpatches.FancyBboxPatch(
            (x - 0.1, y - 0.05),
            0.2,
            0.1,
            boxstyle="round,pad=0.01",
            facecolor=color,
            edgecolor="black",
            linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    for connection in connections:
        try:
            source = component_by_label[connection["from"]]
            target = component_by_label[connection["to"]]
        except KeyError as exc:
            raise ValueError(f"unknown mechanism component: {exc.args[0]}") from exc
        x1, y1 = source["position"]
        x2, y2 = target["position"]
        ax.annotate(
            "",
            xy=(x2 - 0.1, y2),
            xytext=(x1 + 0.1, y1),
            arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "black"},
        )
        if "label" in connection:
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 + 0.02,
                connection["label"],
                ha="center",
                fontsize=8,
            )

    if component_by_label:
        positions = [component["position"] for component in components]
        xs, ys = zip(*positions)
        ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2)
        ax.set_ylim(min(ys) - 0.2, max(ys) + 0.2)
    ax.set_aspect("equal")
    ax.axis("off")


def make_evidence_heatmap(ax, matrix, techniques, mechanisms,
                          cmap="YlOrRd", cbar_label="Evidence strength",
                          annotate=True, fmt="{:.1f}"):
    """Draw a technique-by-mechanism evidence heatmap."""
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    values = np.asarray(matrix)
    if values.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    if len(techniques) != values.shape[0]:
        raise ValueError("techniques must match the matrix row count")
    if len(mechanisms) != values.shape[1]:
        raise ValueError("mechanisms must match the matrix column count")
    if values.size == 0:
        raise ValueError("matrix must not be empty")

    minimum = float(np.nanmin(values))
    maximum = float(np.nanmax(values))
    display_maximum = maximum if maximum > minimum else minimum + 1.0
    image = ax.imshow(
        values,
        cmap=cmap,
        aspect="auto",
        vmin=minimum,
        vmax=display_maximum,
    )
    colorbar = ax.figure.colorbar(image, ax=ax)
    colorbar.set_label(cbar_label)
    ax.set_xticks(range(len(mechanisms)))
    ax.set_xticklabels(mechanisms, rotation=30, ha="right")
    ax.set_yticks(range(len(techniques)))
    ax.set_yticklabels(techniques)

    if annotate:
        norm = mpl.colors.Normalize(vmin=minimum, vmax=display_maximum)
        cmap_object = plt.get_cmap(cmap)
        for (row, column), value in np.ndenumerate(values):
            red, green, blue, _ = cmap_object(norm(value))
            luminance = 0.299 * red + 0.587 * green + 0.114 * blue
            text_color = "white" if luminance < 0.5 else "black"
            ax.text(
                column,
                row,
                fmt.format(value),
                ha="center",
                va="center",
                fontsize=10,
                color=text_color,
            )


def finalize_figure(fig, out_path, formats=None, dpi=300, pad=2,
                    bbox_inches=None, close=True):
    """Tighten and save a figure, returning the written paths."""
    import os
    from pathlib import Path
    import matplotlib.pyplot as plt

    fig.tight_layout(pad=pad)
    base = Path(out_path)
    if formats is None:
        formats = [base.suffix.lstrip(".") or "png"]
    if base.suffix:
        base = base.with_suffix("")
    os.makedirs(base.parent, exist_ok=True)

    saved = []
    for fmt in formats:
        normalized = str(fmt).lstrip(".").lower()
        if not normalized:
            raise ValueError("figure format must not be empty")
        path = str(base) + f".{normalized}"
        save_kwargs = {"dpi": dpi}
        if bbox_inches is not None:
            save_kwargs["bbox_inches"] = bbox_inches
        fig.savefig(path, **save_kwargs)
        saved.append(path)
    if close:
        plt.close(fig)
    return saved
