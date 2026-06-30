import json
from pathlib import Path

from drd_harness.cli.main import main
from drd_harness.kernel.hashline import sha256_file
from drd_harness.orchestrator.recovery import resolve_resume_decision


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


def test_resume_skips_completed_node_when_hashes_match():
    report = resolve_resume_decision(valid_run_state(), "node-1")

    assert report["decision"] == "SKIP"
    assert report["skipped_nodes"] == ["node-1"]
    assert report["replayed_nodes"] == []


def test_resume_replays_when_only_declared_output_hash_changed():
    state = valid_run_state()
    report = resolve_resume_decision(
        state,
        "node-1",
        current_evidence={"output_hashes": {"out/result.json": "2" * 64}},
    )

    assert report["decision"] == "REPLAY"
    assert report["replayed_nodes"] == ["node-1"]
    assert report["invalidation_records"][0]["reason_code"] == "OUTPUT_HASH_CHANGED"


def test_resume_blocks_on_input_hash_drift():
    state = valid_run_state()
    report = resolve_resume_decision(
        state,
        "node-1",
        current_evidence={"input_hashes": {"source.md": "9" * 64}},
    )

    assert report["decision"] == "BLOCK_INVALIDATION"
    assert report["blocked_nodes"] == ["node-1"]
    assert report["invalidation_records"][0]["reason_code"] == "INPUT_HASH_CHANGED"


def test_resume_routes_upstream_lock_drift_to_human_gate():
    state = valid_run_state()
    report = resolve_resume_decision(
        state,
        "node-1",
        current_evidence={"upstream_lock_refs": {"P3_BUILD_LOCK": "9" * 64}},
    )

    assert report["decision"] == "BLOCK_HUMAN_GATE"
    assert report["blocked_nodes"] == ["node-1"]
    assert report["invalidation_records"][0]["reason_code"] == "UPSTREAM_LOCK_HASH_CHANGED"
    assert report["invalidation_records"][0]["required_stop_rule"] == "BLOCK_HUMAN_GATE"


def test_resume_blocks_lock_boundary_gate():
    state = valid_run_state()
    state["gate_states"] = {"node-1": {"gate_type": "LOCK_GATE", "lock_requested": True}}

    report = resolve_resume_decision(state, "node-1")

    assert report["decision"] == "BLOCK_LOCK_BOUNDARY"
    assert report["next_allowed_actions"] == ["REQUEST_EXPLICIT_LOCK_AUTHORIZATION"]


def test_resume_repairs_output_drift_before_lock_boundary():
    state = valid_run_state()
    state["gate_states"] = {"node-1": {"gate_type": "LOCK_GATE", "lock_requested": True}}

    report = resolve_resume_decision(
        state,
        "node-1",
        current_evidence={"output_hashes": {"out/result.json": "MISSING"}},
    )

    assert report["decision"] == "REPLAY"
    assert report["next_allowed_actions"] == ["REPLAY_DECLARED_NODE_OUTPUTS"]
    assert report["invalidation_records"][0]["reason_code"] == "OUTPUT_MISSING"


def test_cli_resume_uses_recovery_when_run_state_file_exists(tmp_path: Path, capsys):
    output = tmp_path / "out" / "result.json"
    output.parent.mkdir()
    output.write_text('{"ok": true}\n', encoding="utf-8")
    state = valid_run_state()
    state["written_paths"] = [str(output)]
    state["output_hashes"] = {str(output): sha256_file(output)}
    state_path = tmp_path / "run_state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    exit_code = main(["resume", "--run-state-ref", str(state_path), "--requested-resume-node", "node-1"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["resume_eligibility"] == "SKIP"
    assert payload["resume_decision_report"]["decision"] == "SKIP"


def test_cli_resume_rechecks_declared_output_files(tmp_path: Path, capsys):
    output = tmp_path / "out" / "result.json"
    state = valid_run_state()
    state["written_paths"] = [str(output)]
    state["output_hashes"] = {str(output): "1" * 64}
    state_path = tmp_path / "run_state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    exit_code = main(["resume", "--run-state-ref", str(state_path), "--requested-resume-node", "node-1"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["resume_eligibility"] == "REPLAY"
    assert payload["resume_decision_report"]["invalidation_records"][0]["reason_code"] == "OUTPUT_MISSING"
