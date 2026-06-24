# P1-SPEC-06 Validation Lock Examples

## Positive Example: Review Binding

```json
{
  "decision_id": "P1-SPEC-05-PRESENTATION-LAYOUT-REVIEW-001",
  "subject_hash": "2749676726510e6c64448df120e1be2bf33a306ae317cf3280e0ee4c57fd8472",
  "decision": "APPROVED",
  "reviewer": "human-user",
  "open_blockers": [],
  "approved_sections": [
    "NATURAL_LANGUAGE_LAYOUT_CONTRACT.md",
    "PRESENTATION_LAYOUT_VALIDATOR_SPEC.md"
  ]
}
```

Why this passes:

- Approval binds to a concrete subject hash.
- Open blockers are empty.
- Approved sections are explicit.

## Negative Example: Self Approval

```json
{
  "workpack_id": "P1-SPEC-06-VALIDATION-LOCKS",
  "approval_state": "APPROVED_BY_CODEX",
  "seal_state": "LOCKED"
}
```

Expected result: fail.

Reason:

- Codex cannot approve or lock its own output.

## Negative Example: Stale Review Hash

```json
{
  "decision_id": "P1-SPEC-05-REVIEW-001",
  "subject_hash": "old_hash",
  "decision": "APPROVED"
}
```

Expected result: fail when current Candidate output hash differs.

Reason:

- Approval applies only to the reviewed subject hash.

## Positive Example: Invalidation Record

```json
{
  "invalidation_id": "INV-P1-0001",
  "cause": "UPSTREAM_HASH_CHANGED",
  "changed_dependency": "P1-SPEC-05-PRESENTATION-LAYOUT/SPEC_LOCK",
  "old_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "new_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "affected_subjects": [
    "P1-IMPLEMENT-05-PRESENTATION-LAYOUT",
    "repository/tests/layout/test_layout_completeness.py"
  ],
  "required_action": "revalidate_rebuild_retest",
  "recovery_owner": "P1-IMPLEMENT-05 owner",
  "required_command": "python -m pytest repository/tests/layout",
  "due_before_consumption": true,
  "blocking_state": true,
  "created_by_runtime": "python"
}
```

Why this passes:

- It names the changed dependency, old and new hashes, affected subjects, action, and blocking state.
- It names recovery owner and executable command.

## Positive Example: Validator Identity

```json
{
  "validator_id": "spec_validator",
  "validator_kind": "python_module",
  "validator_version": "1.0.0",
  "validator_code_hash": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "schema_hashes": {
    "review_decision.schema.json": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
  },
  "runtime_identity": "python-3.12",
  "result_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
}
```

Why this passes:

- The result can be reproduced against a concrete validator and schema identity.

## Positive Example: Typed Dependency Edge

```json
{
  "edge_id": "DEP-P1-0001",
  "edge_type": "SPEC_LOCK_DEPENDENCY",
  "source_subject": "P1-SPEC-05-PRESENTATION-LAYOUT/SPEC_LOCK",
  "target_subject": "P1-IMPLEMENT-05-PRESENTATION-LAYOUT",
  "upstream_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "downstream_binding_field": "spec_lock_hash",
  "invalidation_behavior": "invalidate_target_and_tests"
}
```

Why this passes:

- The graph explains why the downstream subject depends on the upstream hash.

## Positive Example: Partial Unaffected Claim

```json
{
  "claim_id": "UNAFFECTED-P1-0001",
  "changed_dependency": "P1-SPEC-05 layout carrier profile",
  "affected_paths": [
    "repository/tests/layout/test_carrier_adaptation_profile.py"
  ],
  "unaffected_paths": [
    "repository/tests/presentation/test_shared_component_registry.py"
  ],
  "reason": "The change only affects carrier adaptation schemas; shared component registry schema and fixtures do not depend on carrier profiles.",
  "validator_result_ref": "validation_result:shared_component_registry:2026-06-24",
  "review_required": false,
  "expires_on_dependency_change": [
    "shared_component_registry.schema.json"
  ]
}
```

Why this passes:

- The unaffected claim is structured and evidence-bound.

## Negative Example: Lock Missing Review

```json
{
  "lock_id": "SPEC-LOCK-P1-001",
  "phase": "P1",
  "files": [],
  "root_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
}
```

Expected result: fail.

Reason:

- SPEC_LOCK readiness must include approved files, review decision hashes, validator result hashes, and source lock refs.

## Negative Example: Invalidated Test Used As Evidence

```json
{
  "test_result_id": "TEST-P1-001",
  "bound_spec_lock_hash": "old_hash",
  "used_for_build_lock": true,
  "invalidation_state": "INVALIDATED"
}
```

Expected result: fail.

Reason:

- Invalidated evidence cannot justify current build or lock state.

## Negative Example: Supersession Cycle

```json
{
  "lock_id": "SPEC-LOCK-P1-003",
  "supersedes": ["SPEC-LOCK-P1-002"],
  "known_superseded_by": ["SPEC-LOCK-P1-004"],
  "cycle_path": ["SPEC-LOCK-P1-003", "SPEC-LOCK-P1-002", "SPEC-LOCK-P1-004", "SPEC-LOCK-P1-003"]
}
```

Expected result: fail.

Reason:

- Lock supersession must be acyclic.

## Negative Example: Unowned Invalidation

```json
{
  "invalidation_id": "INV-P1-0002",
  "cause": "VALIDATOR_VERSION_CHANGED",
  "affected_subjects": ["BUILD-LOCK-P1-001"],
  "required_action": "retest",
  "blocking_state": false
}
```

Expected result: fail.

Reason:

- The invalidation has no recovery owner and no required command or workflow.
