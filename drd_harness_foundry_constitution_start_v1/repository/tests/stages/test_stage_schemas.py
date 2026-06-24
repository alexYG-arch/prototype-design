import json
from pathlib import Path


def test_source_snapshot_manifest_schema_requires_locked_fields():
    schema = json.loads(Path("repository/schemas/stages/source_snapshot_manifest.schema.json").read_text(encoding="utf-8"))

    assert set(schema["required"]) == {
        "source_prd_snapshot_id",
        "source_path",
        "snapshot_path",
        "snapshot_hash",
        "created_at",
        "byte_size",
        "content_type",
        "normalization_method",
        "source_identity",
    }


def test_stage_manifest_schema_includes_drd03b_and_statuses():
    schema = json.loads(Path("repository/schemas/stages/stage_manifest.schema.json").read_text(encoding="utf-8"))

    assert "DRD-03B" in schema["properties"]["stage_id"]["enum"]
    assert "CANDIDATE" in schema["properties"]["status"]["enum"]
    assert "APPROVED" in schema["properties"]["status"]["enum"]


def test_dependency_manifest_schema_binds_hashes():
    schema = json.loads(Path("repository/schemas/stages/dependency_manifest.schema.json").read_text(encoding="utf-8"))

    assert "input_hashes" in schema["required"]
    assert "output_hashes" in schema["required"]
    assert schema["properties"]["validator_result_hash"]["pattern"] == "^[a-f0-9]{64}$"
