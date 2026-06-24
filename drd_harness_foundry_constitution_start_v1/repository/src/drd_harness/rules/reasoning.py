"""Reasoning record and derivation rule primitives."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class InferenceClass(str, Enum):
    SOURCE_EXPLICIT = "SOURCE_EXPLICIT"
    DEDUCTIVE_NECESSITY = "DEDUCTIVE_NECESSITY"
    INDUCTIVE_CANDIDATE = "INDUCTIVE_CANDIDATE"
    HUMAN_DECIDED = "HUMAN_DECIDED"
    REJECTED_INFERENCE = "REJECTED_INFERENCE"


class CanonicalEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED_PENDING_HUMAN = "BLOCKED_PENDING_HUMAN"
    BLOCKED_INVALID = "BLOCKED_INVALID"
    REJECTED = "REJECTED"


class DerivationStrategy(str, Enum):
    DEDUCTIVE_PRIMARY = "DEDUCTIVE_PRIMARY"
    INDUCTIVE_AUXILIARY = "INDUCTIVE_AUXILIARY"


class ProductExpansionRisk(str, Enum):
    NONE = "NONE"
    PRESENT = "PRESENT"
    UNKNOWN = "UNKNOWN"


CANONICAL_INFERENCE_CLASSES = {
    InferenceClass.SOURCE_EXPLICIT,
    InferenceClass.DEDUCTIVE_NECESSITY,
    InferenceClass.HUMAN_DECIDED,
}


PRODUCT_EXPANSION_TERMS = {
    "capability",
    "integration",
    "role",
    "policy",
    "pricing",
    "workflow promise",
    "data scope",
    "automation",
}


@dataclass(frozen=True)
class InferenceRecord:
    inference_id: str
    inference_class: InferenceClass
    stage_id: str
    artifact_id: str
    source_refs: List[str]
    premises: List[str]
    applied_rules: List[str]
    necessity_basis: Optional[str]
    unresolved_product_choices: List[str]
    conclusion: str
    canonical_eligibility: CanonicalEligibility
    downstream_use: List[str]

    def require_complete(self) -> None:
        _require_text(self.inference_id, "inference_id")
        _require_text(self.stage_id, "stage_id")
        _require_text(self.artifact_id, "artifact_id")
        _require_text(self.conclusion, "conclusion")
        _require_non_empty(self.premises, "premises")
        _require_non_empty(self.applied_rules, "applied_rules")
        _require_non_empty(self.downstream_use, "downstream_use")

    def require_citation_for_canonical_use(self) -> None:
        if self.canonical_eligibility == CanonicalEligibility.ELIGIBLE and not self.source_refs:
            raise ValueError("eligible inference must cite source, upstream, rule, or Human Gate reference")

    def require_deductive_necessity(self) -> None:
        if self.inference_class != InferenceClass.DEDUCTIVE_NECESSITY:
            return
        if not self.necessity_basis:
            raise ValueError("DEDUCTIVE_NECESSITY requires necessity_basis")
        if self.unresolved_product_choices:
            raise ValueError("DEDUCTIVE_NECESSITY cannot have unresolved product choices for canonical use")

    def require_induction_lockout(self) -> None:
        if (
            self.inference_class == InferenceClass.INDUCTIVE_CANDIDATE
            and self.canonical_eligibility == CanonicalEligibility.ELIGIBLE
        ):
            raise ValueError("INDUCTIVE_CANDIDATE cannot be canonical without Human Gate approval")

    def require_rejected_not_consumed(self) -> None:
        if self.inference_class == InferenceClass.REJECTED_INFERENCE and self.downstream_use:
            raise ValueError("REJECTED_INFERENCE must not be consumed downstream")


@dataclass(frozen=True)
class DerivedElementDecision:
    derived_element_id: str
    derived_surface_type: str
    derivation_source: str
    obligation_refs: List[str]
    inference_refs: List[str]
    derivation_strategy: DerivationStrategy
    structural_completion_review: Optional[str]
    canonical_eligibility: CanonicalEligibility
    blocked_by: List[str]

    def require_trace(self) -> None:
        _require_text(self.derived_element_id, "derived_element_id")
        _require_text(self.derived_surface_type, "derived_surface_type")
        _require_text(self.derivation_source, "derivation_source")
        _require_non_empty(self.obligation_refs, "obligation_refs")
        _require_non_empty(self.inference_refs, "inference_refs")

    def require_block_reason_when_blocked(self) -> None:
        if self.canonical_eligibility != CanonicalEligibility.ELIGIBLE and not self.blocked_by:
            raise ValueError("blocked derived element requires blocked_by")


@dataclass(frozen=True)
class StructuralCompletionReview:
    review_id: str
    required_page_or_flow: str
    missing_surface_summary: List[str]
    deductive_obligations: List[str]
    candidate_options: List[str]
    product_expansion_risk: ProductExpansionRisk
    canonical_eligibility: CanonicalEligibility

    def require_review_gate(self) -> None:
        _require_text(self.review_id, "review_id")
        _require_text(self.required_page_or_flow, "required_page_or_flow")
        _require_non_empty(self.missing_surface_summary, "missing_surface_summary")
        _require_non_empty(self.deductive_obligations, "deductive_obligations")
        if self.canonical_eligibility == CanonicalEligibility.ELIGIBLE:
            raise ValueError("structural completion review cannot be canonical before Human Gate approval")

    def requires_product_gap(self) -> bool:
        if self.product_expansion_risk == ProductExpansionRisk.PRESENT:
            return True
        joined = " ".join(self.candidate_options).lower()
        return any(term in joined for term in PRODUCT_EXPANSION_TERMS)


@dataclass(frozen=True)
class InputObligation:
    obligation_id: str
    required_input: str
    task_ref: str
    acquisition_path: Optional[str]
    gap_ref: Optional[str]

    def require_path_or_gap(self) -> None:
        _require_text(self.obligation_id, "obligation_id")
        _require_text(self.required_input, "required_input")
        _require_text(self.task_ref, "task_ref")
        if not self.acquisition_path and not self.gap_ref:
            raise ValueError("input obligation requires acquisition path or gap route")


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")


def _require_non_empty(values: List[str], field: str) -> None:
    if not values or not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"{field} must be a non-empty list of text")
