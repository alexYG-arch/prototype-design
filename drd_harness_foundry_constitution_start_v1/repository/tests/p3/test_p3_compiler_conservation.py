import copy
import json
from pathlib import Path

from drd_harness.validators.p3_compiler import validate_p3_compiler_artifacts


COMPILER_ROOT = Path("repository/fixtures/p3/compiler")


def test_p3_compiler_fixture_validates_complete_package():
    package = _load_compiler_package()

    findings = validate_p3_compiler_artifacts(**package)

    assert findings == []


def test_p3_compiler_rejects_forbidden_input_type():
    package = _load_compiler_package()
    bundle = package["compiler_input_bundle"]["bundle"]
    bundle["approved_semantic_artifacts"][0]["input_type"] = "DIRECT_SOURCE_PRD_SEMANTIC_READ"
    _refresh_closed_input_hash(bundle)

    findings = validate_p3_compiler_artifacts(**package)

    assert "COMP-CHECK-002" in {finding.code for finding in findings}


def test_p3_compiler_rejects_input_type_that_does_not_match_record_group():
    package = _load_compiler_package()
    bundle = package["compiler_input_bundle"]["bundle"]
    bundle["review_decisions"][0]["input_type"] = "APPROVED_OPERATIONAL_INDEX"
    _refresh_closed_input_hash(bundle)
    _refresh_compiled_outputs(package)

    findings = validate_p3_compiler_artifacts(**package)

    assert any(
        finding.code == "COMP-CHECK-002" and "review_decisions records must use input_type REVIEW_DECISION" in finding.message
        for finding in findings
    )


def test_p3_compiler_rejects_stale_review_decision_hash():
    package = _load_compiler_package()
    package["compiler_input_bundle"]["bundle"]["review_decisions"][0]["sha256"] = "0" * 64

    findings = validate_p3_compiler_artifacts(**package)

    assert any(finding.code == "COMP-CHECK-004" and "review decision" in finding.message for finding in findings)


def test_p3_compiler_rejects_closed_input_hash_drift():
    package = _load_compiler_package()
    package["compiler_input_bundle"]["bundle"]["closed_input_hash"] = "0" * 64

    findings = validate_p3_compiler_artifacts(**package)

    assert any("closed_input_hash does not match" in finding.message for finding in findings)


def test_p3_compiler_rejects_schema_hash_drift():
    package = _load_compiler_package()
    bundle = package["compiler_input_bundle"]["bundle"]
    bundle["schema_hashes"]["final_drd_manifest"] = "0" * 64

    findings = validate_p3_compiler_artifacts(**package)

    assert any(finding.code == "COMP-CHECK-012" and finding.subject_id == "final_drd_manifest" for finding in findings)


def test_p3_compiler_rejects_compiler_code_hash_drift():
    package = _load_compiler_package()
    bundle = package["compiler_input_bundle"]["bundle"]
    bundle["compiler_code_hash"] = "0" * 64
    package["final_drd_hash_index"]["index"]["compiler_code_hash"] = "0" * 64
    package["final_drd_manifest"]["manifest"]["assembly_plan"]["compiler_code_hash"] = "0" * 64

    findings = validate_p3_compiler_artifacts(**package)

    assert any(finding.code == "COMP-CHECK-012" and finding.subject_id == "compiler_code_hash" for finding in findings)


def test_p3_compiler_rejects_manual_final_drd_mutation():
    package = _load_compiler_package()
    package["final_drd_text"] += "\nManual final fragment that was not produced by the compiler.\n"

    findings = validate_p3_compiler_artifacts(**package)

    assert any(finding.subject_id == "FINAL_DRD.md" for finding in findings)


def test_p3_compiler_rejects_sidecar_hash_mismatch():
    package = _load_compiler_package()
    package["final_drd_hash_index"]["index"]["full_output_hash"] = "0" * 64

    findings = validate_p3_compiler_artifacts(**package)

    assert any(finding.code == "COMP-CHECK-011" and finding.subject_id == "final_drd_hash_index.json" for finding in findings)


def test_p3_compiler_rejects_qa_mutation():
    package = _load_compiler_package()
    boundary = package["read_only_qa_boundary"]["boundary"]
    boundary["written_paths"].append("FINAL_DRD.md")
    boundary["mutated_artifacts"].append("repository/fixtures/p3/compiler/FINAL_DRD.md")
    boundary["mutation_claim"] = "MUTATION_DETECTED"

    findings = validate_p3_compiler_artifacts(**package)

    assert "COMP-CHECK-014" in {finding.code for finding in findings}


def test_p3_compiler_rejects_incomplete_qa_read_coverage():
    package = _load_compiler_package()
    boundary = package["read_only_qa_boundary"]["boundary"]
    boundary["read_paths"].remove("repository/fixtures/p3/compiler/final_drd_hash_index.json")

    findings = validate_p3_compiler_artifacts(**package)

    assert any(
        finding.code == "COMP-CHECK-014" and "read_paths missing compiler package outputs" in finding.message
        for finding in findings
    )


def _load_compiler_package():
    return {
        "compiler_input_bundle": copy.deepcopy(_load_json("compiler_input_bundle.json")),
        "compiler_semantic_unit_inventory": copy.deepcopy(_load_json("compiler_semantic_unit_inventory.json")),
        "compiler_conservation_report": copy.deepcopy(_load_json("compiler_conservation_report.json")),
        "final_drd_manifest": copy.deepcopy(_load_json("final_drd_manifest.json")),
        "final_drd_toc": copy.deepcopy(_load_json("final_drd_toc.json")),
        "final_drd_reference_index": copy.deepcopy(_load_json("final_drd_reference_index.json")),
        "final_drd_hash_index": copy.deepcopy(_load_json("final_drd_hash_index.json")),
        "read_only_qa_boundary": copy.deepcopy(_load_json("read_only_qa_boundary.json")),
        "final_drd_text": (COMPILER_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8"),
    }


def _load_json(name: str):
    return json.loads((COMPILER_ROOT / name).read_text(encoding="utf-8"))


def _refresh_closed_input_hash(bundle):
    from drd_harness.validators.compiler_conservation import compute_closed_input_hash

    bundle["closed_input_hash"] = compute_closed_input_hash(bundle)


def _refresh_compiled_outputs(package):
    from drd_harness.compiler.final_drd import compile_final_drd

    compiled = compile_final_drd(package["compiler_input_bundle"]["bundle"])
    package["final_drd_text"] = compiled["FINAL_DRD.md"]
    package["compiler_semantic_unit_inventory"]["inventory"]["semantic_units"] = compiled["compiler_semantic_unit_inventory.json"]
    package["compiler_conservation_report"]["report"] = compiled["compiler_conservation_report.json"]
    package["final_drd_manifest"]["manifest"] = compiled["final_drd_manifest.json"]
    package["final_drd_toc"]["records"] = compiled["final_drd_toc.json"]
    package["final_drd_reference_index"]["records"] = compiled["final_drd_reference_index.json"]
    package["final_drd_hash_index"]["index"] = compiled["final_drd_hash_index.json"]
