# P1-SPEC-06 Validation Lock Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `candidate_only_validator` | Ensures Codex output stays Candidate until approval and promotion. |
| `required_output_validator` | Ensures manifest-required outputs exist, are non-empty, and are syntax-valid when structured. |
| `scope_postflight_validator` | Ensures changed paths are allowed and forbidden paths are untouched. |
| `validator_independence_validator` | Ensures validator result is independent from generator self-approval. |
| `review_binding_validator` | Ensures Human Gate decision subject hash matches current Candidate outputs. |
| `promotion_readiness_validator` | Ensures validation, review, upstream binding, and invalidation state allow promotion. |
| `spec_lock_readiness_validator` | Ensures SPEC_LOCK inputs are complete and hash-bound. |
| `build_lock_readiness_validator` | Ensures BUILD_LOCK inputs include spec lock, git commit, outputs, and test evidence. |
| `dependency_graph_validator` | Ensures downstream subjects declare upstream hash dependencies. |
| `invalidation_propagation_validator` | Ensures upstream hash changes invalidate all affected downstream subjects. |
| `lock_supersession_validator` | Ensures old locks are superseded rather than mutated. |

## Checks

### VLOCK-CHECK-001 Candidate-Only State

Fail if Codex output declares itself approved, promoted, locked, or canonical without Human Gate and Python-controlled promotion evidence.

### VLOCK-CHECK-002 Required Output Coverage

Fail if any manifest-required output is missing, empty, invalid JSON when JSON, or contains known placeholder marker strings.

### VLOCK-CHECK-003 Scope Postflight

Fail if changed files include forbidden paths or paths outside the current workpack allowed scope.

### VLOCK-CHECK-004 Validator Independence

Fail if the only validation evidence is a statement from the same Codex generation artifact being checked.

### VLOCK-CHECK-005 Review Binding

Fail if review decision `subject_hash` does not match the deterministic hash of the current reviewed outputs.

### VLOCK-CHECK-006 Promotion Readiness

Fail if validation results, approval, upstream review or lock binding, and invalidation state are not all present and passing.

### VLOCK-CHECK-007 Approved Is Not Locked

Fail if a Candidate treats `APPROVED_BY_HUMAN` as equivalent to `LOCKED` or as permission to bypass lock creation.

### VLOCK-CHECK-008 SPEC_LOCK Input Completeness

Fail if SPEC_LOCK readiness omits approved spec files, review decision hashes, validator result hashes, source lock refs, or ordered file hashes.

### VLOCK-CHECK-009 BUILD_LOCK Input Completeness

Fail if BUILD_LOCK readiness omits git commit, SPEC_LOCK hash, build output hashes, test results, or invalidation dependencies.

### VLOCK-CHECK-010 Deterministic Lock Hash

Fail if root lock hash cannot be reproduced from deterministic ordered path and sha256 records.

### VLOCK-CHECK-011 Dependency Graph Completeness

Fail if a downstream artifact, lock, workpack, skill, test result, or release artifact lacks required upstream hash dependency edges.

### VLOCK-CHECK-012 Invalidation Propagation

Fail if an upstream hash changed and affected downstream subjects are not marked `INVALIDATED` or proven unaffected by dependency analysis.

### VLOCK-CHECK-013 Invalidated Evidence Block

Fail if invalidated tests, locks, artifacts, workpacks, or skills are used as current approval, lock, build, or release evidence.

### VLOCK-CHECK-014 Lock Supersession

Fail if an existing lock is edited in place or supersession does not identify old lock IDs and invalidation impact.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/locks/spec_lock.schema.json`
- `repository/schemas/locks/build_lock.schema.json`
- `repository/schemas/locks/review_lock.schema.json`
- `repository/schemas/locks/validation_result.schema.json`
- `repository/schemas/locks/promotion_audit.schema.json`
- `repository/schemas/locks/invalidation_record.schema.json`
- `repository/schemas/locks/dependency_graph.schema.json`
- `repository/schemas/locks/lock_supersession.schema.json`
