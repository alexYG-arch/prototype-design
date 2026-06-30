from drd_harness.orchestrator.recovery import REASON_CODES, classify_invalidation, resolve_resume_decision


def valid_run_state():
    return {
        "run_id": "run-1",
        "program_id": "program-1",
        "driver_version": "p4-impl-01",
        "original_command": "run",
        "adapter_id": "markdown_prd_adapter",
        "source_refs": ["source.md"],
        "input_hashes": {"source.md": "a" * 64},
        "upstream_lock_refs": {"P3_BUILD_LOCK": "b" * 64},
        "candidate_subject_hashes": {"candidate": "c" * 64},
        "review_decision_hashes": {"review": "d" * 64},
        "dag_snapshot_hash": "e" * 64,
        "execution_plan_hash": "f" * 64,
        "node_states": {"node-1": {"state": "NODE_COMPLETED"}},
        "written_paths": ["out/result.json"],
        "output_hashes": {"out/result.json": "1" * 64},
        "gate_states": {},
        "failure_records": {},
        "recovery_history": [],
    }


def test_invalidation_records_are_structured_and_sorted():
    state = valid_run_state()
    records = classify_invalidation(
        state,
        "node-1",
        {
            "review_decision_hashes": {"review": "9" * 64},
            "candidate_subject_hashes": {"candidate": "8" * 64},
            "written_paths": ["out/result.json", "out/extra.json"],
        },
    )

    rows = [record.__dict__ for record in records]
    assert [row["reason_code"] for row in rows] == sorted(row["reason_code"] for row in rows)
    for row in rows:
        assert row["reason_code"] in REASON_CODES
        assert {
            "reason_code",
            "affected_node_id",
            "affected_path",
            "prior_value",
            "current_value",
            "required_stop_rule",
            "human_gate_required",
        } <= set(row)


def test_review_decision_drift_blocks_human_gate():
    state = valid_run_state()
    report = resolve_resume_decision(
        state,
        "node-1",
        current_evidence={"review_decision_hashes": {"review": "9" * 64}},
    )

    assert report["decision"] == "BLOCK_HUMAN_GATE"
    assert report["invalidation_records"][0]["reason_code"] == "REVIEW_DECISION_HASH_CHANGED"


def test_requested_node_not_in_dag_blocks_unsafe_state():
    report = resolve_resume_decision(valid_run_state(), "missing-node")

    assert report["decision"] == "BLOCK_UNSAFE_STATE"
    assert report["invalidation_records"][0]["reason_code"] == "REQUESTED_NODE_NOT_IN_DAG"
