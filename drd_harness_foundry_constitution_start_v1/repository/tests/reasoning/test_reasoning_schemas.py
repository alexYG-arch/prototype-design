import json
from pathlib import Path


def load_schema(name):
    return json.loads(Path(f"repository/schemas/reasoning/{name}").read_text(encoding="utf-8"))


def test_inference_record_schema_includes_locked_classes_and_required_fields():
    schema = load_schema("inference_record.schema.json")

    assert "DEDUCTIVE_NECESSITY" in schema["properties"]["inference_class"]["enum"]
    assert "INDUCTIVE_CANDIDATE" in schema["properties"]["inference_class"]["enum"]
    assert "unresolved_product_choices" in schema["required"]


def test_prd_element_inventory_schema_is_source_explicit_universe():
    schema = load_schema("prd_element_inventory.schema.json")

    assert set(schema["required"]) == {
        "element_id",
        "element_type",
        "source_refs",
        "source_text_hash",
        "stage_id",
        "artifact_id",
    }


def test_prd_element_decision_schema_includes_gap_routing_outcome():
    schema = load_schema("prd_element_decision.schema.json")

    assert "ROUTE_PRODUCT_GAP" in schema["properties"]["outcome"]["enum"]


def test_structural_completion_schema_has_candidate_options_and_risk():
    schema = load_schema("structural_completion_review.schema.json")

    assert "candidate_options" in schema["required"]
    assert "product_expansion_risk" in schema["required"]


def test_product_gap_and_input_obligation_schemas_exist():
    gap = load_schema("product_expansion_gap.schema.json")
    obligation = load_schema("input_obligation.schema.json")

    assert "STRUCTURAL_COMPLETION_ESCALATED" in gap["properties"]["gap_type"]["enum"]
    assert {"acquisition_path", "gap_ref"} <= set(obligation["required"])


def test_renderable_page_variant_schema_prevents_product_capability_addition():
    schema = load_schema("renderable_page_variant.schema.json")

    assert schema["properties"]["product_capability_addition"]["const"] is False
    assert {"variant_page_id", "parent_page_id", "source_state_id"} <= set(schema["required"])
    assert {
        "module_id",
        "function_group_id",
        "figma_frame_order_index",
        "derivation_origin",
        "derivation_basis_refs",
        "requires_human_review",
    } <= set(schema["required"])
    assert "DEDUCTIVE_REQUIRED" in schema["properties"]["derivation_origin"]["enum"]
