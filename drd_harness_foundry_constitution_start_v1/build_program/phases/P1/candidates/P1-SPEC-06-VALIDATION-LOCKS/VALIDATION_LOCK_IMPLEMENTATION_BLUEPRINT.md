# P1-SPEC-06 Validation Lock Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/validators/spec_validator.py` | Candidate output, required output, schema, placeholder, and review binding validation. | `repository/tests/validators/test_spec_validator.py` |
| `repository/src/drd_harness/validators/postflight.py` | Scope postflight and forbidden path checks. | `repository/tests/validators/test_postflight_scope.py` |
| `repository/src/drd_harness/validators/phase_gate.py` | Review, promotion, lock readiness, and invalidated evidence checks. | `repository/tests/orchestrator/test_promotion_lock_state.py` |
| `repository/src/drd_harness/orchestrator/invalidation.py` | Dependency graph traversal and transitive invalidation records. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/src/drd_harness/orchestrator/promotion.py` | Python-controlled promotion readiness and audit records. | `repository/tests/orchestrator/test_promotion_lock_state.py` |
| `repository/schemas/locks/spec_lock.schema.json` | SPEC_LOCK schema. | `repository/tests/orchestrator/test_promotion_lock_state.py` |
| `repository/schemas/locks/build_lock.schema.json` | BUILD_LOCK schema. | `repository/tests/orchestrator/test_promotion_lock_state.py` |
| `repository/schemas/locks/review_lock.schema.json` | Review lock schema. | `repository/tests/validators/test_spec_validator.py` |
| `repository/schemas/locks/validation_result.schema.json` | Validator result schema. | `repository/tests/validators/test_spec_validator.py` |
| `repository/schemas/locks/validator_identity.schema.json` | Validator code, schema, runtime, and version identity schema. | `repository/tests/validators/test_spec_validator.py` |
| `repository/schemas/locks/promotion_audit.schema.json` | Promotion audit schema. | `repository/tests/orchestrator/test_promotion_lock_state.py` |
| `repository/schemas/locks/invalidation_record.schema.json` | Invalidation record schema. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/schemas/locks/invalidation_recovery_plan.schema.json` | Invalidation recovery owner and required command schema. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/schemas/locks/dependency_graph.schema.json` | Dependency graph schema. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/schemas/locks/dependency_edge.schema.json` | Typed dependency edge schema. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/schemas/locks/partial_unaffected_claim.schema.json` | Partial unaffected claim schema. | `repository/tests/orchestrator/test_invalidation.py` |
| `repository/schemas/locks/lock_supersession.schema.json` | Lock supersession schema. | `repository/tests/orchestrator/test_invalidation.py` |

## Implementation Rules

### IMPL-VLOCK-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-VLOCK-002 Pure Validators

Validators must report findings and must not mutate Candidate semantic content.

### IMPL-VLOCK-003 Deterministic Hash Utilities

Subject hashes and lock root hashes must use deterministic ordered file path and sha256 records.

### IMPL-VLOCK-004 Graph Traversal Required

Invalidation must use dependency graph traversal rather than only scanning filenames.

### IMPL-VLOCK-005 Fixture Coverage

Tests must include positive and negative fixtures for:

- Candidate-only state.
- Codex self-approval rejection.
- Missing required output.
- Forbidden path change.
- Review hash mismatch.
- Validator result missing validator identity.
- Validator code hash or schema hash changed.
- Approved but not locked.
- SPEC_LOCK missing review decision hash.
- BUILD_LOCK missing SPEC_LOCK hash or test result.
- Deterministic lock hash reproduction.
- Upstream hash invalidating downstream artifact.
- Typed dependency edge coverage.
- Transitive invalidation.
- Partial unaffected claim with affected paths, unaffected paths, reason, validator result, and expiry.
- Invalidated subject missing recovery owner or required command.
- Invalidated test result used as evidence.
- Lock supersession without mutation.
- Lock supersession cycle rejection.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/validators repository/tests/orchestrator
```

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-010` | Candidate-only, review, promotion, validator identity, lock readiness | `validators/spec_validator.py`, `validators/phase_gate.py`, `orchestrator/promotion.py` | `VLOCK-CHECK-001`, `VLOCK-CHECK-004`, `VLOCK-CHECK-005`, `VLOCK-CHECK-006`, `VLOCK-CHECK-007`, `VLOCK-CHECK-008`, `VLOCK-CHECK-009`, `VLOCK-CHECK-015` |
| `DRD-CHARTER-015` | Typed dependency graph, invalidation, recovery plan, lock supersession | `orchestrator/invalidation.py`, `validators/phase_gate.py` | `VLOCK-CHECK-011`, `VLOCK-CHECK-012`, `VLOCK-CHECK-013`, `VLOCK-CHECK-014`, `VLOCK-CHECK-016`, `VLOCK-CHECK-017`, `VLOCK-CHECK-018`, `VLOCK-CHECK-019` |
