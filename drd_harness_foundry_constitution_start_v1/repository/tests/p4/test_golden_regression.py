from drd_harness.release.suites import build_suite_report, compute_report_hash, run_golden_suite, validate_suite_report


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def test_golden_suite_passes_with_stable_hashes_and_valid_report():
    report = run_golden_suite(
        command="p4 golden",
        input_hashes={"fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        expected_output_hashes={"final_drd.json": HASH_B},
        actual_output_hashes={"final_drd.json": HASH_B},
        fixture_hash_report={"fixture": HASH_A},
    )

    assert report["status"] == "PASS"
    assert report["exit_code"] == 0
    assert report["findings"] == []
    assert validate_suite_report(report) == []
    assert report["report_hash"] == compute_report_hash(report)


def test_golden_suite_fails_on_expected_hash_drift_without_rewriting_expected():
    expected = {"final_drd.json": HASH_B}
    report = run_golden_suite(
        command="p4 golden",
        input_hashes={"fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        expected_output_hashes=expected,
        actual_output_hashes={"final_drd.json": HASH_C},
    )

    assert expected == {"final_drd.json": HASH_B}
    assert report["status"] == "FAIL"
    assert report["rewritten_expected_outputs"] is False
    assert "P4REL-GOLDEN-CHANGED" in {finding["code"] for finding in report["findings"]}


def test_golden_suite_blocks_update_requests_for_human_review():
    report = run_golden_suite(
        command="p4 golden --update",
        input_hashes={"fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        expected_output_hashes={"final_drd.json": HASH_B},
        actual_output_hashes={"final_drd.json": HASH_C},
        update_expected=True,
    )

    assert report["status"] == "BLOCKED_HUMAN_REVIEW"
    assert report["golden_update_policy"] == {"requested": True, "allowed": False}
    assert report["rewritten_expected_outputs"] is False
    assert "P4REL-GOLDEN-UPDATE-REQUESTED" in {finding["code"] for finding in report["findings"]}


def test_suite_report_rejects_non_sha_report_and_input_hashes():
    report = build_suite_report(
        suite_id="GOLDEN",
        command="p4 golden",
        input_hashes={"fixture": "not-a-hash"},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        status="PASS",
    )
    report["report_hash"] = 123

    findings = validate_suite_report(report)

    assert {finding.code for finding in findings} >= {"P4REL-SUITE-005", "P4REL-SUITE-INPUT-HASH"}


def test_suite_run_id_changes_when_input_hash_values_change():
    first = build_suite_report(
        suite_id="GOLDEN",
        command="p4 golden",
        input_hashes={"fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        status="PASS",
    )
    second = build_suite_report(
        suite_id="GOLDEN",
        command="p4 golden",
        input_hashes={"fixture": HASH_B},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        status="PASS",
    )

    assert first["run_id"] != second["run_id"]


def test_golden_suite_blocks_invalid_expected_hash_shape():
    report = run_golden_suite(
        command="p4 golden",
        input_hashes={"fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json"],
        expected_output_hashes={"final_drd.json": "not-a-hash"},
        actual_output_hashes={"final_drd.json": "not-a-hash"},
    )

    assert report["status"] == "BLOCKED_UNSAFE_STATE"
    assert "P4REL-GOLDEN-EXPECTED-HASH" in {finding["code"] for finding in report["findings"]}
