import copy
import json
from pathlib import Path

from drd_harness.validators.p3_patterns import validate_downstream_pattern_refs, validate_pattern_artifacts


PATTERNS_ROOT = Path("repository/fixtures/p3/patterns")
ELEMENTS_ROOT = Path("repository/fixtures/p3/elements")
CLOSURE_ROOT = Path("repository/fixtures/p3/closure")


def test_p3_patterns_fixture_validates_complete_artifact_set():
    artifacts = _load_fixture_artifacts()

    findings = validate_pattern_artifacts(**artifacts)

    assert findings == []


def test_p3_patterns_upstream_hashes_must_match_actual_inputs():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["upstream_hashes"]["p3.elements.prd_element_inventory"] = "0" * 64

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL010" in {finding.code for finding in findings}


def test_p3_patterns_schema_ref_must_match_contract():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["schema_ref"] = (
        "repository/schemas/presentation/information_presentation_registry.schema.json"
    )

    findings = validate_pattern_artifacts(**artifacts)

    assert "schema_ref does not match contract" in {finding.message for finding in findings}


def test_p3_patterns_source_refs_must_match_invalidation_inputs():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["source_refs"] = []

    findings = validate_pattern_artifacts(**artifacts)

    assert "source_refs must be a non-empty text list" in {finding.message for finding in findings}


def test_p3_patterns_record_fields_must_match_schema():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["registry"]["patterns"][0]["carrier"] = "desktop"

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL010" in {finding.code for finding in findings}


def test_p3_patterns_visual_only_reuse_is_rejected():
    artifacts = _load_fixture_artifacts()
    pattern = artifacts["shared_component_registry"]["registry"]["patterns"][0]
    pattern["semantic_role"] = "Reusable blue rounded card"
    pattern["data_structure"] = []
    pattern["operation_set"] = []
    pattern["state_model"] = []
    pattern["information_hierarchy"] = []
    pattern["interaction_model"] = []
    pattern["reuse_scope"] = ["same color and icon"]
    pattern["reuse_reason"] = "Both surfaces are blue and share an icon."

    findings = validate_pattern_artifacts(**artifacts)

    assert {"PL001", "PL002", "PL006"} <= {finding.code for finding in findings}


def test_p3_patterns_duplicate_pattern_id_is_rejected():
    artifacts = _load_fixture_artifacts()
    duplicate = copy.deepcopy(artifacts["shared_component_registry"]["registry"]["patterns"][0])
    artifacts["shared_component_registry"]["registry"]["patterns"].append(duplicate)

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL001" in {finding.code for finding in findings}


def test_p3_patterns_reuse_scope_must_use_canonical_element_or_message():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["registry"]["patterns"][0]["reuse_scope"].append("p3-gap-missing-product-details")

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL006" in {finding.code for finding in findings}


def test_p3_patterns_layout_boundary_terms_are_rejected():
    artifacts = _load_fixture_artifacts()
    pattern = artifacts["shared_component_registry"]["registry"]["patterns"][0]
    pattern["pattern_kind"] = "LAYOUT_PATTERN"
    pattern["surface_constraints"] = ["desktop carrier width and z-axis placement"]

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL007" in {finding.code for finding in findings}


def test_p3_patterns_approved_message_requires_presentation_decision():
    artifacts = _load_fixture_artifacts()
    artifacts["information_presentation_registry"]["registry"]["decisions"] = []

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL005" in {finding.code for finding in findings}


def test_p3_patterns_unknown_message_ref_is_rejected():
    artifacts = _load_fixture_artifacts()
    artifacts["information_presentation_registry"]["registry"]["decisions"][0]["message_ref"] = "p3-msg-unknown"

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL005" in {finding.code for finding in findings}


