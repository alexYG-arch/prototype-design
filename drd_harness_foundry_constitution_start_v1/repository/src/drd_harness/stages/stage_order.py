"""Explicit DRD stage ordering."""

from typing import Iterable, List

from drd_harness.stages.contracts import CANONICAL_STAGE_ORDER, StageId, sort_stage_ids_by_contract


def require_canonical_stage_order(stage_ids: Iterable[StageId]) -> None:
    ordered = list(stage_ids)
    expected = sort_stage_ids_by_contract(ordered)
    if ordered != expected:
        raise ValueError("stage order must follow explicit stage_order_index")


def ordered_stage_values() -> List[str]:
    return [stage.value for stage in sort_stage_ids_by_contract(CANONICAL_STAGE_ORDER.keys())]
