# Semiconductor Materials — Reviewer Delta
# Adds to the functional-template. Load functional.md first, then this file.

## Domain-specific review axes

- **Hall effect requirement**: Carrier mobility claims must be supported by Hall effect measurement
  (ASTM F43 / F76). Four-point-probe sheet resistance alone cannot give mobility.
- **I-V conditions**: Room temperature (or stated temperature), defined bias sweep range,
  and illumination conditions must all be specified.
- **Doping confirmation**: Doping type and concentration claims require Hall effect carrier
  concentration data AND XPS/SIMS composition confirmation.
- **Wide-bandgap reliability (SiC, GaN)**: Bias/temperature stress conditions (BTS, HTRB)
  must be defined for any device reliability claim.

## Domain-specific fatal flaws

- Mobility reported without Hall effect measurement — sheet resistance alone is insufficient.
- I-V characteristic without temperature, sweep direction, and bias range.
- Doping level claimed from process conditions without electrical or compositional verification.
- Device stability without bias and temperature stress conditions specified.

## Domain-specific reviewer questions

- "Is mobility from Hall effect measurement? What is the carrier concentration?"
- "Are I-V measurement temperature, sweep direction, and light/dark conditions stated?"
- "Is doping concentration verified by Hall or SIMS, not just nominal?"
- "For SiC/GaN reliability, what bias and temperature stress protocol was used?"
