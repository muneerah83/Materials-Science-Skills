# Additively Manufactured Metals — Reviewer Delta
# Adds to the metals-template. Load metals.md first, then this file.

## Domain-specific review axes

- **Density verification**: Archimedes density alone is insufficient for AM parts.
  Micro-CT is required to characterize porosity type (spherical gas pore vs. lack-of-fusion defect).
  Lack-of-fusion defects are planar and far more damaging than spherical pores at the same volume fraction.
- **Build direction documentation**: Tensile and fatigue data must state the build orientation.
  AM microstructures are anisotropic; Z-direction (build direction) properties often differ by 20–40%.
- **Post-processing comparison**: Fatigue and fracture claims require comparison between as-built
  and post-processed (HIP, heat-treated) conditions.
- **Process window mapping**: Single-parameter density optimization is insufficient.
  Laser power × scan speed process window map is expected for any densification claim.

## Domain-specific fatal flaws

- Archimedes density presented as full porosity characterization — Micro-CT required.
- Tensile data without build orientation — anisotropy not characterized.
- Fatigue claims without post-processing (HIP/heat treatment) comparison.
- Single-parameter optimization without process window map.

## Domain-specific reviewer questions

- "Is Micro-CT provided to characterize porosity type (spherical vs. lack-of-fusion)?"
- "What is the build orientation for all mechanical test specimens?"
- "Is a comparison provided between as-built and HIP/heat-treated conditions for fatigue?"
- "Is a laser power × scan speed process window map shown?"
