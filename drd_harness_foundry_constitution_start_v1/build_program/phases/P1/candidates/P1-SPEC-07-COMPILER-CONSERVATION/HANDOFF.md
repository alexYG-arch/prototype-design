# P1-SPEC-07 Compiler Conservation Handoff

## Candidate Status

`P1-SPEC-07-COMPILER-CONSERVATION` has been generated as a Spec Candidate after Human Gate approval of `P1-SPEC-06-VALIDATION-LOCKS`.

This Candidate is not approved and not sealed. It does not authorize Harness business implementation.

## Generated Files

- `COMPILER_CONSERVATION_CONTRACT.md`
- `FINAL_DRD_ASSEMBLY_RULES.md`
- `COMPILER_INPUT_BOUNDARY_RULES.md`
- `COMPILER_PROJECTIONS.md`
- `COMPILER_VALIDATOR_SPEC.md`
- `COMPILER_EXAMPLES.md`
- `COMPILER_IMPLEMENTATION_BLUEPRINT.md`
- `CANDIDATE_MANIFEST.json`
- `PART_SELF_CHECK.md`
- `HANDOFF.md`

## Human Review Focus

Reviewers should inspect:

1. Whether `DRD-05` is limited to deterministic Python assembly.
2. Whether compiler inputs are closed, approved, hash-bound, and free from unapproved Candidates or Codex rewrites.
3. Whether final assembly forbids adding pages, states, CTAs, components, interactions, presentation modes, layout decisions, and user-facing copy.
4. Whether semantic unit inventory is atomic enough that one row cannot hide multiple decisions such as a screen plus its states, CTAs, copy, interactions, and layout.
5. Whether conservation checks detect semantic additions, semantic omissions, hash drift, unapproved inputs, non-atomic inventory, and nondeterministic output.
6. Whether final DRD manifest, TOC, reference index, hash index, input bundle, atomic inventory, and conservation report are sufficient for downstream validation.
7. Whether missing input, conflict, or incomplete upstream semantics route to Human Gate instead of compiler repair.
8. Whether `DRD-06` read-only QA can report findings without mutating compiled outputs, approved inputs, manifests, locks, or review decisions.

## Next Authorized Action

The next action is validation and Human Gate review of this Candidate. If approved by the user, the chain may continue to `P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY`. This handoff does not grant permission to implement Harness code.
