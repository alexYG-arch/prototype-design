import json
from pathlib import Path

from drd_harness.compiler.conservation import compute_unit_hash
from drd_harness.compiler.final_drd import CompilerFailure, compile_final_drd, deterministic_hash
from drd_harness.validators.compiler_conservation import (
    compute_closed_input_hash,
    compute_semantic_content_hash,
    validate_approved_stage_semantic_artifacts,
    validate_approved_semantic_artifact_manifest,
    validate_final_drd_reader_structure,
    validate_final_manifest,
    validate_input_bundle,
    validate_section_order,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64


def atomic_unit(
    unit_id="UNIT-PAGE-ACCOUNT",
    unit_type="PAGE",
    canonical_value="Account page exists.",
    stage_id="DRD-02",
    source_path="artifacts/DRD-02/PAGES.md",
    source_hash=HASH_A,
    approval_ref="reviews/DRD-02-REVIEW_DECISION.json",
    source_section_id="SEC-ACCOUNT",
):
    unit = {
        "semantic_unit_id": unit_id,
        "unit_type": unit_type,
        "unit_class": "Product object",
        "stage_id": stage_id,
        "source_path": source_path,
        "source_section_id": source_section_id,
        "source_span_ref": f"heading:{source_section_id}",
        "source_hash": source_hash,
        "approval_ref": approval_ref,
        "lock_ref": "SPEC-LOCK-DRD02",
        "parent_unit_id": None,
        "relationship_kind": "ROOT",
        "canonical_value": canonical_value,
        "unit_hash": "",
        "inventory_version": "1.0",
    }
    unit["unit_hash"] = compute_unit_hash(unit)
    return unit


def bundle():
    unit = atomic_unit()
    value = {
        "bundle_id": "CIB-001",
        "bundle_version": "1.0",
        "compiler_id": "drd_harness.compiler.final_drd",
        "compiler_version": "1.0.0",
        "compiler_code_hash": HASH_D,
        "compiler_stage_id": "DRD-05",
        "source_snapshot_identity": {"snapshot_id": "DRD-00", "sha256": HASH_E},
        "approved_semantic_artifacts": [
            {
                "input_id": "DRD02-PAGES",
                "input_type": "APPROVED_SEMANTIC_ARTIFACT",
                "stage_id": "DRD-02",
                "path": "artifacts/DRD-02/PAGES.md",
                "sha256": HASH_A,
                "approval_ref": "reviews/DRD-02-REVIEW_DECISION.json",
                "section_index_ref": "artifacts/DRD-02/section_index.json",
            }
        ],
        "approved_operational_indexes": [
            {
                "input_id": "DRD02-SECTION-INDEX",
                "input_type": "APPROVED_OPERATIONAL_INDEX",
                "stage_id": "DRD-02",
                "path": "artifacts/DRD-02/section_index.json",
                "sha256": HASH_B,
                "approval_ref": "reviews/DRD-02-REVIEW_DECISION.json",
            }
        ],
        "review_decisions": [
            {
                "input_id": "REVIEW-DRD02",
                "input_type": "REVIEW_DECISION",
                "path": "reviews/DRD-02-REVIEW_DECISION.json",
                "sha256": HASH_C,
            }
        ],
        "lock_refs": [
            {
                "input_id": "SPEC-LOCK-DRD02",
                "input_type": "SPEC_LOCK_REF",
                "path": "locks/SPEC-LOCK-DRD02.json",
                "sha256": HASH_D,
            }
        ],
        "validator_results": [
            {
                "input_id": "VALIDATOR-DRD02",
                "input_type": "VALIDATOR_RESULT",
                "path": "validation/DRD02.json",
                "sha256": HASH_E,
            }
        ],
        "control_indexes": [
            {
                "input_id": "CONTROL-STAGE-ORDER",
                "input_type": "CONTROL_INDEX",
                "path": "control/stage_order.json",
                "sha256": HASH_A,
            }
        ],
        "schemas": [
            {
                "input_id": "FINAL-MANIFEST-SCHEMA",
                "input_type": "SCHEMA",
                "path": "repository/schemas/compiler/final_drd_manifest.schema.json",
                "sha256": HASH_B,
            }
        ],
        "stage_order": [
            {"stage_id": "DRD-01", "stage_order_index": 10},
            {"stage_id": "DRD-02", "stage_order_index": 20},
            {"stage_id": "DRD-03", "stage_order_index": 30},
            {"stage_id": "DRD-03B", "stage_order_index": 40},
            {"stage_id": "DRD-04", "stage_order_index": 50},
        ],
        "section_order": [
            {"stage_id": "DRD-02", "section_id": "SEC-ACCOUNT", "section_order_index": 1}
        ],
        "sections": [
            {
                "section_id": "SEC-ACCOUNT",
                "stage_id": "DRD-02",
                "stage_order_index": 20,
                "section_order_index": 1,
                "heading_text": "Account",
                "source_path": "artifacts/DRD-02/PAGES.md",
                "source_hash": HASH_A,
                "approved_hash_ref": "reviews/DRD-02-REVIEW_DECISION.json",
                "body": "Account page exists.",
                "semantic_unit_ids": ["UNIT-PAGE-ACCOUNT"],
            }
        ],
        "semantic_units": [unit],
        "schema_hashes": {"final_drd_manifest.schema.json": HASH_B},
        "validator_result_refs": ["validation/DRD02.json"],
        "default_lock_ref": "SPEC-LOCK-DRD02",
        "requires_approved_stage_semantic_artifacts": False,
        "closed_input_hash": "",
    }
    value["closed_input_hash"] = compute_closed_input_hash(value)
    return value


def approved_stage_bundle():
    value = bundle()
    review_ref = "reviews/DRD-02-REVIEW_DECISION.json"
    stage_rows = [
        ("DRD-01", 10, HASH_A),
        ("DRD-02", 20, HASH_B),
        ("DRD-03", 30, HASH_C),
        ("DRD-03B", 40, HASH_D),
        ("DRD-04", 50, HASH_E),
    ]
    value["requires_approved_stage_semantic_artifacts"] = True
    value["approved_semantic_artifacts"] = []
    value["approved_semantic_artifact_manifests"] = []
    value["sections"] = []
    value["section_order"] = []
    value["semantic_units"] = []
    for stage_id, stage_order_index, body_hash in stage_rows:
        section_id = f"SEC-{stage_id}"
        approved_body_path = f"artifacts/{stage_id}/APPROVED_SEMANTIC_ARTIFACT.md"
        approved_manifest_id = f"{stage_id}-approved-semantic-artifact"
        candidate_ref = f"artifacts/{stage_id}/CANDIDATE.md"
        heading = f"{stage_id} Approved Semantics"
        body = f"{stage_id} approved semantic body."
        unit_id = f"UNIT-{stage_id}"
        value["approved_semantic_artifacts"].append(
            {
                "input_id": f"{stage_id}-APPROVED-SEMANTIC-BODY",
                "input_type": "APPROVED_SEMANTIC_ARTIFACT",
                "stage_id": stage_id,
                "artifact_kind": "APPROVED_SEMANTIC_ARTIFACT",
                "path": approved_body_path,
                "sha256": body_hash,
                "approval_ref": review_ref,
                "review_decision_ref": review_ref,
                "semantic_body_path": approved_body_path,
                "semantic_body_sha256": body_hash,
                "semantic_role": "approved_stage_semantic_body",
                "approved_semantic_artifact_ref": approved_manifest_id,
                "source_candidate_refs": [candidate_ref],
            }
        )
        value["approved_semantic_artifact_manifests"].append(
            {
                "artifact": "approved_semantic_artifact",
                "artifact_kind": "APPROVED_SEMANTIC_ARTIFACT",
                "artifact_id": approved_manifest_id,
                "stage_id": stage_id,
                "semantic_body_path": approved_body_path,
                "semantic_body_sha256": body_hash,
                "review_decision_ref": review_ref,
                "review_decision_sha256": HASH_C,
                "source_candidate_refs": [candidate_ref],
                "source_candidate_hashes": {candidate_ref: body_hash},
                "final_drd_section_id": section_id,
                "final_drd_section_title": heading,
                "compiler_eligible": True,
                "product_capability_additions_allowed": False,
                "process_evidence_refs": [review_ref],
            }
        )
        value["section_order"].append(
            {"stage_id": stage_id, "section_id": section_id, "section_order_index": 1}
        )
        value["sections"].append(
            {
                "section_id": section_id,
                "stage_id": stage_id,
                "stage_order_index": stage_order_index,
                "section_order_index": 1,
                "heading_text": heading,
                "source_path": approved_body_path,
                "source_hash": body_hash,
                "approved_hash_ref": review_ref,
                "approved_semantic_artifact_ref": approved_manifest_id,
                "body": body,
                "semantic_unit_ids": [unit_id],
            }
        )
        value["semantic_units"].append(
            atomic_unit(
                unit_id=unit_id,
                canonical_value=body,
                stage_id=stage_id,
                source_path=approved_body_path,
                source_hash=body_hash,
                approval_ref=review_ref,
                source_section_id=section_id,
            )
        )
    value["compiled_semantic_units"] = value["semantic_units"]
    value["semantic_content_hash"] = compute_semantic_content_hash(value)
    value["closed_input_hash"] = compute_closed_input_hash(value)
    return value


def test_closed_bundle_and_final_compile_pass():
    compiled = compile_final_drd(bundle())

    assert validate_input_bundle(bundle()) == []
    assert "# Final DRD" in compiled["FINAL_DRD.md"]
    assert "Account page exists." in compiled["FINAL_DRD.md"]
    assert "_Source:" not in compiled["FINAL_DRD.md"]
    assert "sha256:" not in compiled["FINAL_DRD.md"]
    assert validate_final_drd_reader_structure(compiled["FINAL_DRD.md"]) == []
    assert validate_final_manifest(compiled["final_drd_manifest.json"]) == []
    assert compiled["compiler_conservation_report.json"]["status"] == "PASS"


def test_compiler_bundle_requires_explicit_approved_stage_mode_flag():
    bad = bundle()
    bad.pop("requires_approved_stage_semantic_artifacts")
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_input_bundle(bad)

    assert any("requires_approved_stage_semantic_artifacts is required" in finding.message for finding in findings)


def test_approved_stage_mode_flag_is_bound_into_closed_input_hash():
    base = bundle()
    toggled = dict(base)
    toggled["requires_approved_stage_semantic_artifacts"] = True

    assert compute_closed_input_hash(base) != compute_closed_input_hash(toggled)


def test_staged_compiler_rejects_raw_candidate_as_approved_semantic_artifact():
    bad = bundle()
    bad["requires_approved_stage_semantic_artifacts"] = True
    bad["semantic_content_hash"] = compute_semantic_content_hash(bad)
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_input_bundle(bad)

    assert any(finding.code == "COMP-CHECK-022" for finding in findings)
    assert any("artifact_kind=APPROVED_SEMANTIC_ARTIFACT" in finding.message for finding in findings)
    assert any("semantic_role=approved_stage_semantic_body" in finding.message for finding in findings)


def test_staged_compiler_accepts_approved_semantic_artifact_body():
    good = approved_stage_bundle()
    compiled = compile_final_drd(good)

    assert validate_input_bundle(good) == []
    assert validate_approved_stage_semantic_artifacts(good) == []
    assert validate_final_drd_reader_structure(compiled["FINAL_DRD.md"]) == []
    assert "DRD-01 approved semantic body." in compiled["FINAL_DRD.md"]
    assert "DRD-04 approved semantic body." in compiled["FINAL_DRD.md"]


def test_staged_compiler_requires_every_stage_approved_semantic_artifact():
    bad = approved_stage_bundle()
    bad["approved_semantic_artifacts"] = [
        record for record in bad["approved_semantic_artifacts"] if record["stage_id"] != "DRD-04"
    ]
    bad["sections"] = [section for section in bad["sections"] if section["stage_id"] != "DRD-04"]
    bad["section_order"] = [row for row in bad["section_order"] if row["stage_id"] != "DRD-04"]
    bad["semantic_units"] = [unit for unit in bad["semantic_units"] if unit["stage_id"] != "DRD-04"]
    bad["compiled_semantic_units"] = bad["semantic_units"]
    bad["semantic_content_hash"] = compute_semantic_content_hash(bad)
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("records for every stage" in finding.message and "DRD-04" in finding.message for finding in findings)
    assert any("sections for every approved stage" in finding.message and "DRD-04" in finding.message for finding in findings)


def test_approved_semantic_artifact_manifest_is_validated_and_bound():
    good = approved_stage_bundle()
    manifest = good["approved_semantic_artifact_manifests"][0]

    assert validate_approved_semantic_artifact_manifest(manifest) == []

    bad = approved_stage_bundle()
    bad["approved_semantic_artifact_manifests"][0]["product_capability_additions_allowed"] = True
    bad["approved_semantic_artifact_manifests"][0]["review_decision_sha256"] = HASH_D
    bad["approved_semantic_artifact_manifests"][0]["process_evidence_refs"] = ["validation/DRD01.json"]
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("product_capability_additions_allowed must be false" in finding.message for finding in findings)
    assert any("review_decision_sha256 must match bundled review decision" in finding.message for finding in findings)
    assert any("process_evidence_refs must include review_decision_ref" in finding.message for finding in findings)


def test_approved_semantic_artifact_manifest_requires_bundled_review_decision():
    bad = approved_stage_bundle()
    bad["review_decisions"] = []
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("review_decision_ref must be present in bundled review_decisions" in finding.message for finding in findings)


def test_approved_semantic_artifact_record_must_be_compiled_by_section():
    bad = approved_stage_bundle()
    extra = dict(bad["approved_semantic_artifacts"][0])
    extra["input_id"] = "DRD-01-UNUSED-APPROVED-SEMANTIC-BODY"
    extra["path"] = "artifacts/DRD-01/UNUSED_APPROVED_SEMANTIC_ARTIFACT.md"
    extra["semantic_body_path"] = extra["path"]
    extra["approved_semantic_artifact_ref"] = bad["approved_semantic_artifact_manifests"][0]["artifact_id"]
    bad["approved_semantic_artifacts"].append(extra)
    bad["closed_input_hash"] = compute_closed_input_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("must be referenced by a compiler section" in finding.message for finding in findings)


def test_approved_stage_semantic_heading_rejects_candidate_process_markers():
    bad = approved_stage_bundle()
    bad["sections"][0]["heading_text"] = "DRD-01 候选语义"
    bad["semantic_content_hash"] = compute_semantic_content_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("process evidence marker" in finding.message for finding in findings)


def test_approved_stage_semantic_body_rejects_candidate_process_markers():
    bad = approved_stage_bundle()
    bad["sections"][0]["body"] = "# DRD-02 用户任务流与交互闭包（候选）\n\nreview_gates/DRD-02_REVIEW_A_DECISION.json"
    bad["semantic_content_hash"] = compute_semantic_content_hash(bad)

    findings = validate_approved_stage_semantic_artifacts(bad)

    assert any("must not contain H1" in finding.message for finding in findings)
    assert any("process evidence marker" in finding.message for finding in findings)


def test_compilation_is_deterministic_for_same_bundle():
    first = compile_final_drd(bundle())
    second = compile_final_drd(bundle())

    assert deterministic_hash(first) == deterministic_hash(second)


def test_toc_is_derived_from_section_identity():
    compiled = compile_final_drd(bundle())
    toc = compiled["final_drd_toc.json"]

    assert toc == [
        {
            "toc_entry_id": "TOC-DRD-02-SEC-ACCOUNT",
            "stage_id": "DRD-02",
            "section_id": "SEC-ACCOUNT",
            "stage_order_index": 20,
            "section_order_index": 1,
            "heading_text": "Account",
            "source_path": "artifacts/DRD-02/PAGES.md",
            "source_hash": HASH_A,
        }
    ]


def test_unapproved_candidate_input_is_rejected():
    bad = bundle()
    bad["approved_semantic_artifacts"][0]["input_type"] = "UNAPPROVED_CANDIDATE"

    findings = validate_input_bundle(bad)

    assert "COMP-CHECK-002" in {finding.code for finding in findings}


def test_compile_rejects_unapproved_candidate_input():
    bad = bundle()
    bad["approved_semantic_artifacts"][0]["input_type"] = "UNAPPROVED_CANDIDATE"

    try:
        compile_final_drd(bad)
    except CompilerFailure as exc:
        assert "COMP-CHECK-002" in {finding.code for finding in exc.findings}
    else:
        raise AssertionError("compile_final_drd should fail closed")


def test_prose_only_approval_is_rejected():
    bad = bundle()
    bad["approved_semantic_artifacts"][0]["approval_ref"] = "approved in prose"

    findings = validate_input_bundle(bad)

    assert "COMP-CHECK-003" in {finding.code for finding in findings}


def test_closed_input_hash_is_recomputed_and_checked():
    bad = bundle()
    bad["closed_input_hash"] = "0" * 64

    findings = validate_input_bundle(bad)

    assert "closed_input_hash does not match" in " ".join(finding.message for finding in findings)


def test_compile_reports_uninventoried_semantic_addition():
    bad = bundle()
    bad["sections"][0]["body"] = "Account page exists. Delete account button exists."

    compiled = compile_final_drd(bad)

    assert compiled["compiler_conservation_report.json"]["status"] == "FAIL_SEMANTIC_ADDITION"
    assert compiled["final_drd_manifest.json"]["added_semantic_unit_count"] == 1


def test_nondeterministic_section_order_is_rejected():
    findings = validate_section_order(
        [
            {
                "section_id": "SEC-ACCOUNT",
                "stage_order_index": 20,
                "section_order_index": 1,
                "ordering_source": "filesystem",
            }
        ]
    )

    assert "COMP-CHECK-005" in {finding.code for finding in findings}


def test_final_manifest_rejects_bad_hash_fields():
    manifest = {
        "final_drd_path": "FINAL_DRD.md",
        "final_drd_hash": HASH_A,
        "semantic_hash": HASH_B,
        "mechanical_hash": HASH_C,
        "input_bundle_hash": "not-a-hash",
        "toc_hash": "bad",
        "reference_index_hash": "bad",
        "hash_index_hash": "bad",
        "conservation_report_hash": "bad",
        "approved_input_count": 1,
        "compiled_section_count": 1,
        "compiled_semantic_unit_count": 1,
        "omitted_semantic_unit_count": 0,
        "added_semantic_unit_count": 0,
        "hash_drift_count": 0,
        "unapproved_input_count": 0,
        "conservation_status": "PASS",
        "assembly_plan": {},
    }

    findings = validate_final_manifest(manifest)

    assert "COMP-CHECK-012" in {finding.code for finding in findings}


def test_compiler_schemas_declare_required_outputs():
    root = Path("repository/schemas/compiler")
    manifest_schema = json.loads((root / "final_drd_manifest.schema.json").read_text(encoding="utf-8"))
    bundle_schema = json.loads((root / "compiler_input_bundle.schema.json").read_text(encoding="utf-8"))
    atomic_schema = json.loads((root / "compiler_atomic_semantic_unit.schema.json").read_text(encoding="utf-8"))

    assert {"semantic_hash", "mechanical_hash", "input_bundle_hash"} <= set(manifest_schema["required"])
    assert bundle_schema["properties"]["compiler_stage_id"]["const"] == "DRD-05"
    assert "CTA" in atomic_schema["properties"]["unit_type"]["enum"]
