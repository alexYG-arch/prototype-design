"""Workpack scope, readiness, and Skill binding validators."""

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Any, Iterable, List, Mapping

from drd_harness.orchestrator.workpacks import (
    compute_workpack_readiness_state,
    evaluate_required_output_family_locks,
    evaluate_required_spec_locks,
    evaluate_workpack_scope,
    validate_workpack_candidate_boundary,
)


FORBIDDEN_DEFAULTS = {"constitution/**", "control/**", ".agents/skills/**", "references/**", "tooling/**"}


@dataclass(frozen=True)
class WorkpackScopeFinding:
    code: str
    subject_id: str
    message: str


def validate_spec_before_code(workpack: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    return _convert(evaluate_required_spec_locks(workpack))


def validate_required_output_family_coverage(workpack: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    return _convert(evaluate_required_output_family_locks(workpack))


def validate_allowed_write_paths(workpack: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    allowed = workpack.get("allowed_write_paths", [])
    findings = []
    for target in workpack.get("code_targets", []):
        normalized = _normalize(target)
        if not any(fnmatch(normalized, pattern) for pattern in allowed):
            findings.append(WorkpackScopeFinding("SW-CHECK-005", workpack_id, f"code target outside allowed paths: {target}"))
    return findings


def validate_forbidden_write_paths(workpack: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    forbidden = set(workpack.get("forbidden_write_paths", [])) | FORBIDDEN_DEFAULTS
    findings = []
    for path in workpack.get("changed_paths", []) + workpack.get("code_targets", []):
        normalized = _normalize(path)
        if any(fnmatch(normalized, pattern) for pattern in forbidden):
            findings.append(WorkpackScopeFinding("SW-CHECK-006", workpack_id, f"forbidden path in scope: {path}"))
    return findings


def detect_scope_disputes(workpack: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    families = set(workpack.get("required_specs", []))
    if workpack.get("scope_dispute") or len(families) > 3 or workpack.get("traceability_exception_requested"):
        return [WorkpackScopeFinding("SW-CHECK-017", workpack_id, "scope dispute requires Human Gate")]
    return []


def validate_workpack_readiness(workpack: Mapping[str, Any], traceability_findings: Iterable[Any] = ()) -> List[WorkpackScopeFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    expected = compute_workpack_readiness_state(workpack, traceability_findings)
    actual = workpack.get("status")
    findings = []
    if actual != expected:
        findings.append(WorkpackScopeFinding("SW-CHECK-010", workpack_id, f"status {actual} does not match readiness {expected}"))
    findings.extend(_convert(evaluate_workpack_scope(workpack)))
    findings.extend(_convert(validate_workpack_candidate_boundary(workpack)))
    return findings


def validate_skill_binding_manifest(manifest: Mapping[str, Any]) -> List[WorkpackScopeFinding]:
    skill_id = str(manifest.get("skill_id") or "skill")
    required = [
        "skill_id",
        "skill_version",
        "skill_source_path",
        "skill_source_hash",
        "bound_spec_locks",
        "allowed_workpack_types",
        "allowed_write_paths",
        "forbidden_write_paths",
        "allowed_commands",
        "traceability_rows",
        "validator_refs",
        "test_refs",
        "human_gate_required",
        "invalidation_dependencies",
    ]
    findings = []
    for field in required:
        if field not in manifest or manifest.get(field) in (None, "", []):
            findings.append(WorkpackScopeFinding("SW-CHECK-011", skill_id, f"{field} is required"))
    for lock in manifest.get("bound_spec_locks", []) if isinstance(manifest.get("bound_spec_locks"), list) else []:
        if not lock.get("lock_id") or not _is_hash(lock.get("lock_hash")):
            findings.append(WorkpackScopeFinding("SW-CHECK-011", skill_id, "bound spec lock requires lock_id and lock_hash"))
    if manifest.get("human_gate_required") is not True:
        findings.append(WorkpackScopeFinding("SW-CHECK-011", skill_id, "human_gate_required must be true"))
    return findings


def validate_skill_source_hash(manifest: Mapping[str, Any], current_hash: str) -> List[WorkpackScopeFinding]:
    skill_id = str(manifest.get("skill_id") or "skill")
    if manifest.get("skill_source_hash") != current_hash:
        return [WorkpackScopeFinding("SW-CHECK-012", skill_id, "skill source hash drift")]
    return []


def validate_skill_spec_lock_drift(manifest: Mapping[str, Any], current_locks: Mapping[str, str]) -> List[WorkpackScopeFinding]:
    skill_id = str(manifest.get("skill_id") or "skill")
    findings = []
    locks = manifest.get("bound_spec_locks", [])
    if not isinstance(locks, list):
        return [WorkpackScopeFinding("SW-CHECK-011", skill_id, "bound_spec_locks must be a list")]
    for lock in locks:
        if not isinstance(lock, Mapping):
            findings.append(WorkpackScopeFinding("SW-CHECK-011", skill_id, "bound spec lock entries must be objects"))
            continue
        lock_id = lock.get("lock_id")
        if current_locks.get(lock_id) != lock.get("lock_hash") and not lock.get("unaffected_claim_ref"):
            findings.append(WorkpackScopeFinding("SW-CHECK-013", skill_id, "skill binding references stale spec lock"))
    return findings


def _convert(findings) -> List[WorkpackScopeFinding]:
    return [WorkpackScopeFinding(finding.code, finding.subject_id, finding.message) for finding in findings]


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
