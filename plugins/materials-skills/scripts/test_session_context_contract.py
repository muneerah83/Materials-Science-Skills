"""Static regression checks for skill-qualified session warm fragments."""

from __future__ import annotations

from pathlib import Path

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = PLUGIN_ROOT / "skills" / "_shared" / "core"
CONTRACT = SHARED_ROOT / "session-context-contract.md"
TEMPLATE = SHARED_ROOT / "session-context-template.yaml"

SKILL_SCOPES = {
    "materials-reviewer": "materials-skills/materials-reviewer",
    "materials-figure": "materials-skills/materials-figure",
    "materials-research": "materials-skills/materials-research",
}


def test_contract_requires_a_skill_qualified_key_and_cold_legacy_entries() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    assert "<plugin>/<skill>::<fragment-path>" in text
    assert "Each `warm_fragments` entry must carry the same identity explicitly" in text
    assert "matching `path` without the owning `scope`" in text
    assert "Legacy entries that lack `key` or `scope`" in text
    assert "are **cold**" in text


def test_template_is_valid_yaml_and_demonstrates_same_path_is_scope_qualified() -> None:
    template_text = TEMPLATE.read_text(encoding="utf-8")
    document = yaml.safe_load(template_text)

    assert document["warm_fragments"] == []
    assert "Format: {key, scope, path, label, loaded_turn}" in template_text

    reviewer_key = (
        "materials-skills/materials-reviewer::"
        "static/fragments/domain/civil.md"
    )
    figure_key = (
        "materials-skills/materials-figure::"
        "static/fragments/domain/civil.md"
    )
    assert f"key: {reviewer_key}" in template_text
    assert f"key: {figure_key}" in template_text
    assert reviewer_key != figure_key


def test_skill_session_guards_match_the_shared_contract() -> None:
    required_fragments = (
        'key_format: "<scope>::<fragment path>"',
        "warm_fragments and loaded_turn",
        "append {key, scope, path, label, loaded_turn}",
        "legacy:",
        "scope",
    )

    for skill_name, scope in SKILL_SCOPES.items():
        text = (
            (PLUGIN_ROOT / "skills" / skill_name / "SKILL.md")
            .read_text(encoding="utf-8")
        )
        assert f"scope: {scope}" in text
        for required in required_fragments:
            assert required in text, (skill_name, required)
        assert "qualified key" in text or "matching key" in text
        assert "never match by path" in text
        assert "scope" in text and ("owned by this scope" in text or "in this scope" in text)
        assert "fragment path in warm_fragments" not in text
        assert "append {path, label, loaded_turn}" not in text
