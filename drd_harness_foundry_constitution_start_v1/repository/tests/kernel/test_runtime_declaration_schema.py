import json
from pathlib import Path


def test_runtime_declaration_schema_matches_locked_required_fields():
    schema = json.loads(Path("repository/schemas/runtime_declaration.schema.json").read_text(encoding="utf-8"))

    assert schema["properties"]["primary_runtime"]["enum"] == [
        "PYTHON",
        "CODEX",
        "CODEX_PYTHON_LOOP",
        "HUMAN_GATE",
    ]
    assert set(schema["required"]) == {
        "unit_id",
        "primary_runtime",
        "python_duties",
        "codex_duties",
        "validator",
        "human_gate",
        "authority_inputs",
        "write_scope",
        "forbidden_scope",
    }
