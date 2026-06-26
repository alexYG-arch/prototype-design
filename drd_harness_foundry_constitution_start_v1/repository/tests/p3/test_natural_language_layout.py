import copy
import json
from pathlib import Path

from drd_harness.validators.p3_layout import validate_downstream_layout_refs, validate_layout_artifacts


LAYOUT_ROOT = Path("repository/fixtures/p3/layout")
ELEMENTS_ROOT = Path("repository/fixtures/p3/elements")
CLOSURE_ROOT = Path("repository/fixtures/p3/closure")
PATTERNS_ROOT = Path("repository/fixtures/p3/patterns")


def test_p3_layout_fixture_validates_complete_artifact_set():
    artifacts = _load_fixture_artifacts()

    findings = validate_layout_artifacts(**artifacts)

    assert findings == []


def test_p3_layout_upstream_hashes_must_match_actual_inputs():
    artifacts = _load_fixture_artifacts()
    artifacts["natural_language_layout"]["upstream_hashes"]["p3.elements.prd_element_inventory"] = "0" * 64

    findings = validate_layout_artifacts(**artifacts)

    assert "PL017" in {finding.code for finding in findings}


def test_p3_layout_schema_ref_must_match_contract():
    artifacts = _load_fixture_artifacts()
    artifacts["natural_language_layout"]["schema_ref"] = "repository/schemas/layout/z_axis_layering.schema.json"

    findings = validate_layout_artifacts(**artifacts)

    assert "schema_ref does not match contract" in {finding.message for finding in findings}


def test_p3_layout_nested_schema_fields_must_match_contract():
    artifacts = _load_fixture_artifacts()
    artifacts["containment_hierarchy"]["hierarchy"]["nodes"][0]["unexpected_field"] = "bad"

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL017" and "nodes item has off-schema fields" in finding.message for finding in findings)


def test_p3_layout_requires_pattern_state_z_axis_and_figma_refs():
    artifacts = _load_fixture_artifacts()
    layout = artifacts["natural_language_layout"]["layout"]
    layout["pattern_refs"] = []
    layout["state_variants"] = []
    layout["z_axis_refs"] = []
    layout["figma_metadata_ref"] = None

    findings = validate_layout_artifacts(**artifacts)

    assert "PL018" in {finding.code for finding in findings}


def test_p3_layout_composition_requires_z_axis_refs():
    artifacts = _load_fixture_artifacts()
    artifacts["layout_composition_index"]["index"]["z_axis_refs"] = []

    findings = validate_layout_artifacts(**artifacts)

    assert "composition z_axis_refs is P3-required and must be non-empty" in {
        finding.message for finding in findings
    }


def test_p3_layout_carrier_profile_requires_all_p3_carriers():
    artifacts = _load_fixture_artifacts()
    profile = artifacts["carrier_adaptation_profile"]["profile"]
    profile["required_carriers"] = ["DESKTOP", "TABLET", "MOBILE", "MOBILE_IOS"]

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL007" and "MOBILE_MATERIAL" in finding.message for finding in findings)


def test_p3_layout_ios_constraints_are_required():
    artifacts = _load_fixture_artifacts()
    ios_rule = artifacts["carrier_adaptation_profile"]["profile"]["carrier_rules"]["MOBILE_IOS"]
    ios_rule["width_behavior"] = "iOS width wraps content before any truncation."
    ios_rule["platform_constraints"] = ["iOS navigation stack"]
    ios_rule["safe_area_or_system_bars"] = "iOS bars are respected."

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL007" and "home indicator" in finding.message for finding in findings)


def test_p3_layout_material_constraints_are_required():
    artifacts = _load_fixture_artifacts()
    material_rule = artifacts["carrier_adaptation_profile"]["profile"]["carrier_rules"]["MOBILE_MATERIAL"]
    material_rule["height_scroll_behavior"] = "Material short height uses vertical scroll and disclosure."
    material_rule["input_keyboard_behavior"] = "Material keyboard inset keeps blocked message content reachable."
    material_rule["platform_constraints"] = ["Material app bar", "Material system bar"]

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL007" and "snackbar" in finding.message for finding in findings)


def test_p3_layout_flat_containment_is_rejected():
    artifacts = _load_fixture_artifacts()
    artifacts["containment_hierarchy"]["hierarchy"]["nodes"] = [
        artifacts["containment_hierarchy"]["hierarchy"]["nodes"][0]
    ]

    findings = validate_layout_artifacts(**artifacts)

    assert "PL008" in {finding.code for finding in findings}


def test_p3_layout_height_information_loss_is_rejected():
    artifacts = _load_fixture_artifacts()
    rule = artifacts["information_completeness_rules"]["records"][0]
    rule["height_behavior"] = "Hide required information when the screen is short."
    rule["information_access_path"] = "No recovery path."

    findings = validate_layout_artifacts(**artifacts)

    assert "PL010" in {finding.code for finding in findings}


def test_p3_layout_width_overflow_requires_horizontal_scroll_exception():
    artifacts = _load_fixture_artifacts()
    rule = artifacts["information_completeness_rules"]["records"][0]
    rule["width_behavior"] = "Narrow width may overflow offscreen."
    rule["information_access_path"] = "Required information remains available by scroll."
    rule["horizontal_scroll_exception"] = None

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL010" and "horizontal scroll exception" in finding.message for finding in findings)


