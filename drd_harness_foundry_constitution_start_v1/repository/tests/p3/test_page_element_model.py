import copy
import json
from pathlib import Path

from drd_harness.rules.prd_adoption import AdoptionOutcome, ElementType, PrdElementDecision, PrdElementInventoryItem
from drd_harness.rules.reasoning import CanonicalEligibility, DerivationStrategy, DerivedElementDecision
from drd_harness.validators.p3_page_elements import (
    compute_canonical_element_ids,
    validate_downstream_element_refs,
    validate_page_element_artifacts,
)


ELEMENTS_ROOT = Path("repository/fixtures/p3/elements")
CLOSURE_ROOT = Path("repository/fixtures/p3/closure")


def test_p3_elements_fixture_validates_complete_artifact_set():
    artifacts = _load_fixture_artifacts()

    findings = validate_page_element_artifacts(**artifacts)

    assert findings == []
    inventory = _inventory_items(artifacts)
    decisions = _adoption_decisions(artifacts)
    canonical = compute_canonical_element_ids(inventory, decisions, [])
    assert canonical == {
        "p3-el-operations-console",
        "p3-el-case-ready-state",
        "p3-el-case-blocked-state",
        "p3-el-human-review-waiting-state",
        "p3-el-review-gap-blocked-message",
    }


def test_p3_elements_inventory_must_keep_semantic_source_model():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"].pop("semantic_source_model")

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON014" in {finding.code for finding in findings}


def test_p3_elements_upstream_hashes_must_match_actual_inputs():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"]["upstream_hashes"]["p3.closure.interaction_nodes"] = "0" * 64

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON012" in {finding.code for finding in findings}


def test_p3_elements_record_fields_must_match_schema():
    artifacts = _load_fixture_artifacts()
    artifacts["product_expansion_gaps"]["records"][0]["approved_element_id"] = "p3-el-off-schema"

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON012" in {finding.code for finding in findings}


def test_p3_elements_inventory_row_must_be_atomic():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"]["records"][0]["source_refs"] = [
        "p3-node-operations-console",
        "p3-msg-review-gap-blocked",
    ]

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON014" in {finding.code for finding in findings}


def test_p3_elements_explicit_inventory_requires_adoption_decision():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_decisions"]["records"] = artifacts["prd_element_decisions"]["records"][1:]

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON013" in {finding.code for finding in findings}


def test_p3_elements_closure_message_must_map_to_canonical_element_or_blocked_gap():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"]["records"] = [
        row
        for row in artifacts["prd_element_inventory"]["records"]
        if row["element_id"] != "p3-el-review-gap-blocked-message"
    ]
    artifacts["prd_element_decisions"]["records"] = [
        row
        for row in artifacts["prd_element_decisions"]["records"]
        if row["element_id"] != "p3-el-review-gap-blocked-message"
    ]

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON018" in {finding.code for finding in findings}


def test_p3_elements_each_canonical_state_requires_renderable_page_variant():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"] = [
        record
        for record in artifacts["renderable_page_variants"]["records"]
        if record.get("source_state_id") != "p3-el-case-blocked-state"
    ]

    findings = validate_page_element_artifacts(**artifacts)

    assert any(
        finding.code == "REASON021"
        and finding.subject_id == "p3-el-case-blocked-state"
        and "STATE_VARIANT" in finding.message
        for finding in findings
    )


def test_p3_elements_renderable_page_variant_cannot_add_product_capability():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"][1]["product_capability_addition"] = True

    findings = validate_page_element_artifacts(**artifacts)

    assert any(finding.code == "REASON021" and "product capability" in finding.message for finding in findings)


def test_p3_elements_renderable_page_variant_requires_derivation_origin():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"][1].pop("derivation_origin")

    findings = validate_page_element_artifacts(**artifacts)

    assert any(finding.code == "REASON021" and "derivation_origin" in finding.message for finding in findings)


def test_p3_elements_renderable_page_variant_requires_unique_figma_order():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"][1]["figma_frame_order_index"] = 0

    findings = validate_page_element_artifacts(**artifacts)

    assert any(finding.code == "REASON021" and "figma_frame_order_index" in finding.message for finding in findings)


def test_p3_elements_renderable_surface_id_must_match_variant_page_id():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"][1]["render_surface_id"] = "p3-el-operations-console--wrong"

    findings = validate_page_element_artifacts(**artifacts)

    assert any(finding.code == "REASON021" and "render_surface_id" in finding.message for finding in findings)


