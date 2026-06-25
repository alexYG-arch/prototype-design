"""Validators for shared presentation patterns and information presentation."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Mapping

from drd_harness.rules.presentation import (
    InformationPresentationDecision,
    PatternKind,
    PresentationConsistencyException,
    PresentationMode,
    SharedComponentPattern,
)


@dataclass(frozen=True)
class PresentationFinding:
    code: str
    subject_id: str
    message: str


def validate_shared_component_pattern(pattern: SharedComponentPattern) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    findings.extend(_collect("PL001", pattern.pattern_id, pattern.require_complete))
    findings.extend(_collect("PL002", pattern.pattern_id, pattern.reject_visual_only_reuse))
    return findings


def validate_shared_component_registry(patterns: Iterable[SharedComponentPattern]) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    pattern_list = list(patterns)
    pattern_ids = [pattern.pattern_id for pattern in pattern_list]
    for duplicate_id in _duplicates(pattern_ids):
        findings.append(PresentationFinding("PL001", duplicate_id, "duplicate pattern_id"))
    for pattern in pattern_list:
        findings.extend(validate_shared_component_pattern(pattern))
    return findings


def validate_information_presentation_decision(
    decision: InformationPresentationDecision,
) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    findings.extend(_collect("PL003", decision.presentation_id, decision.require_complete))
    findings.extend(_collect("PL004", decision.presentation_id, decision.reject_transient_only_sustained_information))
    return findings


def validate_presentation_consistency(
    decisions: Iterable[InformationPresentationDecision],
    exceptions: Iterable[PresentationConsistencyException] = (),
) -> List[PresentationFinding]:
    decision_list = list(decisions)
    exception_list = list(exceptions)
    findings: List[PresentationFinding] = []
    decision_ids = [decision.presentation_id for decision in decision_list]
    for duplicate_id in _duplicates(decision_ids):
        findings.append(PresentationFinding("PL003", duplicate_id, "duplicate presentation_id"))

    for decision in decision_list:
        findings.extend(validate_information_presentation_decision(decision))
    for exception in exception_list:
        findings.extend(_collect("PL003", exception.exception_id, exception.require_complete))

    allowed_exception_keys = {
        exception.consistency_key(): {mode.value for mode in exception.allowed_modes}
        for exception in exception_list
    }
    decisions_by_key = defaultdict(list)
    for decision in decision_list:
        decisions_by_key[decision.consistency_key()].append(decision)

    for key, grouped_decisions in decisions_by_key.items():
        modes = {decision.presentation_mode.value for decision in grouped_decisions}
        if len(modes) <= 1:
            continue
        allowed_modes = allowed_exception_keys.get(key)
        if not allowed_modes or not modes <= allowed_modes:
            subject = ",".join(sorted(decision.presentation_id for decision in grouped_decisions))
            findings.append(
                PresentationFinding(
                    code="PL003",
                    subject_id=subject,
                    message="equivalent information uses different presentation modes without approved exception",
                )
            )

    return findings


def shared_component_pattern_from_mapping(record: Mapping[str, object]) -> SharedComponentPattern:
    return SharedComponentPattern(
        pattern_id=str(record["pattern_id"]),
        pattern_kind=PatternKind(str(record["pattern_kind"])),
        semantic_role=str(record["semantic_role"]),
        data_structure=_string_list(record["data_structure"]),
        operation_set=_string_list(record["operation_set"]),
        state_model=_string_list(record["state_model"]),
        information_hierarchy=_string_list(record["information_hierarchy"]),
        interaction_model=_string_list(record["interaction_model"]),
        surface_constraints=_string_list(record["surface_constraints"]),
        reuse_scope=_string_list(record["reuse_scope"]),
        trace_refs=_string_list(record["trace_refs"]),
        reuse_reason=_optional_string(record.get("reuse_reason")),
        non_reuse_reason=_optional_string(record.get("non_reuse_reason")),
    )


def information_presentation_decision_from_mapping(
    record: Mapping[str, object],
) -> InformationPresentationDecision:
    return InformationPresentationDecision(
        presentation_id=str(record["presentation_id"]),
        semantic_intent=str(record["semantic_intent"]),
        trigger_condition=str(record["trigger_condition"]),
        scope=str(record["scope"]),
        information_lifecycle=str(record["information_lifecycle"]),
        presentation_mode=PresentationMode(str(record["presentation_mode"])),
        recoverability=str(record["recoverability"]),
        trace_refs=_string_list(record["trace_refs"]),
        user_decision_need=bool(record.get("user_decision_need", False)),
        sustained_processing_required=bool(record.get("sustained_processing_required", False)),
        message_ref=_optional_string(record.get("message_ref")),
        reason_for_difference=_optional_string(record.get("reason_for_difference")),
    )


def presentation_exception_from_mapping(record: Mapping[str, object]) -> PresentationConsistencyException:
    return PresentationConsistencyException(
        exception_id=str(record["exception_id"]),
        semantic_intent=str(record["semantic_intent"]),
        trigger_condition=str(record["trigger_condition"]),
        scope=str(record["scope"]),
        information_lifecycle=str(record["information_lifecycle"]),
        allowed_modes=[PresentationMode(str(mode)) for mode in _string_list(record["allowed_modes"])],
        reason=str(record["reason"]),
        trace_refs=_string_list(record["trace_refs"]),
    )


def validate_interaction_message_presentation_mapping(
    required_message_ids: Iterable[str],
    decisions: Iterable[InformationPresentationDecision],
) -> List[PresentationFinding]:
    required = set(required_message_ids)
    mapped_message_ids = {decision.message_ref for decision in decisions if decision.message_ref}
    findings: List[PresentationFinding] = []
    for message_id in sorted(required - mapped_message_ids):
        findings.append(
            PresentationFinding(
                code="PL005",
                subject_id=message_id,
                message="interaction message lacks presentation decision",
            )
        )
    for message_id in sorted(mapped_message_ids - required):
        findings.append(
            PresentationFinding(
                code="PL005",
                subject_id=message_id,
                message="presentation decision references unknown interaction message",
            )
        )
    return findings


def validate_layout_pattern_refs(
    layout_pattern_refs: Iterable[str],
    patterns: Iterable[SharedComponentPattern],
) -> List[PresentationFinding]:
    pattern_ids = {pattern.pattern_id for pattern in patterns}
    findings: List[PresentationFinding] = []
    for pattern_ref in sorted(set(layout_pattern_refs) - pattern_ids):
        findings.append(
            PresentationFinding(
                code="PL001",
                subject_id=pattern_ref,
                message="layout pattern_ref does not resolve to shared component registry",
            )
        )
    return findings


def _duplicates(values: List[str]) -> List[str]:
    return sorted({value for value in values if values.count(value) > 1})


def _optional_string(value: object):
    if value is None:
        return None
    return str(value)


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        raise ValueError("expected list")
    return [str(item) for item in value]


def _collect(code: str, subject_id: str, check) -> List[PresentationFinding]:
    try:
        check()
    except ValueError as exc:
        return [PresentationFinding(code=code, subject_id=subject_id, message=str(exc))]
    return []
