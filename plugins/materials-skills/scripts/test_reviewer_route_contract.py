"""Regression tests for reviewer domain and journal-tier route inheritance."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "check_skill_architecture.py"
SPEC = importlib.util.spec_from_file_location("check_skill_architecture", SCRIPT)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

SKILLS_ROOT = SCRIPT.parent.parent / "skills"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(SKILLS_ROOT.resolve()).as_posix()


def test_asphalt_tier2_route_loads_base_delta_and_tier_parent() -> None:
    files, failures = checker._route_skill_payload(
        SKILLS_ROOT,
        "materials-reviewer",
        {
            "review_depth": "detailed",
            "journal_family": "RMPD",
            "review_scope": "methodology",
            "material_family": "civil",
            "domain": "asphalt",
            "journal_tier": "tier2",
        },
        [],
    )

    assert failures == []
    paths = {_relative(path) for path in files}
    assert "materials-reviewer/static/fragments/domain/civil.md" in paths
    assert "materials-reviewer/static/fragments/delta/asphalt.md" in paths
    assert "materials-reviewer/static/fragments/journal_tier/tier1.md" in paths
    assert "materials-reviewer/static/fragments/journal_tier/tier2.md" in paths
    assert "materials-reviewer/static/fragments/journal_tier/tier3.md" not in paths


def test_inheritance_contract_rejects_unrouted_cycle() -> None:
    failures = checker._validate_inheritance_contract(
        {
            "axes": {
                "domain": {
                    "inheritance": {"mode": "additive"},
                    "values": {
                        "a": {"path": "a.md", "inherits": ["b"]},
                        "b": {"path": "b.md", "inherits": ["a"]},
                    },
                }
            }
        }
    )

    assert any("inheritance cycle detected" in failure for failure in failures)