def test_p3_elements_state_variant_parent_must_follow_closure_parent_page():
    artifacts = _load_fixture_artifacts()
    second_closure_node = copy.deepcopy(artifacts["closure_interaction_nodes"]["records"][0])
    second_closure_node["node_id"] = "p3-node-secondary-console"
    second_closure_node["source_refs"] = ["p3-unit-secondary-console"]
    artifacts["closure_interaction_nodes"]["records"].append(second_closure_node)
    second_page = copy.deepcopy(artifacts["prd_element_inventory"]["records"][0])
    second_page["element_id"] = "p3-el-secondary-console"
    second_page["source_refs"] = ["p3-node-secondary-console"]
    second_page["source_text_hash"] = "d" * 64
    artifacts["prd_element_inventory"]["records"].append(second_page)
    second_decision = copy.deepcopy(artifacts["prd_element_decisions"]["records"][0])
    second_decision["element_id"] = "p3-el-secondary-console"
    second_decision["source_refs"] = ["p3-node-secondary-console"]
    artifacts["prd_element_decisions"]["records"].append(second_decision)
    second_base = copy.deepcopy(artifacts["renderable_page_variants"]["records"][0])
    second_base["variant_page_id"] = "p3-el-secondary-console"
    second_base["parent_page_id"] = "p3-el-secondary-console"
    second_base["render_surface_id"] = "p3-el-secondary-console"
    second_base["source_refs"] = ["p3-node-secondary-console"]
    second_base["trace_refs"] = ["p3-el-secondary-console", "p3-node-secondary-console"]
    artifacts["renderable_page_variants"]["records"].append(second_base)
    artifacts["renderable_page_variants"]["records"][1]["parent_page_id"] = "p3-el-secondary-console"

    findings = validate_page_element_artifacts(**artifacts)

    assert any(
        finding.code == "REASON021"
        and finding.subject_id == "p3-el-operations-console--case-ready-state"
        and "closure state parent page" in finding.message
        for finding in findings
    )


def test_p3_elements_base_page_variant_must_exist():
    artifacts = _load_fixture_artifacts()
    artifacts["renderable_page_variants"]["records"] = [
        record
        for record in artifacts["renderable_page_variants"]["records"]
        if record.get("variant_kind") != "BASE"
    ]

    findings = validate_page_element_artifacts(**artifacts)

    assert any(
        finding.code == "REASON021"
        and finding.subject_id == "p3-el-operations-console"
        and "BASE" in finding.message
        for finding in findings
    )


def test_p3_elements_unknown_closure_source_ref_cannot_enter_canonical_projection():
    artifacts = _load_fixture_artifacts()
    row = copy.deepcopy(artifacts["prd_element_inventory"]["records"][0])
    row["element_id"] = "p3-el-settings-page"
    row["source_refs"] = ["p3-node-settings-page"]
    row["source_text_hash"] = "b" * 64
    artifacts["prd_element_inventory"]["records"].append(row)
    decision = copy.deepcopy(artifacts["prd_element_decisions"]["records"][0])
    decision["element_id"] = "p3-el-settings-page"
    decision["source_refs"] = ["p3-node-settings-page"]
    decision["inference_refs"] = ["p3-inf-settings-page"]
    artifacts["prd_element_decisions"]["records"].append(decision)
    inference = copy.deepcopy(artifacts["inference_records"]["records"][0])
    inference["inference_id"] = "p3-inf-settings-page"
    inference["source_refs"] = ["p3-node-settings-page"]
    artifacts["inference_records"]["records"].append(inference)

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON018" in {finding.code for finding in findings}


def test_p3_elements_unknown_source_authority_cannot_enter_canonical_projection():
    artifacts = _load_fixture_artifacts()
    row = copy.deepcopy(artifacts["prd_element_inventory"]["records"][0])
    row["element_id"] = "p3-el-unknown-authority"
    row["source_refs"] = ["p3-src-unknown"]
    row["source_text_hash"] = "c" * 64
    artifacts["prd_element_inventory"]["records"].append(row)
    decision = copy.deepcopy(artifacts["prd_element_decisions"]["records"][0])
    decision["element_id"] = "p3-el-unknown-authority"
    decision["source_refs"] = ["p3-src-unknown"]
    decision["inference_refs"] = ["p3-inf-unknown-authority"]
    artifacts["prd_element_decisions"]["records"].append(decision)
    inference = copy.deepcopy(artifacts["inference_records"]["records"][0])
    inference["inference_id"] = "p3-inf-unknown-authority"
    inference["source_refs"] = ["p3-src-unknown"]
    artifacts["inference_records"]["records"].append(inference)

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON018" in {finding.code for finding in findings}


def test_p3_elements_inductive_candidate_cannot_be_canonical_without_human_gate():
    derived = DerivedElementDecision(
        derived_element_id="p3-el-social-login",
        derived_surface_type="CTA",
        derivation_source="pattern memory",
        obligation_refs=["p3-obligation-social-login"],
        inference_refs=["p3-inf-social-login"],
        derivation_strategy=DerivationStrategy.INDUCTIVE_AUXILIARY,
        structural_completion_review=None,
        canonical_eligibility=CanonicalEligibility.ELIGIBLE,
        blocked_by=[],
    )

    from drd_harness.validators.prd_adoption import validate_derived_element_decision

    findings = validate_derived_element_decision(derived)

    assert [finding.code for finding in findings] == ["REASON004"]


def test_p3_elements_open_gap_cannot_be_consumed_as_canonical_source():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"]["records"][0]["source_refs"] = ["p3-gap-missing-product-details"]

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON009" in {finding.code for finding in findings}


