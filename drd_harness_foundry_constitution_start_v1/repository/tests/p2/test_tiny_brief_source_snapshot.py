import hashlib
import json
from pathlib import Path

from drd_harness.stages.source_snapshot import validate_source_snapshot_manifest


APPROVED_PRD = Path("build_program/phases/P2/candidates/P2-SPEC-01/P2_VERTICAL_SLICE_PRD.md")
FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")
SOURCE_PRD = FIXTURE_ROOT / "source/source_prd.md"
SNAPSHOT_MANIFEST = FIXTURE_ROOT / "source_snapshot_manifest.json"

REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id",
    "stage_id",
    "fixture_id",
    "path",
    "schema_ref",
    "source_refs",
    "upstream_artifact_refs",
    "upstream_hashes",
    "validator_ref",
    "review_gate",
    "promotion_state",
    "invalidation_inputs",
}


def test_tiny_brief_source_prd_is_exact_locked_spec_snapshot():
    assert SOURCE_PRD.read_bytes() == APPROVED_PRD.read_bytes()

    manifest = _load_manifest()["manifest"]
    assert manifest["source_path"] == str(APPROVED_PRD)
    assert manifest["snapshot_path"] == str(SOURCE_PRD)
    assert manifest["snapshot_hash"] == _sha256_file(SOURCE_PRD)
    assert manifest["snapshot_hash"] == _sha256_file(APPROVED_PRD)
    assert manifest["byte_size"] == SOURCE_PRD.stat().st_size


def test_source_snapshot_manifest_declares_artifact_contract_and_validates_hash_binding():
    payload = _load_manifest()

    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == "p2.tiny_brief.source_snapshot_manifest"
    assert payload["stage_id"] == "DRD-00-SOURCE-FREEZE"
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["validator_ref"] == "repository/src/drd_harness/stages/source_snapshot.py"
    assert payload["schema_payload_key"] == "manifest"
    assert validate_source_snapshot_manifest(payload["manifest"]) == []


def test_source_snapshot_manifest_reports_hash_drift():
    manifest = dict(_load_manifest()["manifest"])
    manifest["snapshot_hash"] = "0" * 64

    findings = validate_source_snapshot_manifest(manifest)

    assert [finding.code for finding in findings] == ["STAGE003"]


def test_source_snapshot_manifest_reports_malformed_payload_without_crashing():
    findings = validate_source_snapshot_manifest(object())

    assert [finding.code for finding in findings] == ["STAGE012"]


def test_source_snapshot_manifest_requires_sha256_hex_hash():
    manifest = dict(_load_manifest()["manifest"])
    manifest["snapshot_hash"] = "z" * 64

    findings = validate_source_snapshot_manifest(manifest)

    assert "STAGE003" in [finding.code for finding in findings]


def _load_manifest():
    return json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
