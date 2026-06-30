import json
from pathlib import Path

from drd_harness.cli.main import main


def test_p4_run_command_emits_status_payload(tmp_path: Path, capsys):
    source = tmp_path / "prd.md"
    source.write_text("# PRD\nContent\n", encoding="utf-8")
    output = tmp_path / "out"

    exit_code = main(
        [
            "run",
            "--work-dir",
            str(tmp_path),
            "--adapter-id",
            "markdown_prd_adapter",
            "--source-ref",
            str(source),
            "--output-dir",
            str(output),
            "--target-workpack",
            "P4-IMPL-01",
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["command"] == "run"
    assert payload["status"] == "DRY_RUN"
    assert payload["run_id"]
    assert payload["written_paths"] == []
    assert payload["findings"] == []
    assert payload["exit_code"] == 0
    assert payload["adapter_result_manifest"]["source_sha256"]
    assert payload["program_dag_snapshot"]["dag_nodes"]
    assert payload["stage_execution_plan"]


def test_p4_review_command_reports_decision_binding(tmp_path: Path, capsys):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "OUTPUT.md").write_text("# Candidate\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P4-REVIEW",
        "status": "CANDIDATE",
        "approval_state": "CANDIDATE",
        "seal_state": "NOT_SEALED",
        "generated_outputs": ["OUTPUT.md"],
    }
    (candidate / "CANDIDATE_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

    first_exit = main(["candidate-check", str(candidate)])
    first_payload = json.loads(capsys.readouterr().out)
    review = {
        "decision_id": "P4-REVIEW-001",
        "subject_hash": first_payload["subject_hash"],
        "decision": "APPROVED",
        "reviewer": "human-user",
        "open_blockers": [],
        "approved_sections": ["OUTPUT.md"],
    }
    review_path = candidate / "REVIEW_DECISION.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")

    exit_code = main(["review", str(candidate), "--review-decision", str(review_path)])
    payload = json.loads(capsys.readouterr().out)

    assert first_exit == 0
    assert exit_code == 0
    assert payload["command"] == "review"
    assert payload["candidate_subject_hash"] == first_payload["subject_hash"]
    assert payload["review_decision_binding_status"] == "PASS"


def test_p4_resume_and_release_commands_stop_at_declared_gates(capsys):
    resume_exit = main(
        [
            "resume",
            "--run-state-ref",
            "run-state.json",
            "--requested-resume-node",
            "node-1",
            "--dry-run",
        ]
    )
    resume_payload = json.loads(capsys.readouterr().out)

    release_exit = main(
        [
            "release",
            "--lock-ref",
            "control/locks/P3_BUILD_LOCK.json",
            "--release-scope-ref",
            "build_program/phases/P4/RELEASE_SCOPE.md",
            "--evidence-bundle-ref",
            "evidence.json",
            "--dry-run",
        ]
    )
    release_payload = json.loads(capsys.readouterr().out)

    assert resume_exit == 1
    assert resume_payload["status"] == "STOPPED"
    assert resume_payload["resume_eligibility"] == "BLOCKED_PENDING_RECOVERY_POLICY"
    assert release_exit == 1
    assert release_payload["status"] == "STOPPED"
    assert release_payload["release_lock_eligibility_state"] == "NOT_ELIGIBLE"
    assert release_payload["will_create_release_lock"] is False