def test_p3_elements_structural_completion_review_cannot_be_canonical_before_human_gate():
    artifacts = _load_fixture_artifacts()
    artifacts["structural_completion_review"]["records"][0]["canonical_eligibility"] = "ELIGIBLE"

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON015" in {finding.code for finding in findings}


def test_p3_elements_input_obligation_requires_acquisition_path_or_gap_ref():
    artifacts = _load_fixture_artifacts()
    artifacts["input_obligations"]["records"][0]["gap_ref"] = None

    findings = validate_page_element_artifacts(**artifacts)

    assert "REASON008" in {finding.code for finding in findings}


def test_p3_elements_downstream_refs_must_use_canonical_projection():
    findings = validate_downstream_element_refs(
        ["p3-el-operations-console", "p3-el-unknown"],
        {"p3-el-operations-console"},
    )

    assert [finding.code for finding in findings] == ["REASON020"]


def test_p3_elements_noncanonical_decisions_are_excluded_from_projection():
    inventory = [
        PrdElementInventoryItem(
            element_id="p3-el-gap-routed",
            element_type=ElementType.UI_ELEMENT,
            source_refs=["p3-node-operations-console"],
            source_text_hash="a" * 64,
            stage_id="DRD-03-PAGE-ELEMENTS",
            artifact_id="p3.elements.prd_element_inventory",
        )
    ]
    decisions = [
        PrdElementDecision(
            element_id="p3-el-gap-routed",
            source_refs=["p3-node-operations-console"],
            element_type=ElementType.UI_ELEMENT,
            outcome=AdoptionOutcome.ROUTE_PRODUCT_GAP,
            normalized_label=None,
            blocking_reason="Requires product choice.",
            input_obligations=[],
            inference_refs=["p3-inf-gap-routed"],
        )
    ]

    assert compute_canonical_element_ids(inventory, decisions, []) == set()


def test_p3_elements_resolved_gap_cannot_add_non_schema_approved_element_id():
    canonical = compute_canonical_element_ids(
        [],
        [],
        [],
        [
            {
                "gap_id": "p3-gap-approved",
                "status": "RESOLVED_APPROVED",
                "decision_ref": "human-review-001",
                "approved_element_id": "p3-el-off-schema",
            }
        ],
    )

    assert canonical == set()


def _load_fixture_artifacts():
    return {
        "prd_element_inventory": copy.deepcopy(_load_json(ELEMENTS_ROOT / "prd_element_inventory.json")),
        "prd_element_decisions": copy.deepcopy(_load_json(ELEMENTS_ROOT / "prd_element_decisions.json")),
        "derived_element_decisions": copy.deepcopy(_load_json(ELEMENTS_ROOT / "derived_element_decisions.json")),
        "inference_records": copy.deepcopy(_load_json(ELEMENTS_ROOT / "inference_records.json")),
        "input_obligations": copy.deepcopy(_load_json(ELEMENTS_ROOT / "input_obligations.json")),
        "structural_completion_review": copy.deepcopy(_load_json(ELEMENTS_ROOT / "structural_completion_review.json")),
        "product_expansion_gaps": copy.deepcopy(_load_json(ELEMENTS_ROOT / "product_expansion_gaps.json")),
        "renderable_page_variants": copy.deepcopy(_load_json(ELEMENTS_ROOT / "renderable_page_variants.json")),
        "closure_interaction_nodes": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_nodes.json")),
        "closure_clickable_inventory": copy.deepcopy(_load_json(CLOSURE_ROOT / "clickable_inventory.json")),
        "closure_interaction_messages": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_messages.json")),
        "closure_async_behavior": copy.deepcopy(_load_json(CLOSURE_ROOT / "async_behavior.json")),
        "closure_failure_recovery": copy.deepcopy(_load_json(CLOSURE_ROOT / "failure_recovery.json")),
        "closure_overlay_closure": copy.deepcopy(_load_json(CLOSURE_ROOT / "overlay_closure.json")),
        "closure_handoff_behavior": copy.deepcopy(_load_json(CLOSURE_ROOT / "handoff_behavior.json")),
        "closure_handoff_manifest": copy.deepcopy(_load_json(CLOSURE_ROOT / "closure_handoff_manifest.json")),
    }


def _inventory_items(artifacts):
    return [
        PrdElementInventoryItem(
            element_id=row["element_id"],
            element_type=ElementType(row["element_type"]),
            source_refs=row["source_refs"],
            source_text_hash=row["source_text_hash"],
            stage_id=row["stage_id"],
            artifact_id=row["artifact_id"],
        )
        for row in artifacts["prd_element_inventory"]["records"]
    ]


def _adoption_decisions(artifacts):
    return [
        PrdElementDecision(
            element_id=row["element_id"],
            source_refs=row["source_refs"],
            element_type=ElementType(row["element_type"]),
            outcome=AdoptionOutcome(row["outcome"]),
            normalized_label=row["normalized_label"],
            blocking_reason=row["blocking_reason"],
            input_obligations=row["input_obligations"],
            inference_refs=row["inference_refs"],
        )
        for row in artifacts["prd_element_decisions"]["records"]
    ]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
