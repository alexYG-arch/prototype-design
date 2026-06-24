"""Validators for reasoning records and derived element decisions."""

from dataclasses import dataclass
from typing import List

from drd_harness.rules.reasoning import (
    CanonicalEligibility,
    InferenceClass,
    InferenceRecord,
    InputObligation,
    StructuralCompletionReview,
)


@dataclass(frozen=True)
class ReasoningFinding:
    code: str
    subject_id: str
    message: str


def validate_inference_record(record: InferenceRecord) -> List[ReasoningFinding]:
    checks = [
        ("REASON001", record.require_complete),
        ("REASON002", record.require_citation_for_canonical_use),
        ("REASON003", record.require_deductive_necessity),
        ("REASON004", record.require_induction_lockout),
        ("REASON011", record.require_rejected_not_consumed),
    ]
    return _collect(record.inference_id, checks)


def require_canonical_consumption_allowed(record: InferenceRecord) -> None:
    if record.inference_class not in {
        InferenceClass.SOURCE_EXPLICIT,
        InferenceClass.DEDUCTIVE_NECESSITY,
        InferenceClass.HUMAN_DECIDED,
    }:
        raise ValueError("canonical artifact consumes non-canonical inference class")
    if record.canonical_eligibility != CanonicalEligibility.ELIGIBLE:
        raise ValueError("canonical artifact consumes ineligible inference")


def validate_input_obligation(obligation: InputObligation) -> List[ReasoningFinding]:
    return _collect(obligation.obligation_id, [("REASON008", obligation.require_path_or_gap)])


def validate_structural_completion_review(review: StructuralCompletionReview) -> List[ReasoningFinding]:
    findings = _collect(review.review_id, [("REASON015", review.require_review_gate)])
    if review.requires_product_gap():
        findings.append(
            ReasoningFinding(
                code="REASON016",
                subject_id=review.review_id,
                message="structural completion option has product expansion risk and must route a product gap",
            )
        )
    return findings


def _collect(subject_id: str, checks) -> List[ReasoningFinding]:
    findings: List[ReasoningFinding] = []
    for code, check in checks:
        try:
            check()
        except ValueError as exc:
            findings.append(ReasoningFinding(code=code, subject_id=subject_id, message=str(exc)))
    return findings
