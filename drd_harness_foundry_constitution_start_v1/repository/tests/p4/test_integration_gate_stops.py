import json
from pathlib import Path

from drd_harness.cli.main import main
from drd_harness.orchestrator import program_driver
from drd_harness.orchestrator.program_driver import bind_upstream_p3_build_lock, plan_release_request


def test_upstream_build_lock_binding_rejects_hash_drift(tmp_path: Path, monkeypatch):
    lock = tmp_path / "P3_BUILD_LOCK.json"
    lock.write_text(json.dumps({"phase": "P3", "root_sha256": program_driver.P3_BUILD_LOCK_ROOT_SHA256}), encoding="utf-8")
    monkeypatch.setattr(program_driver, "P3_BUILD_LOCK_SHA256", "a" * 64)

    findings = bind_upstream_p3_build_lock(lock)

    assert "P4INT-GATE-001" in {finding.code for finding in findings}


def test_run_command_stops_when_source_is_unreadable(tmp_path: Path, capsys):
    output = tmp_path / "out"

    exit_code = main(
        [
            "run",
            "--work-dir",
            str(tmp_path),
            "--adapter-id",
            "markdown_prd_adapter",
            "--source-ref",
            str(tmp_path / "missing.md"),
            "--output-dir",
            str(output),
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["findings"][0]["code"] == "CLI-INPUT"


def test_release_request_never_creates_release_lock_or_package():
    payload = plan_release_request(
        ["control/locks/P3_BUILD_LOCK.json"],
        "build_program/phases/P4/RELEASE_SCOPE.md",
        "evidence.json",
    )

    assert payload["status"] == "STOPPED"
    assert payload["will_create_release_lock"] is False
    assert payload["will_publish_package"] is False
    assert payload["written_paths"] == []
