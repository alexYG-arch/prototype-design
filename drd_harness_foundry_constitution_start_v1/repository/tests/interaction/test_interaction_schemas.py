import json
from pathlib import Path


def load_schema(name):
    return json.loads(Path(f"repository/schemas/interaction/{name}").read_text(encoding="utf-8"))


def test_interaction_graph_schema_declares_core_collections():
    schema = load_schema("interaction_graph.schema.json")

    assert set(schema["required"]) == {"graph_id", "entry_node_ids", "nodes", "edges", "clickables", "reactions", "messages"}
    assert schema["properties"]["nodes"]["items"]["$ref"] == "interaction_node.schema.json"
    assert schema["properties"]["edges"]["items"]["$ref"] == "interaction_edge.schema.json"
    assert schema["properties"]["clickables"]["items"]["$ref"] == "clickable_inventory.schema.json"
    assert schema["properties"]["reactions"]["items"]["$ref"] == "reaction_record.schema.json"
    assert schema["properties"]["messages"]["items"]["$ref"] == "interaction_message.schema.json"


def test_reaction_schema_requires_applicability_fields():
    schema = load_schema("reaction_record.schema.json")

    assert {"failure_applicability", "cancel_applicability", "async_applicability", "handoff_applicability"} <= set(schema["required"])
    assert schema["additionalProperties"] is False
    assert "repeat_trigger_strategy" in schema["properties"]
    assert "no_return_terminal" in schema["properties"]


def test_message_schema_covers_handoff_and_failure_copy():
    schema = load_schema("interaction_message.schema.json")

    assert "FAILURE_MESSAGE" in schema["properties"]["message_type"]["enum"]
    assert "HANDOFF_NOTICE" in schema["properties"]["message_type"]["enum"]
    assert "minLength" in schema["properties"]["recovery_targets"]["items"]


def test_node_schema_covers_optional_interaction_state_fields():
    schema = load_schema("interaction_node.schema.json")

    assert schema["additionalProperties"] is False
    for field in ["failure_reason", "recovery_targets", "resume_source", "trap_justification"]:
        assert field in schema["properties"]


def test_auxiliary_interaction_schemas_exist():
    for name in [
        "clickable_inventory.schema.json",
        "reaction_applicability.schema.json",
        "message_coverage_index.schema.json",
        "async_behavior.schema.json",
        "handoff_behavior.schema.json",
        "failure_recovery.schema.json",
        "overlay_closure.schema.json",
    ]:
        assert load_schema(name)["type"] == "object"
