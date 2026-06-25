import hashlib
import json
import re
from pathlib import Path

from drd_harness.rules.prd_adoption import ElementType, PrdElementInventoryItem
from drd_harness.rules.reasoning import CanonicalEligibility, DerivationStrategy, DerivedElementDecision
from drd_harness.validators.prd_adoption import (
    validate_derived_element_decision,
    validate_inventory_items,
    validate_product_expansion_gap,
)


FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")
SOURCE_PRD = FIXTURE_ROOT / "source/source_prd.md"
SPEC_INVENTORY = Path("build_program/phases/P2/candidates/P2-SPEC-01/P2_PRD_ELEMENT_INVENTORY.json")

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
INVENTORY_RECORD_FIELDS = {
    "element_id",
    "element_type",
    "source_refs",
    "source_text_hash",
    "stage_id",
    "artifact_id",
}
DERIVED_RECORD_FIELDS = {
    "derived_element_id",
    "derived_surface_type",
    "derivation_source",
    "obligation_refs",
    "inference_refs",
    "derivation_strategy",
    "structural_completion_review",
    "canonical_eligibility",
    "blocked_by",
}
GAP_RECORD_FIELDS = {
    "gap_id",
    "gap_type",
    "source_refs",
    "blocked_artifacts",
    "candidate_options",
    "required_decision",
    "status",
    "decision_ref",
}


def test_tiny_brief_inventory_matches_approved_prd_element_universe():
    inventory = _load_artifact("prd_element_inventory.json")
    spec = _load_spec_inventory()
    records = inventory["records"]

    _assert_artifact_contract(inventory, "p2.tiny_brief.prd_element_inventory")
    assert inventory["semantic_source_model"]["primary_semantics"] == "natural_language_prd"
    assert inventory["semantic_source_model"]["inventory_role"] == "index_and_verification_skeleton"
    assert all(set(record) == INVENTORY_RECORD_FIELDS for record in records)

    inventory_ids = {record["element_id"] for record in records}
    spec_ids = {element["element_id"] for element in spec["elements"]}
    assert inventory_ids == spec_ids

    inventory_items = [_inventory_item(record) for record in records]
    assert validate_inventory_items(inventory_items) == []
    assert all(record["source_text_hash"] == _hash_source_ref(record["source_refs"][0]) for record in records)


def test_derived_element_decisions_are_deductive_and_do_not_add_product_capability():
    derived = _load_artifact("derived_element_decisions.json")
    spec = _load_spec_inventory()
    records = derived["records"]

    _assert_artifact_contract(derived, "p2.tiny_brief.derived_element_decisions")
    assert derived["review_gate"] == "EXPANSION_GAP_ONLY"
    assert all(set(record) == DERIVED_RECORD_FIELDS for record in records)

    expected_deduced = {
        element["element_id"] for element in spec["elements"] if element["adoption"] == "deduced_required"
    }
    assert {record["derived_element_id"] for record in records} == expected_deduced

    for record in records:
        decision = _derived_decision(record)
        assert record["derivation_strategy"] == "DEDUCTIVE_PRIMARY"
        assert record["canonical_eligibility"] == "ELIGIBLE"
        assert record["structural_completion_review"] is None
        assert "DERIVE-RULE-009" in record["obligation_refs"]
        assert validate_derived_element_decision(decision) == []


def test_product_expansion_candidates_are_open_human_review_gaps_not_adopted_scope():
    gaps = _load_artifact("product_expansion_gaps.json")
    spec = _load_spec_inventory()
    records = gaps["records"]

    _assert_artifact_contract(gaps, "p2.tiny_brief.product_expansion_gaps")
    assert gaps["review_gate"] == "HUMAN_REQUIRED_IF_NON_EMPTY"
    assert all(set(record) == GAP_RECORD_FIELDS for record in records)

    rejected_ids = {candidate["candidate_id"] for candidate in spec["rejected_expansion_candidates"]}
    assert {record["gap_id"] for record in records} == rejected_ids

    for record in records:
        assert record["status"] == "OPEN"
        assert record["decision_ref"] is None
        assert "p2.tiny_brief.final_drd" in record["blocked_artifacts"]
        assert record["gap_id"] in record["candidate_options"]
        assert "Human Gate approval is required" in record["required_decision"]
        assert validate_product_expansion_gap(record) == []


