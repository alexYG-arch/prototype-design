import json
from pathlib import Path

from drd_harness.stages.source_snapshot import create_source_snapshot
from drd_harness.validators.source_intake import validate_source_intake_artifacts


FIXTURE_ROOT = Path("repository/fixtures/p3/source_intake")


def test_p3_source_intake_fixture_validates_multi_source_boundaries():
    artifacts = _load_fixture_artifacts()

    findings = validate_source_intake_artifacts(**artifacts)

    assert findings == []
    authority = {
        row["source_item_id"]: row for row in artifacts["source_authority_index"]["sources"]
    }
    assert authority["p3-src-brief"]["natural_language_primary"] is True
    assert authority["p3-src-brief"]["inventory_role"] == "index_verification_only"


def test_existing_snapshot_freeze_can_feed_p3_visual_review_boundary(tmp_path: Path):
    source = tmp_path / "screen.png"
    snapshot = tmp_path / "snapshots" / "screen.png"
    source.write_bytes(b"fake image bytes")

    manifest = create_source_snapshot(
        source,
        snapshot,
        snapshot_id="screen.snapshot.001",
        created_at="2026-06-26T00:00:00Z",
        content_type="image/png",
    )
    artifacts = {
        "input_register": {
            "sources": [
                {
                    "source_item_id": "screen-001",
                    "source_path": str(source),
                    "media_kind": "screenshot",
                    "origin": "local test upload",
                    "submitted_at": "2026-06-26T00:00:00Z",
                    "source_role": "visual_reference",
                    "access_boundary": "local_snapshot_allowed",
                    "permission_boundary": "run-local",
                }
            ]
        },
        "intake_decisions": {
            "decisions": [
                {
                    "source_item_id": "screen-001",
                    "state": "review_required",
                    "downstream_eligibility": "review_required",
                    "decision_reasons": ["visual source requires separate extraction evidence"],
                    "snapshot_manifest_ref": "screen.snapshot.001",
                    "snapshot_hash": manifest.snapshot_hash,
                    "risk_flags": [],
                    "requires_product_capability_expansion": False,
                    "extraction_evidence_refs": [],
                }
            ]
        },
        "source_snapshot_manifests": {
            "snapshots": [
                {
                    "source_item_id": "screen-001",
                    "manifest": manifest.to_dict(),
                }
            ]
        },
        "source_authority_index": {
            "sources": [
                {
                    "source_item_id": "screen-001",
                    "authority_role": "visual_identity_only_until_extracted",
                    "source_role": "visual_reference",
                    "semantic_authority": False,
                    "natural_language_primary": False,
                    "inventory_role": "identity_hash_only",
                    "conflict_policy": "human_review_required_before_semantic_adoption",
                }
            ]
        },
        "redaction_and_exclusion_log": {
            "records": [
                {
                    "source_item_id": "screen-001",
                    "action": "semantic_adoption_blocked",
                    "reason": "visual source lacks extraction evidence",
                    "downstream_effect": "may preserve blocker only",
                }
            ]
        },
        "downstream_handoff_manifest": {
            "stage_id": "DRD-00",
            "run_id": "p3.source_intake.dynamic.001",
            "input_artifacts": [str(source)],
            "input_hashes": [manifest.snapshot_hash],
            "source_prd_snapshot_hash": manifest.snapshot_hash,
            "output_artifacts": [str(snapshot)],
            "output_hashes": [manifest.snapshot_hash],
            "validator_result_hash": "a" * 64,
        },
    }

    assert validate_source_intake_artifacts(**artifacts) == []


def test_external_link_metadata_cannot_be_eligible_without_local_snapshot():
    artifacts = _load_fixture_artifacts()
    decision = _decision(artifacts, "p3-src-link")
    decision["state"] = "eligible"
    decision["downstream_eligibility"] = "eligible"

    findings = validate_source_intake_artifacts(**artifacts)

    assert "SOURCEINTAKE005" in {finding.code for finding in findings}


def test_visual_source_without_extraction_evidence_cannot_be_semantic_authority():
    artifacts = _load_fixture_artifacts()
    decision = _decision(artifacts, "p3-src-screenshot")
    decision["state"] = "eligible"
    decision["downstream_eligibility"] = "eligible"
    decision["extraction_evidence_refs"] = []

    findings = validate_source_intake_artifacts(**artifacts)

    assert "SOURCEINTAKE006" in {finding.code for finding in findings}


def test_product_capability_expansion_source_requires_human_review():
    artifacts = _load_fixture_artifacts()
    decision = _decision(artifacts, "p3-src-link")
    decision["state"] = "eligible"
    decision["downstream_eligibility"] = "eligible"
    decision["requires_product_capability_expansion"] = True

    findings = validate_source_intake_artifacts(**artifacts)

    assert "SOURCEINTAKE007" in {finding.code for finding in findings}


def test_rejected_source_cannot_be_named_as_downstream_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["downstream_handoff_manifest"]["input_artifacts"].append("p3-src-link")

    findings = validate_source_intake_artifacts(**artifacts)

    assert "SOURCEINTAKE011" in {finding.code for finding in findings}


def _load_fixture_artifacts():
    return {
        "input_register": _load_json("input_register.json"),
        "intake_decisions": _load_json("intake_decisions.json"),
        "source_snapshot_manifests": _load_json("source_snapshot_manifests.json"),
        "source_authority_index": _load_json("source_authority_index.json"),
        "redaction_and_exclusion_log": _load_json("redaction_and_exclusion_log.json"),
        "downstream_handoff_manifest": _load_json("downstream_handoff_manifest.json"),
    }


def _load_json(name: str):
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _decision(artifacts, source_id: str):
    return next(
        row for row in artifacts["intake_decisions"]["decisions"] if row["source_item_id"] == source_id
    )
