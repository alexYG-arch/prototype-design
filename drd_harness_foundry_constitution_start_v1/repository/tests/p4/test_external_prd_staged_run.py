import json
from pathlib import Path

from drd_harness.cli.main import main
from drd_harness.kernel.hashline import sha256_file
from drd_harness.stages.source_snapshot import validate_source_snapshot_manifest


def test_staged_run_materializes_real_stage_boundary_and_human_gate_stop(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text(
        "# Utility PRD\n"
        "Primary button starts scan.\n"
        "Error copy explains failed scan recovery.\n"
        "Responsive layout must preserve all information.\n",
        encoding="utf-8",
    )
    output = tmp_path / "current_capsule" / "outputs" / "staged"

    exit_code = main(
        [
            "staged-run",
            "--work-dir",
            str(tmp_path),
            "--source-ref",
            str(source),
            "--output-dir",
            str(output),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    written_paths = {Path(path).relative_to(output).as_posix(): Path(path) for path in payload["written_paths"]}

    assert exit_code == 0
    assert payload["command"] == "staged-run"
    assert payload["status"] == "STAGE_GATE_STOPPED"
    assert payload["completed_stage_ids"] == ["DRD-00"]
    assert payload["blocked_stage_id"] == "DRD-01"
    assert payload["blocked_gate_id"] == "CODEX_RUNTIME_GATE"
    assert payload["next_required_runtime"] == "CODEX"
    assert payload["staged_execution_complete"] is False
    assert payload["creates_control_lock"] is False
    assert payload["creates_release_lock"] is False
    assert payload["publishes_package"] is False
    assert set(written_paths) == {
        "stage_execution_plan.json",
        "DRD-00/source_prd_snapshot.md",
        "DRD-00/source_snapshot_manifest.json",
        "DRD-00/stage_receipt.json",
        "review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json",
        "codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md",
        "run_state.json",
    }

    assert written_paths["DRD-00/source_prd_snapshot.md"].read_bytes() == source.read_bytes()
    manifest = json.loads(written_paths["DRD-00/source_snapshot_manifest.json"].read_text(encoding="utf-8"))
    assert validate_source_snapshot_manifest(manifest["manifest"]) == []
    drd00_receipt = json.loads(written_paths["DRD-00/stage_receipt.json"].read_text(encoding="utf-8"))
    assert drd00_receipt["output_hashes"][str(written_paths["DRD-00/source_snapshot_manifest.json"])] == sha256_file(
        written_paths["DRD-00/source_snapshot_manifest.json"]
    )

    plan = json.loads(written_paths["stage_execution_plan.json"].read_text(encoding="utf-8"))
    assert [row["stage_id"] for row in plan["stage_chain"]] == [
        "DRD-00",
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
        "DRD-05",
        "DRD-06",
    ]
    assert plan["source_preserving_compile_substitute"] is False
    assert plan["blocked_stage_id"] == "DRD-01"
    drd01_stage = next(row for row in plan["stage_chain"] if row["stage_id"] == "DRD-01")
    assert drd01_stage["candidate_outputs"] == [
        "DRD-01/PRD_EXPERIENCE_BRIEF.md",
        "DRD-01/experience_fact_index.json",
        "DRD-01/page_detail_inventory.json",
    ]
    assert drd01_stage["promotion_outputs"] == [
        "DRD-01/APPROVED_SEMANTIC_ARTIFACT.md",
        "DRD-01/approved_semantic_artifact.json",
    ]
    assert drd01_stage["canonical_outputs"] == drd01_stage["candidate_outputs"] + drd01_stage["promotion_outputs"]
    for stage_id in ["DRD-02", "DRD-03", "DRD-03B", "DRD-04"]:
        stage_row = next(row for row in plan["stage_chain"] if row["stage_id"] == stage_id)
        assert stage_row["promotion_outputs"] == [
            f"{stage_id}/APPROVED_SEMANTIC_ARTIFACT.md",
            f"{stage_id}/approved_semantic_artifact.json",
        ]
        assert set(stage_row["promotion_outputs"]) <= set(stage_row["canonical_outputs"])
    drd05_stage = next(row for row in plan["stage_chain"] if row["stage_id"] == "DRD-05")
    assert drd05_stage["requires_approved_stage_semantic_artifacts"] is True
    assert "DRD-05/compiler_input_bundle.json" in drd05_stage["canonical_outputs"]
    assert "DRD-05/compiler_conservation_report.json" in drd05_stage["canonical_outputs"]

    gate = json.loads(written_paths["review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json"].read_text(encoding="utf-8"))
    assert gate["status"] == "CODEX_RUNTIME_REQUIRED"
    assert gate["expected_candidate_outputs"] == [
        "DRD-01/PRD_EXPERIENCE_BRIEF.md",
        "DRD-01/experience_fact_index.json",
        "DRD-01/page_detail_inventory.json",
    ]
    assert gate["post_review_promotion_outputs"] == [
        "DRD-01/APPROVED_SEMANTIC_ARTIFACT.md",
        "DRD-01/approved_semantic_artifact.json",
    ]
    assert gate["promotion_required_before_successor"] is True
    assert gate["compiler_eligible_artifact_kind"] == "APPROVED_SEMANTIC_ARTIFACT"
    assert gate["product_capability_additions_allowed"] is False
    assert gate["lock_or_release_allowed"] is False
    assert gate["page_detail_conservation_required"] is True
    assert gate["page_detail_inventory_output"] == "DRD-01/page_detail_inventory.json"
    assert gate["derivation_origin_required"] is True
    assert gate["page_arrangement_required_by_successor_stages"] is True

    prompt = written_paths["codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md"].read_text(encoding="utf-8")
    assert "page_detail_inventory.json" in prompt
    assert "Do not collapse page detail into feature-only summaries" in prompt
    assert "PRD_EXPLICIT" in prompt

    run_state = json.loads(written_paths["run_state.json"].read_text(encoding="utf-8"))
    assert run_state["original_command"] == "staged-run"
    assert run_state["node_states"]["DRD-01"]["state"] == "NODE_BLOCKED_CODEX_RUNTIME"
    assert run_state["gate_states"]["DRD-01"]["human_gate_required"] is True
    assert payload["output_hashes"] == {str(path): sha256_file(path) for path in sorted(written_paths.values())}
    assert not (output / "FINAL_DRD.md").exists()
    assert not (output / "DRD-01" / "PRD_EXPERIENCE_BRIEF.md").exists()

    resume_exit = main(
        [
            "resume",
            "--run-state-ref",
            str(written_paths["run_state.json"]),
            "--requested-resume-node",
            "DRD-01",
        ]
    )
    resume_payload = json.loads(capsys.readouterr().out)
    assert resume_exit == 1
    assert resume_payload["resume_eligibility"] == "BLOCK_HUMAN_GATE"
    assert resume_payload["blocked_nodes"] == ["DRD-01"]


def test_staged_run_dry_run_writes_nothing(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text("# PRD\nContent\n", encoding="utf-8")
    output = tmp_path / "current_capsule" / "outputs" / "staged"

    exit_code = main(
        [
            "staged-run",
            "--work-dir",
            str(tmp_path),
            "--source-ref",
            str(source),
            "--output-dir",
            str(output),
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "DRY_RUN"
    assert payload["written_paths"] == []
    assert payload["blocked_stage_id"] == "DRD-01"
    assert not output.exists()
