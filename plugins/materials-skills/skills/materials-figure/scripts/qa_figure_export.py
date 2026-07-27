#!/usr/bin/env python3
"""Mechanical checks for a materials figure export package."""

from __future__ import annotations

import argparse
import json
import re
import struct
import zlib
from pathlib import Path

REQUIRED_EXPORTS = ["figure.svg", "figure.pdf", "figure.png", "figure.tiff"]
SOURCE_ANCHORS = ["source_data.csv", "source_data.tsv", "source_map.json", "data"]
JOURNAL_SAFE_FONTS = {
    "arial", "helvetica", "dejavu sans", "liberation sans", "sans-serif",
    "times", "times new roman",
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PDF_SIGNATURE = b"%PDF-"
PDF_EOF = b"%%EOF"
UNIT_PATTERN = re.compile(r"\(([^()]{1,20})\)\s*$|/\s*\S{1,10}\s*$")
QUANTITY_HINT = re.compile(
    r"\b(strength|stress|strain|modulus|viscosity|temperature|time|content|"
    r"dosage|ratio|intensity|wavenumber|angle|conductivity|density|mass|"
    r"weight|size|diameter|thickness|frequency|voltage|current|efficiency)\b",
    re.IGNORECASE,
)


def check(check_id: str, passed: bool, detail: str) -> dict[str, object]:
    return {"check": check_id, "status": "pass" if passed else "fail", "detail": detail}


def _meaningful(path: Path) -> bool:
    if path.is_file():
        if path.stat().st_size == 0:
            return False
        with path.open("rb") as handle:
            while chunk := handle.read(8192):
                if any(byte not in b" \t\r\n" for byte in chunk):
                    return True
        return False
    if path.is_dir():
        return any(_meaningful(child) for child in path.rglob("*"))
    return False


def _png_valid(path: Path) -> bool:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        return False
    offset = len(PNG_SIGNATURE)
    saw_ihdr = saw_idat = saw_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            return False
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            return False
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            return False
        if not saw_ihdr:
            if kind != b"IHDR" or length != 13:
                return False
            width, height = struct.unpack(">II", payload[:8])
            if width == 0 or height == 0:
                return False
            saw_ihdr = True
        if kind == b"IDAT" and length > 0:
            saw_idat = True
        if kind == b"IEND":
            saw_iend = length == 0
            return saw_ihdr and saw_idat and saw_iend and end == len(data)
        offset = end
    return False


def _tiff_valid(path: Path) -> bool:
    data = path.read_bytes()
    if len(data) < 8 or data[:2] not in (b"II", b"MM"):
        return False
    endian = "<" if data[:2] == b"II" else ">"
    version = struct.unpack(endian + "H", data[2:4])[0]
    if version == 42:
        offset = struct.unpack(endian + "I", data[4:8])[0]
        if offset < 8 or offset + 2 > len(data):
            return False
        count = struct.unpack(endian + "H", data[offset:offset + 2])[0]
        end = offset + 2 + count * 12 + 4
        if end > len(data):
            return False
        tags = {
            struct.unpack(endian + "H", data[offset + 2 + i * 12:offset + 4 + i * 12])[0]
            for i in range(count)
        }
        return 256 in tags and 257 in tags
    if version == 43 and len(data) >= 16:
        offset_size, reserved = struct.unpack(endian + "HH", data[4:8])
        if offset_size != 8 or reserved != 0:
            return False
        offset = struct.unpack(endian + "Q", data[8:16])[0]
        if offset + 8 > len(data):
            return False
        count = struct.unpack(endian + "Q", data[offset:offset + 8])[0]
        end = offset + 8 + count * 20 + 8
        if end > len(data):
            return False
        tags = {
            struct.unpack(endian + "H", data[offset + 8 + i * 20:offset + 10 + i * 20])[0]
            for i in range(count)
        }
        return 256 in tags and 257 in tags
    return False


def _pdf_valid(path: Path) -> bool:
    data = path.read_bytes()
    return bool(data) and data.startswith(PDF_SIGNATURE) and PDF_EOF in data[-1024:]


def png_dpi(path: Path) -> float | None:
    data = path.read_bytes()
    offset = data.find(b"pHYs")
    if offset == -1 or len(data) < offset + 13:
        return None
    try:
        ppu_x, _ppu_y, unit = struct.unpack(">IIB", data[offset + 4:offset + 13])
    except struct.error:
        return None
    return ppu_x * 0.0254 if unit == 1 else None


def tiff_dpi(path: Path) -> float | None:
    data = path.read_bytes()
    if len(data) < 8 or data[:2] not in (b"II", b"MM"):
        return None
    endian = "<" if data[:2] == b"II" else ">"
    try:
        offset = struct.unpack(endian + "I", data[4:8])[0]
        count = struct.unpack(endian + "H", data[offset:offset + 2])[0]
        for index in range(count):
            base = offset + 2 + index * 12
            tag, _kind, _count, value_offset = struct.unpack(endian + "HHII", data[base:base + 12])
            if tag == 282:
                numerator, denominator = struct.unpack(endian + "II", data[value_offset:value_offset + 8])
                return numerator / denominator if denominator else None
    except (IndexError, struct.error, ZeroDivisionError):
        return None
    return None


def _source_values(value) -> list[str]:
    if isinstance(value, str):
        return [value.strip()]
    if isinstance(value, (list, tuple)):
        result = []
        for item in value:
            result.extend(_source_values(item))
        return result
    if isinstance(value, dict):
        for key in ("path", "file", "filename"):
            if key in value:
                return _source_values(value[key])
    return []


def _storyboard_sources(path: Path) -> tuple[list[str], str | None]:
    raw = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        values = []
        for match in re.finditer(r"^\s*source\s*:\s*(.+?)\s*$", raw, re.MULTILINE):
            value = match.group(1).split(" #", 1)[0].strip().strip("'\"")
            if value:
                values.append(value)
        return values, None if values else "storyboard has no panel sources"
    try:
        document = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return [], f"storyboard parse error: {exc}"
    panels = document.get("panels") if isinstance(document, dict) else None
    if not isinstance(panels, list) or not panels:
        return [], "storyboard has no panels"
    values = []
    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            return [], f"storyboard panel {index} is not a mapping"
        panel_values = _source_values(panel.get("source"))
        if not panel_values:
            return [], f"storyboard panel {index} has no source"
        values.extend(panel_values)
    return values, None


def _source_check(figure_dir: Path, storyboard_path: Path | None) -> dict[str, object]:
    storyboard = storyboard_path
    if storyboard is None and (figure_dir / "figure_storyboard.yaml").is_file():
        storyboard = figure_dir / "figure_storyboard.yaml"
    if storyboard is not None:
        if not storyboard.is_file():
            return check("source_data_anchor", False, f"storyboard not found: {storyboard}")
        names, error = _storyboard_sources(storyboard)
        if error:
            return check("source_data_anchor", False, error)
        if names:
            missing = []
            for name in names:
                if not name:
                    missing.append("<empty source>")
                    continue
                source = Path(name)
                candidates = [source] if source.is_absolute() else [storyboard.parent / source, figure_dir / source]
                resolved = next((candidate for candidate in candidates if _meaningful(candidate)), None)
                if resolved is None:
                    missing.append(name or "<empty source>")
            return check(
                "source_data_anchor",
                not missing,
                "all storyboard panel sources are non-empty"
                if not missing else "missing or empty panel sources: " + ", ".join(missing),
            )
    valid = [name for name in SOURCE_ANCHORS if _meaningful(figure_dir / name)]
    return check(
        "source_data_anchor",
        bool(valid),
        "non-empty source anchor present: " + ", ".join(valid)
        if valid else "no non-empty source_data.csv/.tsv, source_map.json, or data/ anchor",
    )


def run_checks(figure_dir: Path, min_dpi: float,
               storyboard_path: Path | None = None) -> list[dict[str, object]]:
    results = []
    missing = [name for name in REQUIRED_EXPORTS if not (figure_dir / name).is_file()]
    results.append(check("export_bundle", not missing, "all exports present" if not missing else "missing: " + ", ".join(missing)))

    svg_path = figure_dir / "figure.svg"
    if svg_path.is_file():
        svg = svg_path.read_text(encoding="utf-8", errors="replace")
        has_text = "<text" in svg
        results.append(check("svg_text_editable", has_text, "SVG keeps <text> nodes" if has_text else "no <text> nodes"))
        families = {family.strip().strip("'\"").lower() for match in re.findall(r"font-family[:=]\s*['\"]?([^;'\"]+)", svg) for family in match.split(",")}
        unsafe = sorted(f for f in families if f and f not in JOURNAL_SAFE_FONTS)
        results.append(check("svg_font_family", not unsafe, "journal-safe fonts only" if not unsafe else "non-journal fonts: " + ", ".join(unsafe)))
        texts = [text.strip() for text in re.findall(r"<text[^>]*>([^<]+)</text>", svg)]
        unitless = [text for text in texts if QUANTITY_HINT.search(text) and not UNIT_PATTERN.search(text)]
        results.append(check("axis_units", not unitless, "quantitative labels carry units" if not unitless else "labels missing units: " + "; ".join(unitless[:5])))

    pdf_path = figure_dir / "figure.pdf"
    if pdf_path.is_file():
        pdf_valid = _pdf_valid(pdf_path)
        results.append(check("pdf_signature", pdf_valid, "PDF signature and EOF marker are valid" if pdf_valid else "PDF is empty, truncated, or lacks %PDF-/%%EOF markers"))

    png_path = figure_dir / "figure.png"
    if png_path.is_file():
        png_valid = _png_valid(png_path)
        results.append(check("png_integrity", png_valid, "PNG structure and CRCs are valid" if png_valid else "PNG is truncated or malformed"))
        dpi = png_dpi(png_path)
        # PNG stores pixels-per-metre as an integer, so a nominal 300 dpi
        # export can decode as 299.999 dpi after unit conversion.
        results.append(check("png_resolution", dpi is not None and dpi + 0.5 >= min_dpi, f"PNG dpi = {dpi:.0f}" if dpi else "PNG has no pHYs chunk"))

    tiff_path = figure_dir / "figure.tiff"
    if tiff_path.is_file():
        tiff_valid = _tiff_valid(tiff_path)
        results.append(check("tiff_integrity", tiff_valid, "TIFF structure is valid" if tiff_valid else "TIFF is truncated or malformed"))
        dpi = tiff_dpi(tiff_path)
        results.append(check("tiff_resolution", dpi is not None and dpi + 0.5 >= min_dpi, f"TIFF dpi = {dpi:.0f}" if dpi else "TIFF has no XResolution tag"))

    results.append(_source_check(figure_dir, storyboard_path))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure-dir", required=True)
    parser.add_argument("--min-dpi", type=float, default=300.0)
    parser.add_argument("--storyboard", type=Path, help="Optional panel-level figure_storyboard.yaml.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    figure_dir = Path(args.figure_dir)
    if not figure_dir.is_dir():
        print(f"error: {figure_dir} is not a directory")
        return 2
    results = run_checks(figure_dir, args.min_dpi, args.storyboard)
    failed = [result for result in results if result["status"] == "fail"]
    payload = {"status": "pass" if not failed else "needs revision", "figure": str(figure_dir), "checked_by": "materials-figure/qa_figure_export.py", "checks": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Status: {payload['status']}")
        for result in results:
            print(f"- [{result['status']}] {result['check']}: {result['detail']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
