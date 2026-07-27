"""Focused regression tests for the manuscript structure checker."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "materials-writing"
    / "scripts"
    / "check_manuscript_structure.py"
)


def draft_text(*, abstract: str | None = "A bounded abstract.", declarations: bool = True) -> str:
    sections = ["# Manuscript title"]
    if abstract is not None:
        sections.extend(["# Abstract", abstract])
    sections.extend(
        [
            "# Keywords",
            "materials; performance",
            "# Highlights",
            "- First bounded finding",
            "- Second bounded finding",
            "- Third bounded finding",
        ]
    )
    if declarations:
        sections.extend(
            [
                "# Declarations",
                "Data availability: available on request.",
                "CRediT author statement: all authors contributed.",
                "Conflict of interest: the authors declare none.",
                "Funding: no external funding.",
            ]
        )
    return "\n\n".join(sections) + "\n"


def run_checker(tmp_path: Path, *, journal: str, article_type: str, draft: str) -> subprocess.CompletedProcess[str]:
    input_path = tmp_path / "draft.md"
    input_path.write_text(draft, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--input",
            str(input_path),
            "--journal",
            journal,
            "--article-type",
            article_type,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def parse_payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


def test_building_environment_letter_without_abstract_passes(tmp_path: Path) -> None:
    result = run_checker(
        tmp_path,
        journal="building-environment",
        article_type="letter",
        draft=draft_text(abstract=None),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = parse_payload(result)
    assert payload["status"] == "pass"
    assert payload["blocking_issues"] == []
    assert not any(item["id"] == "missing_abstract" for item in payload["issues"])


def test_missing_cbm_required_declarations_are_blocking(tmp_path: Path) -> None:
    result = run_checker(
        tmp_path,
        journal="cbm",
        article_type="research-article",
        draft=draft_text(declarations=False),
    )

    assert result.returncode == 1
    payload = parse_payload(result)
    assert payload["status"] == "fail"
    assert {item["id"] for item in payload["blocking_issues"]} >= {
        "missing_declaration_data_availability",
        "missing_declaration_credit_author_statement",
        "missing_declaration_conflict_of_interest",
        "missing_declaration_funding",
    }
    assert any(item["id"] == "missing_declarations" for item in payload["warnings"])


def test_overlong_abstract_remains_blocking(tmp_path: Path) -> None:
    overlong = " ".join(["word"] * 251)
    result = run_checker(
        tmp_path,
        journal="cbm",
        article_type="research-article",
        draft=draft_text(abstract=overlong),
    )

    assert result.returncode == 1
    payload = parse_payload(result)
    assert payload["status"] == "fail"
    assert any(item["id"] == "abstract_over_limit" for item in payload["blocking_issues"])


def test_unknown_article_type_still_fails(tmp_path: Path) -> None:
    result = run_checker(
        tmp_path,
        journal="cbm",
        article_type="not-a-template-type",
        draft=draft_text(),
    )

    assert result.returncode == 1
    payload = parse_payload(result)
    assert payload["status"] == "fail"
    assert any(item["id"] == "unknown_article_type" for item in payload["blocking_issues"])


def test_unknown_journal_remains_usage_error(tmp_path: Path) -> None:
    result = run_checker(
        tmp_path,
        journal="not-a-template-journal",
        article_type="research-article",
        draft=draft_text(),
    )

    assert result.returncode == 2
    assert "unknown journal" in (result.stdout + result.stderr).lower()
