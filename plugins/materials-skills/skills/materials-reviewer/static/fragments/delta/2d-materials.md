# Two-Dimensional Materials (Graphene, MoS₂, MXene) — Reviewer Delta
# Adds to the nano-template. Load nano.md first, then this file.

## Domain-specific review axes

- **Raman completeness**: D/G ratio (defect density) AND G/2D ratio (layer number) must both be reported.
  G/2D ratio alone is insufficient; D/G quantifies synthesis quality and defect impact on transport.
- **Environmental stability**: Stability claims require performance retention after defined conditions
  (humidity, temperature, UV, ambient air). Encapsulated vs. bare device comparison is required.
- **Large-area uniformity statistics**: "Scalable synthesis" or "wafer-scale" claims require
  thickness uniformity mapping (Raman, AFM, optical) and defect density statistics across the area.
  Single-point characterization is not representative.
- **Intrinsic mobility**: Contact resistance must be subtracted before reporting intrinsic mobility.
  Two-terminal FET mobility without contact correction overestimates due to contact resistance.

## Domain-specific fatal flaws

- Raman D/G ratio not reported — defect density unknown, synthesis quality uncharacterized.
- Stability claimed from short ambient exposure without encapsulation comparison.
- "Wafer-scale" uniformity from single-point Raman/AFM measurement.
- Intrinsic mobility from two-terminal measurement without contact resistance correction.

## Domain-specific reviewer questions

- "Are D/G ratio (defect density) and G/2D ratio (layer number) both reported from Raman?"
- "Is environmental stability tested under defined conditions with encapsulated comparison?"
- "Is large-area uniformity characterized by mapping (not single-point measurement)?"
- "Is contact resistance subtracted for intrinsic mobility extraction?"
