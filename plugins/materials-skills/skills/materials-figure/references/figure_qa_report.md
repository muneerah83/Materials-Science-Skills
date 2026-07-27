# Figure QA Report

Use this report before returning a materials figure package.

Mechanical rows (export bundle, PDF signature, PNG/TIFF structure and
resolution, SVG text/fonts, axis units, and source anchors) are executable:
run `python scripts/qa_figure_export.py --figure-dir <package> --json` and
copy its results. When a panel-level `figure_storyboard.yaml` is present next
to the package, its per-panel `source` paths are checked; use
`--storyboard <path>` when it lives elsewhere. Judgment rows (legend overlap,
panel-label order, caption boundary) remain reviewer calls.

## Required checks

| Check | Pass criterion |
|---|---|
| font | Uses a journal-safe sans serif or configured journal font |
| font size | Final-size text remains at least 7 pt equivalent |
| legend | Legend entries match plotted groups and do not cover data |
| units | Every quantitative axis, scale bar, or color bar includes units |
| resolution | PNG/TIFF export is at least 300 dpi for raster use |
| file integrity | PDF has `%PDF-` and `%%EOF` markers; PNG/TIFF have valid headers and structure |
| SVG text | SVG text remains editable; matplotlib uses `svg.fonttype='none'` |
| panel labels | Panel labels follow A-F order and remain visible |
| caption boundary | Panel claims do not exceed evidence in the storyboard |
| source data | Every plotted panel has a non-empty source file declared by the storyboard, or a non-empty conventional anchor |

## Output pattern

```text
Status: pass / needs revision
Figure: [path]
Checked by: materials-figure

Issues:
- [panel/check] [problem] -> [required fix]
```
