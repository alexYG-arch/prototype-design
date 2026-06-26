import copy
import json
from pathlib import Path

from drd_harness.stages.experience_distillation import validate_experience_distillation_artifacts


DISTILL_ROOT = Path("repository/fixtures/p3/distill")
SOURCE_INTAKE_ROOT = Path("repository/fixtures/p3/source_intake")


def test_p3_experience_distillation_fixture_validates_atomic_evidence_package():
    artifacts = _load_fixture_artifacts()

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert findings == []
    units = {row["unit_id"]: row for row in artifacts["semantic_unit_map"]["records"]}
    assert units["p3-unit-console-surface"]["semantic_family"] == "experience.surface"
    assert units["p3-unit-console-surface"]["prd_element_type"] == "PAGE"
    assert units["p3-unit-visual-blocker"]["canonical_eligibility"] == "BLOCKED_PENDING_HUMAN"


def test_review_required_source_cannot_be_promoted_to_eligible_semantics():
    artifacts = _load_fixture_artifacts()
    unit = _unit(artifacts, "p3-unit-visual-blocker")
    unit["canonical_eligibility"] = "ELIGIBLE"
    unit["prd_element_type"] = "UI_ELEMENT"

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL005" in {finding.code for finding in findings}


def test_rejected_source_cannot_feed_semantic_authority():
    artifacts = _load_fixture_artifacts()
    artifacts["semantic_unit_map"]["records"].append(
        {
            "unit_id": "p3-unit-rejected-link",
            "semantic_family": "experience.open_question",
            "atomic_claim_count": 1,
            "claim": "Unretrieved external link content should be treated as a product note.",
            "source_refs": ["p3-src-link"],
            "source_text_hash": "a" * 64,
            "prd_element_type": "MESSAGE",
            "inference_class": "SOURCE_EXPLICIT",
            "canonical_eligibility": "ELIGIBLE",
            "requires_product_capability_expansion": False,
            "necessity_basis": None,
            "downstream_use": ["closure_handoff"],
        }
    )

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL005" in {finding.code for finding in findings}
    assert "DISTILL006" in {finding.code for finding in findings}


def test_semantic_unit_source_refs_must_exist_in_source_intake_decisions():
    artifacts = _load_fixture_artifacts()
    unit = _unit(artifacts, "p3-unit-visual-blocker")
    unit["source_refs"] = ["p3-src-unknown"]

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL003" in {finding.code for finding in findings}


def test_inductive_candidate_cannot_be_canonical_without_human_gate():
    artifacts = _load_fixture_artifacts()
    unit = _unit(artifacts, "p3-unit-visual-blocker")
    unit["inference_class"] = "INDUCTIVE_CANDIDATE"
    unit["canonical_eligibility"] = "ELIGIBLE"
    unit["prd_element_type"] = "UI_ELEMENT"

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL007" in {finding.code for finding in findings}


def test_p3_semantic_family_names_cannot_replace_prd_element_enum_values():
    artifacts = _load_fixture_artifacts()
    artifacts["prd_element_inventory"]["records"][0]["element_type"] = "experience.surface"

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL004" in {finding.code for finding in findings}


def test_input_obligation_requires_path_or_gap_route():
    artifacts = _load_fixture_artifacts()
    obligation = artifacts["input_obligations"]["records"][0]
    obligation["acquisition_path"] = None
    obligation["gap_ref"] = None

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL017" in {finding.code for finding in findings}


def test_adoption_decision_input_obligations_must_reference_known_obligations():
    artifacts = _load_fixture_artifacts()
    decision = next(
        row
        for row in artifacts["prd_element_decisions"]["records"]
        if row["element_id"] == "p3-elem-review-gap-message"
    )
    decision["input_obligations"] = ["p3-obligation-missing"]

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL017" in {finding.code for finding in findings}


def test_closure_handoff_must_cover_all_eligible_and_blocked_units_and_open_gaps():
    artifacts = _load_fixture_artifacts()
    artifacts["closure_handoff_manifest"]["eligible_unit_refs"].remove("p3-unit-review-gap-message")
    artifacts["closure_handoff_manifest"]["blocked_unit_refs"] = []
    artifacts["closure_handoff_manifest"]["blocked_product_gap_refs"] = []

    findings = validate_experience_distillation_artifacts(**artifacts)
    by_subject = {finding.subject_id: finding.code for finding in findings}

    assert by_subject["p3-unit-review-gap-message"] == "DISTILL023"
    assert by_subject["p3-unit-visual-blocker"] == "DISTILL023"
    assert by_subject["p3-gap-missing-product-details"] == "DISTILL025"


def test_product_expansion_unit_cannot_feed_closure_as_eligible():
    artifacts = _load_fixture_artifacts()
    unit = _unit(artifacts, "p3-unit-visual-blocker")
    unit["canonical_eligibility"] = "ELIGIBLE"
    unit["prd_element_type"] = "UI_ELEMENT"
    unit["requires_product_capability_expansion"] = True
    artifacts["closure_handoff_manifest"]["eligible_unit_refs"].append("p3-unit-visual-blocker")

    findings = validate_experience_distillation_artifacts(**artifacts)

    assert "DISTILL008" in {finding.code for finding in findings}
    assert "DISTILL024" in {finding.code for finding in findings}


def _load_fixture_artifacts():
    return {
        "source_intake_decisions": copy.deepcopy(_load_json(SOURCE_INTAKE_ROOT / "intake_decisions.json")),
        "semantic_unit_map": _load_json(DISTILL_ROOT / "semantic_unit_map.json"),
        "prd_element_inventory": _load_json(DISTILL_ROOT / "prd_element_inventory.json"),
        "prd_element_decisions": _load_json(DISTILL_ROOT / "prd_element_decisions.json"),
        "inference_records": _load_json(DISTILL_ROOT / "inference_records.json"),
        "input_obligations": _load_json(DISTILL_ROOT / "input_obligations.json"),
        "derived_element_decisions": _load_json(DISTILL_ROOT / "derived_element_decisions.json"),
        "product_expansion_gaps": _load_json(DISTILL_ROOT / "product_expansion_gaps.json"),
        "structural_completion_review": _load_json(DISTILL_ROOT / "structural_completion_review.json"),
        "closure_handoff_manifest": _load_json(DISTILL_ROOT / "closure_handoff_manifest.json"),
    }


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _unit(artifacts, unit_id: str):
    return next(row for row in artifacts["semantic_unit_map"]["records"] if row["unit_id"] == unit_id)
