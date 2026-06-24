import json
from pathlib import Path

from drd_harness.cli.main import main


HASH_A = "a" * 64


def test_candidate_check_delegates_to_candidate_validators(tmp_path: Path, capsys):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "OUTPUT.md").write_text("# Candidate\n", encoding="utf-8")
    (candidate / "CANDIDATE_MANIFEST.json").write_text(
        json.dumps(
            {
                "workpack_id": "CLI-SMOKE",
                "status": "IMPLEMENTATION_CANDIDATE_READY_FOR_HUMAN_REVIEW",
                "generated_outputs": ["OUTPUT.md", "CANDIDATE_MANIFEST.json"],
                "approval_state": "NOT_APPROVED",
                "build_lock_state": "NOT_LOCKED",
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["candidate-check", str(candidate)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["command"] == "candidate-check"
    assert payload["status"] == "PASS"
    assert len(payload["subject_hash"]) == 64


def test_candidate_check_returns_json_failure_for_missing_output(tmp_path: Path, capsys):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "CANDIDATE_MANIFEST.json").write_text(
        json.dumps(
            {
                "workpack_id": "CLI-BAD",
                "status": "IMPLEMENTATION_CANDIDATE_READY_FOR_HUMAN_REVIEW",
                "generated_outputs": ["MISSING.md"],
                "approval_state": "NOT_APPROVED",
                "build_lock_state": "NOT_LOCKED",
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["candidate-check", str(candidate)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["findings"][0]["code"] == "VLOCK-CHECK-002"


def test_candidate_check_returns_json_failure_for_escaped_output_path(tmp_path: Path, capsys):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "CANDIDATE_MANIFEST.json").write_text(
        json.dumps(
            {
                "workpack_id": "CLI-BAD",
                "status": "IMPLEMENTATION_CANDIDATE_READY_FOR_HUMAN_REVIEW",
                "generated_outputs": ["../escape.md"],
                "approval_state": "NOT_APPROVED",
                "build_lock_state": "NOT_LOCKED",
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["candidate-check", str(candidate)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["findings"][0]["code"] == "VLOCK-CHECK-002"


def test_runtime_boundary_check_reports_forbidden_import(tmp_path: Path, capsys):
    source = tmp_path / "bad.py"
    source.write_text("from build_program.runner import main\n", encoding="utf-8")

    exit_code = main(["runtime-boundary-check", str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["findings"][0]["code"] == "FND007"


def test_workpack_readiness_delegates_to_scope_validator(tmp_path: Path, capsys):
    workpack = tmp_path / "workpack.json"
    workpack.write_text(
        json.dumps(
            {
                "workpack_id": "WP-CLI",
                "required_specs": ["P1-SPEC-08"],
                "required_spec_locks": [{"spec_part": "P1-SPEC-08", "lock_hash": HASH_A}],
                "traceability_rows": ["TRACE-1"],
                "allowed_write_paths": ["repository/src/drd_harness/cli/**"],
                "forbidden_write_paths": ["control/**"],
                "code_targets": ["repository/src/drd_harness/cli/main.py"],
                "validators": ["drd_harness.validators.workpack_scope.validate_workpack_readiness"],
                "tests": ["repository/tests/integration/test_cli_smoke.py"],
                "acceptance_commands": ["python3 -m pytest repository/tests/integration"],
                "skill_bindings": ["NONE"],
                "dependency_edges": ["SPEC_LOCK_DEPENDENCY"],
                "status": "READY",
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["workpack-readiness", str(workpack)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "PASS"
    assert payload["readiness_state"] == "READY"


def test_workpack_readiness_returns_json_failure_for_bad_json(tmp_path: Path, capsys):
    workpack = tmp_path / "workpack.json"
    workpack.write_text("{bad json", encoding="utf-8")

    exit_code = main(["workpack-readiness", str(workpack)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["findings"][0]["code"] == "CLI-INPUT"
