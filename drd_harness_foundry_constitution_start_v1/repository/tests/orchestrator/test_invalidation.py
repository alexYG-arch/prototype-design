from drd_harness.orchestrator.invalidation import (
    DependencyEdge,
    DependencyEdgeType,
    InvalidationCause,
    InvalidationRecoveryPlan,
    LockSupersession,
    PartialUnaffectedClaim,
    build_invalidation_record,
    downstream_subjects,
    reject_invalidated_evidence,
    validate_dependency_edges,
    validate_invalidation_record,
    validate_lock_supersession_acyclic,
    validate_partial_unaffected_claim,
    validate_recovery_plan,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def edge(source, target, edge_id):
    return DependencyEdge(
        edge_id=edge_id,
        edge_type=DependencyEdgeType.SPEC_LOCK_DEPENDENCY,
        source_subject=source,
        target_subject=target,
        upstream_hash=HASH_A,
        downstream_binding_field="spec_lock_hash",
        invalidation_behavior="invalidate_target_and_tests",
    )


def test_dependency_graph_tracks_typed_transitive_downstream_subjects():
    edges = [
        edge("P1-SPEC-LOCK", "P1-IMPLEMENT-06", "DEP-1"),
        edge("P1-IMPLEMENT-06", "P1-BUILD-LOCK", "DEP-2"),
    ]

    assert validate_dependency_edges(edges) == []
    assert downstream_subjects(edges, "P1-SPEC-LOCK") == ["P1-BUILD-LOCK", "P1-IMPLEMENT-06"]


def test_dependency_edge_rejects_undeclared_edge_type():
    bad_edge = DependencyEdge(
        edge_id="DEP-BAD",
        edge_type="BAD_EDGE_TYPE",
        source_subject="P1-SPEC-LOCK",
        target_subject="P1-IMPLEMENT-06",
        upstream_hash=HASH_A,
        downstream_binding_field="spec_lock_hash",
        invalidation_behavior="invalidate_target_and_tests",
    )

    findings = validate_dependency_edges([bad_edge])

    assert "VLOCK-CHECK-011" in {finding.code for finding in findings}
    assert "edge_type" in findings[0].message


def test_invalidation_record_requires_owner_command_and_blocking_state():
    record = build_invalidation_record(
        "INV-P1-0001",
        InvalidationCause.UPSTREAM_HASH_CHANGED,
        "P1-SPEC-LOCK",
        HASH_A,
        HASH_B,
        ["P1-IMPLEMENT-06"],
        "revalidate_retest",
        "P1-IMPLEMENT-06 owner",
        "python3 -m pytest repository/tests/validators repository/tests/orchestrator",
    )

    assert validate_invalidation_record(record) == []


def test_invalidated_evidence_cannot_be_used_for_lock():
    findings = reject_invalidated_evidence(
        {
            "test_result_id": "TEST-P1-001",
            "used_for_build_lock": True,
            "invalidation_state": "INVALIDATED",
        }
    )

    assert findings[0].code == "VLOCK-CHECK-014"


def test_partial_unaffected_claim_requires_structured_evidence():
    claim = PartialUnaffectedClaim(
        claim_id="UNAFFECTED-P1-0001",
        changed_dependency="P1-SPEC-LOCK",
        affected_paths=["repository/tests/orchestrator/test_invalidation.py"],
        unaffected_paths=["repository/tests/layout/test_layout_completeness.py"],
        reason="The changed dependency only binds validation lock orchestration.",
        validator_result_ref="validation_result:P1-IMPLEMENT-06",
        review_required=False,
        expires_on_dependency_change=["repository/src/drd_harness/orchestrator/invalidation.py"],
    )

    assert validate_partial_unaffected_claim(claim) == []


def test_recovery_plan_requires_owner_and_executable_command():
    plan = InvalidationRecoveryPlan(
        plan_id="RECOVER-P1-0001",
        invalidation_ids=["INV-P1-0001"],
        affected_subjects=["P1-IMPLEMENT-06"],
        recovery_owner="P1-IMPLEMENT-06 owner",
        required_command="python3 -m pytest repository/tests/validators repository/tests/orchestrator",
        exit_criteria=["validation passes", "review binding refreshed"],
    )

    assert validate_recovery_plan(plan) == []


def test_lock_supersession_cycle_is_rejected():
    findings = validate_lock_supersession_acyclic(
        [
            LockSupersession("LOCK-A", ["LOCK-B"]),
            LockSupersession("LOCK-B", ["LOCK-C"]),
            LockSupersession("LOCK-C", ["LOCK-A"]),
        ]
    )

    assert findings[0].code == "VLOCK-CHECK-018"
