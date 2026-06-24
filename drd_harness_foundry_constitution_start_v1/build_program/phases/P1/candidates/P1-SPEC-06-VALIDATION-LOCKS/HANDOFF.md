# P1-SPEC-06 Validation Locks Handoff

## Candidate Status

`P1-SPEC-06-VALIDATION-LOCKS` has been generated as a Spec Candidate after Human Gate approval of `P1-SPEC-05-PRESENTATION-LAYOUT`.

This Candidate is not approved and not sealed. It does not authorize Harness business implementation.

## Generated Files

- `VALIDATION_CONTRACT.md`
- `REVIEW_PROMOTION_CONTRACT.md`
- `LOCK_STATE_CONTRACT.md`
- `INVALIDATION_CONTRACT.md`
- `VALIDATION_LOCK_RULES.md`
- `VALIDATION_LOCK_PROJECTIONS.md`
- `VALIDATION_LOCK_VALIDATOR_SPEC.md`
- `VALIDATION_LOCK_EXAMPLES.md`
- `VALIDATION_LOCK_IMPLEMENTATION_BLUEPRINT.md`
- `CANDIDATE_MANIFEST.json`
- `PART_SELF_CHECK.md`
- `HANDOFF.md`

## Human Review Focus

Reviewers should inspect:

1. Whether Candidate-only prevents Codex from approving, promoting, locking, or canonicalizing its own output.
2. Whether approval binds to exact subject hash and requires re-review after changes.
3. Whether approval, promotion, and lock state are distinct.
4. Whether SPEC_LOCK and BUILD_LOCK inputs are complete enough.
5. Whether validator identity binds code hash, schema hash, runtime identity, and version.
6. Whether dependency graph edges are typed by source, review, spec lock, build lock, validator, test, workpack, skill, and release dependency.
7. Whether partial unaffected claims are structured and evidence-bound.
8. Whether invalidation propagates across downstream artifacts, workpacks, tests, skills, locks, and release evidence.
9. Whether invalidated subjects have recovery owner and required command or workflow.
10. Whether invalidated evidence is blocked from current approval, build, lock, or release use.
11. Whether old locks are superseded rather than edited and supersession chains are acyclic.

## Next Authorized Action

The next action is validation and Human Gate review of this Candidate. If approved by the user, the chain may continue to `P1-SPEC-07-COMPILER-CONSERVATION`. This handoff does not grant permission to implement Harness code.
