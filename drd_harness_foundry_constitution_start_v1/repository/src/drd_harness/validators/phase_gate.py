"""Promotion and lock readiness checks."""

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

from drd_harness.validators.spec_validator import (
    ValidationFinding,
    canonical_json_sha256,
    validate_validation_result,
)


PASSING_INVALIDATION_STATES = {"CLEAR", "NONE", "NOT_INVALIDATED", "RESOLVED"}


@dataclass(frozen=True)
class PhaseGateFinding:
    code: str
    subject_id: str
    message: str


def validate_promotion_readiness(
    validation_results: Iterable[Mapping[str, Any]],
    review_decision: Mapping[str, Any],
    subject_hash: str,
    upstream_bindings_present: bool,
    forbidden_write_paths: Iterable[str],
    invalidation_state: str,
) -> List[PhaseGateFinding]:
    findings: List[PhaseGateFinding] = []
    results = list(validation_results)
    if not results:
        findings.append(PhaseGateFinding("VLOCK-CHECK-007", subject_hash, "validation results are required"))
    for result in results:
        findings.extend(_phase_findings(validate_validation_result(result, subject_hash)))

    if review_decision.get("decision") != "APPROVED":
        findings.append(PhaseGateFinding("VLOCK-CHECK-005", subject_hash, "review is not approved"))
    if review_decision.get("subject_hash") != subject_hash:
        findings.append(PhaseGateFinding("VLOCK-CHECK-005", subject_hash, "review subject_hash mismatch"))
    if review_decision.get("open_blockers"):
        findings.append(PhaseGateFinding("VLOCK-CHECK-005", subject_hash, "review has open blockers"))
    if not upstream_bindings_present:
        findings.append(PhaseGateFinding("VLOCK-CHECK-007", subject_hash, "upstream bindings are missing"))
    forbidden = list(forbidden_write_paths)
    if forbidden:
        findings.append(PhaseGateFinding("VLOCK-CHECK-003", subject_hash, "forbidden write paths changed"))
    if invalidation_state not in PASSING_INVALIDATION_STATES:
        findings.append(PhaseGateFinding("VLOCK-CHECK-014", subject_hash, "invalidation is unresolved"))
    return findings


def validate_approved_is_not_locked(state: Mapping[str, Any]) -> List[PhaseGateFinding]:
    subject_id = str(state.get("workpack_id") or state.get("lock_id") or "state")
    approval_state = state.get("approval_state")
    seal_state = state.get("seal_state", state.get("build_lock_state"))
    if approval_state == "APPROVED_BY_HUMAN" and seal_state in {"LOCKED", "SEALED"}:
        return [PhaseGateFinding("VLOCK-CHECK-008", subject_id, "approved state must not imply locked state")]
    return []


def validate_spec_lock_readiness(lock: Mapping[str, Any]) -> List[PhaseGateFinding]:
    findings = _require_fields(
        lock,
        "VLOCK-CHECK-009",
        [
            "lock_id",
            "phase",
            "spec_part_ids",
            "files",
            "root_sha256",
            "review_decision_hashes",
            "source_lock_refs",
            "validator_results",
            "validator_identity_hashes",
            "created_by_runtime",
        ],
    )
    subject_id = str(lock.get("lock_id") or "SPEC_LOCK")
    if lock.get("created_by_runtime") != "python":
        findings.append(PhaseGateFinding("VLOCK-CHECK-009", subject_id, "SPEC_LOCK readiness requires python runtime"))
    findings.extend(_validate_non_empty_list(lock, "spec_part_ids", "VLOCK-CHECK-009"))
    findings.extend(_validate_file_hashes(lock, "VLOCK-CHECK-009"))
    findings.extend(_validate_hash_list(lock, "review_decision_hashes", "VLOCK-CHECK-009"))
    findings.extend(_validate_hash_list(lock, "validator_identity_hashes", "VLOCK-CHECK-009"))
    findings.extend(_validate_validator_result_refs(lock, "VLOCK-CHECK-009"))
    findings.extend(validate_lock_root(lock, "VLOCK-CHECK-009"))
    return findings


