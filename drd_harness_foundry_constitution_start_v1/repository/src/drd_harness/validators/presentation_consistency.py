"""Validators for shared presentation patterns and information presentation."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List

from drd_harness.rules.presentation import (
    InformationPresentationDecision,
    PresentationConsistencyException,
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
    for pattern in patterns:
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


def validate_interaction_message_presentation_mapping(
    required_message_ids: Iterable[str],
    decisions: Iterable[InformationPresentationDecision],
) -> List[PresentationFinding]:
    mapped_message_ids = {decision.message_ref for decision in decisions if decision.message_ref}
    findings: List[PresentationFinding] = []
    for message_id in required_message_ids:
        if message_id not in mapped_message_ids:
            findings.append(
                PresentationFinding(
                    code="PL005",
                    subject_id=message_id,
                    message="interaction message lacks presentation decision",
                )
            )
    return findings


def _collect(code: str, subject_id: str, check) -> List[PresentationFinding]:
    try:
        check()
    except ValueError as exc:
        return [PresentationFinding(code=code, subject_id=subject_id, message=str(exc))]
    return []
