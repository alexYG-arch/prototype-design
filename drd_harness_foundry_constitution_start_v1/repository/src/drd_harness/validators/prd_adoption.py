"""Validators for PRD element inventory and adoption decisions."""

from dataclasses import dataclass
from typing import List, Mapping, Sequence

from drd_harness.rules.prd_adoption import (
    PrdElementDecision,
    PrdElementInventoryItem,
    require_inventory_coverage,
)
from drd_harness.rules.reasoning import CanonicalEligibility, DerivationStrategy, DerivedElementDecision


PRODUCT_EXPANSION_GAP_TYPES = {
    "MISSING_PRODUCT_DECISION",
    "MISSING_INPUT_PATH",
    "UNAPPROVED_CAPABILITY",
    "UNAPPROVED_INTEGRATION",
    "UNAPPROVED_DATA_SCOPE",
    "CONFLICTING_SOURCE",
    "STRUCTURAL_COMPLETION_ESCALATED",
}
PRODUCT_EXPANSION_GAP_STATUSES = {"OPEN", "RESOLVED_APPROVED", "RESOLVED_REJECTED", "SUPERSEDED"}


@dataclass(frozen=True)
class AdoptionFinding:
    code: str
    subject_id: str
    message: str


def validate_adoption_decision(decision: PrdElementDecision) -> List[AdoptionFinding]:
    try:
        decision.require_outcome_integrity()
    except ValueError as exc:
        return [AdoptionFinding(code="REASON006", subject_id=decision.element_id, message=str(exc))]
    return []


def validate_inventory_items(inventory: Sequence[PrdElementInventoryItem]) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    element_ids = [item.element_id for item in inventory]
    duplicates = sorted({element_id for element_id in element_ids if element_ids.count(element_id) > 1})
    if duplicates:
        findings.append(
            AdoptionFinding(
                code="REASON013",
                subject_id="PRD_ELEMENT_INVENTORY",
                message="inventory elements are duplicated: " + ", ".join(duplicates),
            )
        )

    for item in inventory:
        if not item.source_refs:
            findings.append(
                AdoptionFinding(
                    code="REASON013",
                    subject_id=item.element_id,
                    message="inventory item requires at least one source_ref",
                )
            )
        if len(item.source_text_hash) != 64 or any(char not in "0123456789abcdef" for char in item.source_text_hash):
            findings.append(
                AdoptionFinding(
                    code="REASON013",
                    subject_id=item.element_id,
                    message="inventory item source_text_hash must be a sha256 hex digest",
                )
            )
    return findings


def validate_inventory_coverage(
    inventory: List[PrdElementInventoryItem],
    decisions: List[PrdElementDecision],
) -> List[AdoptionFinding]:
    try:
        require_inventory_coverage(inventory, decisions)
    except ValueError as exc:
        return [AdoptionFinding(code="REASON013", subject_id="PRD_ELEMENT_INVENTORY", message=str(exc))]
    return []


def validate_derived_element_decision(decision: DerivedElementDecision) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    checks = [
        (decision.require_trace, "REASON007"),
        (decision.require_block_reason_when_blocked, "REASON007"),
    ]
    for check, code in checks:
        try:
            check()
        except ValueError as exc:
            findings.append(AdoptionFinding(code=code, subject_id=decision.derived_element_id, message=str(exc)))
    if (
        decision.derivation_strategy == DerivationStrategy.INDUCTIVE_AUXILIARY
        and decision.canonical_eligibility == CanonicalEligibility.ELIGIBLE
    ):
        findings.append(
            AdoptionFinding(
                code="REASON004",
                subject_id=decision.derived_element_id,
                message="INDUCTIVE_AUXILIARY derived element cannot be canonical without Human Gate approval",
            )
        )
    return findings


def validate_product_expansion_gap(gap: Mapping[str, object]) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    gap_id = str(gap.get("gap_id", "PRODUCT_EXPANSION_GAP"))
    gap_type = str(gap.get("gap_type", ""))
    status = str(gap.get("status", ""))
    blocked_artifacts = gap.get("blocked_artifacts", [])
    candidate_options = gap.get("candidate_options", [])
    source_refs = gap.get("source_refs", [])
    required_decision = str(gap.get("required_decision", ""))
    decision_ref = gap.get("decision_ref")

    if not gap_id.strip():
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id="PRODUCT_EXPANSION_GAP",
                message="product expansion gap requires gap_id",
            )
        )
    if gap_type not in PRODUCT_EXPANSION_GAP_TYPES:
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="product expansion gap requires a known gap_type",
            )
        )
    if status not in PRODUCT_EXPANSION_GAP_STATUSES:
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="product expansion gap requires a known status",
            )
        )
    if not _non_empty_text_list(source_refs):
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="product expansion gap requires source_refs",
            )
        )
    if candidate_options is not None and not isinstance(candidate_options, list):
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="candidate_options must be a list",
            )
        )

    if status == "OPEN" and not _non_empty_text_list(blocked_artifacts):
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="open product expansion gap blocked_artifacts must name downstream artifacts",
            )
        )
    if status == "OPEN" and not required_decision:
        findings.append(
            AdoptionFinding(
                code="REASON009",
                subject_id=gap_id,
                message="open product expansion gap must declare the required human decision",
            )
        )
    if status in {"RESOLVED_APPROVED", "RESOLVED_REJECTED"} and not decision_ref:
        findings.append(
            AdoptionFinding(
                code="REASON010",
                subject_id=gap_id,
                message="resolved product expansion gap requires a human decision_ref",
            )
        )
    return findings


def _non_empty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)
