from drd_harness.release.lock_inputs import (
    build_release_lock_input_bundle,
    compute_release_lock_input_bundle_hash,
    validate_release_lock_input_bundle,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64


def lock_ref(path, sha256):
    return {"path": path, "sha256": sha256, "lock_id": path.rsplit("/", 1)[-1].replace(".json", "")}


def review_ref(path, sha256):
    return {"path": path, "sha256": sha256, "subject_hash": HASH_E}


def bundle(**overrides):
    data = build_release_lock_input_bundle(
        bundle_id="p4-release-lock-inputs",
        p4_spec_lock_ref=lock_ref("control/locks/P4_SPEC_LOCK.json", HASH_A),
        p4_build_lock_ref=lock_ref("control/locks/P4_BUILD_LOCK.json", HASH_B),
        approved_spec_decisions=[
            review_ref("build_program/phases/P4/candidates/P4-SPEC-01/REVIEW_DECISION.json", HASH_A),
            review_ref("build_program/phases/P4/candidates/P4-SPEC-02/REVIEW_DECISION.json", HASH_B),
            review_ref("build_program/phases/P4/candidates/P4-SPEC-03/REVIEW_DECISION.json", HASH_C),
        ],
        approved_build_decision=review_ref(
            "build_program/phases/P4/candidates/P4-BUILD-LOCK-CREATION-RESULT/REVIEW_DECISION.json",
            HASH_D,
        ),
        suite_report_hashes={"GOLDEN": HASH_A, "INTEGRATION": HASH_B, "RELEASE": HASH_C},
        package_manifest_hash=HASH_A,
        example_project_manifest_hash=HASH_B,
        migration_coverage_hash=HASH_C,
        release_readiness_packet_hash=HASH_D,
        source_git_commit=HASH_E,
    )
    data.update(overrides)
    if overrides:
        data["bundle_hash"] = compute_release_lock_input_bundle_hash(data)
    return data


def test_release_lock_input_bundle_is_candidate_only_and_hash_bound(tmp_path):
    release_lock_path = tmp_path / "DRD_HARNESS_RELEASE_LOCK.json"
    data = bundle()

    assert validate_release_lock_input_bundle(data) == []
    assert data["release_lock_eligibility_state"] == "PENDING_HUMAN_AUTHORIZATION"
    assert data["will_create_release_lock"] is False
    assert data["will_publish_package"] is False
    assert data["bundle_hash"] == compute_release_lock_input_bundle_hash(data)
    assert not release_lock_path.exists()


def test_release_lock_input_bundle_rejects_forbidden_actions_and_embedding():
    data = bundle(
        will_create_release_lock=True,
        forbidden_actions_performed=["create_release_lock"],
        created_lock_path="control/locks/DRD_HARNESS_RELEASE_LOCK.json",
        release_readiness_packet={"readiness_packet_hash": HASH_A},
    )

    findings = validate_release_lock_input_bundle(data)
    codes = {finding.code for finding in findings}

    assert "P4LOCKIN-CHECK-007" in codes


def test_release_lock_input_bundle_rejects_hash_drift_and_auth_bypass():
    data = bundle()
    data["suite_report_hashes"]["RELEASE"] = "not-a-hash"
    data["source_git_commit"] = "not-a-hash"
    data["required_human_authorization"] = {"required": False, "authorization_ref": "bypass"}

    findings = validate_release_lock_input_bundle(data)
    codes = {finding.code for finding in findings}

    assert "P4LOCKIN-CHECK-004" in codes
    assert "P4LOCKIN-CHECK-005" in codes
    assert "P4LOCKIN-CHECK-008" in codes


def test_release_lock_input_bundle_requires_all_p4_spec_decisions():
    data = bundle()
    data["approved_spec_decisions"] = data["approved_spec_decisions"][:1]
    data["bundle_hash"] = compute_release_lock_input_bundle_hash(data)

    findings = validate_release_lock_input_bundle(data)

    assert "P4LOCKIN-CHECK-003" in {finding.code for finding in findings}


def test_release_lock_input_bundle_rejects_semantic_payloads():
    data = bundle(product_requirements=["outside release lock authority"])

    findings = validate_release_lock_input_bundle(data)

    assert "P4REL-SEMANTIC-BOUNDARY" in {finding.code for finding in findings}
