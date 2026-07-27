---
name: materials-figure
description: >-
  Use when creating, revising, auditing, or polishing submission-grade materials-science figures, multi-panel plots, mechanism schematics, evidence maps, or journal SVG/PDF/TIFF outputs for materials, construction materials, or civil engineering research. Trigger for XRD, FTIR, TG/DTG, SEM, performance curves, bonding, rheology, and figure-package QA requests. Do not use for dashboards or Illustrator/Figma-first infographics.
version: "2.1.0"
stability: stable
---

route:
  priority: explicit_request > .materials/profile.yaml > neutral_fallback
  load: manifest axes only — no references preloaded by default

gates:  # check in order; first matching gate blocks execution
  - id: python-gate
    if: Python runtime or a required plotting package is absent
    then: report the exact missing dependency; halt before any rendering

  - id: contract-gate
    if: the figure contract or source-data anchor is missing
    then: request the missing item; do not guess, fabricate, or use placeholder data

  - id: materials-kb-gate  # the materials gate
    if: figure contains materials-science entities — XRD phases, FTIR wavenumbers, or claimed performance values
    then: load static/core/materials_kb.yaml; wrong assignment blocks plotting; warnings stay visible

  - id: storyboard-gate
    if: request covers multiple figures
    then: validate storyboard as a directed-acyclic-graph before any individual figure contract

  - id: mock-data-gate
    if: data is mock data, template-only, or illustrative
    then: label explicitly as template; never present as experimental result

output:
  required: [plot.py, figure.svg, caption.md, qa_report.md]
  caption_rule: "measured claims | inferred claims — boundary explicit in every caption"
  qa_rule: "Python-only backend; export bundle = SVG + PDF + PNG + TIFF; visual QA status reported"

handoffs:
  dashboards: not this skill
  html_decks: → materials-html-deck

session_guard:
  scope: materials-skills/materials-figure
  state_file: .materials/session-context.yaml
  warm_fragment:
    key_format: "<scope>::<fragment path>"
    if: qualified key in warm_fragments and loaded_turn ≤ current turn
    then: acknowledge "[context: <label> — turn <N>]"; apply domain constraints silently
    else: load fully; append {key, scope, path, label, loaded_turn} to warm_fragments
    legacy: entries missing key or scope are cold; never match by path alone
  routing_change:
    if: detected material_family or domain differs from active_routing
    then: clear domain warm entries owned by this scope; reload; update active_routing; emit "[routing: <old> → <new>]"
  contract: ../_shared/core/session-context-contract.md