def test_inductive_derived_element_cannot_be_canonical_without_human_gate():
    record = dict(_load_artifact("derived_element_decisions.json")["records"][0])
    record["derivation_strategy"] = "INDUCTIVE_AUXILIARY"

    findings = validate_derived_element_decision(_derived_decision(record))

    assert [finding.code for finding in findings] == ["REASON004"]


def test_product_expansion_gap_validator_rejects_malformed_open_gap():
    record = dict(_load_artifact("product_expansion_gaps.json")["records"][0])
    record["gap_type"] = "NEW_PRODUCT_FEATURE"
    record["source_refs"] = []
    record["blocked_artifacts"] = []
    record["candidate_options"] = "expansion.secondary_page"

    findings = validate_product_expansion_gap(record)

    assert [finding.code for finding in findings] == ["REASON009", "REASON009", "REASON009", "REASON009"]


def test_product_expansion_gap_validator_rejects_unknown_status():
    record = dict(_load_artifact("product_expansion_gaps.json")["records"][0])
    record["status"] = "ADOPTED"

    findings = validate_product_expansion_gap(record)

    assert [finding.code for finding in findings] == ["REASON009"]


def test_resolved_product_expansion_gap_requires_human_decision_ref():
    record = dict(_load_artifact("product_expansion_gaps.json")["records"][0])
    record["status"] = "RESOLVED_APPROVED"
    record["decision_ref"] = None

    findings = validate_product_expansion_gap(record)

    assert [finding.code for finding in findings] == ["REASON010"]


def test_prd_element_files_keep_source_refs_and_upstream_hashes_bound_to_snapshot():
    snapshot_manifest = _load_artifact("source_snapshot_manifest.json")
    source_hash = snapshot_manifest["manifest"]["snapshot_hash"]
    snapshot_manifest_hash = _sha256_file(FIXTURE_ROOT / "source_snapshot_manifest.json")

    for filename in [
        "prd_element_inventory.json",
        "derived_element_decisions.json",
        "product_expansion_gaps.json",
    ]:
        artifact = _load_artifact(filename)
        assert artifact["upstream_hashes"]["p2.tiny_brief.source_prd"] == source_hash
        assert artifact["upstream_hashes"]["p2.tiny_brief.source_snapshot_manifest"] == snapshot_manifest_hash
        assert artifact["promotion_state"] == "CANDIDATE"
        assert artifact["validator_ref"] == "repository/src/drd_harness/validators/prd_adoption.py"


def _load_artifact(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _load_spec_inventory():
    return json.loads(SPEC_INVENTORY.read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == "DRD-01-PRD-ELEMENTS" or artifact_id.endswith("source_snapshot_manifest")
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["path"] == f"repository/fixtures/p2/tiny_brief_intake/{Path(payload['path']).name}"
    assert payload["schema_ref"]
    assert payload["schema_payload_key"] == "records"
    assert payload["source_refs"]
    assert payload["validator_ref"]
    assert payload["invalidation_inputs"]


def _inventory_item(record) -> PrdElementInventoryItem:
    return PrdElementInventoryItem(
        element_id=record["element_id"],
        element_type=ElementType(record["element_type"]),
        source_refs=record["source_refs"],
        source_text_hash=record["source_text_hash"],
        stage_id=record["stage_id"],
        artifact_id=record["artifact_id"],
    )


def _derived_decision(record) -> DerivedElementDecision:
    return DerivedElementDecision(
        derived_element_id=record["derived_element_id"],
        derived_surface_type=record["derived_surface_type"],
        derivation_source=record["derivation_source"],
        obligation_refs=record["obligation_refs"],
        inference_refs=record["inference_refs"],
        derivation_strategy=DerivationStrategy(record["derivation_strategy"]),
        structural_completion_review=record["structural_completion_review"],
        canonical_eligibility=CanonicalEligibility(record["canonical_eligibility"]),
        blocked_by=record["blocked_by"],
    )


def _hash_source_ref(source_ref: str) -> str:
    path_text, section = source_ref.split("#", 1)
    assert Path(path_text) == SOURCE_PRD
    return hashlib.sha256(_section_text(section).encode("utf-8")).hexdigest()


def _section_text(section: str) -> str:
    text = SOURCE_PRD.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(section)}\n(?P<body>.*?)(?=\n## |\Z)", text, flags=re.S | re.M)
    assert match is not None, section
    return match.group("body").strip() + "\n"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
