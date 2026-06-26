"""P3 shared component and information presentation artifact-set validators."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set

from drd_harness.rules.presentation import PatternKind
from drd_harness.validators.presentation_consistency import (
    PresentationFinding,
    information_presentation_decision_from_mapping,
    presentation_exception_from_mapping,
    shared_component_pattern_from_mapping,
    validate_information_presentation_decision,
    validate_interaction_message_presentation_mapping,
    validate_presentation_consistency,
    validate_shared_component_registry,
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

P3_PATTERNS_VALIDATOR_REF = "repository/src/drd_harness/validators/p3_patterns.py"
PRESENTATION_VALIDATOR_REF = "repository/src/drd_harness/validators/presentation_consistency.py"

P3_PATTERNS_ARTIFACTS = {
    "shared_component_registry": (
        "p3.patterns.shared_component_registry",
        "registry",
        "patterns",
    ),
    "information_presentation_registry": (
        "p3.patterns.information_presentation_registry",
        "registry",
        "decisions",
    ),
    "presentation_consistency_exceptions": (
        "p3.patterns.presentation_consistency_exceptions",
        "records",
        None,
    ),
}

P3_PATTERNS_SCHEMA_CONTRACTS = {
    "p3.patterns.shared_component_registry": (
        "repository/schemas/presentation/shared_component_registry.schema.json",
        "ba27b28986941dcaa4263de2831049c82b9811e9146d38cd517104a3ab3a1b73",
    ),
    "p3.patterns.information_presentation_registry": (
        "repository/schemas/presentation/information_presentation_registry.schema.json",
        "65d2320b6095ec214cad160b7bba521ed1d8bc39a88b2aa0bbed246d523b3149",
    ),
    "p3.patterns.presentation_consistency_exceptions": (
        "repository/schemas/presentation/presentation_consistency_exception.schema.json",
        "418012bacb3492952edaa92474475fd2df10508926fbbf86ea6c6b16e8184f9e",
    ),
}

LAYOUT_BOUNDARY_TERMS = {
    "carrier",
    "breakpoint",
    "scroll",
    "width",
    "height",
    "ordering",
    "z-axis",
    "z axis",
    "containment",
    "placement",
}


def validate_pattern_artifacts(
    *,
    shared_component_registry: Mapping[str, object],
    information_presentation_registry: Mapping[str, object],
    presentation_consistency_exceptions: Mapping[str, object],
    element_inventory: Mapping[str, object],
    element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
    product_expansion_gaps: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
) -> List[PresentationFinding]:
    artifacts = {
        "shared_component_registry": shared_component_registry,
        "information_presentation_registry": information_presentation_registry,
        "presentation_consistency_exceptions": presentation_consistency_exceptions,
    }
    findings: List[PresentationFinding] = []
    for name, artifact in artifacts.items():
        artifact_id, payload_key, record_key = P3_PATTERNS_ARTIFACTS[name]
        findings.extend(_validate_artifact_envelope(artifact, artifact_id, payload_key))
        findings.extend(_validate_payload_shape(artifact, artifact_id, payload_key, record_key))

    try:
        patterns = [
            shared_component_pattern_from_mapping(record)
            for record in _registry_records(shared_component_registry, "patterns")
        ]
        decisions = [
            information_presentation_decision_from_mapping(record)
            for record in _registry_records(information_presentation_registry, "decisions")
        ]
        exceptions = [
            presentation_exception_from_mapping(record)
            for record in _payload_records(presentation_consistency_exceptions)
        ]
    except (KeyError, ValueError) as exc:
        findings.append(PresentationFinding("PL000", "p3.patterns", str(exc)))
        return findings

    findings.extend(validate_shared_component_registry(patterns))
    for decision in decisions:
        findings.extend(validate_information_presentation_decision(decision))
    findings.extend(validate_presentation_consistency(decisions, exceptions))

    canonical_element_ids = _canonical_element_ids(element_inventory, element_decisions, derived_element_decisions)
    blocked_element_ids = _blocked_element_ids(element_decisions, derived_element_decisions, product_expansion_gaps)
    message_ids = _message_ids(closure_interaction_messages)
    exception_ids = {exception.exception_id for exception in exceptions}
    required_information_element_ids = _required_information_element_ids(
        element_inventory,
        element_decisions,
        derived_element_decisions,
    )
    traceable_ref_ids = _traceable_ref_ids(
        element_inventory,
        element_decisions,
        derived_element_decisions,
        product_expansion_gaps,
        closure_interaction_messages,
    )

    findings.extend(_validate_pattern_resolution(patterns, canonical_element_ids, message_ids, exception_ids, blocked_element_ids))
    findings.extend(_validate_layout_boundary(patterns))
    findings.extend(validate_interaction_message_presentation_mapping(message_ids, decisions))
    findings.extend(_validate_decision_message_refs(decisions, message_ids))
    findings.extend(_validate_information_subject_coverage(decisions, required_information_element_ids))
    findings.extend(_validate_exception_mode_coverage(decisions, exceptions))
    findings.extend(_validate_trace_refs(patterns, decisions, exceptions, traceable_ref_ids))
    return findings


def validate_downstream_pattern_refs(
    pattern_refs: Iterable[str],
    shared_component_registry: Mapping[str, object],
) -> List[PresentationFinding]:
    pattern_ids = {
        str(record.get("pattern_id"))
        for record in _registry_records(shared_component_registry, "patterns")
        if record.get("pattern_id")
    }
    findings: List[PresentationFinding] = []
    for pattern_ref in sorted(set(pattern_refs) - pattern_ids):
        findings.append(
            PresentationFinding(
                code="PL001",
                subject_id=pattern_ref,
                message="downstream pattern_ref does not resolve to shared component registry",
            )
        )
    return findings


def _validate_artifact_envelope(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    missing = sorted(REQUIRED_ARTIFACT_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(PresentationFinding("PL010", artifact_id, "artifact envelope missing fields: " + ", ".join(missing)))
    if artifact.get("artifact_id") != artifact_id:
        findings.append(PresentationFinding("PL010", artifact_id, "artifact_id does not match contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(PresentationFinding("PL010", artifact_id, "schema_payload_key does not match contract"))
    schema_ref = artifact.get("schema_ref")
    schema_contract = P3_PATTERNS_SCHEMA_CONTRACTS.get(artifact_id)
    if schema_contract is not None:
        expected_schema_ref, expected_schema_hash = schema_contract
        if schema_ref != expected_schema_ref:
            findings.append(PresentationFinding("PL010", artifact_id, "schema_ref does not match contract"))
        else:
            schema_path = Path(expected_schema_ref)
            if not schema_path.is_file():
                findings.append(PresentationFinding("PL010", artifact_id, f"schema_ref path is missing: {expected_schema_ref}"))
            else:
                schema_hash = hashlib.sha256(schema_path.read_bytes()).hexdigest()
                if schema_hash != expected_schema_hash:
                    findings.append(PresentationFinding("PL010", artifact_id, "schema_ref hash does not match contract"))
    if artifact.get("validator_ref") not in {P3_PATTERNS_VALIDATOR_REF, PRESENTATION_VALIDATOR_REF}:
        findings.append(PresentationFinding("PL010", artifact_id, "validator_ref does not match pattern validator contract"))
    source_refs = artifact.get("source_refs")
    upstream_refs = artifact.get("upstream_artifact_refs")
    upstream_hashes = artifact.get("upstream_hashes")
    invalidation_inputs = artifact.get("invalidation_inputs")
    if not _non_empty_text_list(source_refs):
        findings.append(PresentationFinding("PL010", artifact_id, "source_refs must be a non-empty text list"))
    if not _non_empty_text_list(upstream_refs):
        findings.append(PresentationFinding("PL010", artifact_id, "upstream_artifact_refs must be a non-empty text list"))
    if not isinstance(upstream_hashes, Mapping):
        findings.append(PresentationFinding("PL010", artifact_id, "upstream_hashes must be an object"))
    if not _non_empty_text_list(invalidation_inputs):
        findings.append(PresentationFinding("PL010", artifact_id, "invalidation_inputs must be a non-empty text list"))
    if _non_empty_text_list(source_refs) and _non_empty_text_list(invalidation_inputs):
        source_ref_set = set(_text_values(source_refs))
        invalidation_set = set(_text_values(invalidation_inputs))
        if source_ref_set != invalidation_set:
            findings.append(PresentationFinding("PL010", artifact_id, "source_refs must match invalidation_inputs for replayable provenance"))
    if _non_empty_text_list(upstream_refs) and isinstance(upstream_hashes, Mapping):
        ref_set = set(_text_values(upstream_refs))
        hash_keys = {str(key) for key in upstream_hashes}
        if ref_set != hash_keys:
            findings.append(PresentationFinding("PL010", artifact_id, "upstream_artifact_refs and upstream_hashes keys must match"))
        for ref in sorted(ref_set & hash_keys):
            if not _is_sha256(upstream_hashes.get(ref)):
                findings.append(PresentationFinding("PL010", artifact_id, "upstream_hashes values must be sha256"))
        if _non_empty_text_list(invalidation_inputs):
            input_paths = _text_values(invalidation_inputs)
            ref_list = _text_values(upstream_refs)
            if len(input_paths) != len(ref_list):
                findings.append(PresentationFinding("PL010", artifact_id, "invalidation_inputs must align one-to-one with upstream_artifact_refs"))
            else:
                for ref, input_path in zip(ref_list, input_paths):
                    path = Path(input_path)
                    if not path.is_file():
                        findings.append(PresentationFinding("PL010", artifact_id, f"upstream input path is missing: {input_path}"))
                        continue
                    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    if upstream_hashes.get(ref) != actual_hash:
                        findings.append(PresentationFinding("PL010", artifact_id, f"upstream_hashes[{ref}] does not match {input_path}"))
    return findings


def _validate_payload_shape(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
    record_key: object,
) -> List[PresentationFinding]:
    payload = artifact.get(payload_key)
    if payload_key == "registry":
        if not isinstance(payload, Mapping):
            return [PresentationFinding("PL010", artifact_id, "registry payload must be an object")]
        findings = _validate_schema_keys(artifact, artifact_id, payload, nested_record_key=str(record_key))
        records = payload.get(str(record_key))
        if not isinstance(records, list):
            findings.append(PresentationFinding("PL010", artifact_id, f"registry.{record_key} must be a list"))
        else:
            findings.extend(_validate_record_rows(artifact, artifact_id, records, nested_record_key=str(record_key)))
        return findings
    if not isinstance(payload, list):
        return [PresentationFinding("PL010", artifact_id, "records payload must be a list")]
    return _validate_record_rows(artifact, artifact_id, payload)


def _validate_schema_keys(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload: Mapping[str, object],
    *,
    nested_record_key: str = "",
) -> List[PresentationFinding]:
    schema = _load_schema(artifact, artifact_id)
    if isinstance(schema, PresentationFinding):
        return [schema]
    required = set(_text_values(schema.get("required", [])))
    properties = schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    payload_keys = {str(key) for key in payload}
    findings: List[PresentationFinding] = []
    missing = sorted(required - payload_keys)
    extra = sorted(payload_keys - allowed)
    if missing:
        findings.append(PresentationFinding("PL010", artifact_id, "payload missing schema fields: " + ", ".join(missing)))
    if extra:
        findings.append(PresentationFinding("PL010", artifact_id, "payload has off-schema fields: " + ", ".join(extra)))
    if nested_record_key:
        record_schema = _record_schema(schema, nested_record_key)
        if record_schema is None:
            findings.append(PresentationFinding("PL010", artifact_id, f"schema lacks registry record key: {nested_record_key}"))
    return findings


def _validate_record_rows(
    artifact: Mapping[str, object],
    artifact_id: str,
    records: object,
    *,
    nested_record_key: str = "",
) -> List[PresentationFinding]:
    if not isinstance(records, list):
        return [PresentationFinding("PL010", artifact_id, "records payload must be a list")]
    schema = _load_schema(artifact, artifact_id)
    if isinstance(schema, PresentationFinding):
        return [schema]
    record_schema = _record_schema(schema, nested_record_key)
    if record_schema is None:
        record_schema = schema
    required = set(_text_values(record_schema.get("required", [])))
    properties = record_schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    findings: List[PresentationFinding] = []
    for row in records:
        if not isinstance(row, Mapping):
            findings.append(PresentationFinding("PL010", artifact_id, "record rows must be objects"))
            continue
        row_keys = {str(key) for key in row}
        missing = sorted(required - row_keys)
        extra = sorted(row_keys - allowed)
        subject_id = _record_subject_id(row, artifact_id)
        if missing:
            findings.append(PresentationFinding("PL010", subject_id, "record missing schema fields: " + ", ".join(missing)))
        if extra:
            findings.append(PresentationFinding("PL010", subject_id, "record has off-schema fields: " + ", ".join(extra)))
    return findings


def _validate_pattern_resolution(
    patterns: Sequence[object],
    canonical_element_ids: Set[str],
    message_ids: Set[str],
    exception_ids: Set[str],
    blocked_element_ids: Set[str],
) -> List[PresentationFinding]:
    allowed = canonical_element_ids | message_ids | exception_ids
    findings: List[PresentationFinding] = []
    for pattern in patterns:
        for ref in pattern.reuse_scope:
            if ref in blocked_element_ids:
                findings.append(PresentationFinding("PL006", pattern.pattern_id, f"reuse_scope references blocked element: {ref}"))
            elif ref not in allowed:
                findings.append(PresentationFinding("PL006", pattern.pattern_id, f"reuse_scope reference is not canonical or approved: {ref}"))
    return findings


def _validate_layout_boundary(patterns: Sequence[object]) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    for pattern in patterns:
        if pattern.pattern_kind != PatternKind.LAYOUT_PATTERN:
            continue
        text = " ".join(
            [
                pattern.semantic_role,
                " ".join(pattern.surface_constraints),
                " ".join(pattern.interaction_model),
                " ".join(pattern.reuse_scope),
                pattern.reuse_reason or "",
                pattern.non_reuse_reason or "",
            ]
        ).lower()
        matched_terms = sorted(term for term in LAYOUT_BOUNDARY_TERMS if term in text)
        if matched_terms:
            findings.append(
                PresentationFinding(
                    "PL007",
                    pattern.pattern_id,
                    "layout pattern crosses into P3 layout boundary: " + ", ".join(matched_terms),
                )
            )
    return findings


def _validate_decision_message_refs(
    decisions: Sequence[object],
    message_ids: Set[str],
) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    for decision in decisions:
        if decision.message_ref and decision.message_ref not in message_ids:
            findings.append(PresentationFinding("PL005", decision.presentation_id, "presentation decision references unknown message_ref"))
    return findings


def _validate_information_subject_coverage(
    decisions: Sequence[object],
    required_element_ids: Set[str],
) -> List[PresentationFinding]:
    covered_element_ids = {
        ref
        for decision in decisions
        for ref in decision.trace_refs
        if ref in required_element_ids
    }
    findings: List[PresentationFinding] = []
    for element_id in sorted(required_element_ids - covered_element_ids):
        findings.append(PresentationFinding("PL005", element_id, "canonical information element lacks presentation decision"))
    return findings


def _validate_exception_mode_coverage(
    decisions: Sequence[object],
    exceptions: Sequence[object],
) -> List[PresentationFinding]:
    used_modes: Dict[object, Set[str]] = {}
    for decision in decisions:
        used_modes.setdefault(decision.consistency_key(), set()).add(decision.presentation_mode.value)
    allowed_modes = {
        exception.consistency_key(): {mode.value for mode in exception.allowed_modes}
        for exception in exceptions
    }
    findings: List[PresentationFinding] = []
    for key, modes in used_modes.items():
        if len(modes) <= 1:
            continue
        if key in allowed_modes and not modes <= allowed_modes[key]:
            findings.append(
                PresentationFinding(
                    "PL003",
                    "presentation_consistency_exception",
                    "exception allowed_modes do not cover all used presentation modes",
                )
            )
    return findings


def _validate_trace_refs(
    patterns: Sequence[object],
    decisions: Sequence[object],
    exceptions: Sequence[object],
    traceable_ref_ids: Set[str],
) -> List[PresentationFinding]:
    findings: List[PresentationFinding] = []
    traced_objects = [
        (pattern.pattern_id, pattern.trace_refs)
        for pattern in patterns
    ]
    traced_objects.extend(
        (decision.presentation_id, decision.trace_refs)
        for decision in decisions
    )
    traced_objects.extend(
        (exception.exception_id, exception.trace_refs)
        for exception in exceptions
    )
    for subject_id, trace_refs in traced_objects:
        for trace_ref in trace_refs:
            if trace_ref not in traceable_ref_ids:
                findings.append(PresentationFinding("PL008", subject_id, f"trace_ref does not resolve to upstream authority: {trace_ref}"))
    return findings


def _canonical_element_ids(
    element_inventory: Mapping[str, object],
    element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
) -> Set[str]:
    inventory_ids = {
        str(record.get("element_id"))
        for record in _payload_records(element_inventory)
        if record.get("element_id")
    }
    canonical = {
        str(record.get("element_id"))
        for record in _payload_records(element_decisions)
        if record.get("element_id") in inventory_ids
        and record.get("outcome") in {"ADOPT_AS_IS", "ADOPT_NORMALIZED"}
    }
    canonical.update(
        str(record.get("derived_element_id"))
        for record in _payload_records(derived_element_decisions)
        if record.get("canonical_eligibility") == "ELIGIBLE"
        and record.get("derivation_strategy") == "DEDUCTIVE_PRIMARY"
        and record.get("blocked_by") == []
    )
    return canonical


def _required_information_element_ids(
    element_inventory: Mapping[str, object],
    element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
) -> Set[str]:
    canonical = _canonical_element_ids(element_inventory, element_decisions, derived_element_decisions)
    return {
        str(record.get("element_id"))
        for record in _payload_records(element_inventory)
        if record.get("element_id") in canonical
        and record.get("element_type") in {"STATE", "MESSAGE"}
    }


def _blocked_element_ids(
    element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
    product_expansion_gaps: Mapping[str, object],
) -> Set[str]:
    blocked = {
        str(record.get("element_id"))
        for record in _payload_records(element_decisions)
        if record.get("outcome") in {"REQUEST_CLARIFICATION", "REJECT_CONFLICT", "ROUTE_PRODUCT_GAP"}
    }
    blocked.update(
        str(record.get("derived_element_id"))
        for record in _payload_records(derived_element_decisions)
        if record.get("canonical_eligibility") != "ELIGIBLE" or record.get("blocked_by")
    )
    for gap in _payload_records(product_expansion_gaps):
        if gap.get("status") in {"OPEN", "RESOLVED_REJECTED", "SUPERSEDED"}:
            blocked.add(str(gap.get("gap_id")))
    blocked.discard("")
    return blocked


def _message_ids(closure_interaction_messages: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("message_id"))
        for record in _payload_records(closure_interaction_messages)
        if record.get("message_id")
    }


def _traceable_ref_ids(
    element_inventory: Mapping[str, object],
    element_decisions: Mapping[str, object],
    derived_element_decisions: Mapping[str, object],
    product_expansion_gaps: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
) -> Set[str]:
    refs: Set[str] = set()
    for artifact in (
        element_inventory,
        element_decisions,
        derived_element_decisions,
        product_expansion_gaps,
        closure_interaction_messages,
    ):
        for record in _payload_records(artifact):
            for key in (
                "element_id",
                "derived_element_id",
                "gap_id",
                "message_id",
                "node_id",
                "reaction_id",
                "obligation_id",
            ):
                value = record.get(key)
                if isinstance(value, str) and value.strip():
                    refs.add(value)
            for list_key in (
                "source_refs",
                "trace_refs",
                "inference_refs",
                "input_obligations",
                "recovery_targets",
            ):
                refs.update(_text_values(record.get(list_key)))
    return refs


def _registry_records(artifact: Mapping[str, object], record_key: str) -> List[Mapping[str, object]]:
    registry = artifact.get("registry", {})
    if not isinstance(registry, Mapping):
        return []
    records = registry.get(record_key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _payload_records(artifact: Mapping[str, object], payload_key: str = "records") -> List[Mapping[str, object]]:
    records = artifact.get(payload_key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _load_schema(artifact: Mapping[str, object], artifact_id: str):
    schema_ref = artifact.get("schema_ref")
    if not isinstance(schema_ref, str) or not schema_ref:
        return PresentationFinding("PL010", artifact_id, "schema_ref must be non-empty text")
    schema_path = Path(schema_ref)
    if not schema_path.is_file():
        return PresentationFinding("PL010", artifact_id, f"schema_ref path is missing: {schema_ref}")
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return PresentationFinding("PL010", artifact_id, f"schema_ref is invalid JSON: {exc}")


def _record_schema(schema: Mapping[str, object], record_key: str):
    if not record_key:
        return schema
    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        return None
    records_property = properties.get(record_key, {})
    if not isinstance(records_property, Mapping):
        return None
    item_schema = records_property.get("items")
    return item_schema if isinstance(item_schema, Mapping) else None


def _record_subject_id(record: Mapping[str, object], fallback: str) -> str:
    for key in ("pattern_id", "presentation_id", "exception_id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _non_empty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _text_values(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )
