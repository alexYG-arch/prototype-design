import hashlib
import json
from pathlib import Path

from drd_harness.rules.reasoning import CanonicalEligibility, InferenceClass, ProductExpansionRisk
from drd_harness.validators.reasoning import (
    inference_record_from_mapping,
    structural_completion_review_from_mapping,
    validate_inference_record_set,
    validate_structural_completion_review_set,
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
REQUIRED_INFERENCE_IDS = {
    "p2.tiny_brief.inference.failure_recovery_copy.001",
    "p2.tiny_brief.inference.failure_recovery_copy.002",
    "p2.tiny_brief.inference.clickable_closure.001",
    "p2.tiny_brief.inference.async_failure_copy.001",
    "p2.tiny_brief.inference.no_product_expansion.001",
}
P2_IMPL_01_ARTIFACT_FILES = {
    "p2.tiny_brief.source_prd": FIXTURE_ROOT / "source/source_prd.md",
    "p2.tiny_brief.source_snapshot_manifest": FIXTURE_ROOT / "source_snapshot_manifest.json",
    "p2.tiny_brief.prd_element_inventory": FIXTURE_ROOT / "prd_element_inventory.json",
    "p2.tiny_brief.derived_element_decisions": FIXTURE_ROOT / "derived_element_decisions.json",
    "p2.tiny_brief.product_expansion_gaps": FIXTURE_ROOT / "product_expansion_gaps.json",
}


def test_inference_records_bind_required_p2_derived_and_interaction_obligations():
    artifact = _load("inference_records.json")
    records = [inference_record_from_mapping(record) for record in artifact["records"]]

    _assert_artifact_contract(artifact, "p2.tiny_brief.inference_records", "DRD-02-REASONING")
    assert {record.inference_id for record in records} == REQUIRED_INFERENCE_IDS
    assert validate_inference_record_set(records, required_inference_ids=sorted(REQUIRED_INFERENCE_IDS)) == []
    assert all(record.canonical_eligibility == CanonicalEligibility.ELIGIBLE for record in records)
    assert all(record.inference_class != InferenceClass.INDUCTIVE_CANDIDATE for record in records)
    assert all(record.unresolved_product_choices == [] for record in records)


def test_inference_records_fail_when_reserved_p2_impl01_refs_are_missing():
    records = [
        inference_record_from_mapping(record)
        for record in _load("inference_records.json")["records"]
        if record["inference_id"] != "p2.tiny_brief.inference.failure_recovery_copy.002"
    ]

    findings = validate_inference_record_set(records, required_inference_ids=sorted(REQUIRED_INFERENCE_IDS))

    assert [finding.code for finding in findings] == ["REASON007"]


def test_structural_completion_records_do_not_authorize_hidden_child_surfaces():
    artifact = _load("structural_completion_review.json")
    reviews = [structural_completion_review_from_mapping(record) for record in artifact["records"]]

    _assert_artifact_contract(artifact, "p2.tiny_brief.structural_completion_review", "DRD-02-REASONING")
    assert validate_structural_completion_review_set(reviews) == []
    assert all(review.product_expansion_risk == ProductExpansionRisk.NONE for review in reviews)
    assert all(review.canonical_eligibility != CanonicalEligibility.ELIGIBLE for review in reviews)
    assert any("do not add child pages" in option for review in reviews for option in review.candidate_options)


def test_structural_completion_review_rejects_empty_candidate_options():
    record = dict(_load("structural_completion_review.json")["records"][0])
    record["candidate_options"] = []
    reviews = [structural_completion_review_from_mapping(record)]

    findings = validate_structural_completion_review_set(reviews)

    assert [finding.code for finding in findings] == ["REASON015"]


def test_reasoning_artifacts_bind_p2_impl01_upstream_hashes():
    for filename in ["inference_records.json", "structural_completion_review.json"]:
        artifact = _load(filename)
        for artifact_id, path in P2_IMPL_01_ARTIFACT_FILES.items():
            assert artifact_id in artifact["upstream_artifact_refs"]
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(path)


def _load(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str, stage_id: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == stage_id
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["schema_payload_key"] == "records"
    assert payload["validator_ref"] == "repository/src/drd_harness/validators/reasoning.py"
    assert payload["promotion_state"] == "CANDIDATE"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
