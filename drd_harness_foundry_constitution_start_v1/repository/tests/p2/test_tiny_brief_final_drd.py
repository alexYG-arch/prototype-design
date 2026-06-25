import copy
import hashlib
import json
from pathlib import Path

from drd_harness.compiler.final_drd import compile_final_drd
from drd_harness.validators.compiler_conservation import validate_final_manifest, validate_section_order


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


def test_final_drd_cites_source_hashes_for_every_section():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    final_drd_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")

    for section in bundle["sections"]:
        citation = f"{section['source_path']}#{section['section_id']} sha256:{section['source_hash']}"
        assert citation in final_drd_text


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


def _load_json(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))
