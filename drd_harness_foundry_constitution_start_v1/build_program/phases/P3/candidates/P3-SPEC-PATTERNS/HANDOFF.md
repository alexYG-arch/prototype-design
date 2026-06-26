# P3-SPEC-PATTERNS Handoff

## Candidate

- Workpack: `P3-SPEC-PATTERNS`
- Phase: `P3`
- Lane: `SPEC`
- Module: `shared_component_and_information_patterns`
- Upstream approved candidate: `P3-SPEC-ELEMENTS`

## What This Candidate Defines

`P3-SPEC-PATTERNS` defines semantic shared component patterns, information presentation decisions, and consistency exceptions over the approved element universe. It blocks visual-only reuse, requires message presentation coverage, and leaves carrier-specific layout decisions to `P3-SPEC-LAYOUT`.

## Review Focus

1. Confirm that reuse is semantic and not based on visual similarity.
2. Confirm that pattern refs consume only canonical elements, approved messages, or approved exceptions.
3. Confirm that every approved interaction message has presentation coverage and no unknown message refs are introduced.
4. Confirm that equivalent information cannot use different modes without an approved exception.
5. Confirm that the candidate does not define layout carrier, containment, ordering, width, height, scroll, or z-axis behavior.

## Next Action

If accepted, continue with `P3-SPEC-LAYOUT`. Do not create `P3_SPEC_LOCK`, `P3_BUILD_LOCK`, or repository implementation code from this candidate alone.
