"""Validators for reasoning records and derived element decisions."""

from dataclasses import dataclass
from typing import List, Mapping, Optional, Sequence

from drd_harness.rules.reasoning import (
    CanonicalEligibility,
    InferenceClass,
    InferenceRecord,
    InputObligation,
    ProductExpansionRisk,
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


def inference_record_from_mapping(record: Mapping[str, object]) -> InferenceRecord:
    return InferenceRecord(
        inference_id=str(record["inference_id"]),
        inference_class=InferenceClass(str(record["inference_class"])),
        stage_id=str(record["stage_id"]),
        artifact_id=str(record["artifact_id"]),
        source_refs=_string_list(record["source_refs"]),
        premises=_string_list(record["premises"]),
        applied_rules=_string_list(record["applied_rules"]),
        necessity_basis=_optional_string(record["necessity_basis"]),
        unresolved_product_choices=_string_list(record["unresolved_product_choices"]),
        conclusion=str(record["conclusion"]),
        canonical_eligibility=CanonicalEligibility(str(record["canonical_eligibility"])),
        downstream_use=_string_list(record["downstream_use"]),
    )


def validate_inference_record_set(
    records: Sequence[InferenceRecord],
    *,
    required_inference_ids: Sequence[str] = (),
) -> List[ReasoningFinding]:
    findings: List[ReasoningFinding] = []
    inference_ids = [record.inference_id for record in records]
    for duplicate_id in _duplicates(inference_ids):
        findings.append(ReasoningFinding("REASON001", duplicate_id, "duplicate inference_id"))
    missing_ids = sorted(set(required_inference_ids) - set(inference_ids))
    for missing_id in missing_ids:
        findings.append(ReasoningFinding("REASON007", missing_id, "required inference record is missing"))
    for record in records:
        findings.extend(validate_inference_record(record))
    return findings


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
    if not review.candidate_options:
        findings.append(
            ReasoningFinding(
                code="REASON015",
                subject_id=review.review_id,
                message="structural completion review requires candidate_options",
            )
        )
    if review.requires_product_gap():
        findings.append(
            ReasoningFinding(
                code="REASON016",
                subject_id=review.review_id,
                message="structural completion option has product expansion risk and must route a product gap",
            )
        )
    return findings


def structural_completion_review_from_mapping(record: Mapping[str, object]) -> StructuralCompletionReview:
    return StructuralCompletionReview(
        review_id=str(record["review_id"]),
        required_page_or_flow=str(record["required_page_or_flow"]),
        missing_surface_summary=_string_list(record["missing_surface_summary"]),
        deductive_obligations=_string_list(record["deductive_obligations"]),
        candidate_options=_string_list(record["candidate_options"]),
        product_expansion_risk=ProductExpansionRisk(str(record["product_expansion_risk"])),
        canonical_eligibility=CanonicalEligibility(str(record["canonical_eligibility"])),
    )


def validate_structural_completion_review_set(
    reviews: Sequence[StructuralCompletionReview],
) -> List[ReasoningFinding]:
    findings: List[ReasoningFinding] = []
    review_ids = [review.review_id for review in reviews]
    for duplicate_id in _duplicates(review_ids):
        findings.append(ReasoningFinding("REASON015", duplicate_id, "duplicate structural completion review_id"))
    for review in reviews:
        findings.extend(validate_structural_completion_review(review))
    return findings


def _collect(subject_id: str, checks) -> List[ReasoningFinding]:
    findings: List[ReasoningFinding] = []
    for code, check in checks:
        try:
            check()
        except ValueError as exc:
            findings.append(ReasoningFinding(code=code, subject_id=subject_id, message=str(exc)))
    return findings


def _optional_string(value: object) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        raise ValueError("expected list")
    return [str(item) for item in value]


def _duplicates(values: Sequence[str]) -> List[str]:
    return sorted({value for value in values if values.count(value) > 1})
