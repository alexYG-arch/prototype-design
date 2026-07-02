import json
import sys
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
    assert not (output / "SOURCE_PRESERVING_DRD.md").exists()
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


def test_codex_stage_dry_run_plans_candidate_outputs_without_writing(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-01",
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "CODEX_STAGE_DRY_RUN"
    assert payload["expected_outputs"] == [
        "DRD-01/PRD_EXPERIENCE_BRIEF.md",
        "DRD-01/experience_fact_index.json",
        "DRD-01/page_detail_inventory.json",
    ]
    assert payload["written_paths"] == []
    assert not (output / "runtime_invocations").exists()
    assert not (output / "DRD-01" / "PRD_EXPERIENCE_BRIEF.md").exists()


def test_codex_stage_requires_real_runtime_and_does_not_fallback_to_python(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-01",
            "--runtime-command",
            str(tmp_path / "missing-codex-runtime"),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "CODEX_RUNTIME_UNAVAILABLE"
    assert any(finding["code"] == "CODEX-STAGE-RUNTIME-002" for finding in payload["findings"])
    assert not (output / "DRD-01" / "PRD_EXPERIENCE_BRIEF.md").exists()
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["node_states"]["DRD-01"]["state"] == "NODE_BLOCKED_CODEX_RUNTIME"


def test_codex_stage_records_candidate_ready_from_runtime_outputs(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)
    fake_runtime = tmp_path / "fake_codex_runtime.py"
    fake_runtime.write_text(
        "import os\n"
        "from pathlib import Path\n"
        "stage_id = os.environ['DRD_HARNESS_STAGE_ID']\n"
        "root = Path(os.environ['DRD_HARNESS_OUTPUT_DIR'])\n"
        "for rel in os.environ['DRD_HARNESS_EXPECTED_OUTPUTS'].splitlines():\n"
        "    path = root / rel\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    if path.suffix == '.json':\n"
        "        status = 'PASS' if stage_id == 'DRD-06' else 'CANDIDATE'\n"
        "        path.write_text('{\"artifact\":\"fake_codex_candidate\",\"stage_id\":\"' + stage_id + '\",\"status\":\"' + status + '\"}\\n', encoding='utf-8')\n"
        "    else:\n"
        "        path.write_text('# ' + stage_id + ' fake Codex candidate\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-01",
            "--runtime-command",
            f"{sys.executable} {fake_runtime}",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "CODEX_STAGE_CANDIDATE_READY"
    assert payload["candidate_subject_hash"]
    assert (output / "DRD-01" / "PRD_EXPERIENCE_BRIEF.md").exists()
    assert (output / "runtime_invocations" / "DRD-01_codex_runtime_invocation.json").exists()
    result = json.loads((output / "runtime_results" / "DRD-01_codex_runtime_result.json").read_text(encoding="utf-8"))
    assert result["status"] == "CODEX_STAGE_CANDIDATE_READY"
    assert result["forbidden_actions"] == [
        "review",
        "approve",
        "promote",
        "compile_final_drd",
        "create_lock",
        "release",
        "publish_package",
    ]
    plan = json.loads((output / "stage_execution_plan.json").read_text(encoding="utf-8"))
    drd01_stage = next(row for row in plan["stage_chain"] if row["stage_id"] == "DRD-01")
    assert drd01_stage["status"] == "CODEX_CANDIDATE_READY_PENDING_HUMAN_REVIEW"
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["node_states"]["DRD-01"]["state"] == "NODE_CODEX_CANDIDATE_READY"
    assert run_state["gate_states"]["DRD-01"]["gate_type"] == "HUMAN_REVIEW_GATE"
    assert run_state["gate_states"]["DRD-01"]["human_gate_required"] is True
    assert run_state["candidate_subject_hashes"]["DRD-01"] == payload["candidate_subject_hash"]


def test_codex_stage_blocks_downstream_without_approved_upstream(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-02",
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "STOPPED"
    assert any(finding["code"] == "CODEX-STAGE-UPSTREAM-001" for finding in payload["findings"])


def test_promote_stage_creates_approved_artifact_and_unblocks_next_dry_run(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)
    fake_runtime = tmp_path / "fake_codex_runtime.py"
    fake_runtime.write_text(
        "import os\n"
        "from pathlib import Path\n"
        "stage_id = os.environ['DRD_HARNESS_STAGE_ID']\n"
        "root = Path(os.environ['DRD_HARNESS_OUTPUT_DIR'])\n"
        "for rel in os.environ['DRD_HARNESS_EXPECTED_OUTPUTS'].splitlines():\n"
        "    path = root / rel\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    if path.suffix == '.json':\n"
        "        status = 'PASS' if stage_id == 'DRD-06' else 'CANDIDATE'\n"
        "        path.write_text('{\"artifact\":\"fake_codex_candidate\",\"stage_id\":\"' + stage_id + '\",\"status\":\"' + status + '\"}\\n', encoding='utf-8')\n"
        "    else:\n"
        "        path.write_text('# ' + stage_id + ' fake Codex candidate\\n\\n- Artifact kind: Codex candidate, not approved and not promoted.\\nStatus: CANDIDATE_PENDING_REVIEW\\nRun ID: test-run\\nSource SHA-256: abc\\n\\n## Candidate Status\\n- Status: `CANDIDATE_READY_FOR_VALIDATION`\\n- Required outputs produced by this candidate.\\n\\n## Semantic Content\\nApproved semantic facts.\\n\\n## Candidate Handoff\\nProcess-only handoff should not compile.\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-01",
            "--runtime-command",
            f"{sys.executable} {fake_runtime}",
        ]
    )
    codex_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0

    exit_code = main(
        [
            "promote-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-01",
            "--approved-subject-hash",
            codex_payload["candidate_subject_hash"],
            "--approval-note",
            "Test approval.",
        ]
    )
    promote_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert promote_payload["status"] == "STAGE_PROMOTED"
    approved_body = (output / "DRD-01" / "APPROVED_SEMANTIC_ARTIFACT.md").read_text(encoding="utf-8")
    assert not any(line.startswith("# ") for line in approved_body.splitlines())
    assert "CANDIDATE_PENDING_REVIEW" not in approved_body
    assert "CANDIDATE_READY_FOR_VALIDATION" not in approved_body
    assert "Artifact kind:" not in approved_body
    assert "Candidate Status" not in approved_body
    assert "Run ID:" not in approved_body
    assert "Source SHA-256:" not in approved_body
    assert "Artifact Handoff" not in approved_body
    assert "Process-only handoff" not in approved_body
    manifest = json.loads((output / "DRD-01" / "approved_semantic_artifact.json").read_text(encoding="utf-8"))
    assert manifest["artifact_kind"] == "APPROVED_SEMANTIC_ARTIFACT"
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["gate_states"]["DRD-01"]["human_gate_required"] is False

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-02",
            "--dry-run",
        ]
    )
    drd02_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert drd02_payload["status"] == "CODEX_STAGE_DRY_RUN"
    assert drd02_payload["findings"] == []


def test_compile_stage_blocks_without_all_approved_semantic_artifacts(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)

    exit_code = main(
        [
            "compile-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-05",
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "STOPPED"
    assert any(finding["code"] == "COMPILE-STAGE-UPSTREAM-001" for finding in payload["findings"])
    assert not (output / "DRD-05" / "FINAL_DRD.md").exists()


def test_compile_stage_builds_final_drd_from_approved_semantic_artifacts(tmp_path: Path, capsys):
    output = _materialize_staged_run(tmp_path, capsys)
    fake_runtime = tmp_path / "fake_codex_runtime.py"
    fake_runtime.write_text(
        "import os\n"
        "from pathlib import Path\n"
        "stage_id = os.environ['DRD_HARNESS_STAGE_ID']\n"
        "root = Path(os.environ['DRD_HARNESS_OUTPUT_DIR'])\n"
        "for rel in os.environ['DRD_HARNESS_EXPECTED_OUTPUTS'].splitlines():\n"
        "    path = root / rel\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    if path.suffix == '.json':\n"
        "        status = 'PASS' if stage_id == 'DRD-06' else 'CANDIDATE'\n"
        "        path.write_text('{\"artifact\":\"fake_codex_candidate\",\"stage_id\":\"' + stage_id + '\",\"status\":\"' + status + '\"}\\n', encoding='utf-8')\n"
        "    else:\n"
        "        path.write_text('# ' + stage_id + ' fake Codex candidate\\n\\n- Artifact kind: Codex candidate, not approved and not promoted.\\nStatus: CANDIDATE_PENDING_REVIEW\\nRun ID: test-run\\nStage: ' + stage_id + '\\nSource snapshot: source.md\\nSource SHA-256: abc\\nApproved upstream: test\\nBoundary: candidate only\\n\\n## Candidate Status\\n- Status: `CANDIDATE_READY_FOR_VALIDATION`\\n- Required outputs produced by this candidate.\\n\\n## Semantic Content\\nApproved semantic facts with button, error, and layout coverage.\\n\\n## Candidate Handoff\\nProcess-only handoff should not compile.\\nSource snapshot SHA-256: abc\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )

    for stage_id in ["DRD-01", "DRD-02", "DRD-03", "DRD-03B", "DRD-04"]:
        exit_code = main(
            [
                "codex-stage",
                "--work-dir",
                str(tmp_path),
                "--run-state-ref",
                str(output / "run_state.json"),
                "--stage-id",
                stage_id,
                "--runtime-command",
                f"{sys.executable} {fake_runtime}",
            ]
        )
        codex_payload = json.loads(capsys.readouterr().out)
        assert exit_code == 0
        assert codex_payload["status"] == "CODEX_STAGE_CANDIDATE_READY"

        exit_code = main(
            [
                "promote-stage",
                "--work-dir",
                str(tmp_path),
                "--run-state-ref",
                str(output / "run_state.json"),
                "--stage-id",
                stage_id,
                "--approved-subject-hash",
                codex_payload["candidate_subject_hash"],
                "--approval-note",
                "Test approval.",
            ]
        )
        promote_payload = json.loads(capsys.readouterr().out)
        assert exit_code == 0
        assert promote_payload["status"] == "STAGE_PROMOTED"

    exit_code = main(
        [
            "compile-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-05",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "COMPILE_STAGE_COMPLETE"
    assert payload["staged_execution_complete"] is False
    final_drd = (output / "DRD-05" / "FINAL_DRD.md").read_text(encoding="utf-8")
    assert final_drd.startswith("# Final DRD")
    assert "Approved semantic facts with button, error, and layout coverage." in final_drd
    assert "CANDIDATE_PENDING_REVIEW" not in final_drd
    assert "Run ID:" not in final_drd
    assert "Source SHA-256:" not in final_drd
    assert "Artifact Handoff" not in final_drd
    assert "Process-only handoff" not in final_drd
    assert (output / "DRD-05" / "compiler_input_bundle.json").exists()
    bundle = json.loads((output / "DRD-05" / "compiler_input_bundle.json").read_text(encoding="utf-8"))
    assert bundle["source_snapshot_identity"]["section_count"] == 1
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["node_states"]["DRD-05"]["state"] == "NODE_COMPLETED"
    assert run_state["gate_states"]["DRD-05"]["human_gate_required"] is False

    exit_code = main(
        [
            "codex-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-06",
            "--runtime-command",
            f"{sys.executable} {fake_runtime}",
        ]
    )
    qa_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert qa_payload["status"] == "CODEX_READ_ONLY_QA_READY"
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["node_states"]["DRD-06"]["state"] == "NODE_CODEX_READ_ONLY_QA_READY"

    exit_code = main(
        [
            "qa-complete-stage",
            "--work-dir",
            str(tmp_path),
            "--run-state-ref",
            str(output / "run_state.json"),
            "--stage-id",
            "DRD-06",
        ]
    )
    complete_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert complete_payload["status"] == "STAGED_EXECUTION_COMPLETE"
    assert complete_payload["staged_execution_complete"] is True
    run_state = json.loads((output / "run_state.json").read_text(encoding="utf-8"))
    assert run_state["node_states"]["DRD-06"]["state"] == "NODE_COMPLETED"
    assert run_state["staged_execution_complete"] is True
    plan = json.loads((output / "stage_execution_plan.json").read_text(encoding="utf-8"))
    assert plan["completed_stage_ids"] == ["DRD-00", "DRD-01", "DRD-02", "DRD-03", "DRD-03B", "DRD-04", "DRD-05", "DRD-06"]


def _materialize_staged_run(tmp_path: Path, capsys) -> Path:
    source = tmp_path / "prd.md"
    source.write_text(
        "# Utility PRD\n"
        "Primary button starts scan.\n"
        "Error copy explains failed scan recovery.\n",
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
    assert exit_code == 0
    assert payload["status"] == "STAGE_GATE_STOPPED"
    return output
