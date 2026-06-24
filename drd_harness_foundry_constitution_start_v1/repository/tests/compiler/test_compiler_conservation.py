from drd_harness.compiler.conservation import (
    compare_semantic_units,
    compute_unit_hash,
    validate_atomic_inventory,
)
from drd_harness.validators.compiler_conservation import (
    input_records,
    validate_conservation_report,
    validate_hash_drift,
    validate_read_only_qa_boundary,
)
from repository.tests.compiler.test_final_drd_compilation import HASH_A, HASH_B, atomic_unit, bundle


def test_atomic_inventory_accepts_separate_page_and_cta_rows():
    page = atomic_unit()
    cta = atomic_unit(
        "UNIT-CTA-SAVE",
        "CTA",
        "Save button triggers account save.",
    )
    cta["stage_id"] = "DRD-03"
    cta["source_path"] = "artifacts/DRD-03/INTERACTIONS.md"
    cta["source_section_id"] = "SEC-SAVE"
    cta["source_span_ref"] = "clickable:CLK-SAVE"
    cta["parent_unit_id"] = page["semantic_unit_id"]
    cta["relationship_kind"] = "CONTAINED_BY"
    cta["unit_hash"] = compute_unit_hash(cta)

    assert validate_atomic_inventory([page, cta]) == []


def test_non_atomic_inventory_row_is_rejected():
    row = atomic_unit(
        "UNIT-ACCOUNT-SCREEN",
        "SCREEN_BUNDLE",
        "Account page includes fields, save button, error copy, mobile layout, and recovery.",
    )
    row["source_span_ref"] = "section:Account"
    row["unit_hash"] = compute_unit_hash(row)

    findings = validate_atomic_inventory([row])

    assert {"COMP-CHECK-017", "COMP-CHECK-019"} <= {finding.code for finding in findings}


def test_parent_page_cannot_prove_child_semantics():
    row = atomic_unit(
        "UNIT-PAGE-ACCOUNT",
        "PAGE",
        "Account page includes button, copy, validation, layout, and recovery.",
    )

    findings = validate_atomic_inventory([row])

    assert "COMP-CHECK-020" in {finding.code for finding in findings}


def test_child_unit_requires_existing_parent():
    child = atomic_unit("UNIT-CTA-SAVE", "CTA", "Save button exists.")
    child["parent_unit_id"] = "UNIT-MISSING"
    child["relationship_kind"] = "CONTAINED_BY"
    child["unit_hash"] = compute_unit_hash(child)

    findings = validate_atomic_inventory([child])

    assert "parent_unit_id does not resolve" in " ".join(finding.message for finding in findings)


def test_semantic_addition_and_omission_are_reported():
    approved = [atomic_unit("UNIT-PAGE-ACCOUNT")]
    compiled = [atomic_unit("UNIT-PAGE-ACCOUNT"), atomic_unit("UNIT-CTA-DELETE", "CTA", "Delete account button exists.")]

    report = compare_semantic_units(approved, compiled)
    findings = validate_conservation_report(report)

    assert report["status"] == "FAIL_SEMANTIC_ADDITION"
    assert "COMP-CHECK-007" in {finding.code for finding in findings}


def test_semantic_omission_is_reported():
    approved = [atomic_unit("UNIT-PAGE-ACCOUNT"), atomic_unit("UNIT-CTA-SAVE", "CTA", "Save button exists.")]
    compiled = [atomic_unit("UNIT-PAGE-ACCOUNT")]

    report = compare_semantic_units(approved, compiled)
    findings = validate_conservation_report(report)

    assert report["status"] == "FAIL_SEMANTIC_OMISSION"
    assert "COMP-CHECK-008" in {finding.code for finding in findings}


def test_hash_drift_is_reported_for_bundle_records():
    records = input_records(bundle())

    findings = validate_hash_drift(records, {"artifacts/DRD-02/PAGES.md": HASH_B})

    assert findings[0].code == "COMP-CHECK-004"


def test_read_only_qa_accepts_only_qa_outputs():
    findings = validate_read_only_qa_boundary(
        {
            "drd06_run_id": "QA-RUN-001",
            "written_paths": ["READ_ONLY_QA_REPORT.md", "qa_finding_index.json"],
            "mutated_artifacts": [],
        }
    )

    assert findings == []


def test_read_only_qa_rejects_final_drd_mutation():
    findings = validate_read_only_qa_boundary(
        {
            "drd06_run_id": "QA-RUN-002",
            "written_paths": ["READ_ONLY_QA_REPORT.md", "FINAL_DRD.md"],
            "mutated_artifacts": ["FINAL_DRD.md"],
        }
    )

    assert "COMP-CHECK-014" in {finding.code for finding in findings}
