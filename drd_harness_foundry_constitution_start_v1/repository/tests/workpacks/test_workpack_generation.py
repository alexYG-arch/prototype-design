from drd_harness.orchestrator.workpacks import (
    compute_workpack_readiness_state,
    emit_candidate_workpack_envelope,
    validate_workpack_candidate_boundary,
)
from drd_harness.validators.workpack_scope import (
    detect_scope_disputes,
    validate_allowed_write_paths,
    validate_forbidden_write_paths,
    validate_required_output_family_coverage,
    validate_spec_before_code,
    validate_workpack_readiness,
)


def test_workpack_is_blocked_before_spec_lock(workpack):
    blocked = workpack(required_spec_locks=[], status="WAITING_UPSTREAM_LOCK")

    assert compute_workpack_readiness_state(blocked) == "WAITING_UPSTREAM_LOCK"
    assert "SW-CHECK-001" in {finding.code for finding in validate_spec_before_code(blocked)}


def test_workpack_is_ready_with_current_spec_lock_refs(workpack):
    ready = workpack()

    assert compute_workpack_readiness_state(ready) == "READY"
    assert validate_workpack_readiness(ready) == []


def test_missing_output_family_lock_blocks_workpack(workpack):
    blocked = workpack(required_output_family_locks=[], status="WAITING_UPSTREAM_LOCK")

    assert compute_workpack_readiness_state(blocked) == "WAITING_UPSTREAM_LOCK"
    assert "SW-CHECK-002" in {finding.code for finding in validate_required_output_family_coverage(blocked)}


def test_candidate_envelope_cannot_self_approve_promote_or_lock(workpack):
    envelope = emit_candidate_workpack_envelope(workpack())

    assert envelope["status"] == "CANDIDATE"
    assert envelope["approval_state"] == "NOT_APPROVED"
    assert envelope["promotion_state"] == "NOT_PROMOTED"
    assert envelope["build_lock_state"] == "NOT_LOCKED"

    bad = dict(envelope, approval_state="APPROVED", promotion_state="PROMOTED", build_lock_state="LOCKED")
    assert "SW-CHECK-010" in {finding.code for finding in validate_workpack_candidate_boundary(bad)}


def test_code_targets_and_changed_paths_stay_inside_scope(workpack):
    scoped = workpack(
        code_targets=["repository/src/drd_harness/orchestrator/workpacks.py"],
        changed_paths=["control/locks/P1_SPEC_LOCK.json"],
    )

    assert validate_allowed_write_paths(scoped) == []
    assert "SW-CHECK-006" in {finding.code for finding in validate_forbidden_write_paths(scoped)}


def test_readiness_rejects_forbidden_scope_even_when_fields_exist(workpack):
    scoped = workpack(
        code_targets=["control/locks/P1_SPEC_LOCK.json"],
        changed_paths=[],
        status="READY",
    )

    assert compute_workpack_readiness_state(scoped) == "REVIEW_REQUIRED"
    codes = {finding.code for finding in validate_workpack_readiness(scoped)}

    assert {"SW-CHECK-006", "SW-CHECK-010"} <= codes


def test_scope_dispute_routes_to_human_gate(workpack):
    findings = detect_scope_disputes(workpack(scope_dispute=True))

    assert findings[0].code == "SW-CHECK-017"
