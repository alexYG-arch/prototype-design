import json
from pathlib import Path

from drd_harness.cli.main import main
from drd_harness.validators.compiler_conservation import validate_final_drd_reader_structure


def test_generate_drd_materializes_source_preserving_final_drd(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text(
        "# Utility PRD\n"
        "Primary button starts scan.\n"
        "Error copy explains failed scan recovery.\n"
        "Responsive layout must preserve all information.\n",
        encoding="utf-8",
    )
    output = tmp_path / "current_capsule" / "outputs" / "external_prd_drd"

    exit_code = main(
        [
            "generate-drd",
            "--work-dir",
            str(tmp_path),
            "--source-ref",
            str(source),
            "--output-dir",
            str(output),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    written_paths = {Path(path).name: Path(path) for path in payload["written_paths"]}

    assert exit_code == 0
    assert payload["command"] == "generate-drd"
    assert payload["status"] == "PASS"
    assert payload["conservation_status"] == "PASS"
    assert payload["will_create_release_lock"] is False
    assert payload["will_publish_package"] is False
    assert payload["source_preserving_compile_only"] is True
    assert payload["staged_execution_complete"] is False
    assert payload["staged_execution_command"] == "staged-run"
    assert "release_readiness_packet" not in payload
    assert all("build_program/" not in path and "control/locks/" not in path for path in payload["written_paths"])
    assert set(written_paths) == {
        "external_prd_section_index.json",
        "external_prd_page_detail_inventory.json",
        "external_prd_review_decision.json",
        "external_prd_source_snapshot_binding.json",
        "external_prd_validation_report.json",
        "drd_generation_stage_plan.json",
        "compiler_input_bundle.json",
        "FINAL_DRD.md",
        "final_drd_manifest.json",
        "final_drd_toc.json",
        "final_drd_reference_index.json",
        "final_drd_hash_index.json",
        "compiler_conservation_report.json",
        "compiler_semantic_unit_inventory.json",
    }

    final_drd = written_paths["FINAL_DRD.md"].read_text(encoding="utf-8")
    manifest = json.loads(written_paths["final_drd_manifest.json"].read_text(encoding="utf-8"))
    conservation = json.loads(written_paths["compiler_conservation_report.json"].read_text(encoding="utf-8"))
    bundle = json.loads(written_paths["compiler_input_bundle.json"].read_text(encoding="utf-8"))["bundle"]
    review = json.loads(written_paths["external_prd_review_decision.json"].read_text(encoding="utf-8"))
    source_binding = json.loads(written_paths["external_prd_source_snapshot_binding.json"].read_text(encoding="utf-8"))
    stage_plan = json.loads(written_paths["drd_generation_stage_plan.json"].read_text(encoding="utf-8"))
    detail_inventory = json.loads(written_paths["external_prd_page_detail_inventory.json"].read_text(encoding="utf-8"))
    validation_report = json.loads(written_paths["external_prd_validation_report.json"].read_text(encoding="utf-8"))

    assert "Primary button starts scan." in final_drd
    assert "Responsive layout must preserve all information." in final_drd
    assert validate_final_drd_reader_structure(final_drd) == []
    assert manifest["added_semantic_unit_count"] == 0
    assert conservation["added_semantic_units"] == []
    assert bundle["compiler_stage_id"] == "DRD-05"
    assert bundle["requires_approved_stage_semantic_artifacts"] is False
    assert bundle["approved_semantic_artifacts"][0]["path"] == str(source)
    assert bundle["approved_semantic_artifacts"][0]["semantic_role"] == "source_prd"
    assert review["human_approval"] is False
    assert review["product_capability_additions_allowed"] is False
    assert review["requires_human_review_before_product_inference"] is True
    assert source_binding["creates_control_lock"] is False
    assert source_binding["creates_release_lock"] is False
    assert source_binding["page_detail_inventory_ref"] == str(written_paths["external_prd_page_detail_inventory.json"])
    assert stage_plan["lock_or_release_stage_included"] is False
    assert stage_plan["page_detail_conservation_policy"]
    assert payload["page_detail_conservation_status"] == "PASS"
    assert payload["page_detail_record_count"] == detail_inventory["record_count"]
    assert validation_report["page_detail_conservation_status"] == "PASS"
    assert {record["detail_kind"] for record in detail_inventory["records"]} >= {
        "CONTROL_OR_INTERACTION_DETAIL",
        "STATE_OR_FEEDBACK_COPY",
        "PAGE_STRUCTURE_DETAIL",
    }
    assert [row["stage_id"] for row in stage_plan["stage_order"]] == [
        "DRD-00",
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
        "DRD-05",
        "DRD-06",
    ]
    assert payload["document_generation_stage_order"] == [
        "DRD-00",
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
        "DRD-05",
        "DRD-06",
    ]


def test_generate_drd_dry_run_writes_nothing(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text("# PRD\nContent\n", encoding="utf-8")
    output = tmp_path / "current_capsule" / "outputs" / "out"

    exit_code = main(
        [
            "generate-drd",
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
    assert payload["planned_written_paths"]
    assert not output.exists()


def test_generate_drd_rejects_repository_output_dir(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text("# PRD\nContent\n", encoding="utf-8")
    output = tmp_path / "repository" / "out"

    exit_code = main(
        [
            "generate-drd",
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

    assert exit_code == 1
    assert payload["status"] == "STOPPED"
    assert payload["written_paths"] == []
    assert "RUN-CHECK-OUTPUT-SCOPE" in {finding["code"] for finding in payload["findings"]}
