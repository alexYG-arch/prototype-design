from pathlib import Path

from drd_harness.orchestrator.program_driver import (
    build_run_receipt,
    build_status_payload,
    plan_run,
)


def adapter_manifest(source_refs):
    return {
        "adapter_id": "markdown_prd_adapter",
        "source_section_records": [
            {"section_id": source_ref, "source_path": f"{source_ref}.md", "source_sha256": "a" * 64}
            for source_ref in source_refs
        ],
    }


def external_output(tmp_path: Path) -> Path:
    return tmp_path / "current_capsule" / "outputs" / "out"


def test_run_receipt_is_deterministic_for_same_inputs(tmp_path: Path):
    first = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=adapter_manifest(["alpha", "beta"]),
        output_dir=external_output(tmp_path),
        target_workpack="P4-IMPL-01",
        dry_run=True,
    )
    second = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=adapter_manifest(["alpha", "beta"]),
        output_dir=external_output(tmp_path),
        target_workpack="P4-IMPL-01",
        dry_run=True,
    )

    assert first == second
    assert "review_gate_refs" not in first
    assert "lock_gate_refs" not in first


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
    assert "RUN-CHECK-OUTPUT-SCOPE" in {finding["code"] for finding in payload["findings"]}


def test_plan_run_stops_when_output_dir_is_not_current_capsule_outputs(tmp_path: Path):
    payload = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=adapter_manifest(["alpha"]),
        output_dir=tmp_path / "repository" / "out",
        dry_run=True,
    )

    assert payload["status"] == "STOPPED"
    assert payload["exit_code"] == 1
    assert "RUN-CHECK-OUTPUT-SCOPE" in {finding["code"] for finding in payload["findings"]}


def test_plan_run_binds_section_refs_to_content_hashes(tmp_path: Path):
    source_hash = "a" * 64
    section_hash = "b" * 64
    manifest = {
        "adapter_id": "markdown_prd_adapter",
        "source_path": "source.md",
        "source_sha256": source_hash,
        "source_section_records": [
            {
                "section_id": "section-a",
                "source_path": "source.md",
                "source_sha256": source_hash,
                "content_sha256": section_hash,
            }
        ],
        "source_ref_records": [
            {
                "source_ref": "section-a",
                "source_path": "source.md",
                "source_sha256": source_hash,
            }
        ],
        "handoff_manifest": {
            "source_path": "source.md",
            "source_sha256": source_hash,
        },
    }

    payload = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=manifest,
        output_dir=external_output(tmp_path),
        target_workpack="P4-IMPL-01",
        dry_run=True,
    )

    assert payload["input_hashes"]["section-a"] == section_hash
    assert payload["input_hashes"]["source.md"] == source_hash
    assert payload["lock_in_external_prd_run"] is False
    assert payload["release_in_external_prd_run"] is False
    assert "upstream_lock_refs" not in payload
    assert "gate_states" not in payload


def test_plan_run_uses_minimal_receipt_not_evidence_chain(tmp_path: Path):
    output_dir = external_output(tmp_path)
    payload = plan_run(
        work_dir=tmp_path,
        adapter_result_manifest=adapter_manifest(["alpha", "beta"]),
        output_dir=output_dir,
        target_workpack="P4-IMPL-01",
        dry_run=False,
    )

    assert payload["status"] == "RECEIPT_READY"
    assert payload["written_paths"] == [(output_dir / "run_receipt.json").as_posix()]
    assert "program_dag_snapshot" not in payload
    assert "stage_execution_plan" not in payload
    assert "upstream_lock_refs" not in payload
    assert payload["run_receipt"]["ignored_execution_package_labels"]["target_workpack"] == "P4-IMPL-01"
    assert [row["stage_id"] for row in payload["run_receipt"]["document_generation_stage_order"]] == [
        "DRD-00",
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
        "DRD-05",
        "DRD-06",
    ]


def test_build_run_receipt_excludes_lock_release_and_resume_stages(tmp_path: Path):
    receipt = build_run_receipt(
        run_id="run-1",
        adapter_result_manifest=adapter_manifest(["alpha"]),
        output_dir=tmp_path / "out",
    )

    assert receipt["artifact"] == "external_prd_run_receipt"
    assert receipt["lock_in_external_prd_run"] is False
    assert receipt["release_in_external_prd_run"] is False
    assert receipt["package_publish_in_external_prd_run"] is False
    assert receipt["resume_gate_in_external_prd_run"] is False
    assert receipt["evidence_chain_stage_in_external_prd_run"] is False
