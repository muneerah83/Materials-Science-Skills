#!/usr/bin/env python3
"""Check a manuscript draft against machine-readable journal template specs.

Data-driven from `_shared/journal-templates/<journal>.yaml`: abstract word
count, highlights count and length, required declaration blocks, and keyword
presence. Complements audit_materials_manuscript.py (evidence language) with
journal-structure checks. Usage:

    python check_manuscript_structure.py --input draft.md --journal cbm \
        [--article-type research-article] [--json]

Exit code 0 = pass, 1 = issues found, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "_shared" / "journal-templates"

SECTION_RE = re.compile(r"^#{1,3}\s+(.+?)\s*$", re.MULTILINE)
FIELD_SECTION_HINTS = {
    "title": r"^#\s+\S",
    "abstract": r"abstract|摘要",
    "keywords": r"keywords?|关键词",
    "declarations": r"declaration|conflict of interest|data availability|credit|funding",
}


def issue(issue_id: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"id": issue_id, "severity": severity, "message": message}


def load_template(journal: str) -> dict:
    path = TEMPLATES_DIR / f"{journal}.yaml"
    if not path.is_file():
        available = sorted(p.stem for p in TEMPLATES_DIR.glob("*.yaml"))
        print(
            f"error: unknown journal {journal!r}; available: {', '.join(available)}"
        )
        raise SystemExit(2)  # usage error, consistent with missing --input
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def extract_section(text: str, name_pattern: str) -> str | None:
    """Return body text of the first heading matching name_pattern."""
    headings = list(SECTION_RE.finditer(text))
    for index, match in enumerate(headings):
        if re.search(name_pattern, match.group(1), re.IGNORECASE):
            start = match.end()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            return text[start:end].strip()
    return None


def check_structure(text: str, template: dict, article_type: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    type_specs = {t["id"]: t for t in template.get("article_types", [])}
    spec = type_specs.get(article_type)
    if spec is None:
        issues.append(
            issue(
                "unknown_article_type",
                f"article type {article_type!r} not in template; "
                f"available: {', '.join(type_specs)}",
            )
        )
        spec = {}

    excluded_fields = {
        field
        for field in spec.get("required_fields_exclude", [])
        if isinstance(field, str)
    }
    abstract_required = spec.get("abstract_required", True) is not False
    abstract = extract_section(text, FIELD_SECTION_HINTS["abstract"])
    if abstract is None:
        if abstract_required:
            issues.append(issue("missing_abstract", "No abstract section heading detected."))
    else:
        limit = spec.get("abstract_words")
        if isinstance(limit, int) and limit > 0:
            count = len(abstract.split())
            if count > limit:
                issues.append(
                    issue(
                        "abstract_over_limit",
                        f"Abstract has {count} words; {template['journal_id']} "
                        f"{article_type} allows {limit}.",
                    )
                )

    for field in template.get("required_fields", []):
        if field in excluded_fields:
            continue
        hint = FIELD_SECTION_HINTS.get(field)
        if hint is None:
            continue  # authors/affiliations/corresponding_author live outside drafts
        if not re.search(hint, text, re.IGNORECASE | re.MULTILINE):
            issues.append(
                issue(
                    f"missing_{field}",
                    f"Required element '{field}' was not detected in the draft.",
                    severity="warning" if field == "declarations" else "error",
                )
            )

    if template.get("highlights_required"):
        rules = template.get("highlights_rules", {})
        highlights = extract_section(text, r"highlights?")
        if highlights is None:
            issues.append(
                issue("missing_highlights", "Journal requires highlights; none detected.")
            )
        else:
            items = [
                line.lstrip("-*0123456789. ").strip()
                for line in highlights.splitlines()
                if line.strip().startswith(("-", "*")) or re.match(r"^\d+\.", line.strip())
            ]
            min_count = rules.get("min_count")
            max_count = rules.get("max_count")
            if isinstance(min_count, int) and len(items) < min_count:
                issues.append(
                    issue(
                        "highlights_too_few",
                        f"{len(items)} highlight items; journal requires >= {min_count}.",
                    )
                )
            if isinstance(max_count, int) and len(items) > max_count:
                issues.append(
                    issue(
                        "highlights_too_many",
                        f"{len(items)} highlight items; journal allows <= {max_count}.",
                    )
                )
            max_chars = rules.get("max_characters_per_item")
            if isinstance(max_chars, int):
                for item in items:
                    if len(item) > max_chars:
                        issues.append(
                            issue(
                                "highlight_item_too_long",
                                f"Highlight exceeds {max_chars} chars: {item[:60]}...",
                            )
                        )

    declarations = template.get("declaration_requirements", {})
    declaration_hints = {
        "data_availability": r"data availability",
        "credit_author_statement": r"credit author|author contribution",
        "conflict_of_interest": r"conflict of interest|competing interest",
        "funding": r"funding|financial support|acknowledg",
    }
    for key, required in declarations.items():
        if required is not True:
            continue
        hint = declaration_hints.get(key, re.escape(key.replace("_", " ")))
        if not re.search(hint, text, re.IGNORECASE):
            issues.append(
                issue(
                    f"missing_declaration_{key}",
                    f"Journal requires a '{key.replace('_', ' ')}' statement; none detected.",
                    severity="error",
                )
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Draft manuscript Markdown file.")
    parser.add_argument("--journal", required=True, help="Journal template id, e.g. cbm.")
    parser.add_argument("--article-type", default="research-article")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    draft = Path(args.input)
    if not draft.is_file():
        print(f"error: {draft} not found")
        return 2

    template = load_template(args.journal)
    issues = check_structure(
        draft.read_text(encoding="utf-8"), template, args.article_type
    )
    blocking_issues = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    payload = {
        "status": "pass" if not blocking_issues else "fail",
        "journal": args.journal,
        "article_type": args.article_type,
        "issues": issues,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if issues:
            for item in issues:
                print(f"[{item['severity']}] {item['id']}: {item['message']}")
        else:
            print(f"PASS: draft matches {args.journal} {args.article_type} structure")
    return 0 if not blocking_issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