def test_p3_layout_declared_horizontal_scroll_exception_is_allowed():
    artifacts = _load_fixture_artifacts()
    rule = artifacts["information_completeness_rules"]["records"][0]
    rule["width_behavior"] = "Narrow width may overflow offscreen only for a wide table with horizontal scroll."
    rule["information_access_path"] = "Required columns remain available by horizontal scroll and detail expansion."
    rule["horizontal_scroll_exception"] = "Wide table uses horizontal scroll with visible affordance and recovery."

    findings = validate_layout_artifacts(**artifacts)

    assert findings == []


def test_p3_layout_state_placement_unknown_message_is_rejected():
    artifacts = _load_fixture_artifacts()
    artifacts["state_placement_index"]["index"]["placements"][0]["message_id"] = "p3-msg-unknown"

    findings = validate_layout_artifacts(**artifacts)

    assert "PL011" in {finding.code for finding in findings}


def test_p3_layout_state_placement_mode_must_match_approved_presentation():
    artifacts = _load_fixture_artifacts()
    artifacts["state_placement_index"]["index"]["placements"][0]["presentation_mode"] = "TOAST"

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL011" and "presentation_mode" in finding.message for finding in findings)


def test_p3_layout_material_z_axis_requires_elevation_intent():
    artifacts = _load_fixture_artifacts()
    artifacts["z_axis_layering"]["layering"]["material_elevation_intent"] = None

    findings = validate_layout_artifacts(**artifacts)

    assert "PL013" in {finding.code for finding in findings}


def test_p3_layout_figma_metadata_cannot_introduce_write_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["figma_reconstruction_metadata"]["metadata"]["non_goals"] = [
        "Renderer implementation may write to Figma API"
    ]

    findings = validate_layout_artifacts(**artifacts)

    assert "PL015" in {finding.code for finding in findings}


def test_p3_layout_pattern_refs_must_resolve_to_approved_patterns():
    artifacts = _load_fixture_artifacts()
    artifacts["natural_language_layout"]["layout"]["pattern_refs"].append("p3-pattern-unknown")

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL016" and finding.subject_id == "p3-pattern-unknown" for finding in findings)


def test_p3_layout_trace_refs_must_resolve_to_upstream_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["state_placement_index"]["index"]["placements"][0]["trace_refs"].append("p3-trace-unknown")

    findings = validate_layout_artifacts(**artifacts)

    assert any(finding.code == "PL019" and finding.subject_id == "p3-msg-review-gap-blocked" for finding in findings)


def test_p3_layout_downstream_refs_must_resolve():
    artifacts = _load_fixture_artifacts()
    findings = validate_downstream_layout_refs(
        [
            "p3-layout-operations-console",
            "p3-layout-carrier-profile",
            "p3-el-human-review-waiting-state",
            "p3-el-review-gap-blocked-message",
            "p3-layout-state-placement-index",
            "p3-layout-z-axis",
            "p3-layout-figma-reconstruction",
            "p3-pattern-review-gap-message",
            "p3-msg-review-gap-blocked",
            "p3-layout-missing",
        ],
        artifacts["natural_language_layout"],
        artifacts["layout_composition_index"],
        carrier_adaptation_profile=artifacts["carrier_adaptation_profile"],
        containment_hierarchy=artifacts["containment_hierarchy"],
        content_growth_rules=artifacts["content_growth_rules"],
        information_completeness_rules=artifacts["information_completeness_rules"],
        state_placement_index=artifacts["state_placement_index"],
        z_axis_layering=artifacts["z_axis_layering"],
        figma_reconstruction_metadata=artifacts["figma_reconstruction_metadata"],
    )

    assert [(finding.code, finding.subject_id) for finding in findings] == [("PL016", "p3-layout-missing")]


def _load_fixture_artifacts():
    return {
        "natural_language_layout": copy.deepcopy(_load_json(LAYOUT_ROOT / "natural_language_layout.json")),
        "carrier_adaptation_profile": copy.deepcopy(_load_json(LAYOUT_ROOT / "carrier_adaptation_profile.json")),
        "containment_hierarchy": copy.deepcopy(_load_json(LAYOUT_ROOT / "containment_hierarchy.json")),
        "content_growth_rules": copy.deepcopy(_load_json(LAYOUT_ROOT / "content_growth_rules.json")),
        "information_completeness_rules": copy.deepcopy(
            _load_json(LAYOUT_ROOT / "information_completeness_rules.json")
        ),
        "state_placement_index": copy.deepcopy(_load_json(LAYOUT_ROOT / "state_placement_index.json")),
        "z_axis_layering": copy.deepcopy(_load_json(LAYOUT_ROOT / "z_axis_layering.json")),
        "layout_composition_index": copy.deepcopy(_load_json(LAYOUT_ROOT / "layout_composition_index.json")),
        "figma_reconstruction_metadata": copy.deepcopy(
            _load_json(LAYOUT_ROOT / "figma_reconstruction_metadata.json")
        ),
        "element_inventory": copy.deepcopy(_load_json(ELEMENTS_ROOT / "prd_element_inventory.json")),
        "closure_interaction_messages": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_messages.json")),
        "shared_component_registry": copy.deepcopy(_load_json(PATTERNS_ROOT / "shared_component_registry.json")),
        "information_presentation_registry": copy.deepcopy(
            _load_json(PATTERNS_ROOT / "information_presentation_registry.json")
        ),
    }


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
