"""PRD element inventory and adoption decision primitives."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ElementType(str, Enum):
    PAGE = "PAGE"
    STATE = "STATE"
    CTA = "CTA"
    INPUT = "INPUT"
    NAVIGATION = "NAVIGATION"
    MESSAGE = "MESSAGE"
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"
    UI_ELEMENT = "UI_ELEMENT"


class AdoptionOutcome(str, Enum):
    ADOPT_AS_IS = "ADOPT_AS_IS"
    ADOPT_NORMALIZED = "ADOPT_NORMALIZED"
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"
    REJECT_CONFLICT = "REJECT_CONFLICT"
    ROUTE_PRODUCT_GAP = "ROUTE_PRODUCT_GAP"


BLOCKING_OUTCOMES = {
    AdoptionOutcome.REQUEST_CLARIFICATION,
    AdoptionOutcome.REJECT_CONFLICT,
    AdoptionOutcome.ROUTE_PRODUCT_GAP,
}


@dataclass(frozen=True)
class PrdElementInventoryItem:
    element_id: str
    element_type: ElementType
    source_refs: List[str]
    source_text_hash: str
    stage_id: str
    artifact_id: str


@dataclass(frozen=True)
class PrdElementDecision:
    element_id: str
    source_refs: List[str]
    element_type: ElementType
    outcome: AdoptionOutcome
    normalized_label: Optional[str]
    blocking_reason: Optional[str]
    input_obligations: List[str]
    inference_refs: List[str]

    def require_outcome_integrity(self) -> None:
        if self.outcome == AdoptionOutcome.ADOPT_NORMALIZED and not self.normalized_label:
            raise ValueError("ADOPT_NORMALIZED requires normalized_label")
        if self.outcome in BLOCKING_OUTCOMES and not self.blocking_reason:
            raise ValueError(f"{self.outcome.value} requires blocking_reason")
        if not self.source_refs:
            raise ValueError("adoption decision requires source_refs")
        if not self.inference_refs:
            raise ValueError("adoption decision requires inference_refs")


def require_inventory_coverage(
    inventory: List[PrdElementInventoryItem],
    decisions: List[PrdElementDecision],
) -> None:
    inventory_ids = [item.element_id for item in inventory]
    decision_ids = [decision.element_id for decision in decisions]

    missing = sorted(set(inventory_ids) - set(decision_ids))
    if missing:
        raise ValueError("inventory elements missing adoption decisions: " + ", ".join(missing))

    duplicate = sorted({element_id for element_id in decision_ids if decision_ids.count(element_id) > 1})
    if duplicate:
        raise ValueError("inventory elements have multiple adoption decisions: " + ", ".join(duplicate))

    extra = sorted(set(decision_ids) - set(inventory_ids))
    if extra:
        raise ValueError("adoption decisions reference non-inventory elements: " + ", ".join(extra))
