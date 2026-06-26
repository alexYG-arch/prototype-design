"""P3 experience distillation validators."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set

from drd_harness.rules.prd_adoption import AdoptionOutcome, ElementType
from drd_harness.rules.reasoning import CanonicalEligibility, InferenceClass
from drd_harness.validators.prd_adoption import validate_product_expansion_gap
from drd_harness.validators.reasoning import inference_record_from_mapping, validate_inference_record


SEMANTIC_FAMILIES = {
    "experience.task",
    "experience.actor",
    "experience.role_or_permission",
    "experience.surface",
    "experience.navigation",
    "experience.action",
    "experience.input",
    "experience.message",
    "experience.state",
    "experience.async_or_failure",
    "experience.recovery",
    "experience.constraint",
    "experience.data_object",
    "experience.open_question",
}
PRD_ELEMENT_TYPES = {item.value for item in ElementType}
CANONICAL_INFERENCE_CLASSES = {
    InferenceClass.SOURCE_EXPLICIT.value,
    InferenceClass.DEDUCTIVE_NECESSITY.value,
    InferenceClass.HUMAN_DECIDED.value,
}
BLOCKING_OUTCOMES = {
    AdoptionOutcome.REQUEST_CLARIFICATION.value,
    AdoptionOutcome.REJECT_CONFLICT.value,
    AdoptionOutcome.ROUTE_PRODUCT_GAP.value,
}


@dataclass(frozen=True)
class ExperienceDistillationFinding:
    code: str
    subject_id: str
    message: str


def validate_experience_distillation_artifacts(
    *,
    source_intake_decisions: Mapping[str, Any],
    semantic_unit_map: Mapping[str, Any],
    prd_element_inventory: Mapping[str, Any],
    prd_element_decisions: Mapping[str, Any],
    inference_records: Mapping[str, Any],
    input_obligations: Mapping[str, Any],
    derived_element_decisions: Mapping[str, Any],
    product_expansion_gaps: Mapping[str, Any],
    structural_completion_review: Mapping[str, Any],
    closure_handoff_manifest: Mapping[str, Any],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    source_states = _source_states(source_intake_decisions)
    units = _rows(semantic_unit_map, "records")
    inventory_rows = _rows(prd_element_inventory, "records")
    decision_rows = _rows(prd_element_decisions, "records")
    inference_rows = _rows(inference_records, "records")
    obligation_rows = _rows(input_obligations, "records")
    derived_rows = _rows(derived_element_decisions, "records")
    gap_rows = _rows(product_expansion_gaps, "records")
    review_rows = _rows(structural_completion_review, "records")

    units_by_id = _by_id(units, "unit_id")
    inventory_by_id = _by_id(inventory_rows, "element_id")
    decisions_by_id = _by_id(decision_rows, "element_id")
    inference_ids = set(_by_id(inference_rows, "inference_id"))
    obligation_ids = set(_by_id(obligation_rows, "obligation_id"))
    gap_ids = set(_by_id(gap_rows, "gap_id"))

    findings.extend(_require_unique(units, "unit_id", "DISTILL001", "semantic_unit_map"))
    findings.extend(_validate_semantic_units(units, source_states))
    findings.extend(_validate_inventory(inventory_rows, units_by_id))
    findings.extend(_validate_adoption_decisions(inventory_by_id, decisions_by_id, inference_ids, obligation_ids))
    findings.extend(_validate_inference_records(inference_rows))
    findings.extend(_validate_input_obligations(obligation_rows, gap_ids))
    findings.extend(_validate_derived_decisions(derived_rows, obligation_ids, inference_ids))
    findings.extend(_validate_product_gaps(gap_rows))
    findings.extend(_validate_structural_reviews(review_rows, gap_ids))
    findings.extend(_validate_closure_handoff(closure_handoff_manifest, units_by_id, gap_rows))
    return findings


def _validate_semantic_units(
    units: Sequence[Mapping[str, Any]],
    source_states: Mapping[str, str],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    for unit in units:
        unit_id = str(unit.get("unit_id", "semantic_unit"))
        family = unit.get("semantic_family")
        eligibility = unit.get("canonical_eligibility")
        inference_class = unit.get("inference_class")
        source_refs = _text_list(unit.get("source_refs", []))
        source_hash = unit.get("source_text_hash")
        element_type = unit.get("prd_element_type")

        if family not in SEMANTIC_FAMILIES:
            findings.append(ExperienceDistillationFinding("DISTILL001", unit_id, "semantic_family is not allowed"))
        if unit.get("atomic_claim_count") != 1:
            findings.append(ExperienceDistillationFinding("DISTILL002", unit_id, "semantic unit must represent exactly one atomic claim"))
        if not source_refs:
            findings.append(ExperienceDistillationFinding("DISTILL003", unit_id, "semantic unit requires source_refs"))
        for source_ref in source_refs:
            if source_ref not in source_states:
                findings.append(ExperienceDistillationFinding("DISTILL003", unit_id, "semantic unit references unknown source item"))
        if not _is_hash(source_hash):
            findings.append(ExperienceDistillationFinding("DISTILL003", unit_id, "source_text_hash must be sha256"))
        if element_type is not None and element_type not in PRD_ELEMENT_TYPES:
            findings.append(ExperienceDistillationFinding("DISTILL004", unit_id, "prd_element_type must use existing PRD element enum"))

        states = [source_states.get(ref) for ref in source_refs]
        if eligibility == CanonicalEligibility.ELIGIBLE.value and any(state != "eligible" for state in states):
            findings.append(ExperienceDistillationFinding("DISTILL005", unit_id, "eligible semantic unit must cite only eligible source items"))
        if any(state == "rejected" for state in states) and eligibility != CanonicalEligibility.REJECTED.value:
            findings.append(ExperienceDistillationFinding("DISTILL006", unit_id, "rejected source cannot feed semantic authority"))
        if inference_class == InferenceClass.INDUCTIVE_CANDIDATE.value and eligibility == CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL007", unit_id, "inductive candidate cannot be canonical without Human Gate"))
        if unit.get("requires_product_capability_expansion") is True and eligibility == CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL008", unit_id, "product expansion cannot be eligible during distillation"))
        if (
            inference_class == InferenceClass.DEDUCTIVE_NECESSITY.value
            and eligibility == CanonicalEligibility.ELIGIBLE.value
            and not unit.get("necessity_basis")
        ):
            findings.append(ExperienceDistillationFinding("DISTILL009", unit_id, "eligible deductive necessity requires necessity_basis"))
    return findings


def _validate_inventory(
    inventory_rows: Sequence[Mapping[str, Any]],
    units_by_id: Mapping[str, Mapping[str, Any]],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(inventory_rows, "element_id", "DISTILL010", "prd_element_inventory"))
    for row in inventory_rows:
        element_id = str(row.get("element_id", "element"))
        if row.get("element_type") not in PRD_ELEMENT_TYPES:
            findings.append(ExperienceDistillationFinding("DISTILL004", element_id, "element_type must use existing PRD element enum"))
        unit_refs = _text_list(row.get("source_unit_refs", []))
        if not unit_refs:
            findings.append(ExperienceDistillationFinding("DISTILL011", element_id, "inventory row requires source_unit_refs"))
        for unit_ref in unit_refs:
            if unit_ref not in units_by_id:
                findings.append(ExperienceDistillationFinding("DISTILL011", element_id, "inventory row references unknown semantic unit"))
        if not _is_hash(row.get("source_text_hash")):
            findings.append(ExperienceDistillationFinding("DISTILL011", element_id, "inventory row source_text_hash must be sha256"))
    return findings


def _validate_adoption_decisions(
    inventory_by_id: Mapping[str, Mapping[str, Any]],
    decisions_by_id: Mapping[str, Mapping[str, Any]],
    inference_ids: Set[str],
    obligation_ids: Set[str],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    missing = sorted(set(inventory_by_id) - set(decisions_by_id))
    extra = sorted(set(decisions_by_id) - set(inventory_by_id))
    for element_id in missing:
        findings.append(ExperienceDistillationFinding("DISTILL012", element_id, "inventory element lacks adoption decision"))
    for element_id in extra:
        findings.append(ExperienceDistillationFinding("DISTILL012", element_id, "adoption decision references non-inventory element"))
    for element_id, decision in decisions_by_id.items():
        outcome = decision.get("outcome")
        refs = _text_list(decision.get("inference_refs", []))
        obligation_refs = _text_list(decision.get("input_obligations", []))
        if outcome not in {item.value for item in AdoptionOutcome}:
            findings.append(ExperienceDistillationFinding("DISTILL013", element_id, "adoption outcome is not allowed"))
        if outcome == AdoptionOutcome.ADOPT_NORMALIZED.value and not decision.get("normalized_label"):
            findings.append(ExperienceDistillationFinding("DISTILL013", element_id, "ADOPT_NORMALIZED requires normalized_label"))
        if outcome in BLOCKING_OUTCOMES and not decision.get("blocking_reason"):
            findings.append(ExperienceDistillationFinding("DISTILL013", element_id, "blocking outcome requires blocking_reason"))
        if not refs:
            findings.append(ExperienceDistillationFinding("DISTILL014", element_id, "adoption decision requires inference_refs"))
        for ref in refs:
            if ref not in inference_ids:
                findings.append(ExperienceDistillationFinding("DISTILL014", element_id, "adoption decision references unknown inference"))
        for ref in obligation_refs:
            if ref not in obligation_ids:
                findings.append(ExperienceDistillationFinding("DISTILL017", element_id, "adoption decision references unknown input obligation"))
    return findings


def _validate_inference_records(inference_rows: Sequence[Mapping[str, Any]]) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(inference_rows, "inference_id", "DISTILL015", "inference_records"))
    for row in inference_rows:
        inference_id = str(row.get("inference_id", "inference"))
        try:
            record = inference_record_from_mapping(row)
        except (KeyError, ValueError) as exc:
            findings.append(ExperienceDistillationFinding("DISTILL015", inference_id, str(exc)))
            continue
        for finding in validate_inference_record(record):
            findings.append(ExperienceDistillationFinding(finding.code, finding.subject_id, finding.message))
        if (
            row.get("canonical_eligibility") == CanonicalEligibility.ELIGIBLE.value
            and row.get("inference_class") not in CANONICAL_INFERENCE_CLASSES
        ):
            findings.append(ExperienceDistillationFinding("DISTILL016", inference_id, "canonical inference class is not allowed"))
    return findings


def _validate_input_obligations(
    obligation_rows: Sequence[Mapping[str, Any]],
    gap_ids: Set[str],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(obligation_rows, "obligation_id", "DISTILL017", "input_obligations"))
    for row in obligation_rows:
        obligation_id = str(row.get("obligation_id", "obligation"))
        if not row.get("acquisition_path") and not row.get("gap_ref"):
            findings.append(ExperienceDistillationFinding("DISTILL017", obligation_id, "input obligation requires acquisition_path or gap_ref"))
        gap_ref = row.get("gap_ref")
        if gap_ref and gap_ref not in gap_ids:
            findings.append(ExperienceDistillationFinding("DISTILL017", obligation_id, "input obligation references unknown gap"))
    return findings


def _validate_derived_decisions(
    derived_rows: Sequence[Mapping[str, Any]],
    obligation_ids: Set[str],
    inference_ids: Set[str],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(derived_rows, "derived_element_id", "DISTILL018", "derived_element_decisions"))
    for row in derived_rows:
        derived_id = str(row.get("derived_element_id", "derived"))
        obligation_refs = _text_list(row.get("obligation_refs", []))
        inference_refs = _text_list(row.get("inference_refs", []))
        if not obligation_refs or any(ref not in obligation_ids for ref in obligation_refs):
            findings.append(ExperienceDistillationFinding("DISTILL018", derived_id, "derived decision requires known obligation_refs"))
        if not inference_refs or any(ref not in inference_ids for ref in inference_refs):
            findings.append(ExperienceDistillationFinding("DISTILL018", derived_id, "derived decision requires known inference_refs"))
        if row.get("derivation_strategy") == "INDUCTIVE_AUXILIARY" and row.get("canonical_eligibility") == CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL007", derived_id, "inductive derived element cannot be eligible"))
        if row.get("canonical_eligibility") != CanonicalEligibility.ELIGIBLE.value and not row.get("blocked_by"):
            findings.append(ExperienceDistillationFinding("DISTILL019", derived_id, "blocked derived element requires blocked_by"))
    return findings


def _validate_product_gaps(gap_rows: Sequence[Mapping[str, Any]]) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(gap_rows, "gap_id", "DISTILL020", "product_expansion_gaps"))
    for row in gap_rows:
        for finding in validate_product_expansion_gap(row):
            findings.append(ExperienceDistillationFinding(finding.code, finding.subject_id, finding.message))
    return findings


def _validate_structural_reviews(
    review_rows: Sequence[Mapping[str, Any]],
    gap_ids: Set[str],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    findings.extend(_require_unique(review_rows, "review_id", "DISTILL021", "structural_completion_review"))
    for row in review_rows:
        review_id = str(row.get("review_id", "review"))
        if row.get("canonical_eligibility") == CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL021", review_id, "structural completion review cannot be canonical before Human Gate"))
        if row.get("product_expansion_risk") == "PRESENT" and row.get("gap_ref") not in gap_ids:
            findings.append(ExperienceDistillationFinding("DISTILL022", review_id, "product expansion risk requires matching gap_ref"))
    return findings


def _validate_closure_handoff(
    handoff: Mapping[str, Any],
    units_by_id: Mapping[str, Mapping[str, Any]],
    gap_rows: Sequence[Mapping[str, Any]],
) -> List[ExperienceDistillationFinding]:
    findings: List[ExperienceDistillationFinding] = []
    eligible_units = _text_list(handoff.get("eligible_unit_refs", []))
    blocked_units = _text_list(handoff.get("blocked_unit_refs", []))
    blocked_gaps = _text_list(handoff.get("blocked_product_gap_refs", []))
    gap_ids = {str(row.get("gap_id")) for row in gap_rows if row.get("gap_id")}
    required_eligible_units = sorted(
        unit_id
        for unit_id, unit in units_by_id.items()
        if unit.get("canonical_eligibility") == CanonicalEligibility.ELIGIBLE.value
    )
    required_blocked_units = sorted(
        unit_id
        for unit_id, unit in units_by_id.items()
        if unit.get("canonical_eligibility") != CanonicalEligibility.ELIGIBLE.value
    )
    required_open_gaps = sorted(
        str(row.get("gap_id"))
        for row in gap_rows
        if row.get("gap_id") and row.get("status") == "OPEN"
    )

    for unit_id in required_eligible_units:
        if unit_id not in eligible_units:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "handoff omits eligible semantic unit"))
    for unit_id in required_blocked_units:
        if unit_id not in blocked_units:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "handoff omits blocked semantic unit"))
    for gap_id in required_open_gaps:
        if gap_id not in blocked_gaps:
            findings.append(ExperienceDistillationFinding("DISTILL025", gap_id, "handoff omits open product gap"))

    for unit_id in eligible_units:
        unit = units_by_id.get(unit_id)
        if unit is None:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "handoff references unknown eligible unit"))
            continue
        if unit.get("canonical_eligibility") != CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "handoff eligible units must be canonical eligible"))
        if unit.get("requires_product_capability_expansion") is True:
            findings.append(ExperienceDistillationFinding("DISTILL024", unit_id, "product expansion unit cannot feed closure as eligible"))
    for unit_id in blocked_units:
        unit = units_by_id.get(unit_id)
        if unit is None:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "handoff references unknown blocked unit"))
            continue
        if unit.get("canonical_eligibility") == CanonicalEligibility.ELIGIBLE.value:
            findings.append(ExperienceDistillationFinding("DISTILL023", unit_id, "eligible unit cannot be listed as blocked"))
    for gap_id in blocked_gaps:
        if gap_id not in gap_ids:
            findings.append(ExperienceDistillationFinding("DISTILL025", gap_id, "handoff references unknown product gap"))
    return findings


def _source_states(source_intake_decisions: Mapping[str, Any]) -> Dict[str, str]:
    return {
        str(row["source_item_id"]): str(row["downstream_eligibility"])
        for row in _rows(source_intake_decisions, "decisions")
        if row.get("source_item_id")
    }


def _rows(payload: Mapping[str, Any], key: str) -> List[Mapping[str, Any]]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _by_id(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, Mapping[str, Any]]:
    result: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if isinstance(value, str) and value:
            result[value] = row
    return result


def _require_unique(rows: Sequence[Mapping[str, Any]], key: str, code: str, subject_id: str) -> List[ExperienceDistillationFinding]:
    values = [row.get(key) for row in rows if isinstance(row.get(key), str)]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    return [ExperienceDistillationFinding(code, subject_id, "duplicate ids: " + ", ".join(duplicates))] if duplicates else []


def _text_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)