def test_p3_patterns_canonical_state_requires_presentation_decision():
    artifacts = _load_fixture_artifacts()
    decisions = artifacts["information_presentation_registry"]["registry"]["decisions"]
    artifacts["information_presentation_registry"]["registry"]["decisions"] = [
        decision
        for decision in decisions
        if "p3-el-case-ready-state" not in decision["trace_refs"]
    ]

    findings = validate_pattern_artifacts(**artifacts)

    assert any(
        finding.code == "PL005"
        and finding.subject_id == "p3-el-case-ready-state"
        and finding.message == "canonical information element lacks presentation decision"
        for finding in findings
    )


def test_p3_patterns_trace_refs_must_resolve_to_upstream_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["shared_component_registry"]["registry"]["patterns"][0]["trace_refs"].append("p3-node-unknown")

    findings = validate_pattern_artifacts(**artifacts)

    assert any(
        finding.code == "PL008"
        and finding.subject_id == "p3-pattern-case-state-status"
        for finding in findings
    )


def test_p3_patterns_equivalent_information_modes_require_exception():
    artifacts = _load_fixture_artifacts()
    second = copy.deepcopy(artifacts["information_presentation_registry"]["registry"]["decisions"][0])
    second["presentation_id"] = "p3-presentation-review-gap-blocked-modal"
    second["presentation_mode"] = "MODAL_DIALOG"
    artifacts["information_presentation_registry"]["registry"]["decisions"].append(second)

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL003" in {finding.code for finding in findings}


def test_p3_patterns_exception_allowed_modes_must_cover_used_modes():
    artifacts = _load_fixture_artifacts()
    second = copy.deepcopy(artifacts["information_presentation_registry"]["registry"]["decisions"][0])
    second["presentation_id"] = "p3-presentation-review-gap-blocked-modal"
    second["presentation_mode"] = "MODAL_DIALOG"
    artifacts["information_presentation_registry"]["registry"]["decisions"].append(second)
    artifacts["presentation_consistency_exceptions"]["records"].append(
        {
            "exception_id": "p3-exception-review-gap-mode",
            "semantic_intent": second["semantic_intent"],
            "trigger_condition": second["trigger_condition"],
            "scope": second["scope"],
            "information_lifecycle": second["information_lifecycle"],
            "allowed_modes": ["BANNER"],
            "reason": "Modal would only be allowed by Human Gate in a later decision.",
            "trace_refs": ["p3-msg-review-gap-blocked"],
        }
    )

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL003" in {finding.code for finding in findings}


def test_p3_patterns_sustained_toast_only_information_is_rejected():
    artifacts = _load_fixture_artifacts()
    decision = artifacts["information_presentation_registry"]["registry"]["decisions"][0]
    decision["presentation_mode"] = "TOAST"
    decision["recoverability"] = "Unrecoverable after timeout."

    findings = validate_pattern_artifacts(**artifacts)

    assert "PL004" in {finding.code for finding in findings}


def test_p3_patterns_downstream_pattern_refs_must_resolve():
    findings = validate_downstream_pattern_refs(
        ["p3-pattern-case-state-status", "p3-pattern-missing"],
        _load_json(PATTERNS_ROOT / "shared_component_registry.json"),
    )

    assert [finding.code for finding in findings] == ["PL001"]


def _load_fixture_artifacts():
    return {
        "shared_component_registry": copy.deepcopy(_load_json(PATTERNS_ROOT / "shared_component_registry.json")),
        "information_presentation_registry": copy.deepcopy(
            _load_json(PATTERNS_ROOT / "information_presentation_registry.json")
        ),
        "presentation_consistency_exceptions": copy.deepcopy(
            _load_json(PATTERNS_ROOT / "presentation_consistency_exceptions.json")
        ),
        "element_inventory": copy.deepcopy(_load_json(ELEMENTS_ROOT / "prd_element_inventory.json")),
        "element_decisions": copy.deepcopy(_load_json(ELEMENTS_ROOT / "prd_element_decisions.json")),
        "derived_element_decisions": copy.deepcopy(_load_json(ELEMENTS_ROOT / "derived_element_decisions.json")),
        "product_expansion_gaps": copy.deepcopy(_load_json(ELEMENTS_ROOT / "product_expansion_gaps.json")),
        "closure_interaction_messages": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_messages.json")),
    }


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
