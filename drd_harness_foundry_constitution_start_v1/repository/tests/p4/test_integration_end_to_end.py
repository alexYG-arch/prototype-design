from drd_harness.release.suites import REQUIRED_INTEGRATION_COVERAGE, run_integration_suite, validate_suite_report


HASH_A = "a" * 64


def status_payload(command="run"):
    return {
        "command": command,
        "status": "STOPPED",
        "run_id": f"{command}-1",
        "written_paths": [],
        "findings": [],
        "exit_code": 1,
    }


def test_integration_suite_passes_when_all_gate_coverage_is_present():
    report = run_integration_suite(
        command="p4 integration",
        input_hashes={"adapter-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        coverage_evidence={area: True for area in REQUIRED_INTEGRATION_COVERAGE},
        command_status_payloads=[status_payload("run"), status_payload("resume"), status_payload("release")],
        gate_stop_report={"human_gate_bypassed": False, "lock_gate_bypassed": False},
        write_scope_report={"status": "PASS", "violations": []},
    )

    assert report["status"] == "PASS"
    assert report["findings"] == []
    assert validate_suite_report(report) == []


def test_integration_suite_fails_when_required_surface_is_missing():
    coverage = {area: True for area in REQUIRED_INTEGRATION_COVERAGE}
    coverage["recovery"] = False

    report = run_integration_suite(
        command="p4 integration",
        input_hashes={"adapter-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        coverage_evidence=coverage,
        command_status_payloads=[status_payload()],
        gate_stop_report={"human_gate_bypassed": False, "lock_gate_bypassed": False},
        write_scope_report={"status": "PASS", "violations": []},
    )

    assert report["status"] == "FAIL"
    assert ("P4REL-INTEGRATION-COVERAGE-MISSING", "recovery") in {
        (finding["code"], finding["subject_id"]) for finding in report["findings"]
    }


def test_integration_suite_blocks_gate_bypass_and_write_scope_violations():
    report = run_integration_suite(
        command="p4 integration",
        input_hashes={"adapter-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        coverage_evidence={area: True for area in REQUIRED_INTEGRATION_COVERAGE},
        command_status_payloads=[status_payload()],
        gate_stop_report={"human_gate_bypassed": True, "lock_gate_bypassed": False},
        write_scope_report={"status": "FAIL", "violations": ["control/locks/P4_BUILD_LOCK.json"]},
    )

    assert report["status"] == "BLOCKED_HUMAN_REVIEW"
    codes = {finding["code"] for finding in report["findings"]}
    assert "P4REL-INTEGRATION-HUMAN-GATE-BYPASS" in codes
    assert "P4REL-INTEGRATION-WRITE-SCOPE" in codes


def test_integration_suite_blocks_non_machine_readable_payload_shapes():
    payload = status_payload()
    payload["written_paths"] = "out.json"
    payload["findings"] = "none"
    payload["exit_code"] = "0"

    report = run_integration_suite(
        command="p4 integration",
        input_hashes={"adapter-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        coverage_evidence={area: True for area in REQUIRED_INTEGRATION_COVERAGE},
        command_status_payloads=[payload],
        gate_stop_report={"human_gate_bypassed": False, "lock_gate_bypassed": False},
        write_scope_report={"status": "PASS", "violations": []},
    )

    assert report["status"] == "BLOCKED_UNSAFE_STATE"
    assert "P4REL-INTEGRATION-PAYLOAD-SHAPE" in {finding["code"] for finding in report["findings"]}