def validate_build_lock_readiness(lock: Mapping[str, Any]) -> List[PhaseGateFinding]:
    findings = _require_fields(
        lock,
        "VLOCK-CHECK-010",
        [
            "lock_id",
            "phase",
            "git_commit",
            "spec_lock_hash",
            "files",
            "test_results",
            "validator_identity_hashes",
            "root_sha256",
            "invalidates_on",
        ],
    )
    findings.extend(_validate_file_hashes(lock, "VLOCK-CHECK-010"))
    findings.extend(_validate_hash_field(lock, "spec_lock_hash", "VLOCK-CHECK-010"))
    findings.extend(_validate_hash_list(lock, "validator_identity_hashes", "VLOCK-CHECK-010"))
    findings.extend(_validate_test_results(lock, "VLOCK-CHECK-010"))
    findings.extend(_validate_non_empty_list(lock, "invalidates_on", "VLOCK-CHECK-010"))
    findings.extend(validate_lock_root(lock, "VLOCK-CHECK-010"))
    return findings


def canonical_lock_root(lock: Mapping[str, Any], root_field: str = "root_sha256") -> str:
    payload = {key: value for key, value in lock.items() if key != root_field}
    return canonical_json_sha256(payload)


def validate_lock_root(lock: Mapping[str, Any], code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    if lock.get("root_sha256") != canonical_lock_root(lock):
        return [PhaseGateFinding(code, subject_id, "root_sha256 does not match canonical lock content")]
    return []


def _require_fields(lock: Mapping[str, Any], code: str, fields: Iterable[str]) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    findings: List[PhaseGateFinding] = []
    for field in fields:
        if field not in lock or lock.get(field) in (None, "", []):
            findings.append(PhaseGateFinding(code, subject_id, f"{field} is required"))
    return findings


def _validate_non_empty_list(lock: Mapping[str, Any], field: str, code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    if not isinstance(lock.get(field), list) or not lock.get(field):
        return [PhaseGateFinding(code, subject_id, f"{field} must be a non-empty list")]
    return []


def _validate_file_hashes(lock: Mapping[str, Any], code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    findings = _validate_non_empty_list(lock, "files", code)
    for entry in lock.get("files", []) if isinstance(lock.get("files"), list) else []:
        if not isinstance(entry, Mapping) or not entry.get("path") or not _is_hash(entry.get("sha256")):
            findings.append(PhaseGateFinding(code, subject_id, "files entries require path and sha256"))
    findings.extend(_validate_hash_field(lock, "root_sha256", code))
    return findings


def _validate_hash_field(lock: Mapping[str, Any], field: str, code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    if not _is_hash(lock.get(field)):
        return [PhaseGateFinding(code, subject_id, f"{field} must be sha256")]
    return []


def _validate_hash_list(lock: Mapping[str, Any], field: str, code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    findings = _validate_non_empty_list(lock, field, code)
    for value in lock.get(field, []) if isinstance(lock.get(field), list) else []:
        if not _is_hash(value):
            findings.append(PhaseGateFinding(code, subject_id, f"{field} entries must be sha256"))
    return findings


def _validate_validator_result_refs(lock: Mapping[str, Any], code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    findings = _validate_non_empty_list(lock, "validator_results", code)
    for result in lock.get("validator_results", []) if isinstance(lock.get("validator_results"), list) else []:
        if not isinstance(result, Mapping):
            findings.append(PhaseGateFinding(code, subject_id, "validator_results entries must be objects"))
            continue
        if not result.get("command") or result.get("exit_code") != 0 or not _is_hash(result.get("result_hash")):
            findings.append(
                PhaseGateFinding(code, subject_id, "validator result requires command, exit_code 0, and result_hash")
            )
    return findings


def _validate_test_results(lock: Mapping[str, Any], code: str) -> List[PhaseGateFinding]:
    subject_id = str(lock.get("lock_id") or "lock")
    findings = _validate_non_empty_list(lock, "test_results", code)
    for result in lock.get("test_results", []) if isinstance(lock.get("test_results"), list) else []:
        if not isinstance(result, Mapping):
            findings.append(PhaseGateFinding(code, subject_id, "test_results entries must be objects"))
            continue
        if not result.get("command") or result.get("exit_code") != 0 or not _is_hash(result.get("result_hash")):
            findings.append(PhaseGateFinding(code, subject_id, "test result requires command, exit_code 0, and result_hash"))
    return findings


def _phase_findings(findings: Iterable[ValidationFinding]) -> List[PhaseGateFinding]:
    return [PhaseGateFinding(finding.code, finding.subject_id, finding.message) for finding in findings]


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
