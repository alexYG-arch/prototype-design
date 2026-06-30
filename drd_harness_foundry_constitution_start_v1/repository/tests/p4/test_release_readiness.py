from drd_harness.release.readiness import (
    build_release_readiness_packet,
    compute_readiness_packet_hash,
    validate_release_readiness_packet,
)
from drd_harness.release.suites import run_release_suite, validate_suite_report


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64


def lock_ref(path, sha256):
    return {"path": path, "sha256": sha256, "lock_id": path.rsplit("/", 1)[-1].replace(".json", "")}


def release_evidence():
    return {
        "package_dry_run_report": HASH_A,
        "example_project_smoke_report": HASH_B,
        "migration_coverage_report": HASH_C,
        "release_readiness_packet": HASH_D,
    }


def test_release_suite_report_shape_passes_with_required_evidence():
    report = run_release_suite(
        command="p4 release suite",
        input_hashes={"release-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json", "control/locks/P4_BUILD_LOCK.json"],
        evidence_hashes=release_evidence(),
    )

    assert report["status"] == "PASS"
    assert report["exit_code"] == 0
    assert report["would_publish_package"] is False
    assert report["would_create_release_lock"] is False
    assert validate_suite_report(report) == []


def test_release_suite_fails_when_required_evidence_is_missing():
    evidence = release_evidence()
    evidence.pop("example_project_smoke_report")

    report = run_release_suite(
        command="p4 release suite",
        input_hashes={"release-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json", "control/locks/P4_BUILD_LOCK.json"],
        evidence_hashes=evidence,
    )

    assert report["status"] == "FAIL"
    assert ("P4REL-RELEASE-EVIDENCE-MISSING", "example_project_smoke_report") in {
        (finding["code"], finding["subject_id"]) for finding in report["findings"]
    }


def test_release_suite_blocks_publish_and_release_lock_actions():
    report = run_release_suite(
        command="p4 release suite --publish",
        input_hashes={"release-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json", "control/locks/P4_BUILD_LOCK.json"],
        evidence_hashes=release_evidence(),
        requested_actions=["publish_package", "create_DRD_HARNESS_RELEASE_LOCK"],
    )

    assert report["status"] == "BLOCKED_LOCK_BOUNDARY"
    assert report["would_publish_package"] is False
    assert report["would_create_release_lock"] is False
    assert {finding["subject_id"] for finding in report["findings"]} == {
        "publish_package",
        "create_DRD_HARNESS_RELEASE_LOCK",
    }


def test_release_suite_blocks_invalid_evidence_hash_shape():
    evidence = release_evidence()
    evidence["package_dry_run_report"] = "not-a-hash"

    report = run_release_suite(
        command="p4 release suite",
        input_hashes={"release-fixture": HASH_A},
        upstream_lock_refs=["control/locks/P4_SPEC_LOCK.json", "control/locks/P4_BUILD_LOCK.json"],
        evidence_hashes=evidence,
    )

    assert report["status"] == "BLOCKED_UNSAFE_STATE"
    assert ("P4REL-RELEASE-EVIDENCE-HASH", "package_dry_run_report") in {
        (finding["code"], finding["subject_id"]) for finding in report["findings"]
    }


def readiness_packet(**overrides):
    params = {
        "release_candidate_id": "p4-release-candidate",
        "p4_spec_lock_ref": lock_ref("control/locks/P4_SPEC_LOCK.json", HASH_A),
        "p4_build_lock_ref": lock_ref("control/locks/P4_BUILD_LOCK.json", HASH_B),
        "test_suite_reports": {"GOLDEN": HASH_A, "INTEGRATION": HASH_B, "RELEASE": HASH_C},
        "migration_coverage_report": HASH_D,
        "package_manifest": HASH_A,
        "example_project_manifest": HASH_B,
        "source_git_commit": HASH_E,
        "dirty_state_policy": "CLEAN",
        "dirty_state_records": [],
    }
    params.update(overrides)
    packet = build_release_readiness_packet(**params)
    return packet


def test_release_readiness_packet_accepts_complete_clean_evidence():
    packet = readiness_packet()

    assert validate_release_readiness_packet(packet) == []
    assert packet["status"] == "PASS"
    assert packet["release_lock_eligibility_state"] == "ELIGIBLE_FOR_INPUT_BUNDLE"
    assert packet["human_authorization_required"] is True
    assert packet["readiness_packet_hash"] == compute_readiness_packet_hash(packet)
    assert packet["release_lock_input_bundle_preview"]["blocked_until_human_authorization"] is True
    assert set(packet["release_lock_input_bundle_preview"]["required_input_kinds"]) == {
        "p4_spec_lock_ref",
        "p4_build_lock_ref",
        "approved_spec_decisions",
        "approved_build_decision",
        "suite_report_hashes",
        "package_manifest_hash",
        "example_project_manifest_hash",
        "migration_coverage_hash",
        "release_readiness_packet_hash",
        "source_git_commit",
        "required_human_authorization",
    }
    assert "release_readiness_packet_hash" not in packet["release_lock_input_bundle_preview"]
    assert "bundle_hash" not in packet["release_lock_input_bundle_preview"]


def test_release_readiness_packet_blocks_missing_gates_and_hash_cycles():
    packet = readiness_packet(
        missing_gate_list=["example_project_smoke_report"],
        release_lock_input_bundle_preview={
            "expected_bundle_id": "bundle-1",
            "required_input_kinds": ["p4_spec_lock_ref"],
            "missing_input_kinds": [],
            "blocked_until_human_authorization": True,
            "bundle_hash": HASH_A,
        },
    )
    packet["release_readiness_packet_hash"] = HASH_A

    findings = validate_release_readiness_packet(packet)
    codes = {finding.code for finding in findings}

    assert "P4READY-CHECK-004" in codes
    assert "P4READY-CHECK-007" in codes
    assert "P4READY-CHECK-008" in codes


def test_release_readiness_dirty_state_policy_blocks_release_inputs():
    documented = readiness_packet(
        dirty_state_policy="DOCUMENTED_DIRTY",
        dirty_state_records=[
            {
                "path": "notes/local.md",
                "git_status": "??",
                "is_release_input": False,
                "classification": "EXCLUDED_FROM_RELEASE_INPUTS",
                "reason": "local note excluded from release inputs",
                "required_action": "leave_untracked",
            }
        ],
    )
    blocked = readiness_packet(
        dirty_state_policy="DOCUMENTED_DIRTY",
        dirty_state_records=[
            {
                "path": "repository/src/drd_harness/release/readiness.py",
                "git_status": "M",
                "is_release_input": True,
                "classification": "AFFECTS_RELEASE_INPUTS",
                "reason": "release input changed",
                "required_action": "commit_or_remove_from_release",
            }
        ],
    )

    assert validate_release_readiness_packet(documented) == []
    blocked_codes = {finding.code for finding in validate_release_readiness_packet(blocked)}
    assert "P4READY-CHECK-006" in blocked_codes


def test_release_readiness_rejects_semantic_payloads():
    packet = readiness_packet()
    packet["product_requirements"] = ["outside release authority"]
    packet["readiness_packet_hash"] = compute_readiness_packet_hash(packet)

    findings = validate_release_readiness_packet(packet)

    assert "P4REL-SEMANTIC-BOUNDARY" in {finding.code for finding in findings}
