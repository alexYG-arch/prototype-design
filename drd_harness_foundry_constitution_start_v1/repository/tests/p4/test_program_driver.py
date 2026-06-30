from pathlib import Path

from drd_harness.orchestrator.program_driver import (
    build_program_dag,
    build_status_payload,
    plan_run,
    validate_acyclic,
)


def adapter_manifest(source_refs):
    return {
        "adapter_id": "markdown_prd_adapter",
        "source_section_records": [
            {"section_id": source_ref, "source_path": f"{source_ref}.md", "source_sha256": "a" * 64}
            for source_ref in source_refs
        ],
    }


def test_program_dag_is_deterministic_for_same_inputs():
    first = build_program_dag(
        adapter_result_manifest=adapter_manifest(["beta", "alpha"]),
        upstream_lock_refs=["control/locks/P3_BUILD_LOCK.json"],
        target_phase="P4",
        target_workpack="P4-IMPL-01",
        output_dir="out",
    )
    second = build_program_dag(
        adapter_result_manifest=adapter_manifest(["alpha", "beta"]),
        upstream_lock_refs=["control/locks/P3_BUILD_LOCK.json"],
        target_phase="P4",
        target_workpack="P4-IMPL-01",
        output_dir="out",
    )

    assert first == second
    assert validate_acyclic(first["dag_nodes"], first["dag_edges"]) == []
    assert first["review_gate_refs"]
    assert first["lock_gate_refs"]


def test_status_payload_shape_is_machine_readable_and_sorted():
    payload = build_status_payload(
        command="run",
        status="DRY_RUN",
        run_id="run-1",
        written_paths=["z.json", "a.json"],
        findings=[],
        exit_code=0,
    )

    assert payload["command"] == "run"
    assert payload["status"] == "DRY_RUN"
    assert payload["run_id"] == "run-1"
    assert payload["written_paths"] == ["a.json", "z.json"]
    assert payload["findings"] == []
    assert payload["exit_code"] == 0


def test_plan_run_stops_when_output_dir_escapes_work_dir(tmp_path: Path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    payload = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=adapter_manifest(["alpha"]),
        output_dir=outside,
        target_phase="P4",
        dry_run=True,
    )

    assert payload["status"] == "STOPPED"
    assert payload["exit_code"] == 1
    assert "P4INT-GATE-OUTPUT-SCOPE" in {finding["code"] for finding in payload["findings"]}
