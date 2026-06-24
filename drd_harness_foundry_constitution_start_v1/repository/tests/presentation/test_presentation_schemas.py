import json
from pathlib import Path


def load_schema(name):
    return json.loads(Path(f"repository/schemas/presentation/{name}").read_text(encoding="utf-8"))


def test_shared_component_schema_requires_semantic_fields():
    schema = load_schema("shared_component_registry.schema.json")
    pattern_schema = schema["properties"]["patterns"]["items"]

    assert pattern_schema["additionalProperties"] is False
    for field in ["semantic_role", "data_structure", "operation_set", "state_model", "trace_refs"]:
        assert field in pattern_schema["required"]


def test_information_presentation_schema_declares_modes():
    schema = load_schema("information_presentation_registry.schema.json")
    decision_schema = schema["properties"]["decisions"]["items"]

    assert "TOAST" in decision_schema["properties"]["presentation_mode"]["enum"]
    assert "ERROR_SUMMARY" in decision_schema["properties"]["presentation_mode"]["enum"]


def test_exception_schema_requires_reason_and_allowed_modes():
    schema = load_schema("presentation_consistency_exception.schema.json")

    assert {"allowed_modes", "reason", "trace_refs"} <= set(schema["required"])
