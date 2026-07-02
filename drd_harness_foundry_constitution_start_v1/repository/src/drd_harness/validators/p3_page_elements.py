"""P3 page element artifact-set validators."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set

from drd_harness.rules.prd_adoption import (
    AdoptionOutcome,
    ElementType,
    PrdElementDecision,
    PrdElementInventoryItem,
)
from drd_harness.rules.reasoning import (
    CanonicalEligibility,
    DerivationStrategy,
    DerivedElementDecision,
    InputObligation,
)
from drd_harness.validators.prd_adoption import (
    AdoptionFinding,
    validate_adoption_decision,
    validate_derived_element_decision,
    validate_inventory_coverage,
    validate_inventory_items,
    validate_product_expansion_gap,
)
from drd_harness.validators.reasoning import (
    inference_record_from_mapping,
    require_canonical_consumption_allowed,
    structural_completion_review_from_mapping,
    validate_inference_record_set,
    validate_input_obligation,
    validate_structural_completion_review_set,
)


REQUIRED_ARTIFACT_ENVELOPE_FIELDS = {
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

P3_PRD_ADOPTION_VALIDATOR_REF = "repository/src/drd_harness/validators/prd_adoption.py"
P3_REASONING_VALIDATOR_REF = "repository/src/drd_harness/validators/reasoning.py"

P3_ELEMENTS_ARTIFACTS = {
    "prd_element_inventory": (
        "p3.elements.prd_element_inventory",
        "records",
        P3_PRD_ADOPTION_VALIDATOR_REF,
    ),
    "prd_element_decisions": (
        "p3.elements.prd_element_decisions",
        "records",
        P3_PRD_ADOPTION_VALIDATOR_REF,
    ),
    "derived_element_decisions": (
        "p3.elements.derived_element_decisions",
        "records",
        P3_PRD_ADOPTION_VALIDATOR_REF,
    ),
    "inference_records": (
        "p3.elements.inference_records",
        "records",
        P3_REASONING_VALIDATOR_REF,
    ),
    "input_obligations": (
        "p3.elements.input_obligations",
        "records",
        P3_REASONING_VALIDATOR_REF,
    ),
    "structural_completion_review": (
        "p3.elements.structural_completion_review",
        "records",
        P3_REASONING_VALIDATOR_REF,
    ),
    "product_expansion_gaps": (
        "p3.elements.product_expansion_gaps",
        "records",
        P3_PRD_ADOPTION_VALIDATOR_REF,
    ),
    "renderable_page_variants": (
        "p3.elements.renderable_page_variants",
        "records",
        P3_PRD_ADOPTION_VALIDATOR_REF,
    ),
}

ADOPTED_OUTCOMES = {AdoptionOutcome.ADOPT_AS_IS, AdoptionOutcome.ADOPT_NORMALIZED}
NON_CANONICAL_GAP_STATUSES = {"OPEN", "RESOLVED_REJECTED", "SUPERSEDED"}
RENDERABLE_DERIVATION_ORIGINS = {
    "PRD_EXPLICIT",
    "DEDUCTIVE_REQUIRED",
    "HUMAN_APPROVED_INFERENCE",
    "REVIEW_REQUIRED_INFERENCE",
}
RENDERABLE_ORDER_FIELDS = (
    "module_order_index",
    "page_order_index",
    "variant_order_index",
    "figma_frame_order_index",
)

REQUIRED_SEMANTIC_SOURCE_MODEL = {
    "primary_semantics": "natural_language_source_and_approved_closure",
    "inventory_role": "index_and_verification_skeleton",
}

NODE_ELEMENT_TYPES = {
    "PAGE": {ElementType.PAGE},
    "STATE": {ElementType.STATE},
    "OVERLAY": {ElementType.UI_ELEMENT},
}
CLICKABLE_ELEMENT_TYPES = {ElementType.CTA, ElementType.NAVIGATION, ElementType.INPUT, ElementType.UI_ELEMENT}
MESSAGE_ELEMENT_TYPES = {ElementType.MESSAGE}
RECOVERY_ELEMENT_TYPES = {ElementType.CTA, ElementType.NAVIGATION, ElementType.UI_ELEMENT}


def validate_page_element_artifacts(
    *,
    prd_element_inventory: Mapping[str, object],
    prd_element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
    inference_records: Mapping[str, object],
    input_obligations: Mapping[str, object],
    structural_completion_review: Mapping[str, object],
    product_expansion_gaps: Mapping[str, object],
    renderable_page_variants: Mapping[str, object],
    closure_interaction_nodes: Mapping[str, object],
    closure_clickable_inventory: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
    closure_async_behavior: Mapping[str, object],
    closure_failure_recovery: Mapping[str, object],
    closure_overlay_closure: Mapping[str, object],
    closure_handoff_behavior: Mapping[str, object],
    closure_handoff_manifest: Mapping[str, object],
) -> List[AdoptionFinding]:
    artifacts = {
        "prd_element_inventory": prd_element_inventory,
        "prd_element_decisions": prd_element_decisions,
        "derived_element_decisions": derived_element_decisions,
        "inference_records": inference_records,
        "input_obligations": input_obligations,
        "structural_completion_review": structural_completion_review,
        "product_expansion_gaps": product_expansion_gaps,
        "renderable_page_variants": renderable_page_variants,
    }
    findings: List[AdoptionFinding] = []
    for name, artifact in artifacts.items():
        artifact_id, payload_key, validator_ref = P3_ELEMENTS_ARTIFACTS[name]
        findings.extend(_validate_artifact_envelope(artifact, artifact_id, payload_key, validator_ref))
        findings.extend(_validate_records_payload(artifact, artifact_id, payload_key))
    findings.extend(_validate_semantic_source_model(prd_element_inventory))

    try:
        inventory = [_inventory_item_from_mapping(record) for record in _payload_records(prd_element_inventory)]
        decisions = [_decision_from_mapping(record) for record in _payload_records(prd_element_decisions)]
        derived = [_derived_decision_from_mapping(record) for record in _payload_records(derived_element_decisions)]
        inferences = [inference_record_from_mapping(record) for record in _payload_records(inference_records)]
        obligations = [_input_obligation_from_mapping(record) for record in _payload_records(input_obligations)]
        reviews = [
            structural_completion_review_from_mapping(record)
            for record in _payload_records(structural_completion_review)
        ]
    except (KeyError, ValueError) as exc:
        findings.append(AdoptionFinding("REASON000", "p3.elements", str(exc)))
        return findings

    gap_records = _payload_records(product_expansion_gaps)
    source_authority_refs, authority_findings = _load_upstream_authority_refs(prd_element_inventory)
    findings.extend(authority_findings)
    findings.extend(validate_inventory_items(inventory))
    findings.extend(_validate_atomic_inventory(inventory))
    for decision in decisions:
        findings.extend(validate_adoption_decision(decision))
    findings.extend(validate_inventory_coverage(inventory, decisions))
    for decision in derived:
        findings.extend(validate_derived_element_decision(decision))
    for gap in gap_records:
        findings.extend(validate_product_expansion_gap(gap))
    findings.extend(
        _convert_reasoning_findings(
            validate_inference_record_set(inferences, required_inference_ids=_required_inference_ids(decisions, derived))
        )
    )
    for obligation in obligations:
        findings.extend(_convert_reasoning_findings(validate_input_obligation(obligation)))
    findings.extend(_convert_reasoning_findings(validate_structural_completion_review_set(reviews)))

    findings.extend(_validate_element_cross_references(decisions, derived, obligations, reviews, gap_records, inferences))
    canonical_projection = compute_canonical_element_ids(inventory, decisions, derived, gap_records)
    findings.extend(_validate_canonical_inference_use(decisions, derived, inferences))
    findings.extend(
        _validate_renderable_page_variants(
            renderable_page_variants,
            inventory,
            canonical_projection,
            closure_interaction_nodes,
        )
    )
    findings.extend(
        _validate_closure_element_coverage(
            inventory,
            gap_records,
            source_authority_refs,
            canonical_projection,
            closure_interaction_nodes,
            closure_clickable_inventory,
            closure_interaction_messages,
            closure_async_behavior,
            closure_failure_recovery,
            closure_overlay_closure,
            closure_handoff_behavior,
            closure_handoff_manifest,
        )
    )
    return findings


def compute_canonical_element_ids(
    inventory: Sequence[PrdElementInventoryItem],
    decisions: Sequence[PrdElementDecision],
    derived: Sequence[DerivedElementDecision],
    product_gaps: Sequence[Mapping[str, object]] = (),
) -> Set[str]:
    inventory_ids = {item.element_id for item in inventory}
    canonical = {
        decision.element_id
        for decision in decisions
        if decision.element_id in inventory_ids and decision.outcome in ADOPTED_OUTCOMES
    }
    canonical.update(
        decision.derived_element_id
        for decision in derived
        if decision.canonical_eligibility == CanonicalEligibility.ELIGIBLE
        and decision.derivation_strategy == DerivationStrategy.DEDUCTIVE_PRIMARY
        and not decision.blocked_by
    )
    del product_gaps
    return canonical


def validate_downstream_element_refs(
    element_refs: Iterable[str],
    canonical_element_ids: Iterable[str],
    *,
    blocked_element_ids: Iterable[str] = (),
) -> List[AdoptionFinding]:
    canonical = set(canonical_element_ids)
    blocked = set(blocked_element_ids)
    findings: List[AdoptionFinding] = []
    for element_ref in element_refs:
        if element_ref in blocked:
            findings.append(
                AdoptionFinding(
                    "REASON020",
                    element_ref,
                    "downstream element ref points to a blocked or projection-excluded element",
                )
            )
        elif element_ref not in canonical:
            findings.append(
                AdoptionFinding(
                    "REASON020",
                    element_ref,
                    "downstream element ref is not in the canonical element projection",
                )
            )
    return findings


def _validate_artifact_envelope(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
    validator_ref: str,
) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    missing = sorted(REQUIRED_ARTIFACT_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(
            AdoptionFinding("REASON012", artifact_id, "artifact envelope missing fields: " + ", ".join(missing))
        )
    if artifact.get("artifact_id") != artifact_id:
        findings.append(AdoptionFinding("REASON012", artifact_id, "artifact_id does not match contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(AdoptionFinding("REASON012", artifact_id, "schema_payload_key does not match contract"))
    if artifact.get("validator_ref") != validator_ref:
        findings.append(AdoptionFinding("REASON012", artifact_id, "validator_ref does not match contract"))
    upstream_refs = artifact.get("upstream_artifact_refs")
    upstream_hashes = artifact.get("upstream_hashes")
    invalidation_inputs = artifact.get("invalidation_inputs")
    if not _non_empty_text_list(upstream_refs):
        findings.append(AdoptionFinding("REASON012", artifact_id, "upstream_artifact_refs must be a non-empty text list"))
    if not isinstance(upstream_hashes, Mapping):
        findings.append(AdoptionFinding("REASON012", artifact_id, "upstream_hashes must be an object"))
    if not _non_empty_text_list(invalidation_inputs):
        findings.append(AdoptionFinding("REASON012", artifact_id, "invalidation_inputs must be a non-empty text list"))
    if _non_empty_text_list(upstream_refs) and isinstance(upstream_hashes, Mapping):
        ref_set = set(str(ref) for ref in upstream_refs)
        hash_keys = {str(key) for key in upstream_hashes}
        if ref_set != hash_keys:
            findings.append(AdoptionFinding("REASON012", artifact_id, "upstream_artifact_refs and upstream_hashes keys must match"))
        for ref in sorted(ref_set & hash_keys):
            if not _is_sha256(upstream_hashes.get(ref)):
                findings.append(AdoptionFinding("REASON012", artifact_id, "upstream_hashes values must be sha256"))
        if _non_empty_text_list(invalidation_inputs):
            input_paths = _text_values(invalidation_inputs)
            ref_list = _text_values(upstream_refs)
            if len(input_paths) != len(ref_list):
                findings.append(
                    AdoptionFinding(
                        "REASON012",
                        artifact_id,
                        "invalidation_inputs must align one-to-one with upstream_artifact_refs",
                    )
                )
            else:
                for ref, input_path in zip(ref_list, input_paths):
                    path = Path(input_path)
                    if not path.is_file():
                        findings.append(AdoptionFinding("REASON012", artifact_id, f"upstream input path is missing: {input_path}"))
                        continue
                    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    if upstream_hashes.get(ref) != actual_hash:
                        findings.append(AdoptionFinding("REASON012", artifact_id, f"upstream_hashes[{ref}] does not match {input_path}"))
    return findings


def _validate_records_payload(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
) -> List[AdoptionFinding]:
    payload = artifact.get(payload_key)
    if not isinstance(payload, list):
        return [AdoptionFinding("REASON012", artifact_id, f"{payload_key} payload must be a list")]
    findings = [
        AdoptionFinding("REASON012", artifact_id, f"{payload_key} payload rows must be objects")
        for row in payload
        if not isinstance(row, Mapping)
    ]
    findings.extend(_validate_schema_record_keys(artifact, artifact_id, payload))
    return findings


def _validate_schema_record_keys(
    artifact: Mapping[str, object],
    artifact_id: str,
    records: object,
) -> List[AdoptionFinding]:
    if not isinstance(records, list):
        return []
    schema_ref = artifact.get("schema_ref")
    if not isinstance(schema_ref, str) or not schema_ref:
        return [AdoptionFinding("REASON012", artifact_id, "schema_ref must be non-empty text")]
    schema_path = Path(schema_ref)
    if not schema_path.is_file():
        return [AdoptionFinding("REASON012", artifact_id, f"schema_ref path is missing: {schema_ref}")]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [AdoptionFinding("REASON012", artifact_id, f"schema_ref is invalid JSON: {exc}")]
    required = set(_text_values(schema.get("required", [])))
    properties = schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    findings: List[AdoptionFinding] = []
    for row in records:
        if not isinstance(row, Mapping):
            continue
        row_keys = {str(key) for key in row}
        missing = sorted(required - row_keys)
        extra = sorted(row_keys - allowed)
        row_id = _record_subject_id(row, artifact_id)
        if missing:
            findings.append(AdoptionFinding("REASON012", row_id, "record missing schema fields: " + ", ".join(missing)))
        if extra:
            findings.append(AdoptionFinding("REASON012", row_id, "record has off-schema fields: " + ", ".join(extra)))
    return findings


def _validate_semantic_source_model(inventory_artifact: Mapping[str, object]) -> List[AdoptionFinding]:
    model = inventory_artifact.get("semantic_source_model")
    if not isinstance(model, Mapping):
        return [
            AdoptionFinding(
                "REASON014",
                "p3.elements.prd_element_inventory",
                "semantic_source_model is required",
            )
        ]
    findings: List[AdoptionFinding] = []
    for key, expected in REQUIRED_SEMANTIC_SOURCE_MODEL.items():
        if model.get(key) != expected:
            findings.append(
                AdoptionFinding(
                    "REASON014",
                    "p3.elements.prd_element_inventory",
                    f"semantic_source_model.{key} must be {expected}",
                )
            )
    return findings


def _inventory_item_from_mapping(record: Mapping[str, object]) -> PrdElementInventoryItem:
    return PrdElementInventoryItem(
        element_id=str(record["element_id"]),
        element_type=ElementType(str(record["element_type"])),
        source_refs=_string_list(record["source_refs"]),
        source_text_hash=str(record["source_text_hash"]),
        stage_id=str(record["stage_id"]),
        artifact_id=str(record["artifact_id"]),
    )


def _decision_from_mapping(record: Mapping[str, object]) -> PrdElementDecision:
    return PrdElementDecision(
        element_id=str(record["element_id"]),
        source_refs=_string_list(record["source_refs"]),
        element_type=ElementType(str(record["element_type"])),
        outcome=AdoptionOutcome(str(record["outcome"])),
        normalized_label=_optional_string(record["normalized_label"]),
        blocking_reason=_optional_string(record["blocking_reason"]),
        input_obligations=_string_list(record["input_obligations"]),
        inference_refs=_string_list(record["inference_refs"]),
    )


def _derived_decision_from_mapping(record: Mapping[str, object]) -> DerivedElementDecision:
    return DerivedElementDecision(
        derived_element_id=str(record["derived_element_id"]),
        derived_surface_type=str(record["derived_surface_type"]),
        derivation_source=str(record["derivation_source"]),
        obligation_refs=_string_list(record["obligation_refs"]),
        inference_refs=_string_list(record["inference_refs"]),
        derivation_strategy=DerivationStrategy(str(record["derivation_strategy"])),
        structural_completion_review=_optional_string(record["structural_completion_review"]),
        canonical_eligibility=CanonicalEligibility(str(record["canonical_eligibility"])),
        blocked_by=_string_list(record["blocked_by"]),
    )


def _input_obligation_from_mapping(record: Mapping[str, object]) -> InputObligation:
    return InputObligation(
        obligation_id=str(record["obligation_id"]),
        required_input=str(record["required_input"]),
        task_ref=str(record["task_ref"]),
        acquisition_path=_optional_string(record["acquisition_path"]),
        gap_ref=_optional_string(record["gap_ref"]),
    )


def _validate_atomic_inventory(inventory: Sequence[PrdElementInventoryItem]) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    for item in inventory:
        closure_kinds = {_closure_ref_kind(ref) for ref in item.source_refs}
        closure_kinds.discard(None)
        if len(closure_kinds) > 1:
            findings.append(
                AdoptionFinding(
                    "REASON014",
                    item.element_id,
                    "inventory row bundles multiple closure semantic kinds: " + ", ".join(sorted(closure_kinds)),
                )
            )
    return findings


def _required_inference_ids(
    decisions: Sequence[PrdElementDecision],
    derived: Sequence[DerivedElementDecision],
) -> List[str]:
    required: List[str] = []
    for decision in decisions:
        required.extend(decision.inference_refs)
    for decision in derived:
        required.extend(decision.inference_refs)
    return required


def _validate_element_cross_references(
    decisions: Sequence[PrdElementDecision],
    derived: Sequence[DerivedElementDecision],
    obligations: Sequence[InputObligation],
    reviews: Sequence[object],
    product_gaps: Sequence[Mapping[str, object]],
    inferences: Sequence[object],
) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    obligation_ids = {obligation.obligation_id for obligation in obligations}
    review_ids = {review.review_id for review in reviews}
    gap_ids = {str(gap.get("gap_id")) for gap in product_gaps if gap.get("gap_id")}
    inference_ids = {inference.inference_id for inference in inferences}

    for decision in decisions:
        for obligation_id in decision.input_obligations:
            if obligation_id not in obligation_ids:
                findings.append(AdoptionFinding("REASON008", decision.element_id, "decision references unknown input obligation"))
        for inference_id in decision.inference_refs:
            if inference_id not in inference_ids:
                findings.append(AdoptionFinding("REASON007", decision.element_id, "decision references unknown inference"))

    for decision in derived:
        for obligation_id in decision.obligation_refs:
            if obligation_id not in obligation_ids:
                findings.append(AdoptionFinding("REASON008", decision.derived_element_id, "derived decision references unknown input obligation"))
        for inference_id in decision.inference_refs:
            if inference_id not in inference_ids:
                findings.append(AdoptionFinding("REASON007", decision.derived_element_id, "derived decision references unknown inference"))
        if decision.structural_completion_review and decision.structural_completion_review not in review_ids:
            findings.append(AdoptionFinding("REASON015", decision.derived_element_id, "derived decision references unknown structural review"))

    for obligation in obligations:
        if obligation.gap_ref and obligation.gap_ref not in gap_ids:
            findings.append(AdoptionFinding("REASON009", obligation.obligation_id, "input obligation references unknown product gap"))
    return findings


def _validate_canonical_inference_use(
    decisions: Sequence[PrdElementDecision],
    derived: Sequence[DerivedElementDecision],
    inferences: Sequence[object],
) -> List[AdoptionFinding]:
    findings: List[AdoptionFinding] = []
    by_id = {inference.inference_id: inference for inference in inferences}
    for decision in decisions:
        if decision.outcome not in ADOPTED_OUTCOMES:
            continue
        for inference_id in decision.inference_refs:
            inference = by_id.get(inference_id)
            if inference is None:
                continue
            try:
                require_canonical_consumption_allowed(inference)
            except ValueError as exc:
                findings.append(AdoptionFinding("REASON002", decision.element_id, str(exc)))

    for decision in derived:
        if decision.canonical_eligibility != CanonicalEligibility.ELIGIBLE:
            continue
        if decision.derivation_strategy != DerivationStrategy.DEDUCTIVE_PRIMARY or decision.blocked_by:
            findings.append(
                AdoptionFinding(
                    "REASON004",
                    decision.derived_element_id,
                    "canonical derived element must be DEDUCTIVE_PRIMARY and unblocked",
                )
            )
        for inference_id in decision.inference_refs:
            inference = by_id.get(inference_id)
            if inference is None:
                continue
            try:
                require_canonical_consumption_allowed(inference)
            except ValueError as exc:
                findings.append(AdoptionFinding("REASON002", decision.derived_element_id, str(exc)))
    return findings


def _validate_renderable_page_variants(
    renderable_page_variants: Mapping[str, object],
    inventory: Sequence[PrdElementInventoryItem],
    canonical_projection: Set[str],
    closure_interaction_nodes: Mapping[str, object],
) -> List[AdoptionFinding]:
    canonical_pages = {
        item.element_id
        for item in inventory
        if item.element_type == ElementType.PAGE and item.element_id in canonical_projection
    }
    canonical_states = {
        item.element_id
        for item in inventory
        if item.element_type == ElementType.STATE and item.element_id in canonical_projection
    }
    canonical_elements = set(canonical_projection)
    findings: List[AdoptionFinding] = []
    seen_variant_ids: Set[str] = set()
    base_pages: Set[str] = set()
    rendered_states: Set[str] = set()
    seen_frame_order_indexes: Dict[int, str] = {}
    seen_variant_order_slots: Dict[tuple, str] = {}
    expected_parent_page_by_state = _expected_parent_page_by_state(inventory, closure_interaction_nodes)

    for record in _payload_records(renderable_page_variants):
        variant_id = str(record.get("variant_page_id", ""))
        parent_page_id = str(record.get("parent_page_id", ""))
        variant_kind = str(record.get("variant_kind", ""))
        source_state_id = _optional_string(record.get("source_state_id"))
        module_id = str(record.get("module_id", ""))
        function_group_id = str(record.get("function_group_id", ""))
        derivation_origin = str(record.get("derivation_origin", ""))
        subject_id = variant_id or "p3.elements.renderable_page_variants"

        if not variant_id:
            findings.append(AdoptionFinding("REASON021", subject_id, "variant_page_id is required"))
            continue
        if variant_id in seen_variant_ids:
            findings.append(AdoptionFinding("REASON021", variant_id, "variant_page_id must be unique"))
        seen_variant_ids.add(variant_id)

        if parent_page_id not in canonical_pages:
            findings.append(AdoptionFinding("REASON021", variant_id, "parent_page_id must resolve to a canonical PAGE"))
        if str(record.get("render_surface_id", "")) != variant_id:
            findings.append(AdoptionFinding("REASON021", variant_id, "render_surface_id must equal variant_page_id"))
        if record.get("figma_frame_required") is not True:
            findings.append(AdoptionFinding("REASON021", variant_id, "figma_frame_required must be true"))
        if record.get("product_capability_addition") is not False:
            findings.append(AdoptionFinding("REASON021", variant_id, "renderable page variants cannot add product capability"))
        if not str(record.get("state_condition", "")).strip():
            findings.append(AdoptionFinding("REASON021", variant_id, "state_condition is required"))
        if not module_id:
            findings.append(AdoptionFinding("REASON021", variant_id, "module_id is required for module/function page ordering"))
        if not function_group_id:
            findings.append(AdoptionFinding("REASON021", variant_id, "function_group_id is required for module/function page ordering"))
        for order_field in RENDERABLE_ORDER_FIELDS:
            value = record.get(order_field)
            if not isinstance(value, int) or value < 0:
                findings.append(AdoptionFinding("REASON021", variant_id, f"{order_field} must be a non-negative integer"))
        frame_order = record.get("figma_frame_order_index")
        if isinstance(frame_order, int) and frame_order >= 0:
            if frame_order in seen_frame_order_indexes:
                findings.append(
                    AdoptionFinding(
                        "REASON021",
                        variant_id,
                        "figma_frame_order_index must be unique; duplicates " + seen_frame_order_indexes[frame_order],
                    )
                )
            seen_frame_order_indexes.setdefault(frame_order, variant_id)
        variant_order_slot = (
            record.get("module_id"),
            record.get("function_group_id"),
            record.get("page_order_index"),
            record.get("variant_order_index"),
        )
        if all(value not in (None, "") for value in variant_order_slot):
            if variant_order_slot in seen_variant_order_slots:
                findings.append(
                    AdoptionFinding(
                        "REASON021",
                        variant_id,
                        "variant order slot must be unique within module/function/page; duplicates "
                        + seen_variant_order_slots[variant_order_slot],
                    )
                )
            seen_variant_order_slots.setdefault(variant_order_slot, variant_id)
        if derivation_origin not in RENDERABLE_DERIVATION_ORIGINS:
            findings.append(AdoptionFinding("REASON021", variant_id, "derivation_origin must declare explicit or inferred origin"))
        if not _text_values(record.get("derivation_basis_refs")):
            findings.append(AdoptionFinding("REASON021", variant_id, "derivation_basis_refs must bind source or inference basis"))
        requires_review = record.get("requires_human_review")
        if not isinstance(requires_review, bool):
            findings.append(AdoptionFinding("REASON021", variant_id, "requires_human_review must be boolean"))
        elif derivation_origin == "REVIEW_REQUIRED_INFERENCE" and requires_review is not True:
            findings.append(AdoptionFinding("REASON021", variant_id, "review-required inference must require human review"))
        elif derivation_origin in {"PRD_EXPLICIT", "DEDUCTIVE_REQUIRED", "HUMAN_APPROVED_INFERENCE"} and requires_review is not False:
            findings.append(AdoptionFinding("REASON021", variant_id, "approved or explicit variant must not remain human-review required"))

        unresolved_refs = sorted(
            set(_text_values(record.get("shared_element_refs")) + _text_values(record.get("variant_element_refs")))
            - canonical_elements
        )
        for element_ref in unresolved_refs:
            findings.append(AdoptionFinding("REASON020", element_ref, "renderable page variant ref is not canonical"))

        if variant_kind == "BASE":
            if source_state_id is not None:
                findings.append(AdoptionFinding("REASON021", variant_id, "BASE variant must not bind source_state_id"))
            if parent_page_id and variant_id != parent_page_id:
                findings.append(AdoptionFinding("REASON021", variant_id, "BASE variant must use the parent page id"))
            base_pages.add(parent_page_id)
        elif variant_kind == "STATE_VARIANT":
            if not source_state_id or source_state_id not in canonical_states:
                findings.append(
                    AdoptionFinding("REASON021", variant_id, "STATE_VARIANT source_state_id must resolve to a canonical STATE")
                )
            else:
                rendered_states.add(source_state_id)
                expected_parent_page_id = expected_parent_page_by_state.get(source_state_id)
                if expected_parent_page_id and parent_page_id != expected_parent_page_id:
                    findings.append(
                        AdoptionFinding(
                            "REASON021",
                            variant_id,
                            "STATE_VARIANT parent_page_id does not match closure state parent page",
                        )
                    )
            if variant_id == parent_page_id:
                findings.append(AdoptionFinding("REASON021", variant_id, "STATE_VARIANT must use a distinct page variant id"))
        else:
            findings.append(AdoptionFinding("REASON021", variant_id, "variant_kind must be BASE or STATE_VARIANT"))

    for page_id in sorted(canonical_pages - base_pages):
        findings.append(AdoptionFinding("REASON021", page_id, "canonical PAGE lacks a BASE renderable page variant"))
    for state_id in sorted(canonical_states - rendered_states):
        findings.append(AdoptionFinding("REASON021", state_id, "canonical STATE lacks a STATE_VARIANT renderable page variant"))
    return findings


def _expected_parent_page_by_state(
    inventory: Sequence[PrdElementInventoryItem],
    closure_interaction_nodes: Mapping[str, object],
) -> Dict[str, str]:
    page_by_node_id: Dict[str, str] = {}
    state_source_refs_by_element_id: Dict[str, Set[str]] = {}
    for item in inventory:
        if item.element_type == ElementType.PAGE:
            for source_ref in item.source_refs:
                page_by_node_id[source_ref] = item.element_id
        elif item.element_type == ElementType.STATE:
            state_source_refs_by_element_id[item.element_id] = set(item.source_refs)

    closure_node_by_id = {
        str(record.get("node_id")): record
        for record in _payload_records(closure_interaction_nodes)
        if record.get("node_id")
    }
    expected: Dict[str, str] = {}
    for state_element_id, source_refs in state_source_refs_by_element_id.items():
        for source_ref in source_refs:
            closure_node = closure_node_by_id.get(source_ref)
            if not isinstance(closure_node, Mapping):
                continue
            resume_source = closure_node.get("resume_source")
            if isinstance(resume_source, str) and resume_source in page_by_node_id:
                expected[state_element_id] = page_by_node_id[resume_source]
                break
    return expected


def _validate_closure_element_coverage(
    inventory: Sequence[PrdElementInventoryItem],
    product_gaps: Sequence[Mapping[str, object]],
    source_authority_refs: Set[str],
    canonical_projection: Set[str],
    closure_interaction_nodes: Mapping[str, object],
    closure_clickable_inventory: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
    closure_async_behavior: Mapping[str, object],
    closure_failure_recovery: Mapping[str, object],
    closure_overlay_closure: Mapping[str, object],
    closure_handoff_behavior: Mapping[str, object],
    closure_handoff_manifest: Mapping[str, object],
) -> List[AdoptionFinding]:
    required_units = {}
    for record in _payload_records(closure_interaction_nodes):
        unit_id = str(record.get("node_id", ""))
        if unit_id:
            required_units[unit_id] = NODE_ELEMENT_TYPES.get(str(record.get("node_type", "")), {ElementType.UI_ELEMENT})
    for record in _payload_records(closure_clickable_inventory):
        unit_id = str(record.get("clickable_id", ""))
        if unit_id:
            required_units[unit_id] = CLICKABLE_ELEMENT_TYPES
    for record in _payload_records(closure_interaction_messages):
        unit_id = str(record.get("message_id", ""))
        if unit_id:
            required_units[unit_id] = MESSAGE_ELEMENT_TYPES
    for record in _payload_records(closure_async_behavior):
        unit_id = _first_text(record, ("message_id", "async_id", "reaction_id"))
        if unit_id:
            required_units[unit_id] = MESSAGE_ELEMENT_TYPES
    for record in _payload_records(closure_failure_recovery):
        unit_id = _first_text(record, ("recovery_id", "reaction_id", "failure_id"))
        if unit_id:
            required_units[unit_id] = RECOVERY_ELEMENT_TYPES
    for record in _payload_records(closure_overlay_closure):
        unit_id = str(record.get("overlay_node_id", ""))
        if unit_id:
            required_units[unit_id] = {ElementType.UI_ELEMENT}
    for record in _payload_records(closure_handoff_behavior):
        unit_id = _first_text(record, ("handoff_id", "reaction_id"))
        if unit_id:
            required_units[unit_id] = {ElementType.UI_ELEMENT}

    blocked_refs = _blocked_refs(product_gaps, closure_handoff_manifest)
    canonical_inventory = {
        item.element_id: item
        for item in inventory
        if item.element_id in canonical_projection
    }
    source_ref_index: Dict[str, List[PrdElementInventoryItem]] = {}
    for item in canonical_inventory.values():
        for source_ref in item.source_refs:
            source_ref_index.setdefault(source_ref, []).append(item)

    findings: List[AdoptionFinding] = []
    for unit_id, allowed_types in sorted(required_units.items()):
        mapped_items = source_ref_index.get(unit_id, [])
        if not mapped_items:
            if unit_id not in blocked_refs:
                findings.append(
                    AdoptionFinding(
                        "REASON018",
                        unit_id,
                        "eligible closure unit is not mapped to a canonical element or blocked gap",
                    )
                )
            continue
        for item in mapped_items:
            if item.element_type not in allowed_types:
                findings.append(
                    AdoptionFinding(
                        "REASON019",
                        item.element_id,
                        f"closure unit {unit_id} maps to incompatible element_type {item.element_type.value}",
                    )
                )

    open_gap_ids = {
        str(gap.get("gap_id"))
        for gap in product_gaps
        if gap.get("status") in NON_CANONICAL_GAP_STATUSES and gap.get("gap_id")
    }
    for item in canonical_inventory.values():
        resolved_source_refs = set(item.source_refs) & (set(required_units) | blocked_refs | source_authority_refs)
        if not resolved_source_refs:
            findings.append(
                AdoptionFinding(
                    "REASON018",
                    item.element_id,
                    "canonical element lacks a source_ref from approved closure, distill authority, or blocked gap",
                )
            )
        for source_ref in item.source_refs:
            if _closure_ref_kind(source_ref) and source_ref not in required_units and source_ref not in blocked_refs:
                findings.append(
                    AdoptionFinding(
                        "REASON018",
                        item.element_id,
                        f"canonical element source_ref {source_ref} is not an approved closure unit or blocked gap",
                    )
                )
        if set(item.source_refs) & open_gap_ids:
            findings.append(
                AdoptionFinding(
                    "REASON009",
                    item.element_id,
                    "canonical element cannot use an open, rejected, or superseded product gap as source authority",
                )
            )
    return findings


def _load_upstream_authority_refs(
    artifact: Mapping[str, object],
) -> tuple[Set[str], List[AdoptionFinding]]:
    refs: Set[str] = set()
    findings: List[AdoptionFinding] = []
    for input_path in _text_values(artifact.get("invalidation_inputs", [])):
        path = Path(input_path)
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(AdoptionFinding("REASON012", input_path, f"authority input is invalid JSON: {exc}"))
            continue
        for record in _payload_records(payload):
            for key in ("element_id", "gap_id"):
                value = record.get(key)
                if isinstance(value, str) and value.strip():
                    refs.add(value)
            refs.update(_text_values(record.get("source_unit_refs", [])))
    return refs, findings


def _record_subject_id(record: Mapping[str, object], fallback: str) -> str:
    for key in (
        "element_id",
        "variant_page_id",
        "derived_element_id",
        "inference_id",
        "obligation_id",
        "review_id",
        "gap_id",
    ):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _blocked_refs(
    product_gaps: Sequence[Mapping[str, object]],
    closure_handoff_manifest: Mapping[str, object],
) -> Set[str]:
    refs: Set[str] = set()
    for record in _payload_records(closure_handoff_manifest):
        refs.update(_text_values(record.get("blocked_graph_units", [])))
        refs.update(_text_values(record.get("review_blockers", [])))
    for gap in product_gaps:
        if gap.get("status") in NON_CANONICAL_GAP_STATUSES:
            refs.add(str(gap.get("gap_id", "")))
            refs.update(_text_values(gap.get("source_refs", [])))
            refs.update(_text_values(gap.get("blocked_artifacts", [])))
    refs.discard("")
    return refs


def _payload_records(artifact: Mapping[str, object], payload_key: str = "records") -> List[Mapping[str, object]]:
    records = artifact.get(payload_key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _convert_reasoning_findings(findings) -> List[AdoptionFinding]:
    return [
        AdoptionFinding(code=finding.code, subject_id=finding.subject_id, message=finding.message)
        for finding in findings
    ]


def _non_empty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        raise ValueError("expected list")
    return [str(item) for item in value]


def _optional_string(value: object) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _text_values(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _first_text(record: Mapping[str, object], keys: Sequence[str]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _closure_ref_kind(source_ref: str) -> Optional[str]:
    prefixes = {
        "p3-node-": "node",
        "p3-msg-": "message",
        "p3-clickable-": "clickable",
        "p3-reaction-": "reaction",
        "p3-async-": "async",
        "p3-failure-": "failure",
        "p3-handoff-": "handoff",
        "p3-overlay-": "overlay",
    }
    for prefix, kind in prefixes.items():
        if source_ref.startswith(prefix):
            return kind
    return None


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )
