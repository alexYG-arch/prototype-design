"""Validators for natural-language layout completeness and reconstruction metadata."""

from dataclasses import dataclass
from typing import Iterable, List, Set

from drd_harness.rules.layout import (
    Carrier,
    ContainmentHierarchy,
    ContentGrowthRule,
    FIGMA_WRITE_TERMS,
    FigmaReconstructionMetadata,
    HEIGHT_LOSS_TERMS,
    InformationCompletenessRule,
    LAYOUT_COVERAGE_TERMS,
    LayerKind,
    NaturalLanguageLayout,
    StatePlacementIndex,
    SurfaceKind,
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
    placed = index.message_ids()
    for message_id in required_message_ids:
        if message_id not in placed:
            findings.append(LayoutFinding("PL011", message_id, "interaction message lacks layout placement"))
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
) -> List[LayoutFinding]:
    findings: List[LayoutFinding] = []
    findings.extend(validate_natural_language_layout(layout))
    findings.extend(validate_carrier_adaptation_profile(carrier_profile))
    findings.extend(validate_containment_hierarchy(hierarchy))
    for rule in growth_rules:
        findings.extend(validate_content_growth_rule(rule))
    for rule in completeness_rules:
        findings.extend(validate_information_completeness_rule(rule))
    material_required = Carrier.MOBILE_MATERIAL in carrier_profile.required_carriers
    findings.extend(validate_z_axis_layering(z_axis_layering, material_required))
    findings.extend(validate_state_placement_index(state_index, required_message_ids))
    findings.extend(validate_nested_surface_layout(hierarchy))
    findings.extend(validate_figma_metadata(figma_metadata, layout))
    return findings


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
