"""Traceability completeness, orphan code, test obligation, and Skill authority validators."""

from typing import Any, Iterable, List, Mapping

from drd_harness.orchestrator.traceability import (
    TraceabilityFinding,
    detect_orphan_code_targets,
    invalidated_trace_rows,
    validate_skill_second_authority,
    validate_test_obligation_matrix,
    validate_traceability_rows,
)


def validate_code_target_map(rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    return validate_traceability_rows(rows)


def validate_trace_row_to_test_matrix(
    rows: Iterable[Mapping[str, Any]],
    matrix_rows: Iterable[Mapping[str, Any]],
) -> List[TraceabilityFinding]:
    return validate_test_obligation_matrix(rows, matrix_rows)


def validate_orphan_code_targets(code_targets: Iterable[str], rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    return detect_orphan_code_targets(code_targets, rows)


def validate_skill_text_no_second_authority(skill_text: str) -> List[TraceabilityFinding]:
    return validate_skill_second_authority(skill_text)


def validate_traceability_invalidation(rows: Iterable[Mapping[str, Any]], changed_edge_type: str) -> List[TraceabilityFinding]:
    affected = invalidated_trace_rows(rows, changed_edge_type)
    if not affected:
        return [TraceabilityFinding("SW-CHECK-016", changed_edge_type, "changed dependency did not invalidate dependent rows")]
    return []
