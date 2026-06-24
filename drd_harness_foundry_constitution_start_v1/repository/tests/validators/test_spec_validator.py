import json
from pathlib import Path

from drd_harness.validators.spec_validator import (
    compute_candidate_subject_hash,
    validate_candidate_only_state,
    validate_required_outputs,
    validate_review_binding,
    validate_validation_result,
    validate_validator_identity,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def write_candidate(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "HANDOFF.md").write_text("# Handoff\nComplete output.\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        "status": "CANDIDATE",
        "approval_state": "CANDIDATE",
        "seal_state": "NOT_SEALED",
        "generated_outputs": ["HANDOFF.md"],
    }
    return candidate, manifest


def test_candidate_subject_hash_binds_generated_outputs(tmp_path: Path):
    candidate, manifest = write_candidate(tmp_path)

    subject_hash = compute_candidate_subject_hash(candidate, manifest["generated_outputs"])

    assert len(subject_hash) == 64
    (candidate / "HANDOFF.md").write_text("# Handoff\nChanged output.\n", encoding="utf-8")
    assert compute_candidate_subject_hash(candidate, manifest["generated_outputs"]) != subject_hash


def test_review_binding_accepts_matching_human_approval(tmp_path: Path):
    candidate, manifest = write_candidate(tmp_path)
    subject_hash = compute_candidate_subject_hash(candidate, manifest["generated_outputs"])
    review = {
        "decision_id": "P1-REVIEW-001",
        "subject_hash": subject_hash,
        "decision": "APPROVED",
        "reviewer": "human-user",
        "open_blockers": [],
        "approved_sections": ["HANDOFF.md"],
    }

    assert validate_review_binding(candidate, manifest, review) == []


def test_review_binding_rejects_stale_subject_hash(tmp_path: Path):
    candidate, manifest = write_candidate(tmp_path)
    review = {
        "decision_id": "P1-REVIEW-001",
        "subject_hash": HASH_A,
        "decision": "APPROVED",
        "reviewer": "human-user",
        "open_blockers": [],
        "approved_sections": ["HANDOFF.md"],
    }

    findings = validate_review_binding(candidate, manifest, review)

    assert "VLOCK-CHECK-005" in {finding.code for finding in findings}


def test_candidate_only_state_rejects_self_approval_and_locked_state():
    manifest = {
        "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        "approval_state": "APPROVED_BY_CODEX",
        "seal_state": "LOCKED",
    }

    findings = validate_candidate_only_state(manifest)

    assert {"VLOCK-CHECK-001", "VLOCK-CHECK-008"} <= {finding.code for finding in findings}


def test_required_outputs_reject_missing_empty_json_and_placeholders(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "empty.md").write_text("", encoding="utf-8")
    (candidate / "bad.json").write_text("{bad", encoding="utf-8")
    (candidate / "placeholder.md").write_text("FIXME fill this later\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        "generated_outputs": ["missing.md", "empty.md", "bad.json", "placeholder.md"],
    }

    findings = validate_required_outputs(candidate, manifest)

    assert len(findings) == 4
    assert {finding.code for finding in findings} == {"VLOCK-CHECK-002"}


def test_required_outputs_reject_parent_directory_escape(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (tmp_path / "outside.md").write_text("outside candidate\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        "generated_outputs": ["../outside.md"],
    }

    findings = validate_required_outputs(candidate, manifest)

    assert findings[0].code == "VLOCK-CHECK-002"
    assert "escapes candidate directory" in findings[0].message


def test_required_outputs_reject_absolute_path_escape(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside candidate\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P1-IMPLEMENT-06-VALIDATION-LOCKS",
        "generated_outputs": [str(outside)],
    }

    findings = validate_required_outputs(candidate, manifest)

    assert findings[0].code == "VLOCK-CHECK-002"
    assert "must be relative" in findings[0].message


def test_validator_identity_binds_code_schema_runtime_and_result_hash():
    identity = {
        "validator_id": "spec_validator",
        "validator_kind": "python_module",
        "validator_version": "1.0.0",
        "validator_code_hash": HASH_A,
        "schema_hashes": {"validator_identity.schema.json": HASH_B},
        "runtime_identity": "python-3.9.6",
        "result_hash": HASH_C,
    }

    assert validate_validator_identity(identity) == []


def test_validator_identity_requires_schema_hashes():
    identity = {
        "validator_id": "spec_validator",
        "validator_kind": "python_module",
        "validator_version": "1.0.0",
        "validator_code_hash": HASH_A,
        "schema_hashes": {},
        "runtime_identity": "python-3.9.6",
        "result_hash": HASH_C,
    }

    findings = validate_validator_identity(identity)

    assert "VLOCK-CHECK-004" in {finding.code for finding in findings}


def test_validation_result_uses_schema_checked_subject_hash():
    result = {
        "result_id": "VAL-P1-001",
        "command": "python3 -m pytest",
        "exit_code": 0,
        "status": "PASS",
        "checked_subject_hash": HASH_A,
        "result_hash": HASH_B,
        "validator_identity": {
            "validator_id": "spec_validator",
            "validator_kind": "python_module",
            "validator_version": "1.0.0",
            "validator_code_hash": HASH_A,
            "schema_hashes": {"validation_result.schema.json": HASH_B},
            "runtime_identity": "python-3.9.6",
            "result_hash": HASH_C,
        },
    }

    assert validate_validation_result(result, HASH_A) == []


def test_validation_result_rejects_legacy_subject_hash_only():
    result = {
        "result_id": "VAL-P1-001",
        "command": "python3 -m pytest",
        "exit_code": 0,
        "status": "PASS",
        "subject_hash": HASH_A,
        "result_hash": HASH_B,
        "validator_identity": {
            "validator_id": "spec_validator",
            "validator_kind": "python_module",
            "validator_version": "1.0.0",
            "validator_code_hash": HASH_A,
            "schema_hashes": {"validation_result.schema.json": HASH_B},
            "runtime_identity": "python-3.9.6",
            "result_hash": HASH_C,
        },
    }

    findings = validate_validation_result(result, HASH_A)

    assert "VLOCK-CHECK-004" in {finding.code for finding in findings}


def test_validation_result_rejects_nonzero_exit_code():
    result = {
        "result_id": "VAL-P1-001",
        "command": "python3 -m pytest",
        "exit_code": 1,
        "status": "PASS",
        "checked_subject_hash": HASH_A,
        "result_hash": HASH_B,
        "validator_identity": {
            "validator_id": "spec_validator",
            "validator_kind": "python_module",
            "validator_version": "1.0.0",
            "validator_code_hash": HASH_A,
            "schema_hashes": {"validation_result.schema.json": HASH_B},
            "runtime_identity": "python-3.9.6",
            "result_hash": HASH_C,
        },
    }

    findings = validate_validation_result(result, HASH_A)

    assert "VLOCK-CHECK-006" in {finding.code for finding in findings}


def test_lock_schemas_declare_required_contract_fields():
    schema_root = Path("repository/schemas/locks")
    spec_lock = json.loads((schema_root / "spec_lock.schema.json").read_text(encoding="utf-8"))
    build_lock = json.loads((schema_root / "build_lock.schema.json").read_text(encoding="utf-8"))
    identity = json.loads((schema_root / "validator_identity.schema.json").read_text(encoding="utf-8"))

    assert "validator_identity_hashes" in spec_lock["required"]
    assert spec_lock["properties"]["created_by_runtime"]["const"] == "python"
    assert {"spec_lock_hash", "test_results", "invalidates_on"} <= set(build_lock["required"])
    assert {"validator_code_hash", "schema_hashes", "runtime_identity"} <= set(identity["required"])
