import copy
import hashlib
import json
from pathlib import Path

from drd_harness.compiler.final_drd import compile_final_drd
from drd_harness.validators.compiler_conservation import (
    validate_final_drd_reader_structure,
    validate_final_manifest,
    validate_section_order,
)


FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")


def test_final_drd_matches_deterministic_compiler_output():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    compiled = compile_final_drd(bundle)
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")

    assert final_drd_text == compiled["FINAL_DRD.md"]
    assert hashlib.sha256(final_drd_text.encode("utf-8")).hexdigest() == compiled["final_drd_manifest.json"]["final_drd_hash"]
    assert validate_final_manifest(compiled["final_drd_manifest.json"]) == []
    assert compiled["final_drd_manifest.json"]["conservation_status"] == "PASS"


def test_final_drd_uses_stable_stage_and_section_order():
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")

    assert final_drd_text.index("## PRD Element Inventory") < final_drd_text.index("## Deduction and Structural Completion")
    assert final_drd_text.index("## Deduction and Structural Completion") < final_drd_text.index("## Interaction Closure")
    assert final_drd_text.index("## Interaction Closure") < final_drd_text.index("## Information Presentation and Shared Patterns")
    assert final_drd_text.index("## Information Presentation and Shared Patterns") < final_drd_text.index("## Carrier Layout and Layering")
    assert "- 10.1 PRD Element Inventory" in final_drd_text
    assert "- 50.1 Carrier Layout and Layering" in final_drd_text


def test_section_order_rejects_duplicate_section_id_within_stage():
    sections = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"]["sections"])
    sections[1]["stage_id"] = sections[0]["stage_id"]
    sections[1]["section_id"] = sections[0]["section_id"]

    findings = validate_section_order(sections)

    assert any("section_id must be unique within a stage" in finding.message for finding in findings)


def test_section_order_rejects_duplicate_order_slot():
    sections = copy.deepcopy(_load_json("compiler_input_bundle.json")["bundle"]["sections"])
    sections[1]["stage_order_index"] = sections[0]["stage_order_index"]
    sections[1]["section_order_index"] = sections[0]["section_order_index"]

    findings = validate_section_order(sections)

    assert any("section order slot must be unique" in finding.message for finding in findings)


def test_final_drd_keeps_source_hashes_out_of_reader_text_and_in_reference_index():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    reference_index = _load_json("final_drd_reference_index.json")["reference_index"]

    assert validate_final_drd_reader_structure(final_drd_text) == []
    assert "_Source:" not in final_drd_text
    assert "sha256:" not in final_drd_text
    refs_by_section = {entry["compiled_section_id"]: entry for entry in reference_index}
    for section in bundle["sections"]:
        ref = refs_by_section[section["section_id"]]
        assert ref["source_path"] == section["source_path"]
        assert ref["source_hash"] == section["source_hash"]


def test_final_drd_contains_only_compiled_semantic_unit_values():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    unit_values = {unit["canonical_value"] for unit in bundle["semantic_units"]}

    for value in unit_values:
        assert value in final_drd_text
    assert "Delete account" not in final_drd_text
    assert "Manual final fragment" not in final_drd_text


def test_final_drd_manifest_has_zero_blocking_counts():
    compiled = compile_final_drd(_load_json("compiler_input_bundle.json")["bundle"])
    manifest = compiled["final_drd_manifest.json"]

    assert manifest["omitted_semantic_unit_count"] == 0
    assert manifest["added_semantic_unit_count"] == 0
    assert manifest["hash_drift_count"] == 0
    assert manifest["unapproved_input_count"] == 0
    assert manifest["compiled_semantic_unit_count"] == 33


def test_final_drd_reader_structure_rejects_candidate_or_evidence_bundle_text():
    bad_text = (
        "# Final DRD\n\n"
        "## Section\n\n"
        "# DRD-01 PRD 体验事实简报（候选）\n\n"
        "_Source: staged/DRD-01/PRD_EXPERIENCE_BRIEF.md sha256:abc approval:review_gates/DRD-01_REVIEW_DECISION.json_\n"
    )

    findings = validate_final_drd_reader_structure(bad_text)

    assert any(finding.code == "COMP-CHECK-021" for finding in findings)


def _load_json(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))
