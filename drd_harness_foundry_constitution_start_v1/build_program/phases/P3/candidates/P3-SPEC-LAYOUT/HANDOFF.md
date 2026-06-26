# P3-SPEC-LAYOUT Handoff

## Candidate

- Workpack: `P3-SPEC-LAYOUT`
- Phase: `P3`
- Lane: `SPEC`
- Module: `natural_language_layout`
- Upstream approved candidate: `P3-SPEC-PATTERNS`

## What This Candidate Defines

`P3-SPEC-LAYOUT` defines natural-language layout authority and its validation skeleton: carrier adaptation, containment hierarchy, content growth, information completeness, state placement, z-axis layering, composition index, and non-authoritative Figma reconstruction metadata.

## Review Focus

1. Confirm that desktop, tablet, mobile, iOS, and Material carrier constraints are explicit.
2. Confirm that containment is multi-level and coupled to arrangement, order, sizing, scroll, and width behavior.
3. Confirm that required information remains accessible under height limits and width limits.
4. Confirm that horizontal scroll is allowed only as a declared exception for wide structures.
5. Confirm that Material z-axis layering, blocking behavior, background context, and focus restoration are explicit.
6. Confirm that Figma metadata is reconstruction guidance only and cannot write, render, or become canonical authority.

## Next Action

If accepted, continue with `P3-SPEC-COMPILER`. Do not create `P3_SPEC_LOCK`, `P3_BUILD_LOCK`, repository implementation code, or Figma output from this candidate alone.
