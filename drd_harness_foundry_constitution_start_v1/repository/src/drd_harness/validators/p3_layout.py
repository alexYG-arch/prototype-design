"""P3 natural-language layout artifact-set validators."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set

from drd_harness.rules.layout import Carrier
from drd_harness.validators.layout_completeness import (
    LayoutFinding,
    carrier_adaptation_profile_from_mapping,
    containment_hierarchy_from_mapping,
    content_growth_rule_from_mapping,
    figma_reconstruction_metadata_from_mapping,
    information_completeness_rule_from_mapping,
    natural_language_layout_from_mapping,
    state_placement_index_from_mapping,
    validate_layout_package,
    z_axis_layering_from_mapping,
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

P3_LAYOUT_VALIDATOR_REF = "repository/src/drd_harness/validators/p3_layout.py"
LAYOUT_VALIDATOR_REF = "repository/src/drd_harness/validators/layout_completeness.py"

P3_LAYOUT_ARTIFACTS = {
    "natural_language_layout": (
        "p3.layout.natural_language_layout",
        "layout",
        "repository/schemas/layout/natural_language_layout.schema.json",
        "200db205fbf9d26d177d1508f3e48e5d223a266fc5b30e95a98c43f60bbb9808",
    ),
    "carrier_adaptation_profile": (
        "p3.layout.carrier_adaptation_profile",
        "profile",
        "repository/schemas/layout/carrier_adaptation_profile.schema.json",
        "3357cebb6c57b4af57f1d2b5e090b3aa94ed19a575a11f9fb27231b0e913a779",
    ),
    "containment_hierarchy": (
        "p3.layout.containment_hierarchy",
        "hierarchy",
        "repository/schemas/layout/containment_hierarchy.schema.json",
        "98cfe72f29f3aa21873162d51730208a0faba12c9593b83c247d659472759ae7",
    ),
    "content_growth_rules": (
        "p3.layout.content_growth_rules",
        "records",
        "repository/schemas/layout/content_growth_rule.schema.json",
        "79f57ce83dc131f82b2cd85c5ffb0ef4c0b9bc46d28dc5bc49d003b8191801bd",
    ),
    "information_completeness_rules": (
        "p3.layout.information_completeness_rules",
        "records",
        "repository/schemas/layout/information_completeness_rule.schema.json",
        "8030efdad6f255924ba7c2b3597065e54fde04f13deaabb793ce5402e90aec5b",
    ),
    "state_placement_index": (
        "p3.layout.state_placement_index",
        "index",
        "repository/schemas/layout/state_placement_index.schema.json",
        "1d54dc6754204a5c2c5c3b62a7e0485ff58d730840d3753e50a10585166d6b1b",
    ),
    "z_axis_layering": (
        "p3.layout.z_axis_layering",
        "layering",
        "repository/schemas/layout/z_axis_layering.schema.json",
        "35c7b9c5bf111c0431624690463f9c76993706bc3dc0b21ba8d05bc652ba4730",
    ),
    "layout_composition_index": (
        "p3.layout.layout_composition_index",
        "index",
        "repository/schemas/layout/layout_composition_index.schema.json",
        "e0a4c5978fc0742a4f24244ef8dacd768e37d311d5f29733ea162bebeff0275f",
    ),
    "figma_reconstruction_metadata": (
        "p3.layout.figma_reconstruction_metadata",
        "metadata",
        "repository/schemas/layout/figma_reconstruction_metadata.schema.json",
        "59e743676ec5818b32398b3e97bd04e3cc06057f8d16482b764a14e4ae0fdea6",
    ),
}

P3_REQUIRED_CARRIERS = {
    Carrier.DESKTOP,
    Carrier.TABLET,
    Carrier.MOBILE,
    Carrier.MOBILE_IOS,
    Carrier.MOBILE_MATERIAL,
}

IOS_REQUIRED_TERMS = {"safe area", "status", "home indicator", "navigation", "keyboard"}
MATERIAL_REQUIRED_TERMS = {"app bar", "system bar", "keyboard", "elevation", "dialog", "snackbar", "bottom action"}
P3_REQUIRED_LAYOUT_REFS = {"pattern_refs", "state_variants", "z_axis_refs", "figma_metadata_ref"}


def validate_layout_artifacts(
    *,
    natural_language_layout: Mapping[str, object],
    carrier_adaptation_profile: Mapping[str, object],
    containment_hierarchy: Mapping[str, object],
    content_growth_rules: Mapping[str, object],
    information_completeness_rules: Mapping[str, object],
    state_placement_index: Mapping[str, object],
    z_axis_layering: Mapping[str, object],
    layout_composition_index: Mapping[str, object],
    figma_reconstruction_metadata: Mapping[str, object],
    element_inventory: Mapping[str, object],
    renderable_page_variants: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
    shared_component_registry: Mapping[str, object],
    information_presentation_registry: Mapping[str, object],
) -> List[LayoutFinding]:
    artifacts = {
        "natural_language_layout": natural_language_layout,
        "carrier_adaptation_profile": carrier_adaptation_profile,
        "containment_hierarchy": containment_hierarchy,
        "content_growth_rules": content_growth_rules,
        "information_completeness_rules": information_completeness_rules,
        "state_placement_index": state_placement_index,
        "z_axis_layering": z_axis_layering,
        "layout_composition_index": layout_composition_index,
        "figma_reconstruction_metadata": figma_reconstruction_metadata,
    }
    findings: List[LayoutFinding] = []
    for name, artifact in artifacts.items():
        artifact_id, payload_key, schema_ref, schema_hash = P3_LAYOUT_ARTIFACTS[name]
        findings.extend(_validate_artifact_envelope(artifact, artifact_id, payload_key, schema_ref, schema_hash))
        findings.extend(_validate_payload_shape(artifact, artifact_id, payload_key, schema_ref))

    try:
        layout = natural_language_layout_from_mapping(_payload_mapping(natural_language_layout, "layout"))
        carrier_profile = carrier_adaptation_profile_from_mapping(_payload_mapping(carrier_adaptation_profile, "profile"))
        hierarchy = containment_hierarchy_from_mapping(_payload_mapping(containment_hierarchy, "hierarchy"))
        growth_rules = [
            content_growth_rule_from_mapping(record)
            for record in _payload_records(content_growth_rules)
        ]
        completeness_rules = [
            information_completeness_rule_from_mapping(record)
            for record in _payload_records(information_completeness_rules)
        ]
        state_index = state_placement_index_from_mapping(_payload_mapping(state_placement_index, "index"))
        layering = z_axis_layering_from_mapping(_payload_mapping(z_axis_layering, "layering"))
        composition_index = _payload_mapping(layout_composition_index, "index")
        figma_metadata = figma_reconstruction_metadata_from_mapping(
            _payload_mapping(figma_reconstruction_metadata, "metadata")
        )
    except (KeyError, ValueError) as exc:
        findings.append(LayoutFinding("PL000", "p3.layout", str(exc)))
        return findings

    message_ids = _message_ids(closure_interaction_messages)
    pattern_ids = _pattern_ids(shared_component_registry)
    presentation_ids = _presentation_ids(information_presentation_registry)
    known_information_refs = _canonical_information_refs(element_inventory) | message_ids | presentation_ids
    traceable_refs = _traceable_ref_ids(
        element_inventory,
        renderable_page_variants,
        closure_interaction_messages,
        shared_component_registry,
        information_presentation_registry,
    )
    renderable_variant_ids = _renderable_page_variant_ids(renderable_page_variants)

    findings.extend(
        validate_layout_package(
            layout,
            carrier_profile,
            hierarchy,
            growth_rules,
            completeness_rules,
            layering,
            state_index,
            message_ids,
            figma_metadata,
            known_information_refs,
        )
    )
    findings.extend(_validate_p3_required_layout_refs(layout))
    findings.extend(_validate_required_carriers(carrier_profile))
    findings.extend(_validate_pattern_refs(layout.pattern_refs, pattern_ids))
    findings.extend(_validate_state_placement_presentations(state_index.placements, information_presentation_registry))
    findings.extend(_validate_state_placement_renderable_variants(state_index.placements, renderable_variant_ids))
    findings.extend(_validate_renderable_page_variant_layout_refs(layout, hierarchy, figma_metadata, renderable_page_variants))
    findings.extend(
        _validate_composition_index(
            composition_index,
            layout.layout_id,
            hierarchy.hierarchy_id,
            {rule.growth_rule_id for rule in growth_rules},
            {rule.completeness_id for rule in completeness_rules},
            state_index.index_id,
            layering.z_axis_layer_id,
        )
    )
    findings.extend(_validate_trace_refs(artifacts, traceable_refs | _layout_ref_ids(artifacts)))
    return findings


def validate_downstream_layout_refs(
    layout_refs: Iterable[str],
    natural_language_layout: Mapping[str, object],
    layout_composition_index: Mapping[str, object],
    *,
    carrier_adaptation_profile: Optional[Mapping[str, object]] = None,
    containment_hierarchy: Optional[Mapping[str, object]] = None,
    content_growth_rules: Optional[Mapping[str, object]] = None,
    information_completeness_rules: Optional[Mapping[str, object]] = None,
    state_placement_index: Optional[Mapping[str, object]] = None,
    z_axis_layering: Optional[Mapping[str, object]] = None,
    figma_reconstruction_metadata: Optional[Mapping[str, object]] = None,
) -> List[LayoutFinding]:
    artifacts = {
        "natural_language_layout": natural_language_layout,
        "layout_composition_index": layout_composition_index,
    }
    optional_artifacts = {
        "carrier_adaptation_profile": carrier_adaptation_profile,
        "containment_hierarchy": containment_hierarchy,
        "content_growth_rules": content_growth_rules,
        "information_completeness_rules": information_completeness_rules,
        "state_placement_index": state_placement_index,
        "z_axis_layering": z_axis_layering,
        "figma_reconstruction_metadata": figma_reconstruction_metadata,
    }
    artifacts.update(
        {
            name: artifact
            for name, artifact in optional_artifacts.items()
            if artifact is not None
        }
    )
    known_refs = _layout_ref_ids(artifacts)
    findings: List[LayoutFinding] = []
    for layout_ref in sorted(set(layout_refs) - known_refs):
        findings.append(LayoutFinding("PL016", layout_ref, "downstream layout_ref does not resolve to layout package"))
    return findings


def _validate_artifact_envelope(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
    schema_ref: str,
    schema_hash: str,
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    missing = sorted(REQUIRED_ARTIFACT_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(LayoutFinding("PL017", artifact_id, "artifact envelope missing fields: " + ", ".join(missing)))
    if artifact.get("artifact_id") != artifact_id:
        findings.append(LayoutFinding("PL017", artifact_id, "artifact_id does not match contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(LayoutFinding("PL017", artifact_id, "schema_payload_key does not match contract"))
    if artifact.get("schema_ref") != schema_ref:
        findings.append(LayoutFinding("PL017", artifact_id, "schema_ref does not match contract"))
    else:
        schema_path = Path(schema_ref)
        if not schema_path.is_file():
            findings.append(LayoutFinding("PL017", artifact_id, f"schema_ref path is missing: {schema_ref}"))
        elif hashlib.sha256(schema_path.read_bytes()).hexdigest() != schema_hash:
            findings.append(LayoutFinding("PL017", artifact_id, "schema_ref hash does not match contract"))
    if artifact.get("validator_ref") not in {P3_LAYOUT_VALIDATOR_REF, LAYOUT_VALIDATOR_REF}:
        findings.append(LayoutFinding("PL017", artifact_id, "validator_ref does not match layout validator contract"))

    source_refs = artifact.get("source_refs")
    upstream_refs = artifact.get("upstream_artifact_refs")
    upstream_hashes = artifact.get("upstream_hashes")
    invalidation_inputs = artifact.get("invalidation_inputs")
    if not _non_empty_text_list(source_refs):
        findings.append(LayoutFinding("PL017", artifact_id, "source_refs must be a non-empty text list"))
    if not _non_empty_text_list(upstream_refs):
        findings.append(LayoutFinding("PL017", artifact_id, "upstream_artifact_refs must be a non-empty text list"))
    if not isinstance(upstream_hashes, Mapping):
        findings.append(LayoutFinding("PL017", artifact_id, "upstream_hashes must be an object"))
    if not _non_empty_text_list(invalidation_inputs):
        findings.append(LayoutFinding("PL017", artifact_id, "invalidation_inputs must be a non-empty text list"))
    if _non_empty_text_list(source_refs) and _non_empty_text_list(invalidation_inputs):
        if set(_text_values(source_refs)) != set(_text_values(invalidation_inputs)):
            findings.append(LayoutFinding("PL017", artifact_id, "source_refs must match invalidation_inputs for replayable provenance"))
    if _non_empty_text_list(upstream_refs) and isinstance(upstream_hashes, Mapping):
        ref_list = _text_values(upstream_refs)
        ref_set = set(ref_list)
        hash_keys = {str(key) for key in upstream_hashes}
        if ref_set != hash_keys:
            findings.append(LayoutFinding("PL017", artifact_id, "upstream_artifact_refs and upstream_hashes keys must match"))
        if _non_empty_text_list(invalidation_inputs):
            input_paths = _text_values(invalidation_inputs)
            if len(input_paths) != len(ref_list):
                findings.append(LayoutFinding("PL017", artifact_id, "invalidation_inputs must align one-to-one with upstream_artifact_refs"))
            else:
                for ref, input_path in zip(ref_list, input_paths):
                    path = Path(input_path)
                    if not path.is_file():
                        findings.append(LayoutFinding("PL017", artifact_id, f"upstream input path is missing: {input_path}"))
                        continue
                    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    if upstream_hashes.get(ref) != actual_hash:
                        findings.append(LayoutFinding("PL017", artifact_id, f"upstream_hashes[{ref}] does not match {input_path}"))
        for ref in sorted(ref_set & hash_keys):
            if not _is_sha256(upstream_hashes.get(ref)):
                findings.append(LayoutFinding("PL017", artifact_id, "upstream_hashes values must be sha256"))
    return findings


def _validate_payload_shape(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
    schema_ref: str,
) -> List[LayoutFinding]:
    payload = artifact.get(payload_key)
    if payload_key == "records":
        if not isinstance(payload, list):
            return [LayoutFinding("PL017", artifact_id, "records payload must be a list")]
        return _validate_record_rows(payload, artifact_id, schema_ref)
    if not isinstance(payload, Mapping):
        return [LayoutFinding("PL017", artifact_id, f"{payload_key} payload must be an object")]
    return _validate_schema_keys(payload, artifact_id, schema_ref)


def _validate_schema_keys(payload: Mapping[str, object], artifact_id: str, schema_ref: str) -> List[LayoutFinding]:
    schema = _load_schema(schema_ref, artifact_id)
    if isinstance(schema, LayoutFinding):
        return [schema]
    required = set(_text_values(schema.get("required", [])))
    properties = schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    payload_keys = {str(key) for key in payload}
    findings: List[LayoutFinding] = []
    missing = sorted(required - payload_keys)
    extra = sorted(payload_keys - allowed)
    if missing:
        findings.append(LayoutFinding("PL017", artifact_id, "payload missing schema fields: " + ", ".join(missing)))
    if extra:
        findings.append(LayoutFinding("PL017", artifact_id, "payload has off-schema fields: " + ", ".join(extra)))
    findings.extend(_validate_nested_schema_keys(payload, properties, artifact_id))
    return findings


def _validate_record_rows(records: Sequence[object], artifact_id: str, schema_ref: str) -> List[LayoutFinding]:
    schema = _load_schema(schema_ref, artifact_id)
    if isinstance(schema, LayoutFinding):
        return [schema]
    required = set(_text_values(schema.get("required", [])))
    properties = schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    findings: List[LayoutFinding] = []
    for record in records:
        if not isinstance(record, Mapping):
            findings.append(LayoutFinding("PL017", artifact_id, "record rows must be objects"))
            continue
        row_keys = {str(key) for key in record}
        subject_id = _record_subject_id(record, artifact_id)
        missing = sorted(required - row_keys)
        extra = sorted(row_keys - allowed)
        if missing:
            findings.append(LayoutFinding("PL017", subject_id, "record missing schema fields: " + ", ".join(missing)))
        if extra:
            findings.append(LayoutFinding("PL017", subject_id, "record has off-schema fields: " + ", ".join(extra)))
        findings.extend(_validate_nested_schema_keys(record, properties, subject_id))
    return findings


def _validate_nested_schema_keys(
    record: Mapping[str, object],
    properties: object,
    subject_id: str,
) -> List[LayoutFinding]:
    if not isinstance(properties, Mapping):
        return []
    findings: List[LayoutFinding] = []
    for field_name, field_schema in properties.items():
        if not isinstance(field_schema, Mapping) or field_name not in record:
            continue
        value = record.get(field_name)
        item_schema = field_schema.get("items")
        if isinstance(value, list) and isinstance(item_schema, Mapping):
            for item in value:
                if isinstance(item, Mapping):
                    findings.extend(_validate_object_against_schema(item, item_schema, subject_id, str(field_name)))
        additional_schema = field_schema.get("additionalProperties")
        if isinstance(value, Mapping) and isinstance(additional_schema, Mapping):
            for item in value.values():
                if isinstance(item, Mapping):
                    findings.extend(_validate_object_against_schema(item, additional_schema, subject_id, str(field_name)))
    return findings


def _validate_object_against_schema(
    value: Mapping[str, object],
    schema: Mapping[str, object],
    subject_id: str,
    field_name: str,
) -> List[LayoutFinding]:
    required = set(_text_values(schema.get("required", [])))
    properties = schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) else set(required)
    value_keys = {str(key) for key in value}
    findings: List[LayoutFinding] = []
    missing = sorted(required - value_keys)
    extra = sorted(value_keys - allowed)
    if missing:
        findings.append(LayoutFinding("PL017", subject_id, f"{field_name} item missing schema fields: " + ", ".join(missing)))
    if extra:
        findings.append(LayoutFinding("PL017", subject_id, f"{field_name} item has off-schema fields: " + ", ".join(extra)))
    return findings


def _validate_p3_required_layout_refs(layout) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    for field_name in sorted(P3_REQUIRED_LAYOUT_REFS):
        value = getattr(layout, field_name)
        if isinstance(value, list) and not value:
            findings.append(LayoutFinding("PL018", layout.layout_id, f"{field_name} is P3-required and must be non-empty"))
        elif value is None or value == "":
            findings.append(LayoutFinding("PL018", layout.layout_id, f"{field_name} is P3-required and must be non-empty"))
    return findings


def _validate_required_carriers(profile) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    required = set(profile.required_carriers)
    missing = sorted(carrier.value for carrier in P3_REQUIRED_CARRIERS - required)
    if missing:
        findings.append(LayoutFinding("PL007", profile.carrier_profile_id, "P3 carrier profile missing carriers: " + ", ".join(missing)))
    if Carrier.MOBILE_IOS in profile.carrier_rules:
        ios_rule = profile.carrier_rules[Carrier.MOBILE_IOS]
        ios_text = _carrier_rule_text(ios_rule)
        missing_ios = sorted(term for term in IOS_REQUIRED_TERMS if term not in ios_text)
        if missing_ios:
            findings.append(LayoutFinding("PL007", profile.carrier_profile_id, "MOBILE_IOS missing platform constraints: " + ", ".join(missing_ios)))
    if Carrier.MOBILE_MATERIAL in profile.carrier_rules:
        material_rule = profile.carrier_rules[Carrier.MOBILE_MATERIAL]
        material_text = _carrier_rule_text(material_rule)
        missing_material = sorted(term for term in MATERIAL_REQUIRED_TERMS if term not in material_text)
        if missing_material:
            findings.append(LayoutFinding("PL007", profile.carrier_profile_id, "MOBILE_MATERIAL missing platform constraints: " + ", ".join(missing_material)))
    return findings


def _validate_pattern_refs(pattern_refs: Iterable[str], pattern_ids: Set[str]) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    for ref in sorted(set(pattern_refs) - pattern_ids):
        findings.append(LayoutFinding("PL016", ref, "layout pattern_ref does not resolve to approved pattern registry"))
    return findings


def _validate_state_placement_presentations(placements: Iterable[object], information_presentation_registry: Mapping[str, object]) -> List[LayoutFinding]:
    presentation_by_message = {
        str(record.get("message_ref")): str(record.get("presentation_mode"))
        for record in _registry_records(information_presentation_registry, "decisions")
        if record.get("message_ref")
    }
    findings: List[LayoutFinding] = []
    for placement in placements:
        expected_mode = presentation_by_message.get(placement.message_id)
        if expected_mode is None:
            findings.append(LayoutFinding("PL011", placement.message_id, "state placement lacks approved presentation decision"))
        elif placement.presentation_mode != expected_mode:
            findings.append(LayoutFinding("PL011", placement.message_id, "state placement presentation_mode does not match approved decision"))
    return findings


def _validate_state_placement_renderable_variants(
    placements: Iterable[object],
    renderable_page_variant_ids: Iterable[str],
) -> List[LayoutFinding]:
    variant_ids = set(renderable_page_variant_ids)
    findings: List[LayoutFinding] = []
    for placement in placements:
        if placement.surface_id not in variant_ids:
            findings.append(
                LayoutFinding(
                    "PL020",
                    placement.message_id,
                    "state placement surface_id does not resolve to renderable page variant",
                )
            )
    return findings


def _validate_composition_index(
    index: Mapping[str, object],
    layout_id: str,
    hierarchy_id: str,
    growth_ids: Set[str],
    completeness_ids: Set[str],
    state_index_id: str,
    z_axis_id: str,
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    index_id = str(index.get("index_id", "p3.layout.layout_composition_index"))
    if index.get("layout_id") != layout_id:
        findings.append(LayoutFinding("PL016", index_id, "composition layout_id does not bind layout"))
    if index.get("containment_tree_ref") != hierarchy_id:
        findings.append(LayoutFinding("PL016", index_id, "composition containment_tree_ref does not bind hierarchy"))
    if set(_text_values(index.get("content_growth_refs"))) != growth_ids:
        findings.append(LayoutFinding("PL016", index_id, "composition content_growth_refs do not bind growth records"))
    if set(_text_values(index.get("information_completeness_refs"))) != completeness_ids:
        findings.append(LayoutFinding("PL016", index_id, "composition information_completeness_refs do not bind completeness records"))
    if index.get("state_placement_index_ref") != state_index_id:
        findings.append(LayoutFinding("PL016", index_id, "composition state_placement_index_ref does not bind state index"))
    z_refs = _text_values(index.get("z_axis_refs"))
    if not z_refs:
        findings.append(LayoutFinding("PL018", index_id, "composition z_axis_refs is P3-required and must be non-empty"))
    elif z_axis_id not in set(z_refs):
        findings.append(LayoutFinding("PL016", index_id, "composition z_axis_refs do not bind z-axis layering"))
    return findings


def _validate_trace_refs(artifacts: Mapping[str, Mapping[str, object]], traceable_refs: Set[str]) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    for name, artifact in artifacts.items():
        artifact_id, payload_key, _, _ = P3_LAYOUT_ARTIFACTS[name]
        payload = artifact.get(payload_key)
        records = payload if isinstance(payload, list) else [payload]
        for record in records:
            if isinstance(record, Mapping):
                subject_id = _record_subject_id(record, artifact_id)
                for trace_ref in _text_values(record.get("trace_refs")):
                    if trace_ref not in traceable_refs:
                        findings.append(LayoutFinding("PL019", subject_id, f"trace_ref does not resolve to upstream authority: {trace_ref}"))
                for nested_key in ("placements",):
                    nested_records = record.get(nested_key)
                    if not isinstance(nested_records, list):
                        continue
                    for nested_record in nested_records:
                        if not isinstance(nested_record, Mapping):
                            continue
                        nested_subject_id = _record_subject_id(nested_record, subject_id)
                        for trace_ref in _text_values(nested_record.get("trace_refs")):
                            if trace_ref not in traceable_refs:
                                findings.append(LayoutFinding("PL019", nested_subject_id, f"trace_ref does not resolve to upstream authority: {trace_ref}"))
    return findings


def _layout_ref_ids(artifacts: Mapping[str, Mapping[str, object]]) -> Set[str]:
    refs: Set[str] = set()
    for name, artifact in artifacts.items():
        _, payload_key, _, _ = P3_LAYOUT_ARTIFACTS[name]
        payload = artifact.get(payload_key)
        records = payload if isinstance(payload, list) else [payload]
        for record in records:
            if isinstance(record, Mapping):
                for key in (
                    "layout_id",
                    "carrier_profile_id",
                    "hierarchy_id",
                    "growth_rule_id",
                    "completeness_id",
                    "index_id",
                    "z_axis_layer_id",
                    "figma_metadata_id",
                    "surface_id",
                    "target_ref",
                    "state_placement_index_ref",
                    "containment_tree_ref",
                    "figma_metadata_ref",
                ):
                    value = record.get(key)
                    if isinstance(value, str) and value.strip():
                        refs.add(value)
                for list_key in (
                    "carrier_profile_refs",
                    "section_index",
                    "pattern_refs",
                    "state_variants",
                    "content_growth_refs",
                    "z_axis_refs",
                    "information_completeness_refs",
                    "required_information_refs",
                ):
                    refs.update(_text_values(record.get(list_key)))
                for node in record.get("nodes", []) if isinstance(record.get("nodes"), list) else []:
                    if isinstance(node, Mapping):
                        refs.update(_text_values([node.get("node_id"), node.get("parent_id")]))
                for layer in record.get("layers", []) if isinstance(record.get("layers"), list) else []:
                    if isinstance(layer, Mapping):
                        refs.update(_text_values([layer.get("surface_ref")]))
                for placement in record.get("placements", []) if isinstance(record.get("placements"), list) else []:
                    if isinstance(placement, Mapping):
                        refs.update(
                            _text_values(
                                [
                                    placement.get("message_id"),
                                    placement.get("surface_id"),
                                ]
                            )
                        )
    refs.discard("None")
    return refs


def _traceable_ref_ids(
    element_inventory: Mapping[str, object],
    renderable_page_variants: Mapping[str, object],
    closure_interaction_messages: Mapping[str, object],
    shared_component_registry: Mapping[str, object],
    information_presentation_registry: Mapping[str, object],
) -> Set[str]:
    refs: Set[str] = set()
    for artifact in (element_inventory, renderable_page_variants, closure_interaction_messages):
        for record in _payload_records(artifact):
            refs.update(_text_values(record.values()))
            for list_key in ("source_refs", "trace_refs", "shared_element_refs", "variant_element_refs", "recovery_targets"):
                refs.update(_text_values(record.get(list_key)))
    for record in _registry_records(shared_component_registry, "patterns"):
        refs.update(_text_values(record.values()))
        for list_key in ("reuse_scope", "trace_refs"):
            refs.update(_text_values(record.get(list_key)))
    for record in _registry_records(information_presentation_registry, "decisions"):
        refs.update(_text_values(record.values()))
        refs.update(_text_values(record.get("trace_refs")))
    refs.discard("None")
    return refs


def _canonical_information_refs(element_inventory: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("element_id"))
        for record in _payload_records(element_inventory)
        if record.get("element_type") in {"STATE", "MESSAGE"}
    }


def _renderable_page_variant_ids(renderable_page_variants: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("variant_page_id"))
        for record in _payload_records(renderable_page_variants)
        if record.get("variant_page_id")
    }


def _validate_renderable_page_variant_layout_refs(
    layout,
    hierarchy,
    figma_metadata,
    renderable_page_variants: Mapping[str, object],
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    layout_state_refs = set(layout.state_variants)
    layout_sections = set(layout.section_index)
    hierarchy_node_ids = set(hierarchy.node_ids())
    figma_frames = set(figma_metadata.frame_hierarchy)
    figma_state_refs = set(figma_metadata.state_variants)
    for record in _payload_records(renderable_page_variants):
        variant_id = str(record.get("variant_page_id", ""))
        if not variant_id:
            continue
        if variant_id not in layout_state_refs:
            findings.append(LayoutFinding("PL020", variant_id, "renderable page variant is absent from layout.state_variants"))
        if variant_id not in layout_sections:
            findings.append(LayoutFinding("PL020", variant_id, "renderable page variant is absent from layout.section_index"))
        if variant_id not in hierarchy_node_ids:
            findings.append(LayoutFinding("PL020", variant_id, "renderable page variant is absent from containment hierarchy"))
        if record.get("figma_frame_required") is True and variant_id not in figma_frames:
            findings.append(LayoutFinding("PL020", variant_id, "renderable page variant lacks required Figma frame"))
        if variant_id not in figma_state_refs:
            findings.append(LayoutFinding("PL020", variant_id, "renderable page variant is absent from Figma state_variants"))
    return findings


def _pattern_ids(shared_component_registry: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("pattern_id"))
        for record in _registry_records(shared_component_registry, "patterns")
        if record.get("pattern_id")
    }


def _presentation_ids(information_presentation_registry: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("presentation_id"))
        for record in _registry_records(information_presentation_registry, "decisions")
        if record.get("presentation_id")
    }


def _message_ids(closure_interaction_messages: Mapping[str, object]) -> Set[str]:
    return {
        str(record.get("message_id"))
        for record in _payload_records(closure_interaction_messages)
        if record.get("message_id")
    }


def _payload_mapping(artifact: Mapping[str, object], payload_key: str) -> Mapping[str, object]:
    payload = artifact.get(payload_key)
    if not isinstance(payload, Mapping):
        raise ValueError(f"{payload_key} payload must be an object")
    return payload


def _payload_records(artifact: Mapping[str, object], payload_key: str = "records") -> List[Mapping[str, object]]:
    records = artifact.get(payload_key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _registry_records(artifact: Mapping[str, object], record_key: str) -> List[Mapping[str, object]]:
    registry = artifact.get("registry", {})
    if not isinstance(registry, Mapping):
        return []
    records = registry.get(record_key, [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _load_schema(schema_ref: str, artifact_id: str):
    path = Path(schema_ref)
    if not path.is_file():
        return LayoutFinding("PL017", artifact_id, f"schema_ref path is missing: {schema_ref}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return LayoutFinding("PL017", artifact_id, f"schema_ref is invalid JSON: {exc}")


def _record_subject_id(record: Mapping[str, object], fallback: str) -> str:
    for key in (
        "layout_id",
        "carrier_profile_id",
        "hierarchy_id",
        "growth_rule_id",
        "completeness_id",
        "index_id",
        "z_axis_layer_id",
        "figma_metadata_id",
        "message_id",
    ):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _carrier_rule_text(rule) -> str:
    return " ".join(
        [
            rule.arrangement,
            rule.width_behavior,
            rule.height_scroll_behavior,
            rule.navigation_placement,
            rule.safe_area_or_system_bars,
            rule.input_keyboard_behavior,
            " ".join(rule.platform_constraints),
        ]
    ).lower()


def _non_empty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _text_values(value: object) -> List[str]:
    if isinstance(value, Mapping):
        return []
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value if isinstance(item, str) and item.strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )
