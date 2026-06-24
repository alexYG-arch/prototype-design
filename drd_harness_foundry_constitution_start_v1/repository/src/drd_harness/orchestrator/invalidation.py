"""Dependency invalidation and lock supersession helpers."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set


class DependencyEdgeType(str, Enum):
    SOURCE_DEPENDENCY = "SOURCE_DEPENDENCY"
    REVIEW_DEPENDENCY = "REVIEW_DEPENDENCY"
    SPEC_LOCK_DEPENDENCY = "SPEC_LOCK_DEPENDENCY"
    BUILD_LOCK_DEPENDENCY = "BUILD_LOCK_DEPENDENCY"
    VALIDATOR_DEPENDENCY = "VALIDATOR_DEPENDENCY"
    TEST_EVIDENCE_DEPENDENCY = "TEST_EVIDENCE_DEPENDENCY"
    WORKPACK_DEPENDENCY = "WORKPACK_DEPENDENCY"
    SKILL_DEPENDENCY = "SKILL_DEPENDENCY"
    RELEASE_DEPENDENCY = "RELEASE_DEPENDENCY"


class InvalidationCause(str, Enum):
    UPSTREAM_HASH_CHANGED = "UPSTREAM_HASH_CHANGED"
    REVIEW_DECISION_SUPERSEDED = "REVIEW_DECISION_SUPERSEDED"
    LOCK_SUPERSEDED = "LOCK_SUPERSEDED"
    VALIDATOR_VERSION_CHANGED = "VALIDATOR_VERSION_CHANGED"
    FORBIDDEN_SCOPE_CHANGE = "FORBIDDEN_SCOPE_CHANGE"
    SOURCE_LOCK_CHANGED = "SOURCE_LOCK_CHANGED"


VALID_DEPENDENCY_EDGE_TYPES = {edge_type.value for edge_type in DependencyEdgeType}


@dataclass(frozen=True)
class InvalidationFinding:
    code: str
    subject_id: str
    message: str


@dataclass(frozen=True)
class DependencyEdge:
    edge_id: str
    edge_type: DependencyEdgeType
    source_subject: str
    target_subject: str
    upstream_hash: str
    downstream_binding_field: str
    invalidation_behavior: str


@dataclass(frozen=True)
class InvalidationRecord:
    invalidation_id: str
    cause: InvalidationCause
    changed_dependency: str
    old_hash: str
    new_hash: Optional[str]
    affected_subjects: List[str]
    required_action: str
    recovery_owner: str
    required_command: str
    due_before_consumption: bool
    blocking_state: bool
    created_by_runtime: str


@dataclass(frozen=True)
class PartialUnaffectedClaim:
    claim_id: str
    changed_dependency: str
    affected_paths: List[str]
    unaffected_paths: List[str]
    reason: str
    validator_result_ref: str
    review_required: bool
    expires_on_dependency_change: List[str]


@dataclass(frozen=True)
class InvalidationRecoveryPlan:
    plan_id: str
    invalidation_ids: List[str]
    affected_subjects: List[str]
    recovery_owner: str
    required_command: str
    exit_criteria: List[str]


@dataclass(frozen=True)
class LockSupersession:
    lock_id: str
    supersedes: List[str]


def validate_dependency_edges(edges: Iterable[DependencyEdge]) -> List[InvalidationFinding]:
    findings: List[InvalidationFinding] = []
    seen = set()
    for edge in edges:
        edge_type_value = edge.edge_type.value if isinstance(edge.edge_type, DependencyEdgeType) else edge.edge_type
        if edge.edge_id in seen:
            findings.append(InvalidationFinding("VLOCK-CHECK-011", edge.edge_id, "edge_id must be unique"))
        seen.add(edge.edge_id)
        if edge_type_value not in VALID_DEPENDENCY_EDGE_TYPES:
            findings.append(InvalidationFinding("VLOCK-CHECK-011", edge.edge_id, "edge_type is not declared"))
        for field_name, value in (
            ("source_subject", edge.source_subject),
            ("target_subject", edge.target_subject),
            ("upstream_hash", edge.upstream_hash),
            ("downstream_binding_field", edge.downstream_binding_field),
            ("invalidation_behavior", edge.invalidation_behavior),
        ):
            if not value:
                findings.append(InvalidationFinding("VLOCK-CHECK-011", edge.edge_id, f"{field_name} is required"))
        if not _is_hash(edge.upstream_hash):
            findings.append(InvalidationFinding("VLOCK-CHECK-011", edge.edge_id, "upstream_hash must be sha256"))
    return findings


def downstream_subjects(edges: Iterable[DependencyEdge], changed_source_subject: str) -> List[str]:
    graph: Dict[str, Set[str]] = {}
    for edge in edges:
        graph.setdefault(edge.source_subject, set()).add(edge.target_subject)

    affected: Set[str] = set()
    frontier = list(graph.get(changed_source_subject, set()))
    while frontier:
        current = frontier.pop(0)
        if current in affected:
            continue
        affected.add(current)
        frontier.extend(sorted(graph.get(current, set())))
    return sorted(affected)


def build_invalidation_record(
    invalidation_id: str,
    cause: InvalidationCause,
    changed_dependency: str,
    old_hash: str,
    new_hash: Optional[str],
    affected_subjects: List[str],
    required_action: str,
    recovery_owner: str,
    required_command: str,
    created_by_runtime: str = "python",
) -> InvalidationRecord:
    return InvalidationRecord(
        invalidation_id=invalidation_id,
        cause=cause,
        changed_dependency=changed_dependency,
        old_hash=old_hash,
        new_hash=new_hash,
        affected_subjects=affected_subjects,
        required_action=required_action,
        recovery_owner=recovery_owner,
        required_command=required_command,
        due_before_consumption=True,
        blocking_state=True,
        created_by_runtime=created_by_runtime,
    )


def validate_invalidation_record(record: InvalidationRecord) -> List[InvalidationFinding]:
    findings: List[InvalidationFinding] = []
    required = {
        "invalidation_id": record.invalidation_id,
        "changed_dependency": record.changed_dependency,
        "old_hash": record.old_hash,
        "required_action": record.required_action,
        "recovery_owner": record.recovery_owner,
        "required_command": record.required_command,
        "created_by_runtime": record.created_by_runtime,
    }
    for field_name, value in required.items():
        if not value:
            findings.append(InvalidationFinding("VLOCK-CHECK-013", record.invalidation_id, f"{field_name} is required"))
    if not record.affected_subjects:
        findings.append(InvalidationFinding("VLOCK-CHECK-013", record.invalidation_id, "affected_subjects is required"))
    if not record.due_before_consumption or not record.blocking_state:
        findings.append(InvalidationFinding("VLOCK-CHECK-014", record.invalidation_id, "invalidations must block consumption"))
    if not _is_hash(record.old_hash) or (record.new_hash is not None and not _is_hash(record.new_hash)):
        findings.append(InvalidationFinding("VLOCK-CHECK-013", record.invalidation_id, "old_hash and new_hash must be sha256"))
    return findings


def validate_partial_unaffected_claim(claim: PartialUnaffectedClaim) -> List[InvalidationFinding]:
    findings: List[InvalidationFinding] = []
    required = {
        "claim_id": claim.claim_id,
        "changed_dependency": claim.changed_dependency,
        "reason": claim.reason,
        "validator_result_ref": claim.validator_result_ref,
    }
    for field_name, value in required.items():
        if not value:
            findings.append(InvalidationFinding("VLOCK-CHECK-015", claim.claim_id or "claim", f"{field_name} is required"))
    if not claim.affected_paths:
        findings.append(InvalidationFinding("VLOCK-CHECK-015", claim.claim_id, "affected_paths is required"))
    if not claim.unaffected_paths:
        findings.append(InvalidationFinding("VLOCK-CHECK-015", claim.claim_id, "unaffected_paths is required"))
    if not claim.expires_on_dependency_change:
        findings.append(InvalidationFinding("VLOCK-CHECK-015", claim.claim_id, "expiry dependencies are required"))
    return findings


def validate_recovery_plan(plan: InvalidationRecoveryPlan) -> List[InvalidationFinding]:
    findings: List[InvalidationFinding] = []
    required = {
        "plan_id": plan.plan_id,
        "recovery_owner": plan.recovery_owner,
        "required_command": plan.required_command,
    }
    for field_name, value in required.items():
        if not value:
            findings.append(InvalidationFinding("VLOCK-CHECK-016", plan.plan_id or "recovery_plan", f"{field_name} is required"))
    if not plan.invalidation_ids:
        findings.append(InvalidationFinding("VLOCK-CHECK-016", plan.plan_id, "invalidation_ids is required"))
    if not plan.affected_subjects:
        findings.append(InvalidationFinding("VLOCK-CHECK-016", plan.plan_id, "affected_subjects is required"))
    if not plan.exit_criteria:
        findings.append(InvalidationFinding("VLOCK-CHECK-016", plan.plan_id, "exit_criteria is required"))
    return findings


def reject_invalidated_evidence(evidence: Mapping[str, Any]) -> List[InvalidationFinding]:
    subject_id = str(evidence.get("test_result_id") or evidence.get("evidence_id") or "evidence")
    in_use = any(
        bool(evidence.get(field))
        for field in ("used_for_build_lock", "used_for_spec_lock", "used_for_approval", "used_for_release")
    )
    if evidence.get("invalidation_state") == "INVALIDATED" and in_use:
        return [InvalidationFinding("VLOCK-CHECK-014", subject_id, "invalidated evidence cannot be consumed")]
    return []


def validate_lock_supersession_acyclic(records: Iterable[LockSupersession]) -> List[InvalidationFinding]:
    graph = {record.lock_id: list(record.supersedes) for record in records}
    findings: List[InvalidationFinding] = []

    def visit(node: str, stack: List[str], seen: Set[str]) -> None:
        if node in stack:
            cycle = stack[stack.index(node):] + [node]
            findings.append(
                InvalidationFinding("VLOCK-CHECK-018", node, "supersession cycle: " + " -> ".join(cycle))
            )
            return
        if node in seen:
            return
        seen.add(node)
        for child in graph.get(node, []):
            visit(child, stack + [node], seen)

    visited: Set[str] = set()
    for lock_id in sorted(graph):
        visit(lock_id, [], visited)
    return findings


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
