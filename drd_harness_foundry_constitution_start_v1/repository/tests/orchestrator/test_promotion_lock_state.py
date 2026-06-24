from drd_harness.orchestrator.promotion import (
    create_promotion_audit,
    promotion_readiness_findings,
    validate_promotion_audit,
)
from drd_harness.validators.phase_gate import (
    canonical_lock_root,
    validate_approved_is_not_locked,
    validate_build_lock_readiness,
    validate_lock_root,
    validate_spec_lock_readiness,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64


def validator_identity():
    return {
        "validator_id": "phase_gate",
        "validator_kind": "python_module",
        "validator_version": "1.0.0",
        "validator_code_hash": HASH_A,
        "schema_hashes": {"validation_result.schema.json": HASH_B},
        "runtime_identity": "python-3.9.6",
        "result_hash": HASH_C,
    }


def validation_result(subject_hash=HASH_D):
    return {
        "result_id": "VAL-P1-001",
        "command": "python3 -m pytest",
        "exit_code": 0,
        "checked_subject_hash": subject_hash,
        "result_hash": HASH_E,
        "status": "PASS",
        "validator_identity": validator_identity(),
    }


def test_promotion_readiness_accepts_validated_reviewed_subject():
    findings = promotion_readiness_findings(
        [validation_result()],
        {
            "decision": "APPROVED",
            "subject_hash": HASH_D,
            "open_blockers": [],
        },
        HASH_D,
        upstream_bindings_present=True,
        forbidden_write_paths=[],
        invalidation_state="CLEAR",
    )

    assert findings == []


def test_promotion_readiness_blocks_unresolved_invalidation():
    findings = promotion_readiness_findings(
        [validation_result()],
        {
            "decision": "APPROVED",
            "subject_hash": HASH_D,
            "open_blockers": [],
        },
        HASH_D,
        upstream_bindings_present=True,
        forbidden_write_paths=[],
        invalidation_state="INVALIDATED",
    )

    assert "VLOCK-CHECK-014" in {finding.code for finding in findings}


def test_approved_by_human_does_not_imply_locked():
    findings = validate_approved_is_not_locked(
        {
            "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
            "approval_state": "APPROVED_BY_HUMAN",
            "build_lock_state": "LOCKED",
        }
    )

    assert findings[0].code == "VLOCK-CHECK-008"


def test_spec_lock_readiness_requires_review_and_validator_identity_hashes():
    lock = {
        "lock_id": "P1-SPEC-LOCK-002",
        "phase": "P1",
        "spec_part_ids": ["P1-SPEC-06"],
        "files": [{"path": "spec.md", "sha256": HASH_A}],
        "review_decision_hashes": [HASH_C],
        "source_lock_refs": ["SOURCE-LOCK-001"],
        "validator_results": [{"command": "python3 -m pytest", "exit_code": 0, "result_hash": HASH_D}],
        "validator_identity_hashes": [HASH_E],
        "created_by_runtime": "python",
    }
    lock["root_sha256"] = canonical_lock_root(lock)

    assert validate_spec_lock_readiness(lock) == []


def test_spec_lock_readiness_rejects_failed_validator_result():
    lock = {
        "lock_id": "P1-SPEC-LOCK-002",
        "phase": "P1",
        "spec_part_ids": ["P1-SPEC-06"],
        "files": [{"path": "spec.md", "sha256": HASH_A}],
        "review_decision_hashes": [HASH_C],
        "source_lock_refs": ["SOURCE-LOCK-001"],
        "validator_results": [{"command": "python3 -m pytest", "exit_code": 1, "result_hash": HASH_D}],
        "validator_identity_hashes": [HASH_E],
        "created_by_runtime": "python",
    }
    lock["root_sha256"] = canonical_lock_root(lock)

    findings = validate_spec_lock_readiness(lock)

    assert "VLOCK-CHECK-009" in {finding.code for finding in findings}


def test_spec_lock_readiness_rejects_noncanonical_root():
    lock = {
        "lock_id": "P1-SPEC-LOCK-002",
        "phase": "P1",
        "spec_part_ids": ["P1-SPEC-06"],
        "files": [{"path": "spec.md", "sha256": HASH_A}],
        "root_sha256": HASH_B,
        "review_decision_hashes": [HASH_C],
        "source_lock_refs": ["SOURCE-LOCK-001"],
        "validator_results": [{"command": "python3 -m pytest", "exit_code": 0, "result_hash": HASH_D}],
        "validator_identity_hashes": [HASH_E],
        "created_by_runtime": "python",
    }

    findings = validate_spec_lock_readiness(lock)

    assert "root_sha256 does not match" in " ".join(finding.message for finding in findings)


def test_build_lock_readiness_requires_test_results_and_invalidates_on():
    lock = {
        "lock_id": "P1-BUILD-LOCK-001",
        "phase": "P1",
        "git_commit": "abcdef123456",
        "spec_lock_hash": HASH_A,
        "files": [{"path": "artifact.py", "sha256": HASH_B}],
        "test_results": [{"command": "python3 -m pytest", "exit_code": 0, "result_hash": HASH_C}],
        "validator_identity_hashes": [HASH_D],
        "invalidates_on": ["P1_SPEC_LOCK"],
    }
    lock["root_sha256"] = canonical_lock_root(lock)

    assert validate_build_lock_readiness(lock) == []


def test_build_lock_readiness_rejects_failed_test_result():
    lock = {
        "lock_id": "P1-BUILD-LOCK-001",
        "phase": "P1",
        "git_commit": "abcdef123456",
        "spec_lock_hash": HASH_A,
        "files": [{"path": "artifact.py", "sha256": HASH_B}],
        "test_results": [{"command": "python3 -m pytest", "exit_code": 1, "result_hash": HASH_C}],
        "validator_identity_hashes": [HASH_D],
        "invalidates_on": ["P1_SPEC_LOCK"],
    }
    lock["root_sha256"] = canonical_lock_root(lock)

    findings = validate_build_lock_readiness(lock)

    assert "VLOCK-CHECK-010" in {finding.code for finding in findings}


def test_canonical_lock_root_detects_mutation():
    lock = {
        "lock_id": "P1-BUILD-LOCK-001",
        "phase": "P1",
        "files": [{"path": "artifact.py", "sha256": HASH_B}],
    }
    lock["root_sha256"] = canonical_lock_root(lock)

    assert validate_lock_root(lock, "VLOCK-CHECK-010") == []
    mutated = dict(lock)
    mutated["phase"] = "P2"
    assert validate_lock_root(mutated, "VLOCK-CHECK-010")


def test_promotion_audit_names_hashes_and_python_runtime():
    audit = create_promotion_audit(
        "PROMOTE-P1-001",
        "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        HASH_A,
        [HASH_B],
        HASH_C,
        [HASH_D],
    )

    assert validate_promotion_audit(audit) == []
