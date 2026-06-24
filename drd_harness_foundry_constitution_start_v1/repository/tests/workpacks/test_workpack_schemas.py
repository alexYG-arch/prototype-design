import json
from pathlib import Path


def test_workpack_schemas_are_parseable_json():
    schema_dir = Path("repository/schemas/workpacks")
    schema_names = {
        "implementation_workpack.schema.json",
        "code_target_map.schema.json",
        "test_obligation_matrix.schema.json",
        "implementation_workpack_index.schema.json",
        "skill_binding_manifest.schema.json",
        "traceability_exception.schema.json",
        "workpack_readiness_report.schema.json",
    }

    parsed = {path.name: json.loads(path.read_text()) for path in schema_dir.glob("*.schema.json")}

    assert set(parsed) == schema_names
    assert all(schema["$schema"].endswith("draft/2020-12/schema") for schema in parsed.values())
    assert parsed["implementation_workpack.schema.json"]["additionalProperties"] is False
