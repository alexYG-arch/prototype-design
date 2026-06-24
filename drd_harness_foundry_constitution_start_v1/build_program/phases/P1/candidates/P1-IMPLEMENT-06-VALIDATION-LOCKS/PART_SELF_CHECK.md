# P1-IMPLEMENT-06 Self Check

## Scope

This implementation candidate stays inside validation, orchestration, lock schema, and test paths. It does not edit constitution, control locks, source references, tooling, or skills.

## Contract Coverage

The implementation covers:

1. Candidate-only state checks.
2. Required output coverage checks.
3. Scope postflight checks.
4. Validator identity binding.
5. Review decision to subject hash binding.
6. Promotion readiness checks.
7. SPEC_LOCK and BUILD_LOCK readiness checks.
8. Typed dependency graph and transitive invalidation.
9. Invalidated evidence blocking.
10. Partial unaffected claim structure.
11. Invalidation recovery ownership and executable command.
12. Lock supersession acyclicity.
13. Validation result field alignment with the lock schema.
14. Candidate output path containment inside the candidate directory.
15. Failed validator or test exit codes blocking lock readiness.
16. Canonical lock root verification during readiness checks.
17. Runtime validation of dependency edge types.

## Authority Boundary

The workpack does not approve itself, does not promote itself, and does not create a canonical lock. It prepares deterministic checks and records for human review and later Python-controlled lock steps.

## Validation

Local validation passed with `python3`:

- `python3 -m pytest repository/tests/validators repository/tests/orchestrator -q`: 34 passed.
- `python3 -m pytest repository/tests/kernel repository/tests/stages repository/tests/reasoning repository/tests/interaction repository/tests/presentation repository/tests/layout repository/tests/validators repository/tests/orchestrator -q`: 158 passed.

The local shell has no `python` executable, so the blueprint command form using `python` is recorded as environment-blocked rather than failed.
