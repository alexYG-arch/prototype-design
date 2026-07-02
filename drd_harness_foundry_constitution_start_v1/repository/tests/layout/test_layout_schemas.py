import json
from pathlib import Path


def load_schema(path):
    return json.loads(Path(f"repository/schemas/layout/{path}").read_text(encoding="utf-8"))


def test_required_layout_schemas_exist_and_are_objects():
    for name in [
        "natural_language_layout.schema.json",
        "carrier_adaptation_profile.schema.json",
        "containment_hierarchy.schema.json",
        "layout_composition_index.schema.json",
        "content_growth_rule.schema.json",
        "information_completeness_rule.schema.json",
        "z_axis_layering.schema.json",
        "state_placement_index.schema.json",
        "figma_reconstruction_metadata.schema.json",
    ]:
        assert load_schema(name)["type"] == "object"


def test_natural_language_layout_schema_requires_core_indices():
    schema = load_schema("natural_language_layout.schema.json")

    assert {"carrier_profile_refs", "containment_tree_ref", "content_growth_refs"} <= set(schema["required"])
    assert {"semantic_authority", "inventory_role"} <= set(schema["required"])


def test_carrier_schema_covers_ios_and_material():
    schema = load_schema("carrier_adaptation_profile.schema.json")

    carrier_enum = schema["properties"]["required_carriers"]["items"]["enum"]
    assert "MOBILE_IOS" in carrier_enum
    assert "MOBILE_MATERIAL" in carrier_enum


def test_z_axis_schema_covers_material_layer_types():
    schema = load_schema("z_axis_layering.schema.json")

    layer_enum = schema["properties"]["layers"]["items"]["properties"]["layer_kind"]["enum"]
    assert "MODAL" in layer_enum
    assert "SNACKBAR" in layer_enum


def test_information_completeness_schema_allows_horizontal_scroll_exception():
    schema = load_schema("information_completeness_rule.schema.json")

    assert "horizontal_scroll_exception" in schema["properties"]


def test_figma_metadata_schema_requires_page_arrangement_order():
    schema = load_schema("figma_reconstruction_metadata.schema.json")

    assert "page_arrangement_order" in schema["required"]
    order_props = schema["properties"]["page_arrangement_order"]["items"]["properties"]
    assert {"module_id", "function_group_id", "figma_frame_order_index", "derivation_origin"} <= set(order_props)
