"""Validators for natural-language layout completeness and reconstruction metadata."""

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Set

from drd_harness.rules.layout import (
    Carrier,
    CarrierRule,
    ContainmentHierarchy,
    ContainmentNode,
    ContentGrowthRule,
    FIGMA_WRITE_TERMS,
    FigmaReconstructionMetadata,
    HEIGHT_LOSS_TERMS,
    InformationCompletenessRule,
    LAYOUT_COVERAGE_TERMS,
    LayerKind,
    NaturalLanguageLayout,
    StatePlacementRecord,
    StatePlacementIndex,
    SurfaceKind,
    ZAxisLayer,
    HORIZONTAL_SCROLL_TERMS,
    WIDTH_FATAL_TERMS,
    WIDTH_HORIZONTAL_EXCEPTION_TERMS,
    ZAxisLayering,
    CarrierAdaptationProfile,
)


@dataclass(frozen=True)
class LayoutFinding:
    code: str
    subject_id: str
    message: str


def validate_natural_language_layout(layout: NaturalLanguageLayout) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    findings.extend(_collect("PL006", layout.layout_id, layout.require_complete))
    authority_text = layout.semantic_authority.lower()
    inventory_text = layout.inventory_role.lower()
    if "natural language" not in authority_text or "canonical" not in authority_text:
        findings.append(LayoutFinding("PL006", layout.layout_id, "natural language must be declared as canonical semantic authority"))
    if not _inventory_is_index_only(inventory_text):
        findings.append(LayoutFinding("PL006", layout.layout_id, "inventory must be declared as index and validation skeleton only"))
    text = layout.layout_text.lower()
    missing_groups = [
        group for group, terms in LAYOUT_COVERAGE_TERMS.items()
        if not any(term in text for term in terms)
    ]
    if missing_groups:
        findings.append(
            LayoutFinding(
                code="PL006",
                subject_id=layout.layout_id,
                message="layout prose missing coverage groups: " + ", ".join(missing_groups),
            )
        )
    return findings


def validate_carrier_adaptation_profile(profile: CarrierAdaptationProfile) -> List[LayoutFinding]:
    findings = _collect("PL007", profile.carrier_profile_id, profile.require_complete)
    required = set(profile.required_carriers)
    if Carrier.MOBILE_IOS in required and Carrier.MOBILE not in required:
        findings.append(LayoutFinding("PL007", profile.carrier_profile_id, "MOBILE_IOS requires MOBILE carrier context"))
    if Carrier.MOBILE_MATERIAL in required and Carrier.MOBILE not in required:
        findings.append(LayoutFinding("PL007", profile.carrier_profile_id, "MOBILE_MATERIAL requires MOBILE carrier context"))
    return findings


def validate_containment_hierarchy(hierarchy: ContainmentHierarchy) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    if not hierarchy.nodes:
        return [LayoutFinding("PL008", hierarchy.hierarchy_id, "containment hierarchy has no nodes")]

    node_ids = hierarchy.node_ids()
    root_count = 0
    for node in hierarchy.nodes:
        findings.extend(_collect("PL008", node.node_id, node.require_local_layout))
        findings.extend(_collect("PL012", node.node_id, node.require_nested_surface_context))
        if node.parent_id is None:
            root_count += 1
        elif node.parent_id not in node_ids:
            findings.append(LayoutFinding("PL008", node.node_id, "parent_id does not resolve"))
        if _contradicts_parent(node.scroll_behavior) or _contradicts_parent(node.width_behavior):
            findings.append(LayoutFinding("PL008", node.node_id, "child layout contradicts parent constraints"))

    if root_count != 1:
        findings.append(LayoutFinding("PL008", hierarchy.hierarchy_id, "containment hierarchy must have exactly one root"))
    if _max_depth(hierarchy) < 2:
        findings.append(LayoutFinding("PL008", hierarchy.hierarchy_id, "containment hierarchy is too flat for layout closure"))
    return findings


