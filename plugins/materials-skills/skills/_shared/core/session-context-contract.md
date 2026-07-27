# Session Context Contract

## Purpose

This contract governs lightweight fragment-load tracking within a single
conversation session. It is distinct from the **research-state-contract**
(which tracks scientific content across skills) and from **profile.yaml**
(which persists research direction across sessions).

A session context is active from the first skill invocation in a
conversation until the conversation ends or the user explicitly resets it.

## Why this matters

Every materials-* skill reads routing fragments (domain template, domain
delta, journal-tier file) before responding. Without tracking, the same
fragment is fully re-processed on every turn whenever its trigger keywords
appear. With tracking, subsequent turns can acknowledge "already in context"
and skip re-stating known criteria — reducing redundant output and keeping
the model's attention on the current question.

## State file

- Path: `.materials/session-context.yaml`
- User-local, not tracked by git (`.materials/` is in `.gitignore`).
- Created on first skill use in a conversation; deleted or overwritten to
  reset.
- Template: `_shared/core/session-context-template.yaml`

## Warm fragment rule

A fragment's warm identity is a **qualified key**, never its relative path
alone. The canonical key format is:

`<plugin>/<skill>::<fragment-path>`

For example, the civil fragment owned by the reviewer skill is
`materials-skills/materials-reviewer::static/fragments/domain/civil.md`.
Each `warm_fragments` entry must carry the same identity explicitly:
`{key, scope, path, label, loaded_turn}`, where `scope` is the owning
`<plugin>/<skill>` value and `key` is exactly `<scope>::<path>`.

A fragment is **warm** only when its qualified `key` appears in
`warm_fragments` with a `loaded_turn` ≤ the current turn number. Skills must
compare the complete key; matching `path` without the owning `scope` is
invalid.

When a fragment is warm:
- Do not re-emit its full content.
- Acknowledge with: `[context: <label> — loaded turn <N>, criteria active]`
- Apply its constraints silently (they still govern the response).

When a fragment is not warm:
- Load and apply it fully.
- Append `{key, scope, path, label, loaded_turn}` to `warm_fragments` with
  the current turn number.

Legacy entries that lack `key` or `scope` (including the former
`{path, label, loaded_turn}` shape) are **cold**. Do not infer their owner or
use their path as a warm match. After loading the fragment fully, append a
new qualified entry; the legacy entry may be discarded during that write.

## Active routing change rule

If the current request's detected `material_family`, `domain`, or
`journal_tier` differs from `active_routing` in the session context:
- Clear the corresponding warm fragment entries for the current skill's
  `scope` only; entries owned by other skills remain isolated by their keys.
- Load the new fragment fully and update `active_routing`.
- Emit a brief note: `[routing updated: <old> → <new>]`

`review_depth` and `review_scope` changes do NOT clear warm fragments —
these are per-request overrides, not session-level resets.

## Lifecycle

| Event | Action |
|---|---|
| First skill use in conversation | Create session-context.yaml from template |
| Fragment loaded for the first time | Append to warm_fragments, increment turn_count |
| Same fragment re-encountered | Acknowledge warm, do not re-emit |
| Direction (family/domain/tier) changed | Clear relevant axis entries, reload |
| User says "reset context" or "start fresh" | Delete or clear warm_fragments |
| Conversation ends | File may be left (stale); skills ignore entries > 50 turns old |

## Context notes

Skills may append short `context_notes` entries to record key findings
from the session (e.g., "dosage optimum identified as 8–12%"). These
persist within the session and help continuity without reloading full
research state.

## Relation to other state files

| File | Scope | Content |
|---|---|---|
| `.materials/profile.yaml` | Persistent (across sessions) | Research direction |
| `.materials/session-context.yaml` | Single conversation | Loaded fragments, warm state |
| `research-state.yaml` (user-created) | Multi-skill workflow | Scientific content |
