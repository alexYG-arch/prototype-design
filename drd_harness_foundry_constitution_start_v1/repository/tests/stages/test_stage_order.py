import pytest

from drd_harness.stages.contracts import (
    StageId,
    candidate_outputs_for_stage,
    canonical_outputs_for_stage,
    canonical_stage_order,
    promotion_outputs_for_stage,
    sort_stage_ids_by_contract,
)
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


def test_semantic_stage_outputs_split_candidate_and_promotion_artifacts():
    candidate_outputs = candidate_outputs_for_stage(StageId.DRD_01)
    promotion_outputs = promotion_outputs_for_stage(StageId.DRD_01)

    assert candidate_outputs == [
        "DRD-01/PRD_EXPERIENCE_BRIEF.md",
        "DRD-01/experience_fact_index.json",
        "DRD-01/page_detail_inventory.json",
    ]
    assert promotion_outputs == [
        "DRD-01/APPROVED_SEMANTIC_ARTIFACT.md",
        "DRD-01/approved_semantic_artifact.json",
    ]
    assert canonical_outputs_for_stage(StageId.DRD_01) == candidate_outputs + promotion_outputs


def test_drd05_canonical_outputs_include_compiler_sidecars():
    assert canonical_outputs_for_stage(StageId.DRD_05) == [
        "DRD-05/FINAL_DRD.md",
        "DRD-05/final_drd_manifest.json",
        "DRD-05/final_drd_toc.json",
        "DRD-05/final_drd_reference_index.json",
        "DRD-05/final_drd_hash_index.json",
        "DRD-05/compiler_conservation_report.json",
        "DRD-05/compiler_semantic_unit_inventory.json",
        "DRD-05/compiler_input_bundle.json",
    ]
