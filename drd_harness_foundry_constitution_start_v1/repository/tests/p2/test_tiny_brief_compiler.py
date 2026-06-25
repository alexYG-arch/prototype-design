import copy
import hashlib
import json
from pathlib import Path

from drd_harness.compiler.conservation import compute_unit_hash
from drd_harness.compiler.final_drd import compile_final_drd
from drd_harness.validators.compiler_conservation import (
    compute_closed_input_hash,
    compute_semantic_content_hash,
    validate_atomic_inventory_for_compiler,
    validate_compiler_output_package,
    validate_input_bundle,
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
    "p2.tiny_brief.information_presentation_registry": FIXTURE_ROOT / "information_presentation_registry.json",
    "p2.tiny_brief.shared_component_registry": FIXTURE_ROOT / "shared_component_registry.json",
    "p2.tiny_brief.natural_language_layout": FIXTURE_ROOT / "natural_language_layout.json",
    "p2.tiny_brief.carrier_adaptation_profile": FIXTURE_ROOT / "carrier_adaptation_profile.json",
    "p2.tiny_brief.containment_hierarchy": FIXTURE_ROOT / "containment_hierarchy.json",
    "p2.tiny_brief.z_axis_layering": FIXTURE_ROOT / "z_axis_layering.json",
}


def test_compiler_input_bundle_is_closed_and_approved():
    artifact = _load_json("compiler_input_bundle.json")
    bundle = artifact["bundle"]

    _assert_artifact_contract(
        artifact,
        "p2.tiny_brief.compiler_input_bundle",
        "bundle",
        "repository/schemas/compiler/compiler_input_bundle.schema.json",
    )
    assert validate_input_bundle(bundle) == []
    assert bundle["closed_input_hash"] == compute_closed_input_hash(bundle)
    assert bundle["semantic_content_hash"] == compute_semantic_content_hash(bundle)
    assert all(
        record["input_type"] != "DIRECT_SOURCE_PRD_SEMANTIC_READ"
        for record in bundle["approved_semantic_artifacts"]
    )
    assert {
        "build_program/phases/P2/candidates/P2-IMPL-01/REVIEW_DECISION.json",
        "build_program/phases/P2/candidates/P2-IMPL-02/REVIEW_DECISION.json",
        "build_program/phases/P2/candidates/P2-IMPL-03/REVIEW_DECISION.json",
    } <= {record.get("review_decision_ref") for record in bundle["approved_semantic_artifacts"]}


def test_semantic_content_hash_binds_sections_and_semantic_units():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    mutated = copy.deepcopy(bundle)
    mutated["sections"][0]["body"] += "\n- Manual semantic sentence."

    findings = validate_input_bundle(mutated)

    assert any("semantic_content_hash does not match" in finding.message for finding in findings)


def test_input_record_groups_must_be_lists():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    bundle["approved_semantic_artifacts"] = {"not": "a list"}

    findings = validate_input_bundle(bundle)

    assert any("approved_semantic_artifacts must be a list" in finding.message for finding in findings)


def test_compiler_output_package_requires_semantic_content_hash():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    bundle.pop("semantic_content_hash")

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any("semantic_content_hash is required" in finding.message for finding in findings)


def test_compiler_output_package_requires_current_hashes():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    bundle.pop("current_hashes")

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any("current_hashes is required" in finding.message for finding in findings)


def test_approved_semantic_artifact_cannot_rely_on_lock_ref_only():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    bundle["approved_semantic_artifacts"][0].pop("review_decision_ref")
    bundle["approved_semantic_artifacts"][0].pop("approval_ref", None)
    bundle["closed_input_hash"] = compute_closed_input_hash(bundle)

    findings = validate_input_bundle(bundle)

    assert any("semantic artifact requires approval or review decision reference" in finding.message for finding in findings)


def test_section_semantic_unit_refs_reject_unknown_unit_id():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = copy.deepcopy(_load_json("compiler_semantic_unit_inventory.json")["inventory"])
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    bundle["sections"][0]["semantic_unit_ids"].append("p2.unit.missing")
    bundle["semantic_content_hash"] = compute_semantic_content_hash(bundle)
    inventory["source_artifact_hash"] = bundle["semantic_content_hash"]

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any("unknown semantic_unit_ids" in finding.message for finding in findings)


