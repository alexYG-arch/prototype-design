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
| `validator_identity_validator` | Ensures validation evidence binds validator code hash, schema hash, runtime identity, and version. |
| `dependency_edge_type_validator` | Ensures dependency graph edges declare source, review, spec lock, build lock, validator, test, workpack, skill, or release type. |
| `partial_unaffected_claim_validator` | Ensures partial unaffected claims are structured and evidence-bound. |
| `invalidation_recovery_plan_validator` | Ensures invalidated subjects name owner and required command or workflow. |
| `supersession_acyclicity_validator` | Ensures lock supersession graph is acyclic. |

## Checks

### VLOCK-CHECK-001 Candidate-Only State

Fail if Codex output declares itself approved, promoted, locked, or canonical without Human Gate and Python-controlled promotion evidence.

### VLOCK-CHECK-002 Required Output Coverage

Fail if any manifest-required output is missing, empty, invalid JSON when JSON, or contains known placeholder marker strings.

### VLOCK-CHECK-003 Scope Postflight

Fail if changed files include forbidden paths or paths outside the current workpack allowed scope.

### VLOCK-CHECK-004 Validator Independence

Fail if the only validation evidence is a statement from the same Codex generation artifact being checked.

Fail if validation evidence lacks validator code hash, schema hash, runtime identity, or version.

### VLOCK-CHECK-005 Review Binding

Fail if review decision `subject_hash` does not match the deterministic hash of the current reviewed outputs.

### VLOCK-CHECK-006 Promotion Readiness

Fail if validation results, approval, upstream review or lock binding, and invalidation state are not all present and passing.

### VLOCK-CHECK-007 Approved Is Not Locked

Fail if a Candidate treats `APPROVED_BY_HUMAN` as equivalent to `LOCKED` or as permission to bypass lock creation.

### VLOCK-CHECK-008 SPEC_LOCK Input Completeness

Fail if SPEC_LOCK readiness omits approved spec files, review decision hashes, validator result hashes, source lock refs, or ordered file hashes.

Fail if validator identity hashes are omitted for validator results used by SPEC_LOCK readiness.

### VLOCK-CHECK-009 BUILD_LOCK Input Completeness

Fail if BUILD_LOCK readiness omits git commit, SPEC_LOCK hash, build output hashes, test results, or invalidation dependencies.

Fail if validator identity hashes are omitted for build validation or test evidence acceptance.

### VLOCK-CHECK-010 Deterministic Lock Hash

Fail if root lock hash cannot be reproduced from deterministic ordered path and sha256 records.

### VLOCK-CHECK-011 Dependency Graph Completeness

Fail if a downstream artifact, lock, workpack, skill, test result, or release artifact lacks required upstream hash dependency edges.

Fail if dependency edges lack declared edge type or use an edge type outside the approved dependency edge enum.

### VLOCK-CHECK-012 Invalidation Propagation

Fail if an upstream hash changed and affected downstream subjects are not marked `INVALIDATED` or proven unaffected by dependency analysis.

Fail if a partial unaffected claim is prose-only or lacks affected paths, unaffected paths, reason, validator result reference, review requirement, and dependency expiry.

### VLOCK-CHECK-013 Invalidated Evidence Block

Fail if invalidated tests, locks, artifacts, workpacks, or skills are used as current approval, lock, build, or release evidence.

### VLOCK-CHECK-014 Lock Supersession

Fail if an existing lock is edited in place or supersession does not identify old lock IDs and invalidation impact.

Fail if the lock supersession graph contains a direct or transitive cycle.

### VLOCK-CHECK-015 Validator Identity Binding

Fail if a validation result used for approval, promotion, lock readiness, unaffected claim, build evidence, or release evidence does not bind validator code hash, schema hash, runtime identity, and version.

### VLOCK-CHECK-016 Typed Dependency Edges

Fail if dependency graph edges do not identify one of the approved edge types: source, review, spec lock, build lock, validator, test evidence, workpack, skill, or release.

### VLOCK-CHECK-017 Partial Unaffected Claim Structure

Fail if an unaffected claim lacks `affected_paths`, `unaffected_paths`, `reason`, `validator_result_ref`, `review_required`, or `expires_on_dependency_change`.

### VLOCK-CHECK-018 Invalidation Recovery Ownership

Fail if an invalidated subject lacks recovery owner and required command or workflow before leaving blocking state.

### VLOCK-CHECK-019 Supersession Acyclicity

Fail if lock supersession traversal finds that a lock directly or transitively supersedes itself.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/locks/spec_lock.schema.json`
- `repository/schemas/locks/build_lock.schema.json`
- `repository/schemas/locks/review_lock.schema.json`
- `repository/schemas/locks/validation_result.schema.json`
- `repository/schemas/locks/validator_identity.schema.json`
- `repository/schemas/locks/promotion_audit.schema.json`
- `repository/schemas/locks/invalidation_record.schema.json`
- `repository/schemas/locks/invalidation_recovery_plan.schema.json`
- `repository/schemas/locks/dependency_graph.schema.json`
- `repository/schemas/locks/dependency_edge.schema.json`
- `repository/schemas/locks/partial_unaffected_claim.schema.json`
- `repository/schemas/locks/lock_supersession.schema.json`