def validate_content_growth_rule(rule: ContentGrowthRule) -> List[LayoutFinding]:
    return _collect("PL009", rule.growth_rule_id, rule.require_complete)


def validate_information_completeness_rule(rule: InformationCompletenessRule) -> List[LayoutFinding]:
    findings = _collect("PL010", rule.completeness_id, rule.require_complete)
    height_text = f"{rule.height_behavior} {rule.information_access_path}".lower()
    width_text = f"{rule.width_behavior} {rule.information_access_path}".lower()
    if any(term in height_text for term in HEIGHT_LOSS_TERMS) and not _has_access_path(rule.information_access_path):
        findings.append(LayoutFinding("PL010", rule.completeness_id, "height constraint hides or omits required information"))
    if any(term in width_text for term in WIDTH_FATAL_TERMS):
        findings.append(LayoutFinding("PL010", rule.completeness_id, "width constraint is ignored instead of adapted"))
    if any(term in width_text for term in WIDTH_HORIZONTAL_EXCEPTION_TERMS) and not _has_horizontal_scroll_exception(rule):
        findings.append(LayoutFinding("PL010", rule.completeness_id, "width overflow requires declared horizontal scroll exception"))
    if not _has_access_path(rule.information_access_path):
        findings.append(LayoutFinding("PL010", rule.completeness_id, "required information lacks recovery or access path"))
    return findings


def validate_information_completeness_refs(
    completeness_rules: Iterable[InformationCompletenessRule],
    known_information_refs: Iterable[str],
) -> List[LayoutFinding]:
    known = set(known_information_refs)
    findings: List[LayoutFinding] = []
    for rule in completeness_rules:
        for ref in sorted(set(rule.required_information_refs) - known):
            findings.append(LayoutFinding("PL010", ref, "required information ref does not resolve"))
    return findings


def validate_z_axis_layering(layering: ZAxisLayering, material_profile_required: bool = False) -> List[LayoutFinding]:
    findings = _collect("PL013", layering.z_axis_layer_id, layering.require_complete)
    layer_values = [layer.layer for layer in layering.layers]
    if len(layer_values) != len(set(layer_values)):
        findings.append(LayoutFinding("PL013", layering.z_axis_layer_id, "z-axis layer numbers must be unique"))
    if layer_values != sorted(layer_values):
        findings.append(LayoutFinding("PL013", layering.z_axis_layer_id, "z-axis layers must be ordered from lower to higher"))
    layered_kinds = {layer.layer_kind for layer in layering.layers}
    if layered_kinds & {LayerKind.OVERLAY, LayerKind.MODAL, LayerKind.DRAWER, LayerKind.POPOVER, LayerKind.MENU}:
        if not any(layer.blocks_lower_layers for layer in layering.layers):
            findings.append(LayoutFinding("PL013", layering.z_axis_layer_id, "interactive layered surface must declare blocking behavior"))
    if material_profile_required and not layering.material_elevation_intent:
        findings.append(LayoutFinding("PL013", layering.z_axis_layer_id, "Material profile requires elevation or z-axis intent"))
    return findings