def test_section_semantic_unit_refs_reject_duplicate_unit_id():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = copy.deepcopy(_load_json("compiler_semantic_unit_inventory.json")["inventory"])
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    duplicate_id = bundle["sections"][0]["semantic_unit_ids"][0]
    bundle["sections"][0]["semantic_unit_ids"].append(duplicate_id)
    bundle["semantic_content_hash"] = compute_semantic_content_hash(bundle)
    inventory["source_artifact_hash"] = bundle["semantic_content_hash"]

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any("more than once" in finding.message for finding in findings)


def test_compiler_semantic_unit_inventory_is_atomic_and_source_bound():
    artifact = _load_json("compiler_semantic_unit_inventory.json")
    inventory = artifact["inventory"]
    units = inventory["semantic_units"]

    _assert_artifact_contract(
        artifact,
        "p2.tiny_brief.compiler_semantic_unit_inventory",
        "inventory",
        "repository/schemas/compiler/compiler_semantic_unit_inventory.schema.json",
    )
    assert validate_atomic_inventory_for_compiler(units) == []
    assert len(units) == 33
    assert {unit["stage_id"] for unit in units} == {"DRD-01", "DRD-02", "DRD-03", "DRD-03B", "DRD-04"}
    assert {"CTA", "INPUT_FIELD", "COPY_STRING", "ARRANGEMENT_RULE", "CARRIER_ADAPTATION_RULE", "Z_AXIS_LAYER"} <= {
        unit["unit_type"] for unit in units
    }
    assert all(unit["unit_hash"] == compute_unit_hash(unit) for unit in units)
    assert all(not unit["source_span_ref"].startswith("section:") for unit in units)
    for unit in units:
        assert unit["source_hash"] == _sha256_file(Path(unit["source_path"]))


def test_conservation_report_matches_deterministic_compiler_output():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    compiled = compile_final_drd(bundle)

    assert validate_compiler_output_package(bundle, inventory, report, final_drd_text) == []
    assert inventory["semantic_units"] == compiled["compiler_semantic_unit_inventory.json"]
    assert report == compiled["compiler_conservation_report.json"]
    assert report["status"] == "PASS"
    assert report["added_semantic_units"] == []
    assert report["omitted_semantic_units"] == []
    assert report["hash_drift"] == []


def test_compiler_output_package_rejects_manual_final_fragment():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8") + "\nManual final fragment."

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any(finding.code == "COMP-CHECK-011" and finding.subject_id == "FINAL_DRD.md" for finding in findings)


def test_compiler_output_package_rejects_hash_drift():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    bundle["current_hashes"]["repository/fixtures/p2/tiny_brief_intake/prd_element_inventory.json"] = "0" * 64

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert "COMP-CHECK-004" in {finding.code for finding in findings}


def test_compiler_output_package_rejects_missing_current_hash_coverage():
    bundle = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"])
    inventory = _load_json("compiler_semantic_unit_inventory.json")["inventory"]
    report = _load_json("compiler_conservation_report.json")["report"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    bundle["current_hashes"].pop("repository/fixtures/p2/tiny_brief_intake/prd_element_inventory.json")

    findings = validate_compiler_output_package(bundle, inventory, report, final_drd_text)

    assert any("current hash is missing" in finding.message for finding in findings)


def test_compiler_artifacts_bind_upstream_hashes():
    for filename in [
        "compiler_input_bundle.json",
        "compiler_semantic_unit_inventory.json",
        "compiler_conservation_report.json",
    ]:
        artifact = _load_json(filename)
        for artifact_id, path in UPSTREAM_ARTIFACT_FILES.items():
            assert artifact_id in artifact["upstream_artifact_refs"]
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(path)


def _load_json(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str, payload_key: str, schema_ref: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == "DRD-05-COMPILATION"
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["schema_payload_key"] == payload_key
    assert payload["schema_ref"] == schema_ref
    assert payload["validator_ref"] == "repository/src/drd_harness/validators/compiler_conservation.py"
    assert payload["promotion_state"] == "CANDIDATE"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
