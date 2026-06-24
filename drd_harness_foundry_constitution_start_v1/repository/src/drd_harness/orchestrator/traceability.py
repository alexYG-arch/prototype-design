"""Traceability rows, test matrices, and invalidation helpers."""

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.orchestrator.invalidation import VALID_DEPENDENCY_EDGE_TYPES


REQUIRED_TRACE_FIELDS = {
    "trace_row_id",
    "implementation_duty",
    "contract_clause_id",
    "source_spec_part",
    "spec_lock_ref",
    "contract_section_id",
    "rule_id",
    "projection_id",
    "implementation_workpack_id",
    "code_target",
    "class_or_function",
    "validator",
    "test",
    "acceptance_command",
    "validator_check_ids",
    "allowed_write_paths",
    "forbidden_write_paths",
    "dependency_edges",
    "invalidation_policy",
}

GENERIC_DUTIES = {
    "implement_workpack_system",
    "validate_traceability",
    "handle_skills",
    "implement_workpack",
    "do_all_p1",
}

MULTI_DUTY_MARKERS = {"_and_", "_or_", "all_", "handle_", "manage_"}


@dataclass(frozen=True)
class TraceabilityFinding:
    code: str
    subject_id: str
    message: str


def validate_traceability_row(row: Mapping[str, Any]) -> List[TraceabilityFinding]:
    row_id = str(row.get("trace_row_id") or "trace_row")
    findings: List[TraceabilityFinding] = []
    for field in sorted(REQUIRED_TRACE_FIELDS):
        if field not in row or row.get(field) in (None, "", []):
            findings.append(TraceabilityFinding("SW-CHECK-003", row_id, f"{field} is required"))

    duty = str(row.get("implementation_duty") or "")
    if not _single_action_duty(duty):
        findings.append(TraceabilityFinding("SW-CHECK-004", row_id, "implementation_duty is too broad"))
    checks = row.get("validator_check_ids", [])
    if not isinstance(checks, list) or not checks:
        findings.append(TraceabilityFinding("SW-CHECK-003", row_id, "validator_check_ids must be a non-empty list"))
    elif len(checks) > 1:
        findings.append(TraceabilityFinding("SW-CHECK-004", row_id, "one trace row must not bundle independent checks"))

    for edge in row.get("dependency_edges", []) if isinstance(row.get("dependency_edges"), list) else []:
        edge_type = edge.get("edge_type") if isinstance(edge, Mapping) else edge
        if edge_type not in VALID_DEPENDENCY_EDGE_TYPES:
            findings.append(TraceabilityFinding("SW-CHECK-016", row_id, "dependency edge type is not declared"))
    return findings


def validate_code_target_scope(row: Mapping[str, Any]) -> List[TraceabilityFinding]:
    row_id = str(row.get("trace_row_id") or "trace_row")
    code_target = _normalize(str(row.get("code_target") or ""))
    findings: List[TraceabilityFinding] = []
    allowed = row.get("allowed_write_paths", [])
    forbidden = row.get("forbidden_write_paths", [])
    if _matches_any(code_target, forbidden):
        findings.append(TraceabilityFinding("SW-CHECK-006", row_id, "code target is inside forbidden path"))
    if not _matches_any(code_target, allowed):
        findings.append(TraceabilityFinding("SW-CHECK-005", row_id, "code target is outside allowed paths"))
    return findings


def validate_traceability_rows(rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    seen = set()
    for row in rows:
        row_id = str(row.get("trace_row_id") or "trace_row")
        if row_id in seen:
            findings.append(TraceabilityFinding("SW-CHECK-003", row_id, "trace_row_id must be unique"))
        seen.add(row_id)
        findings.extend(validate_traceability_row(row))
        findings.extend(validate_code_target_scope(row))
    return findings


def validate_test_obligation_matrix(
    trace_rows: Iterable[Mapping[str, Any]],
    matrix_rows: Iterable[Mapping[str, Any]],
) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    trace_rows_list = list(trace_rows)
    matrix_rows_list = list(matrix_rows)
    trace_ids = {str(row.get("trace_row_id") or "trace_row") for row in trace_rows_list}
    matrix_by_trace = {}
    seen_matrix_ids = set()
    for row in matrix_rows_list:
        row_id = str(row.get("trace_row_id") or "trace_row")
        if row_id in seen_matrix_ids:
            findings.append(TraceabilityFinding("SW-CHECK-019", row_id, "duplicate test obligation row"))
            continue
        seen_matrix_ids.add(row_id)
        matrix_by_trace[row_id] = row
    for matrix_id in sorted(set(matrix_by_trace) - trace_ids):
        findings.append(TraceabilityFinding("SW-CHECK-019", matrix_id, "test matrix row lacks matching trace row"))

    for trace_row in trace_rows_list:
        row_id = str(trace_row.get("trace_row_id") or "trace_row")
        matrix = matrix_by_trace.get(row_id)
        if not matrix:
            findings.append(TraceabilityFinding("SW-CHECK-019", row_id, "trace row lacks matching test obligation"))
            continue
        if matrix.get("implementation_duty") != trace_row.get("implementation_duty"):
            findings.append(TraceabilityFinding("SW-CHECK-019", row_id, "test matrix duty does not match trace row"))
        if matrix.get("validator_check_ids") != trace_row.get("validator_check_ids"):
            findings.append(TraceabilityFinding("SW-CHECK-019", row_id, "test matrix check IDs do not match trace row"))
        if not matrix.get("positive_case") or not matrix.get("negative_case"):
            findings.append(TraceabilityFinding("SW-CHECK-008", row_id, "positive and negative test obligations are required"))
        if not matrix.get("acceptance_command"):
            findings.append(TraceabilityFinding("SW-CHECK-009", row_id, "acceptance command is required"))
    return findings


def detect_orphan_code_targets(code_targets: Iterable[str], trace_rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    traced = {_normalize(str(row.get("code_target") or "")) for row in trace_rows}
    findings = []
    for target in sorted(_normalize(target) for target in code_targets):
        if target not in traced:
            findings.append(TraceabilityFinding("SW-CHECK-015", target, "code target has no current traceability row"))
    return findings


def validate_skill_second_authority(skill_text: str) -> List[TraceabilityFinding]:
    lowered = skill_text.lower()
    forbidden_phrases = [
        "treat this skill as a fact source",
        "skill overrides spec",
        "skill overrides validator",
        "skill may approve",
        "optional unless",
        "ignore validator",
        "bypass review",
        "approve automatically",
        "promote automatically",
        "allowed path",
        "new acceptance",
    ]
    findings = []
    for phrase in forbidden_phrases:
        if phrase in lowered:
            findings.append(TraceabilityFinding("SW-CHECK-014", "skill_text", "skill text creates or relaxes authority"))
            break
    return findings


def invalidated_trace_rows(rows: Iterable[Mapping[str, Any]], changed_edge_type: str) -> List[str]:
    affected = []
    for row in rows:
        edges = row.get("dependency_edges", [])
        edge_types = [edge.get("edge_type") if isinstance(edge, Mapping) else edge for edge in edges]
        if changed_edge_type in edge_types:
            affected.append(str(row.get("trace_row_id")))
    return sorted(affected)


def _single_action_duty(duty: str) -> bool:
    if not duty or duty in GENERIC_DUTIES:
        return False
    if duty.count("_") < 1:
        return False
    return not any(marker in duty for marker in MULTI_DUTY_MARKERS)


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _matches_any(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)
