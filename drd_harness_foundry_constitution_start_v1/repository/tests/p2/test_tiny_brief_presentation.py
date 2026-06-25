import hashlib
import json
from pathlib import Path

from drd_harness.validators.presentation_consistency import (
    information_presentation_decision_from_mapping,
    shared_component_pattern_from_mapping,
    validate_interaction_message_presentation_mapping,
    validate_layout_pattern_refs,
    validate_presentation_consistency,
    validate_shared_component_registry,
)


FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")
REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id",
    "stage_id",
    "fixture_id",
    "path",
    "schema_ref",
    "schema_payload_key",
    "source_refs",
    "upstream_artifact_refs",
    "upstream_hashes",
    "validator_ref",
    "review_gate",
    "promotion_state",
    "invalidation_inputs",
}
UPSTREAM_ARTIFACT_FILES = {
    "p2.tiny_brief.source_prd": FIXTURE_ROOT / "source/source_prd.md",
    "p2.tiny_brief.source_snapshot_manifest": FIXTURE_ROOT / "source_snapshot_manifest.json",
    "p2.tiny_brief.prd_element_inventory": FIXTURE_ROOT / "prd_element_inventory.json",
    "p2.tiny_brief.derived_element_decisions": FIXTURE_ROOT / "derived_element_decisions.json",
    "p2.tiny_brief.product_expansion_gaps": FIXTURE_ROOT / "product_expansion_gaps.json",
    "p2.tiny_brief.inference_records": FIXTURE_ROOT / "inference_records.json",
    "p2.tiny_brief.structural_completion_review": FIXTURE_ROOT / "structural_completion_review.json",
    "p2.tiny_brief.interaction_graph": FIXTURE_ROOT / "interaction_graph.json",
    "p2.tiny_brief.clickable_inventory": FIXTURE_ROOT / "clickable_inventory.json",
    "p2.tiny_brief.async_behavior": FIXTURE_ROOT / "async_behavior.json",
    "p2.tiny_brief.failure_recovery": FIXTURE_ROOT / "failure_recovery.json",
    "p2.tiny_brief.interaction_messages": FIXTURE_ROOT / "interaction_messages.json",
}


def test_information_presentation_registry_covers_interaction_messages_and_primary_actions():
    artifact = _load("information_presentation_registry.json")
    registry = artifact["registry"]
    decisions = [information_presentation_decision_from_mapping(record) for record in registry["decisions"]]
    decision_ids = {decision.presentation_id for decision in decisions}

    _assert_artifact_contract(
        artifact,
        "p2.tiny_brief.information_presentation_registry",
        "registry",
        "repository/src/drd_harness/validators/presentation_consistency.py",
    )
    assert validate_presentation_consistency(decisions) == []
    assert validate_interaction_message_presentation_mapping(_interaction_message_ids(), decisions) == []
    assert {
        "presentation.action.validate",
        "presentation.action.generate",
        "presentation.msg.validation_progress",
        "presentation.msg.generation_progress",
    } <= decision_ids
    assert all(decision.presentation_mode.value != "TOAST" for decision in decisions if decision.user_decision_need)


def test_shared_component_registry_uses_semantic_reuse_not_visual_similarity():
    artifact = _load("shared_component_registry.json")
    patterns = [
        shared_component_pattern_from_mapping(record)
        for record in artifact["registry"]["patterns"]
    ]

    _assert_artifact_contract(
        artifact,
        "p2.tiny_brief.shared_component_registry",
        "registry",
        "repository/src/drd_harness/validators/presentation_consistency.py",
    )
    assert validate_shared_component_registry(patterns) == []
    assert {pattern.pattern_id for pattern in patterns} == {
        "pattern.primary_action_group",
        "pattern.overlay_status_panel",
        "pattern.brief_field_stack",
    }
    assert all("visual" not in (pattern.reuse_reason or "").lower() for pattern in patterns)


def test_presentation_mapping_reports_unmapped_interaction_message():
    decisions = [
        information_presentation_decision_from_mapping(record)
        for record in _load("information_presentation_registry.json")["registry"]["decisions"]
        if record.get("message_ref") != "msg.final_ready"
    ]

    findings = validate_interaction_message_presentation_mapping(_interaction_message_ids(), decisions)

    assert [finding.code for finding in findings] == ["PL005"]
    assert findings[0].subject_id == "msg.final_ready"


def test_presentation_mapping_reports_unknown_interaction_message_ref():
    records = list(_load("information_presentation_registry.json")["registry"]["decisions"])
    unknown_record = {
        **records[0],
        "presentation_id": "presentation.msg.unknown",
        "message_ref": "msg.unknown",
    }
    decisions = [
        information_presentation_decision_from_mapping(record)
        for record in records + [unknown_record]
    ]

    findings = validate_interaction_message_presentation_mapping(_interaction_message_ids(), decisions)

    assert [finding.code for finding in findings] == ["PL005"]
    assert findings[0].subject_id == "msg.unknown"


def test_layout_pattern_refs_bind_shared_component_registry():
    layout = _load("natural_language_layout.json")["layout"]
    patterns = [
        shared_component_pattern_from_mapping(record)
        for record in _load("shared_component_registry.json")["registry"]["patterns"]
    ]

    assert validate_layout_pattern_refs(layout["pattern_refs"], patterns) == []


def test_layout_pattern_refs_reject_missing_shared_component_pattern():
    patterns = [
        shared_component_pattern_from_mapping(record)
        for record in _load("shared_component_registry.json")["registry"]["patterns"]
    ]

    findings = validate_layout_pattern_refs(["pattern.missing"], patterns)

    assert [finding.code for finding in findings] == ["PL001"]
    assert findings[0].subject_id == "pattern.missing"


def test_shared_component_registry_rejects_duplicate_pattern_id():
    records = list(_load("shared_component_registry.json")["registry"]["patterns"])
    patterns = [shared_component_pattern_from_mapping(record) for record in records + [dict(records[0])]]

    findings = validate_shared_component_registry(patterns)

    assert [finding.code for finding in findings] == ["PL001"]


def test_presentation_artifacts_bind_upstream_hashes():
    for filename in ["information_presentation_registry.json", "shared_component_registry.json"]:
        artifact = _load(filename)
        for artifact_id, path in UPSTREAM_ARTIFACT_FILES.items():
            assert artifact_id in artifact["upstream_artifact_refs"]
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(path)


def _interaction_message_ids():
    return [record["message_id"] for record in _load("interaction_messages.json")["records"]]


def _load(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str, payload_key: str, validator_ref: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == "DRD-04-PRESENTATION-LAYOUT"
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["schema_payload_key"] == payload_key
    assert payload["validator_ref"] == validator_ref
    assert payload["promotion_state"] == "CANDIDATE"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
