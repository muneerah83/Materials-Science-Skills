# Dielectric and Piezoelectric Materials — Reviewer Delta
# Adds to the functional-template. Load functional.md first, then this file.

## Domain-specific review axes

- **d33 method and poling**: Quasi-static d33 (Berlincourt) and IEEE 180 resonance give different values.
  Poling conditions (field strength, temperature, time) must be stated.
  Unpoled samples cannot yield meaningful d33.
- **P-E loop at saturation**: P-E hysteresis loop must reach saturation; Pr and Ec from an
  undersaturated loop are not reliable. Applied field strength must be stated.
- **Frequency-dependent dielectric data**: Minimum 3 frequencies spanning several decades required.
  Single-frequency dielectric constant cannot reveal relaxation behavior or loss mechanisms.
- **Curie temperature measurement**: For any temperature-stability claim, Tc must be located
  by dielectric vs. temperature sweep or DSC.

## Domain-specific fatal flaws

- d33 without poling conditions — value is not reproducible.
- P-E loop that does not reach saturation — Pr and Ec values are artifactual.
- Dielectric data at one frequency only — frequency dispersion not characterized.
- Temperature stability claimed without Curie temperature measurement.

## Domain-specific reviewer questions

- "What are the poling field, temperature, and time for d33 measurement?"
- "Does the P-E loop reach saturation? What is the maximum applied field?"
- "Is dielectric constant measured at ≥ 3 frequencies (e.g., 1 kHz, 100 kHz, 1 MHz)?"
- "Is the Curie temperature located by dielectric vs. temperature or DSC?"
