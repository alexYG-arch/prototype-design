# P1-SPEC-06 Part Self Check

## Scope Check

- Candidate only: PASS.
- Repository implementation code changed: NO.
- Constitution, control, references, tooling, and skills changed: NO.
- Owned clauses covered: `DRD-CHARTER-010`, `DRD-CHARTER-015`.

## Coverage Check

| Requirement | Coverage |
|---|---|
| Candidate-only enforcement | `VALIDATION_CONTRACT.md`, `REVIEW_PROMOTION_CONTRACT.md`, `VALIDATION_LOCK_RULES.md` |
| Validator independence | `VALIDATION_CONTRACT.md`, `VALIDATION_LOCK_VALIDATOR_SPEC.md` |
| Human Gate review binding | `REVIEW_PROMOTION_CONTRACT.md`, `VALIDATION_LOCK_EXAMPLES.md` |
| Promotion state | `REVIEW_PROMOTION_CONTRACT.md`, `VALIDATION_LOCK_PROJECTIONS.md` |
| SPEC_LOCK and BUILD_LOCK | `LOCK_STATE_CONTRACT.md`, `VALIDATION_LOCK_IMPLEMENTATION_BLUEPRINT.md` |
| Invalidation | `INVALIDATION_CONTRACT.md`, `VALIDATION_LOCK_RULES.md`, `VALIDATION_LOCK_VALIDATOR_SPEC.md` |
| Validator version and hash binding | `VALIDATION_CONTRACT.md`, `VALIDATION_LOCK_VALIDATOR_SPEC.md`, `VALIDATION_LOCK_EXAMPLES.md` |
| Typed dependency edges | `INVALIDATION_CONTRACT.md`, `VALIDATION_LOCK_PROJECTIONS.md`, `VALIDATION_LOCK_IMPLEMENTATION_BLUEPRINT.md` |
| Structured partial unaffected claim | `INVALIDATION_CONTRACT.md`, `VALIDATION_LOCK_VALIDATOR_SPEC.md`, `VALIDATION_LOCK_EXAMPLES.md` |
| Lock supersession acyclicity | `LOCK_STATE_CONTRACT.md`, `VALIDATION_LOCK_RULES.md`, `VALIDATION_LOCK_VALIDATOR_SPEC.md` |
| Invalidation owner and required command | `INVALIDATION_CONTRACT.md`, `VALIDATION_LOCK_RULES.md`, `VALIDATION_LOCK_EXAMPLES.md` |
| Implementation traceability | `VALIDATION_LOCK_IMPLEMENTATION_BLUEPRINT.md` |

## Review Risks

Review should focus on:

1. Whether Candidate-only state blocks every path where Codex could self-approve.
2. Whether approval, promotion, and lock state are separated strongly enough.
3. Whether subject hash and review hash binding are deterministic and reproducible.
4. Whether validator code hash, schema hash, runtime identity, and version binding are strict enough.
5. Whether dependency graph edge types distinguish source, review, spec lock, build lock, validator, test, workpack, skill, and release dependencies.
6. Whether partial unaffected claims require enough structured evidence.
7. Whether invalidation covers artifacts, tests, locks, workpacks, skills, and release evidence.
8. Whether each invalidated subject has an owner and required command or workflow.
9. Whether transitive invalidation requires graph traversal rather than shallow file checks.
10. Whether lock supersession is explicit, acyclic, and old locks are never mutated.

## Self Check Result

This Candidate is ready for Human Gate review. It is not approved and not sealed.
