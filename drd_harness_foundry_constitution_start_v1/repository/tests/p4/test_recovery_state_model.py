from drd_harness.orchestrator.recovery import (
    REQUIRED_RUN_STATE_FIELDS,
    reject_semantic_recovery_fields,
    resolve_resume_decision,
    validate_run_state_shape,
)


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


def test_validate_run_state_shape_requires_all_contract_fields():
    state = valid_run_state()
    for field in REQUIRED_RUN_STATE_FIELDS:
        bad = dict(state)
        bad.pop(field)
        assert field in validate_run_state_shape(bad)


def test_resume_blocks_unsafe_state_when_required_field_is_missing():
    state = valid_run_state()
    state.pop("output_hashes")

    report = resolve_resume_decision(state, "node-1")

    assert report["decision"] == "BLOCK_UNSAFE_STATE"
    assert "FAILURE_RECORD_INCOMPLETE" in report["node_decisions"][0]["reason_codes"]


def test_recovery_rejects_semantic_fill_fields():
    forbidden = reject_semantic_recovery_fields({"business_contracts": [], "product_requirements": []})

    assert forbidden == ["business_contracts", "product_requirements"]
