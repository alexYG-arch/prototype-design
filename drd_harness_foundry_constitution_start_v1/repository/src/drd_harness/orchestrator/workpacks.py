"""Implementation workpack envelope and readiness helpers."""

from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from typing import Any, Iterable, List, Mapping


READY_STATES = {"READY", "RUNNING", "CANDIDATE", "VALIDATED", "APPROVED", "PROMOTED"}
FORBIDDEN_DEFAULTS = {"constitution/**", "control/**", ".agents/skills/**", "references/**", "tooling/**"}


@dataclass(frozen=True)
class WorkpackFinding:
    code: str
    subject_id: str
    message: str


@dataclass(frozen=True)
class ImplementationWorkpack:
    workpack_id: str
    phase: str
    lane: str
    objective: str
    required_specs: List[str]
    required_spec_locks: List[dict]
    traceability_rows: List[str]
    allowed_write_paths: List[str]
    forbidden_write_paths: List[str]
    code_targets: List[str]
    validators: List[str]
    tests: List[str]
    acceptance_commands: List[str]
    skill_bindings: List[str]
    dependency_edges: List[str]
    status: str
    review_policy: str
    promotion_policy: str
    invalidation_policy: str

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_required_spec_locks(workpack: Mapping[str, Any]) -> List[WorkpackFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    required_specs = set(workpack.get("required_specs", []))
    locks = workpack.get("required_spec_locks", [])
    locked_specs = {
        lock.get("spec_part")
        for lock in locks
        if lock.get("spec_part") and _is_hash(lock.get("lock_hash"))
    }
    missing = sorted(required_specs - locked_specs)
    if missing:
        return [WorkpackFinding("SW-CHECK-001", workpack_id, "missing SPEC_LOCK refs: " + ", ".join(missing))]
    return []


def evaluate_required_output_family_locks(workpack: Mapping[str, Any]) -> List[WorkpackFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    required_families = set(workpack.get("required_output_families", []))
    locks = workpack.get("required_output_family_locks", [])
    locked_families = {
        lock.get("output_family")
        for lock in locks
        if lock.get("output_family") and _is_hash(lock.get("lock_hash"))
    }
    missing = sorted(required_families - locked_families)
    if missing:
        return [WorkpackFinding("SW-CHECK-002", workpack_id, "missing output family lock coverage: " + ", ".join(missing))]
    return []


def evaluate_workpack_scope(workpack: Mapping[str, Any]) -> List[WorkpackFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    allowed = workpack.get("allowed_write_paths", [])
    forbidden = set(workpack.get("forbidden_write_paths", [])) | FORBIDDEN_DEFAULTS
    findings: List[WorkpackFinding] = []

    for target in workpack.get("code_targets", []):
        normalized = _normalize(target)
        if not any(fnmatch(normalized, pattern) for pattern in allowed):
            findings.append(WorkpackFinding("SW-CHECK-005", workpack_id, f"code target outside allowed paths: {target}"))

    for path in list(workpack.get("changed_paths", [])) + list(workpack.get("code_targets", [])):
        normalized = _normalize(path)
        if any(fnmatch(normalized, pattern) for pattern in forbidden):
            findings.append(WorkpackFinding("SW-CHECK-006", workpack_id, f"forbidden path in scope: {path}"))
    return findings


def compute_workpack_readiness_state(workpack: Mapping[str, Any], traceability_findings: Iterable[Any] = ()) -> str:
    if workpack.get("invalidation_state") == "INVALIDATED" or workpack.get("invalidated_dependencies"):
        return "INVALIDATED"
    if evaluate_required_spec_locks(workpack) or evaluate_required_output_family_locks(workpack):
        return "WAITING_UPSTREAM_LOCK"
    if list(traceability_findings) or workpack.get("scope_dispute") or evaluate_workpack_scope(workpack):
        return "REVIEW_REQUIRED"
    required_lists = [
        "traceability_rows",
        "allowed_write_paths",
        "forbidden_write_paths",
        "code_targets",
        "validators",
        "tests",
        "acceptance_commands",
        "skill_bindings",
        "dependency_edges",
    ]
    if any(not workpack.get(field) for field in required_lists):
        return "REVIEW_REQUIRED"
    return "READY"


def emit_candidate_workpack_envelope(workpack: Mapping[str, Any]) -> dict:
    state = compute_workpack_readiness_state(workpack)
    if state != "READY":
        raise ValueError(f"workpack is not READY: {state}")
    envelope = dict(workpack)
    envelope["status"] = "CANDIDATE"
    envelope["approval_state"] = "NOT_APPROVED"
    envelope["promotion_state"] = "NOT_PROMOTED"
    envelope["build_lock_state"] = "NOT_LOCKED"
    return envelope


def validate_workpack_candidate_boundary(workpack: Mapping[str, Any]) -> List[WorkpackFinding]:
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    findings = []
    if workpack.get("approval_state") in {"APPROVED", "APPROVED_BY_CODEX", "APPROVED_BY_HUMAN"}:
        findings.append(WorkpackFinding("SW-CHECK-010", workpack_id, "candidate envelope must not self-approve"))
    if workpack.get("promotion_state") in {"PROMOTED", "PROMOTION_READY"}:
        findings.append(WorkpackFinding("SW-CHECK-010", workpack_id, "candidate envelope must not self-promote"))
    if workpack.get("build_lock_state") in {"LOCKED", "SEALED"}:
        findings.append(WorkpackFinding("SW-CHECK-010", workpack_id, "candidate envelope must not self-lock"))
    return findings


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")
