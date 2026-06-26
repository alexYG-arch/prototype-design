import copy
import json
from pathlib import Path

from drd_harness.validators.p3_interaction_closure import validate_interaction_closure_artifacts


CLOSURE_ROOT = Path("repository/fixtures/p3/closure")
DISTILL_ROOT = Path("repository/fixtures/p3/distill")


def test_p3_closure_fixture_validates_complete_artifact_set():
    artifacts = _load_fixture_artifacts()

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert findings == []
    graph = artifacts["interaction_graph"]["graph"]
    assert graph["entry_node_ids"] == ["p3-node-operations-console"]
    assert artifacts["reaction_applicability"]["records"] == {}
    handoff = artifacts["closure_handoff_manifest"]["records"][0]
    assert "p3-unit-visual-blocker" in handoff["blocked_graph_units"]
    assert "p3-gap-missing-product-details" in handoff["review_blockers"]


def test_p3_closure_node_slice_must_match_canonical_graph():
    artifacts = _load_fixture_artifacts()
    artifacts["interaction_nodes"]["records"][0]["node_type"] = "STATE"

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION001" in {finding.code for finding in findings}


def test_p3_closure_edge_slice_must_match_canonical_graph():
    artifacts = _load_fixture_artifacts()
    artifacts["interaction_edges"]["records"][0]["target_ref"] = "p3-node-case-blocked-state"

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION013" in {finding.code for finding in findings}


def test_p3_closure_message_coverage_index_must_cover_all_messages():
    artifacts = _load_fixture_artifacts()
    artifacts["message_coverage_index"]["coverage_index"]["coverage"] = []

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION017" in {finding.code for finding in findings}


def test_p3_closure_payload_shape_must_match_contract():
    artifacts = _load_fixture_artifacts()
    artifacts["clickable_inventory"]["records"] = {}

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION021" in {finding.code for finding in findings}


def test_p3_closure_payload_rows_must_be_objects():
    artifacts = _load_fixture_artifacts()
    artifacts["clickable_inventory"]["records"] = ["bad-row"]

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION021" in {finding.code for finding in findings}


def test_p3_closure_upstream_hashes_must_match_declared_refs():
    artifacts = _load_fixture_artifacts()
    artifacts["async_behavior"]["upstream_hashes"]["p3.distill.semantic_unit_map"] = "bad-hash"

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION021" in {finding.code for finding in findings}


def test_p3_closure_duplicate_split_rows_are_rejected():
    artifacts = _load_fixture_artifacts()
    duplicate = copy.deepcopy(artifacts["interaction_nodes"]["records"][0])
    artifacts["interaction_nodes"]["records"].append(duplicate)

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION012" in {finding.code for finding in findings}


def test_p3_closure_reaction_applicability_must_be_reaction_id_keyed():
    artifacts = _load_fixture_artifacts()
    artifacts["reaction_applicability"]["records"] = {
        "p3-reaction-unknown": {
            "failure_applicability": "CANNOT_FAIL",
            "cancel_applicability": "NOT_CANCELLABLE",
            "async_applicability": "IMMEDIATE",
            "handoff_applicability": "INTERNAL_ONLY",
        }
    }

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION005" in {finding.code for finding in findings}


def test_blocked_distilled_unit_cannot_become_eligible_graph_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["interaction_graph"]["graph"]["nodes"][0]["source_refs"].append("p3-unit-visual-blocker")
    artifacts["interaction_nodes"]["records"][0]["source_refs"].append("p3-unit-visual-blocker")

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION022" in {finding.code for finding in findings}


def test_open_product_gap_must_remain_review_blocked_in_closure_handoff():
    artifacts = _load_fixture_artifacts()
    artifacts["closure_handoff_manifest"]["records"][0]["review_blockers"] = []

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION022" in {finding.code for finding in findings}


def test_closure_handoff_source_hashes_must_match_artifact_upstream_hashes():
    artifacts = _load_fixture_artifacts()
    artifacts["closure_handoff_manifest"]["records"][0]["source_artifact_hashes"][
        "p3.distill.semantic_unit_map"
    ] = "0" * 64

    findings = validate_interaction_closure_artifacts(**artifacts)

    assert "INTERACTION022" in {finding.code for finding in findings}


def _load_fixture_artifacts():
    return {
        "interaction_graph": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_graph.json")),
        "interaction_nodes": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_nodes.json")),
        "interaction_edges": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_edges.json")),
        "clickable_inventory": copy.deepcopy(_load_json(CLOSURE_ROOT / "clickable_inventory.json")),
        "reaction_records": copy.deepcopy(_load_json(CLOSURE_ROOT / "reaction_records.json")),
        "reaction_applicability": copy.deepcopy(_load_json(CLOSURE_ROOT / "reaction_applicability.json")),
        "async_behavior": copy.deepcopy(_load_json(CLOSURE_ROOT / "async_behavior.json")),
        "handoff_behavior": copy.deepcopy(_load_json(CLOSURE_ROOT / "handoff_behavior.json")),
        "failure_recovery": copy.deepcopy(_load_json(CLOSURE_ROOT / "failure_recovery.json")),
        "overlay_closure": copy.deepcopy(_load_json(CLOSURE_ROOT / "overlay_closure.json")),
        "interaction_messages": copy.deepcopy(_load_json(CLOSURE_ROOT / "interaction_messages.json")),
        "message_coverage_index": copy.deepcopy(_load_json(CLOSURE_ROOT / "message_coverage_index.json")),
        "closure_handoff_manifest": copy.deepcopy(_load_json(CLOSURE_ROOT / "closure_handoff_manifest.json")),
        "distill_closure_handoff_manifest": copy.deepcopy(_load_json(DISTILL_ROOT / "closure_handoff_manifest.json")),
        "distill_product_expansion_gaps": copy.deepcopy(_load_json(DISTILL_ROOT / "product_expansion_gaps.json")),
    }


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
