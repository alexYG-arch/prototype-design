import hashlib
import json
from pathlib import Path

from drd_harness.rules.layout import Carrier
from drd_harness.validators.layout_completeness import (
    carrier_adaptation_profile_from_mapping,
    containment_hierarchy_from_mapping,
    content_growth_rule_from_mapping,
    figma_reconstruction_metadata_from_mapping,
    information_completeness_rule_from_mapping,
    natural_language_layout_from_mapping,
    state_placement_index_from_mapping,
    validate_carrier_adaptation_profile,
    validate_information_completeness_refs,
    validate_information_completeness_rule,
    validate_layout_package,
    validate_layout_reference_integrity,
    validate_state_placement_index,
    z_axis_layering_from_mapping,
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


def test_layout_package_passes_carrier_containment_growth_z_axis_and_figma_validation():
    package = _layout_package()

    _assert_artifact_contract(
        _load("natural_language_layout.json"),
        "p2.tiny_brief.natural_language_layout",
        "layout",
    )
    _assert_artifact_contract(
        _load("carrier_adaptation_profile.json"),
        "p2.tiny_brief.carrier_adaptation_profile",
        "profile",
    )
    _assert_artifact_contract(
        _load("containment_hierarchy.json"),
        "p2.tiny_brief.containment_hierarchy",
        "hierarchy",
    )
    _assert_artifact_contract(
        _load("z_axis_layering.json"),
        "p2.tiny_brief.z_axis_layering",
        "layering",
    )
    assert validate_layout_package(
        package["layout"],
        package["carrier_profile"],
        package["hierarchy"],
        package["growth_rules"],
        package["completeness_rules"],
        package["z_axis_layering"],
        package["state_index"],
        _interaction_message_ids(),
        package["figma_metadata"],
        _known_information_refs(),
    ) == []


def test_carrier_profile_covers_desktop_tablet_mobile_ios_and_material():
    profile = _layout_package()["carrier_profile"]

    assert validate_carrier_adaptation_profile(profile) == []
    assert set(profile.required_carriers) == {
        Carrier.DESKTOP,
        Carrier.TABLET,
        Carrier.MOBILE,
        Carrier.MOBILE_IOS,
        Carrier.MOBILE_MATERIAL,
    }


def test_layout_state_placements_cover_every_interaction_message():
    package = _layout_package()

    assert package["state_index"].message_ids() == set(_interaction_message_ids())


def test_layout_state_placement_rejects_unknown_interaction_message():
    record = dict(_load("natural_language_layout.json")["state_placement_index"])
    placements = list(record["placements"])
    placements.append({**placements[0], "message_id": "msg.unknown"})
    index = state_placement_index_from_mapping({**record, "placements": placements})

    findings = validate_state_placement_index(index, _interaction_message_ids())

    assert [finding.code for finding in findings] == ["PL011"]
    assert findings[0].subject_id == "msg.unknown"


def test_information_completeness_preserves_height_and_width_access():
    for rule in _layout_package()["completeness_rules"]:
        assert validate_information_completeness_rule(rule) == []
        text = f"{rule.width_behavior} {rule.information_access_path}".lower()
        assert "horizontal scroll" not in text or "not use horizontal scroll" in text


def test_information_completeness_refs_bind_known_information_sources():
    package = _layout_package()

    assert validate_information_completeness_refs(package["completeness_rules"], _known_information_refs()) == []


def test_information_completeness_refs_reject_unknown_information_source():
    record = dict(_load("natural_language_layout.json")["information_completeness_rules"][0])
    refs = list(record["required_information_refs"])
    refs.append("brief.field.unknown")
    rule = information_completeness_rule_from_mapping({**record, "required_information_refs": refs})

    findings = validate_information_completeness_refs([rule], _known_information_refs())

    assert [finding.code for finding in findings] == ["PL010"]
    assert findings[0].subject_id == "brief.field.unknown"


def test_layout_reference_integrity_rejects_unresolved_growth_ref():
    package = _layout_package()
    broken_layout = natural_language_layout_from_mapping(
        {
            **_load("natural_language_layout.json")["layout"],
            "content_growth_refs": ["p2.tiny_brief.growth.missing"],
        }
    )

    findings = validate_layout_reference_integrity(
        broken_layout,
        package["carrier_profile"],
        package["hierarchy"],
        package["growth_rules"],
        package["completeness_rules"],
        package["z_axis_layering"],
        package["state_index"],
        package["figma_metadata"],
    )

    assert [finding.code for finding in findings] == ["PL016"]


def test_layout_package_validates_generator_growth_rules_in_reference_integrity():
    package = _layout_package()
    layout_artifact = _load("natural_language_layout.json")
    growth_records = list(layout_artifact["content_growth_rules"])
    growth_records[0] = {**growth_records[0], "target_ref": "layout.missing"}
    growth_rules = (content_growth_rule_from_mapping(record) for record in growth_records)

    findings = validate_layout_package(
        package["layout"],
        package["carrier_profile"],
        package["hierarchy"],
        growth_rules,
        package["completeness_rules"],
        package["z_axis_layering"],
        package["state_index"],
        _interaction_message_ids(),
        package["figma_metadata"],
        _known_information_refs(),
    )

    assert any(finding.code == "PL016" and finding.subject_id == "layout.missing" for finding in findings)


def test_layout_reference_integrity_rejects_unresolved_growth_target_ref():
    package = _layout_package()
    layout_artifact = _load("natural_language_layout.json")
    growth_records = list(layout_artifact["content_growth_rules"])
    growth_records[0] = {**growth_records[0], "target_ref": "layout.missing"}
    growth_rules = [content_growth_rule_from_mapping(record) for record in growth_records]

    findings = validate_layout_reference_integrity(
        package["layout"],
        package["carrier_profile"],
        package["hierarchy"],
        growth_rules,
        package["completeness_rules"],
        package["z_axis_layering"],
        package["state_index"],
        package["figma_metadata"],
    )

    assert [finding.code for finding in findings] == ["PL016"]
    assert findings[0].subject_id == "layout.missing"


def test_layout_reference_integrity_rejects_unresolved_z_axis_surface_ref():
    package = _layout_package()
    layering_record = dict(_load("z_axis_layering.json")["layering"])
    layers = list(layering_record["layers"])
    layers[0] = {**layers[0], "surface_ref": "layer.missing"}
    broken_layering = z_axis_layering_from_mapping({**layering_record, "layers": layers})

    findings = validate_layout_reference_integrity(
        package["layout"],
        package["carrier_profile"],
        package["hierarchy"],
        package["growth_rules"],
        package["completeness_rules"],
        broken_layering,
        package["state_index"],
        package["figma_metadata"],
    )

    assert [finding.code for finding in findings] == ["PL016"]
    assert findings[0].subject_id == "layer.missing"


def test_layout_reference_integrity_rejects_unresolved_state_surface_id():
    package = _layout_package()
    state_record = dict(_load("natural_language_layout.json")["state_placement_index"])
    placements = list(state_record["placements"])
    placements[0] = {**placements[0], "surface_id": "surface.missing"}
    broken_index = state_placement_index_from_mapping({**state_record, "placements": placements})

    findings = validate_layout_reference_integrity(
        package["layout"],
        package["carrier_profile"],
        package["hierarchy"],
        package["growth_rules"],
        package["completeness_rules"],
        package["z_axis_layering"],
        broken_index,
        package["figma_metadata"],
    )

    assert [finding.code for finding in findings] == ["PL016"]
    assert findings[0].subject_id == "surface.missing"


def test_layout_artifacts_bind_upstream_hashes():
    for filename in [
        "natural_language_layout.json",
        "carrier_adaptation_profile.json",
        "containment_hierarchy.json",
        "z_axis_layering.json",
    ]:
        artifact = _load(filename)
        for artifact_id, path in UPSTREAM_ARTIFACT_FILES.items():
            assert artifact_id in artifact["upstream_artifact_refs"]
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(path)


def _layout_package():
    layout_artifact = _load("natural_language_layout.json")
    return {
        "layout": natural_language_layout_from_mapping(layout_artifact["layout"]),
        "carrier_profile": carrier_adaptation_profile_from_mapping(_load("carrier_adaptation_profile.json")["profile"]),
        "hierarchy": containment_hierarchy_from_mapping(_load("containment_hierarchy.json")["hierarchy"]),
        "growth_rules": [
            content_growth_rule_from_mapping(record)
            for record in layout_artifact["content_growth_rules"]
        ],
        "completeness_rules": [
            information_completeness_rule_from_mapping(record)
            for record in layout_artifact["information_completeness_rules"]
        ],
        "z_axis_layering": z_axis_layering_from_mapping(_load("z_axis_layering.json")["layering"]),
        "state_index": state_placement_index_from_mapping(layout_artifact["state_placement_index"]),
        "figma_metadata": figma_reconstruction_metadata_from_mapping(layout_artifact["figma_metadata"]),
    }


def _interaction_message_ids():
    return [record["message_id"] for record in _load("interaction_messages.json")["records"]]


def _known_information_refs():
    prd_refs = {record["element_id"] for record in _load("prd_element_inventory.json")["records"]}
    clickable_refs = {record["clickable_id"] for record in _load("clickable_inventory.json")["records"]}
    return sorted(prd_refs | clickable_refs | set(_interaction_message_ids()))


def _load(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str, payload_key: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == "DRD-04-PRESENTATION-LAYOUT"
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["schema_payload_key"] == payload_key
    assert payload["validator_ref"] == "repository/src/drd_harness/validators/layout_completeness.py"
    assert payload["promotion_state"] == "CANDIDATE"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
