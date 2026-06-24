# P1-SPEC-05 Presentation Layout Handoff

## Candidate Status

`P1-SPEC-05-PRESENTATION-LAYOUT` has been generated as a Spec Candidate after Human Gate approval of `P1-SPEC-04-INTERACTION-CLOSURE`.

This Candidate is not approved and not sealed. It does not authorize Harness business implementation.

## Generated Files

- `SHARED_COMPONENT_CONTRACT.md`
- `INFORMATION_PRESENTATION_CONTRACT.md`
- `NATURAL_LANGUAGE_LAYOUT_CONTRACT.md`
- `FIGMA_COMPATIBILITY_CONTRACT.md`
- `PRESENTATION_LAYOUT_RULES.md`
- `PRESENTATION_LAYOUT_PROJECTIONS.md`
- `PRESENTATION_LAYOUT_VALIDATOR_SPEC.md`
- `PRESENTATION_LAYOUT_EXAMPLES.md`
- `PRESENTATION_LAYOUT_IMPLEMENTATION_BLUEPRINT.md`
- `CANDIDATE_MANIFEST.json`
- `PART_SELF_CHECK.md`
- `HANDOFF.md`

## Human Review Focus

Reviewers should inspect:

1. Whether shared components require semantic compatibility and reject visual-only reuse.
2. Whether equivalent information uses consistent presentation modes.
3. Whether sustained decision information cannot be transient-only.
4. Whether natural-language layout prose is complete enough for review and reconstruction.
5. Whether carrier-specific adaptation covers desktop, tablet, mobile, iOS, and Material profiles.
6. Whether containment is multi-level and coupled to arrangement, ordering, sizing, and scroll behavior.
7. Whether Material z-axis and all layered surfaces declare layer order, occlusion, blocking, and focus restoration.
8. Whether layout preserves complete information under height changes while obeying width constraints.
9. Whether variable content growth behavior is explicit.
10. Whether interaction messages from P1-SPEC-04 are placed in layout.
11. Whether Figma metadata supports reconstruction but does not authorize API, renderer, or writer behavior.

## Next Authorized Action

The next action is validation and Human Gate review of this Candidate. If approved by the user, the chain may continue to `P1-SPEC-06-VALIDATION-LOCKS`. This handoff does not grant permission to implement Harness code.
