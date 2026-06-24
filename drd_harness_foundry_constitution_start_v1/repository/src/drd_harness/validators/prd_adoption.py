"""Validators for PRD element inventory and adoption decisions."""

from dataclasses import dataclass
from typing import List

from drd_harness.rules.prd_adoption import (
    PrdElementDecision,
    PrdElementInventoryItem,
    require_inventory_coverage,
)


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


def validate_inventory_coverage(
    inventory: List[PrdElementInventoryItem],
    decisions: List[PrdElementDecision],
) -> List[AdoptionFinding]:
    try:
        require_inventory_coverage(inventory, decisions)
    except ValueError as exc:
        return [AdoptionFinding(code="REASON013", subject_id="PRD_ELEMENT_INVENTORY", message=str(exc))]
    return []
