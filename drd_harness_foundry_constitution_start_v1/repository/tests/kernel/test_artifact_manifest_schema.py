import json
from pathlib import Path

import pytest

from drd_harness.kernel.artifacts import ArtifactManifest, sha256_file


def test_artifact_manifest_accepts_human_markdown():
    manifest = ArtifactManifest.from_dict(
        {
            "artifact_id": "LAYOUT-COMPOSITION-SPEC",
            "path": "LAYOUT_COMPOSITION_SPEC.md",
            "format": "markdown",
            "authority_role": "human_semantic",
        }
    )

    manifest.validate_format_policy()
    assert manifest.to_dict()["format"] == "markdown"


def test_artifact_manifest_requires_json_for_operational_control():
    manifest = ArtifactManifest.from_dict(
        {
            "artifact_id": "LOCK",
            "path": "SPEC_LOCK.md",
            "format": "markdown",
            "authority_role": "operational_control",
        }
    )

    with pytest.raises(ValueError, match="must be json"):
        manifest.validate_format_policy()


def test_artifact_manifest_rejects_yaml():
    manifest = ArtifactManifest.from_dict(
        {
            "artifact_id": "PAGE_LAYOUT",
            "path": "PAGE_LAYOUT.yaml",
            "format": "json",
            "authority_role": "operational_control",
        }
    )

    with pytest.raises(ValueError, match="YAML"):
        manifest.validate_format_policy()


def test_sha256_file_reads_file_content(tmp_path: Path):
    target = tmp_path / "artifact.json"
    target.write_text('{"ok": true}\n', encoding="utf-8")

    assert sha256_file(target) == "55f66c2c5aeb275ff5b1ae26b321d5c0b8ceda8c034b19c2643e046d024919f3"


def test_artifact_manifest_schema_declares_required_fields():
    schema = json.loads(Path("repository/schemas/artifact_manifest.schema.json").read_text(encoding="utf-8"))

    assert set(schema["required"]) == {"artifact_id", "path", "format", "authority_role"}
    assert schema["properties"]["sha256"]["pattern"] == "^[a-f0-9]{64}$"
