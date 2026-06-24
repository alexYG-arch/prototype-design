import pytest

from drd_harness.stages.contracts import StageId, canonical_stage_order, sort_stage_ids_by_contract
from drd_harness.stages.stage_order import ordered_stage_values, require_canonical_stage_order


def test_stage_order_places_drd03b_between_drd03_and_drd04():
    assert ordered_stage_values() == [
        "DRD-00",
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
        "DRD-05",
        "DRD-06",
    ]


def test_stage_order_uses_explicit_index_not_lexical_sort():
    stage_ids = [StageId.DRD_04, StageId.DRD_03B, StageId.DRD_03]

    assert [stage.value for stage in sort_stage_ids_by_contract(stage_ids)] == ["DRD-03", "DRD-03B", "DRD-04"]


def test_noncanonical_stage_order_is_rejected():
    with pytest.raises(ValueError, match="stage_order_index"):
        require_canonical_stage_order([StageId.DRD_03, StageId.DRD_04, StageId.DRD_03B])


def test_canonical_stage_order_projection_has_numeric_indexes():
    rows = canonical_stage_order()

    assert {"stage_id": "DRD-03B", "stage_order_index": 35} in rows
