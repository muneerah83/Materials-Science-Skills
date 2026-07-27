**Python-only execution rule.** Do all figure drawing, previewing, exporting, and visual QA in Python. Do not call any other plotting backend or language as a fallback. If Python or required packages are missing, stop before rendering, report the exact missing dependency, and wait.

## Canonical style and export (executable, do not re-type)

Palettes, publication rcParams, and the 4-format export bundle live in
`scripts/materials_plot_style.py` — import or copy it instead of rewriting:

```python
from materials_plot_style import apply_publication_style, save_pub, PALETTE_MATERIALS

apply_publication_style(font_size=8, axes_linewidth=1)  # dense journal panels
...
save_pub(fig, "figure")   # figure.svg + .pdf + .png + .tiff, editable SVG text
```

Non-negotiable defaults enforced by the module: journal-safe sans fonts,
`svg.fonttype='none'`, `pdf.fonttype=42`. Use `text.usetex = True` only when
LaTeX is installed and math-rich labels are required.

After export, run the mechanical QA gate:
`python scripts/qa_figure_export.py --figure-dir <package> --json`.

## Reference files (load on demand)
- `references/characterization-figures.md` — XRD/FTIR/TG/SEM plotting patterns
- `references/performance-figures.md` — strength/bonding/viscosity curves
- `references/mechanism-figures.md` — mechanism schematics and interface figures
- `references/figure-package-protocol.md` — complete figure package assembly
- `references/figure-qa-contract.md` — font, legend, units, resolution checks
- `references/figure-production-spec.md` — export DPI, TIFF/EPS/PDF, final size
- `references/materials-figure-atlas.md` — fixed materials figure archetypes