def validate_state_placement_index(
    index: StatePlacementIndex,
    required_message_ids: Iterable[str],
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    for placement in index.placements:
        findings.extend(_collect("PL011", placement.message_id, placement.require_complete))
    required = set(required_message_ids)
    placed = index.message_ids()
    for message_id in sorted(required - placed):
        findings.append(LayoutFinding("PL011", message_id, "interaction message lacks layout placement"))
    for message_id in sorted(placed - required):
        findings.append(LayoutFinding("PL011", message_id, "layout placement references unknown interaction message"))
    return findings


def validate_nested_surface_layout(hierarchy: ContainmentHierarchy) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    for node in hierarchy.nodes:
        if node.surface_kind in {SurfaceKind.OVERLAY, SurfaceKind.DRAWER, SurfaceKind.PANEL, SurfaceKind.POPOVER}:
            findings.extend(_collect("PL012", node.node_id, node.require_nested_surface_context))
    return findings


def validate_figma_metadata(
    metadata: FigmaReconstructionMetadata,
    layout: NaturalLanguageLayout,
) -> List[LayoutFinding]:
    findings = _collect("PL014", metadata.figma_metadata_id, metadata.require_complete)
    if metadata.layout_id != layout.layout_id:
        findings.append(LayoutFinding("PL014", metadata.figma_metadata_id, "Figma metadata layout_id does not match layout"))

    non_goal_text = " ".join(metadata.non_goals).lower()
    if not all(term in non_goal_text for term in ["no figma api", "no renderer", "no file write"]):
        findings.append(LayoutFinding("PL015", metadata.figma_metadata_id, "Figma non_goals must exclude API, renderer, and file write authority"))
    allowed_text = " ".join(
        metadata.frame_hierarchy
        + metadata.selection_box_hierarchy
        + metadata.component_instances
        + metadata.state_variants
        + metadata.carrier_variants
        + metadata.z_axis_layers
        + metadata.scroll_frames
        + metadata.constraints
        + [metadata.auto_layout_guidance]
    ).lower()
    if any(term in allowed_text for term in FIGMA_WRITE_TERMS):
        findings.append(LayoutFinding("PL015", metadata.figma_metadata_id, "Figma metadata introduces write, renderer, or canonical authority"))

    layout_refs = set(layout.pattern_refs + layout.state_variants + layout.z_axis_refs + layout.carrier_profile_refs)
    metadata_refs = set(metadata.component_instances + metadata.state_variants + metadata.z_axis_layers + metadata.carrier_variants)
    drift_refs = {ref for ref in metadata_refs if ref and ref not in layout_refs}
    if drift_refs:
        findings.append(
            LayoutFinding(
                code="PL016",
                subject_id=metadata.figma_metadata_id,
                message="Figma metadata introduces refs absent from layout authority: " + ", ".join(sorted(drift_refs)),
            )
        )
    findings.extend(_validate_page_arrangement_order(metadata))
    return findings


def _validate_page_arrangement_order(metadata: FigmaReconstructionMetadata) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    rows = list(metadata.page_arrangement_order or [])
    if not rows:
        return findings
    frame_ids = set(metadata.frame_hierarchy)
    seen_frame_order: Set[int] = set()
    previous_sort_key = None
    for position, row in enumerate(rows):
        subject = str(row.get("variant_page_id") or row.get("frame_id") or f"page_arrangement_order[{position}]")
        frame_id = str(row.get("frame_id") or "")
        if frame_id not in frame_ids:
            findings.append(LayoutFinding("PL017", subject, "page arrangement frame_id must exist in frame_hierarchy"))
        order_value = row.get("figma_frame_order_index")
        if not isinstance(order_value, int) or order_value < 0:
            findings.append(LayoutFinding("PL017", subject, "figma_frame_order_index must be a non-negative integer"))
            continue
        if order_value in seen_frame_order:
            findings.append(LayoutFinding("PL017", subject, "figma_frame_order_index must be unique"))
        seen_frame_order.add(order_value)
        sort_key = (
            str(row.get("module_id") or ""),
            str(row.get("function_group_id") or ""),
            row.get("page_order_index") if isinstance(row.get("page_order_index"), int) else -1,
            row.get("variant_order_index") if isinstance(row.get("variant_order_index"), int) else -1,
            order_value,
        )
        if previous_sort_key is not None and sort_key < previous_sort_key:
            findings.append(LayoutFinding("PL017", subject, "page arrangement must be sorted by module, function, page, variant, and frame order"))
        previous_sort_key = sort_key
        if row.get("derivation_origin") not in {
            "PRD_EXPLICIT",
            "DEDUCTIVE_REQUIRED",
            "HUMAN_APPROVED_INFERENCE",
            "REVIEW_REQUIRED_INFERENCE",
        }:
            findings.append(LayoutFinding("PL017", subject, "page arrangement must expose derivation_origin"))
    expected_frame_order = [metadata.frame_hierarchy[index] for index in sorted(seen_frame_order) if index < len(metadata.frame_hierarchy)]
    arranged_frame_order = [str(row.get("frame_id")) for row in sorted(rows, key=lambda row: row.get("figma_frame_order_index", -1))]
    if arranged_frame_order and arranged_frame_order != expected_frame_order:
        findings.append(LayoutFinding("PL017", metadata.figma_metadata_id, "page arrangement frame order must match frame_hierarchy order"))
    return findings


def validate_layout_package(
    layout: NaturalLanguageLayout,
    carrier_profile: CarrierAdaptationProfile,
    hierarchy: ContainmentHierarchy,
    growth_rules: Iterable[ContentGrowthRule],
    completeness_rules: Iterable[InformationCompletenessRule],
    z_axis_layering: ZAxisLayering,
    state_index: StatePlacementIndex,
    required_message_ids: Iterable[str],
    figma_metadata: FigmaReconstructionMetadata,
    known_information_refs: Iterable[str] = (),
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    growth_rule_list = list(growth_rules)
    completeness_rule_list = list(completeness_rules)
    findings.extend(validate_natural_language_layout(layout))
    findings.extend(validate_carrier_adaptation_profile(carrier_profile))
    findings.extend(validate_containment_hierarchy(hierarchy))
    for rule in growth_rule_list:
        findings.extend(validate_content_growth_rule(rule))
    for rule in completeness_rule_list:
        findings.extend(validate_information_completeness_rule(rule))
    known_refs = set(known_information_refs)
    if known_refs:
        findings.extend(validate_information_completeness_refs(completeness_rule_list, known_refs))
    material_required = Carrier.MOBILE_MATERIAL in carrier_profile.required_carriers
    findings.extend(validate_z_axis_layering(z_axis_layering, material_required))
    findings.extend(validate_state_placement_index(state_index, required_message_ids))
    findings.extend(validate_nested_surface_layout(hierarchy))
    findings.extend(validate_figma_metadata(figma_metadata, layout))
    findings.extend(
        validate_layout_reference_integrity(
            layout,
            carrier_profile,
            hierarchy,
            growth_rule_list,
            completeness_rule_list,
            z_axis_layering,
            state_index,
            figma_metadata,
        )
    )
    return findings


def validate_layout_reference_integrity(
    layout: NaturalLanguageLayout,
    carrier_profile: CarrierAdaptationProfile,
    hierarchy: ContainmentHierarchy,
    growth_rules: Iterable[ContentGrowthRule],
    completeness_rules: Iterable[InformationCompletenessRule],
    z_axis_layering: ZAxisLayering,
    state_index: StatePlacementIndex,
    figma_metadata: FigmaReconstructionMetadata,
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    growth_rule_list = list(growth_rules)
    completeness_rule_list = list(completeness_rules)
    surface_ids = hierarchy.node_ids() | {hierarchy.surface_id, layout.surface_id}
    if layout.carrier_profile_refs != [carrier_profile.carrier_profile_id]:
        findings.append(LayoutFinding("PL016", layout.layout_id, "carrier_profile_refs do not bind carrier profile"))
    if layout.containment_tree_ref != hierarchy.hierarchy_id:
        findings.append(LayoutFinding("PL016", layout.layout_id, "containment_tree_ref does not bind hierarchy"))

    growth_ids = {rule.growth_rule_id for rule in growth_rule_list}
    missing_growth = sorted(set(layout.content_growth_refs) - growth_ids)
    for missing_id in missing_growth:
        findings.append(LayoutFinding("PL016", missing_id, "content growth ref does not resolve"))
    for rule in growth_rule_list:
        if not _surface_ref_resolves(rule.target_ref, surface_ids):
            findings.append(LayoutFinding("PL016", rule.target_ref, "content growth target_ref does not resolve"))

    completeness_ids = {rule.completeness_id for rule in completeness_rule_list}
    missing_completeness = sorted(set(layout.information_completeness_refs) - completeness_ids)
    for missing_id in missing_completeness:
        findings.append(LayoutFinding("PL016", missing_id, "information completeness ref does not resolve"))

    if layout.z_axis_refs and z_axis_layering.z_axis_layer_id not in set(layout.z_axis_refs):
        findings.append(LayoutFinding("PL016", z_axis_layering.z_axis_layer_id, "z-axis layering is not referenced by layout"))
    for layer in z_axis_layering.layers:
        if not _surface_ref_resolves(layer.surface_ref, surface_ids):
            findings.append(LayoutFinding("PL016", layer.surface_ref, "z-axis surface_ref does not resolve"))
    if layout.figma_metadata_ref and layout.figma_metadata_ref != figma_metadata.figma_metadata_id:
        findings.append(LayoutFinding("PL016", layout.figma_metadata_ref, "figma metadata ref does not resolve"))
    if state_index.index_id not in layout.state_variants:
        findings.append(LayoutFinding("PL016", state_index.index_id, "state placement index is not referenced by layout state_variants"))
    for placement in state_index.placements:
        if not _surface_ref_resolves(placement.surface_id, surface_ids):
            findings.append(LayoutFinding("PL016", placement.surface_id, "state placement surface_id does not resolve"))
    return findings


def natural_language_layout_from_mapping(record: Mapping[str, object]) -> NaturalLanguageLayout:
    return NaturalLanguageLayout(
        layout_id=str(record["layout_id"]),
        surface_id=str(record["surface_id"]),
        layout_body_ref=str(record["layout_body_ref"]),
        layout_text=str(record["layout_text"]),
        semantic_authority=str(record["semantic_authority"]),
        inventory_role=str(record["inventory_role"]),
        carrier_profile_refs=_string_list(record["carrier_profile_refs"]),
        section_index=_string_list(record["section_index"]),
        containment_tree_ref=str(record["containment_tree_ref"]),
        pattern_refs=_string_list(record.get("pattern_refs", [])),
        state_variants=_string_list(record.get("state_variants", [])),
        content_growth_refs=_string_list(record["content_growth_refs"]),
        z_axis_refs=_string_list(record.get("z_axis_refs", [])),
        information_completeness_refs=_string_list(record["information_completeness_refs"]),
        figma_metadata_ref=_optional_string(record.get("figma_metadata_ref")),
        trace_refs=_string_list(record["trace_refs"]),
    )


def carrier_adaptation_profile_from_mapping(record: Mapping[str, object]) -> CarrierAdaptationProfile:
    carrier_rules = {
        Carrier(str(carrier_name)): carrier_rule_from_mapping(rule)
        for carrier_name, rule in _mapping(record["carrier_rules"]).items()
    }
    unsupported = record.get("unsupported_carriers")
    unsupported_carriers = None
    if isinstance(unsupported, Mapping):
        unsupported_carriers = {Carrier(str(carrier)): str(reason) for carrier, reason in unsupported.items()}
    return CarrierAdaptationProfile(
        carrier_profile_id=str(record["carrier_profile_id"]),
        required_carriers=[Carrier(str(carrier)) for carrier in _string_list(record["required_carriers"])],
        carrier_rules=carrier_rules,
        unsupported_carriers=unsupported_carriers,
    )


def carrier_rule_from_mapping(record: Mapping[str, object]) -> CarrierRule:
    return CarrierRule(
        arrangement=str(record["arrangement"]),
        width_behavior=str(record["width_behavior"]),
        height_scroll_behavior=str(record["height_scroll_behavior"]),
        navigation_placement=str(record["navigation_placement"]),
        safe_area_or_system_bars=str(record["safe_area_or_system_bars"]),
        input_keyboard_behavior=str(record["input_keyboard_behavior"]),
        platform_constraints=_string_list(record["platform_constraints"]),
    )


def containment_hierarchy_from_mapping(record: Mapping[str, object]) -> ContainmentHierarchy:
    return ContainmentHierarchy(
        hierarchy_id=str(record["hierarchy_id"]),
        surface_id=str(record["surface_id"]),
        nodes=[containment_node_from_mapping(node) for node in _mapping_list(record["nodes"])],
    )


def containment_node_from_mapping(record: Mapping[str, object]) -> ContainmentNode:
    return ContainmentNode(
        node_id=str(record["node_id"]),
        surface_kind=SurfaceKind(str(record["surface_kind"])),
        parent_id=_optional_string(record.get("parent_id")),
        order=int(record["order"]),
        arrangement=str(record["arrangement"]),
        sizing=str(record["sizing"]),
        scroll_behavior=str(record["scroll_behavior"]),
        width_behavior=str(record["width_behavior"]),
        entry_context=_optional_string(record.get("entry_context")),
        return_placement=_optional_string(record.get("return_placement")),
    )


def content_growth_rule_from_mapping(record: Mapping[str, object]) -> ContentGrowthRule:
    return ContentGrowthRule(
        growth_rule_id=str(record["growth_rule_id"]),
        target_ref=str(record["target_ref"]),
        variable_content=_string_list(record["variable_content"]),
        wrapping=str(record["wrapping"]),
        overflow=str(record["overflow"]),
        scroll=str(record["scroll"]),
        collapse=_optional_string(record.get("collapse")),
        truncation=_optional_string(record.get("truncation")),
        truncation_recovery=_optional_string(record.get("truncation_recovery")),
        expansion=_optional_string(record.get("expansion")),
        pagination=_optional_string(record.get("pagination")),
        empty_behavior=str(record["empty_behavior"]),
        trace_refs=_string_list(record["trace_refs"]),
    )


def information_completeness_rule_from_mapping(record: Mapping[str, object]) -> InformationCompletenessRule:
    return InformationCompletenessRule(
        completeness_id=str(record["completeness_id"]),
        required_information_refs=_string_list(record["required_information_refs"]),
        height_behavior=str(record["height_behavior"]),
        width_behavior=str(record["width_behavior"]),
        information_access_path=str(record["information_access_path"]),
        trace_refs=_string_list(record["trace_refs"]),
        horizontal_scroll_exception=_optional_string(record.get("horizontal_scroll_exception")),
    )


def z_axis_layering_from_mapping(record: Mapping[str, object]) -> ZAxisLayering:
    return ZAxisLayering(
        z_axis_layer_id=str(record["z_axis_layer_id"]),
        layers=[
            ZAxisLayer(
                layer=int(layer["layer"]),
                surface_ref=str(layer["surface_ref"]),
                layer_kind=LayerKind(str(layer["layer_kind"])),
                blocks_lower_layers=bool(layer["blocks_lower_layers"]),
                preserves_background_context=bool(layer["preserves_background_context"]),
                occlusion_rule=str(layer["occlusion_rule"]),
            )
            for layer in _mapping_list(record["layers"])
        ],
        material_elevation_intent=_optional_string(record.get("material_elevation_intent")),
        focus_restoration=str(record["focus_restoration"]),
        trace_refs=_string_list(record["trace_refs"]),
    )


def state_placement_index_from_mapping(record: Mapping[str, object]) -> StatePlacementIndex:
    return StatePlacementIndex(
        index_id=str(record["index_id"]),
        placements=[state_placement_record_from_mapping(item) for item in _mapping_list(record["placements"])],
    )


def state_placement_record_from_mapping(record: Mapping[str, object]) -> StatePlacementRecord:
    return StatePlacementRecord(
        message_id=str(record["message_id"]),
        state_type=str(record["state_type"]),
        presentation_mode=str(record["presentation_mode"]),
        layout_placement=str(record["layout_placement"]),
        surface_id=str(record["surface_id"]),
        trace_refs=_string_list(record["trace_refs"]),
    )


def figma_reconstruction_metadata_from_mapping(record: Mapping[str, object]) -> FigmaReconstructionMetadata:
    return FigmaReconstructionMetadata(
        figma_metadata_id=str(record["figma_metadata_id"]),
        layout_id=str(record["layout_id"]),
        frame_hierarchy=_string_list(record["frame_hierarchy"]),
        selection_box_hierarchy=_string_list(record["selection_box_hierarchy"]),
        auto_layout_guidance=str(record["auto_layout_guidance"]),
        component_instances=_string_list(record.get("component_instances", [])),
        state_variants=_string_list(record.get("state_variants", [])),
        carrier_variants=_string_list(record["carrier_variants"]),
        z_axis_layers=_string_list(record.get("z_axis_layers", [])),
        scroll_frames=_string_list(record["scroll_frames"]),
        constraints=_string_list(record["constraints"]),
        non_goals=_string_list(record["non_goals"]),
        trace_refs=_string_list(record["trace_refs"]),
        page_arrangement_order=[
            dict(item)
            for item in record.get("page_arrangement_order", [])
            if isinstance(item, Mapping)
        ],
    )


def _collect(code: str, subject_id: str, check) -> List[LayoutFinding]:
    try:
        check()
    except ValueError as exc:
        return [LayoutFinding(code=code, subject_id=subject_id, message=str(exc))]
    return []


def _contradicts_parent(value: str) -> bool:
    lowered = value.lower()
    if "without contradiction" in lowered or "no contradiction" in lowered:
        return False
    return "contradict" in lowered or "exceeds parent" in lowered or "ignore parent" in lowered


def _has_access_path(value: str) -> bool:
    lowered = value.lower()
    if "no recovery" in lowered or "no access" in lowered or "unrecoverable" in lowered:
        return False
    return any(term in lowered for term in ["scroll", "expand", "pagination", "disclosure", "open", "detail", "recover"])


def _has_horizontal_scroll_exception(rule: InformationCompletenessRule) -> bool:
    exception = (rule.horizontal_scroll_exception or "").lower()
    width_text = f"{rule.width_behavior} {rule.information_access_path}".lower()
    if not exception:
        return False
    return any(term in exception for term in HORIZONTAL_SCROLL_TERMS) and any(
        term in width_text for term in HORIZONTAL_SCROLL_TERMS | {"overflow offscreen"}
    )


def _inventory_is_index_only(value: str) -> bool:
    has_index = "index" in value
    has_validation = "validation" in value or "check" in value
    has_limited_role = "skeleton" in value or "only" in value
    no_semantic_authority = all(term not in value for term in ["canonical", "authority", "source of truth"])
    return has_index and has_validation and has_limited_role and no_semantic_authority


def _surface_ref_resolves(surface_ref: str, surface_ids: Set[str]) -> bool:
    if surface_ref in surface_ids:
        return True
    parts = surface_ref.split(".")
    for end in range(len(parts) - 1, 0, -1):
        if ".".join(parts[:end]) in surface_ids:
            return True
    return False


def _max_depth(hierarchy: ContainmentHierarchy) -> int:
    children_by_parent = {}
    for node in hierarchy.nodes:
        children_by_parent.setdefault(node.parent_id, []).append(node.node_id)

    def depth(node_id: str, seen: Set[str]) -> int:
        if node_id in seen:
            return 0
        child_ids = children_by_parent.get(node_id, [])
        if not child_ids:
            return 1
        return 1 + max(depth(child_id, seen | {node_id}) for child_id in child_ids)

    roots = children_by_parent.get(None, [])
    if not roots:
        return 0
    return max(depth(root, set()) for root in roots)


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("expected mapping")
    return value


def _mapping_list(value: object) -> List[Mapping[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise ValueError("expected list of mapping records")
    return value


def _optional_string(value: object):
    if value is None:
        return None
    return str(value)


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        raise ValueError("expected list")
    return [str(item) for item in value]
