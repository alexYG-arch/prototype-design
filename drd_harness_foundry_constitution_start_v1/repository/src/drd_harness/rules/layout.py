"""Natural-language layout and reconstruction metadata rule primitives."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Carrier(str, Enum):
    DESKTOP = "DESKTOP"
    TABLET = "TABLET"
    MOBILE = "MOBILE"
    MOBILE_IOS = "MOBILE_IOS"
    MOBILE_MATERIAL = "MOBILE_MATERIAL"


class SurfaceKind(str, Enum):
    PAGE = "PAGE"
    SECTION = "SECTION"
    GROUP = "GROUP"
    REPEATED_ITEM = "REPEATED_ITEM"
    OVERLAY = "OVERLAY"
    DRAWER = "DRAWER"
    PANEL = "PANEL"
    POPOVER = "POPOVER"
    STATE_CONTAINER = "STATE_CONTAINER"


class LayerKind(str, Enum):
    BASE = "BASE"
    STICKY = "STICKY"
    FIXED = "FIXED"
    OVERLAY = "OVERLAY"
    MODAL = "MODAL"
    DRAWER = "DRAWER"
    POPOVER = "POPOVER"
    MENU = "MENU"
    TOAST = "TOAST"
    SNACKBAR = "SNACKBAR"
    LOADING = "LOADING"


LAYOUT_COVERAGE_TERMS = {
    "carrier": ["desktop", "tablet", "mobile", "ios", "material", "carrier"],
    "spatial": ["column", "row", "stack", "region", "section", "frame", "container"],
    "hierarchy": ["hierarchy", "primary", "secondary", "group", "header", "main"],
    "containment": ["contain", "inside", "parent", "child", "nested", "group"],
    "ordering": ["order", "above", "below", "before", "after", "then"],
    "sizing": ["width", "height", "minimum", "maximum", "density", "sizing"],
    "scrolling": ["scroll", "sticky", "fixed", "overflow"],
    "states": ["empty", "loading", "error", "disabled", "permission", "success", "recovery", "state"],
    "growth": ["wrap", "overflow", "truncate", "expand", "pagination", "growth", "long"],
    "layering": ["z-axis", "elevation", "overlay", "modal", "drawer", "popover", "layer"],
    "constraints": ["safe area", "system bar", "keyboard", "constraint", "responsive"],
}

HEIGHT_LOSS_TERMS = {"hide", "omit", "remove", "drop", "first three", "screen is short"}
WIDTH_FATAL_TERMS = {"ignore width", "no width constraint", "clip without recovery"}
WIDTH_HORIZONTAL_EXCEPTION_TERMS = {"overflow offscreen"}
HORIZONTAL_SCROLL_TERMS = {"horizontal scroll", "sideways scroll", "side-scroll", "table scroll", "carousel scroll"}
FIGMA_WRITE_TERMS = {"figma api", "write to figma", "renderer implementation", "file write", "canonical figma"}


@dataclass(frozen=True)
class CarrierRule:
    arrangement: str
    width_behavior: str
    height_scroll_behavior: str
    navigation_placement: str
    safe_area_or_system_bars: str
    input_keyboard_behavior: str
    platform_constraints: List[str]

    def require_complete(self, carrier: Carrier) -> None:
        _require_text(self.arrangement, f"{carrier.value}.arrangement")
        _require_text(self.width_behavior, f"{carrier.value}.width_behavior")
        _require_text(self.height_scroll_behavior, f"{carrier.value}.height_scroll_behavior")
        _require_text(self.navigation_placement, f"{carrier.value}.navigation_placement")
        _require_text(self.safe_area_or_system_bars, f"{carrier.value}.safe_area_or_system_bars")
        _require_text(self.input_keyboard_behavior, f"{carrier.value}.input_keyboard_behavior")
        _require_non_empty(self.platform_constraints, f"{carrier.value}.platform_constraints")


@dataclass(frozen=True)
class CarrierAdaptationProfile:
    carrier_profile_id: str
    required_carriers: List[Carrier]
    carrier_rules: Dict[Carrier, CarrierRule]
    unsupported_carriers: Optional[Dict[Carrier, str]] = None

    def require_complete(self) -> None:
        _require_text(self.carrier_profile_id, "carrier_profile_id")
        if not self.required_carriers:
            raise ValueError("required_carriers must not be empty")
        for carrier in self.required_carriers:
            if carrier not in self.carrier_rules:
                raise ValueError(f"required carrier {carrier.value} lacks adaptation rule")
            self.carrier_rules[carrier].require_complete(carrier)


@dataclass(frozen=True)
class ContainmentNode:
    node_id: str
    surface_kind: SurfaceKind
    parent_id: Optional[str]
    order: int
    arrangement: str
    sizing: str
    scroll_behavior: str
    width_behavior: str
    entry_context: Optional[str] = None
    return_placement: Optional[str] = None

    def require_local_layout(self) -> None:
        _require_text(self.node_id, "node_id")
        _require_text(self.arrangement, "arrangement")
        _require_text(self.sizing, "sizing")
        _require_text(self.scroll_behavior, "scroll_behavior")
        _require_text(self.width_behavior, "width_behavior")
        if self.order < 0:
            raise ValueError("order must be zero or greater")

    def require_nested_surface_context(self) -> None:
        if self.surface_kind not in {SurfaceKind.OVERLAY, SurfaceKind.DRAWER, SurfaceKind.PANEL, SurfaceKind.POPOVER}:
            return
        _require_text(self.entry_context or "", "entry_context")
        _require_text(self.return_placement or "", "return_placement")


@dataclass(frozen=True)
class ContainmentHierarchy:
    hierarchy_id: str
    surface_id: str
    nodes: List[ContainmentNode]

    def node_ids(self) -> set:
        return {node.node_id for node in self.nodes}


@dataclass(frozen=True)
class ContentGrowthRule:
    growth_rule_id: str
    target_ref: str
    variable_content: List[str]
    wrapping: str
    overflow: str
    scroll: str
    collapse: Optional[str]
    truncation: Optional[str]
    truncation_recovery: Optional[str]
    expansion: Optional[str]
    pagination: Optional[str]
    empty_behavior: str
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.growth_rule_id, "growth_rule_id")
        _require_text(self.target_ref, "target_ref")
        _require_non_empty(self.variable_content, "variable_content")
        _require_text(self.wrapping, "wrapping")
        _require_text(self.overflow, "overflow")
        _require_text(self.scroll, "scroll")
        _require_text(self.empty_behavior, "empty_behavior")
        _require_non_empty(self.trace_refs, "trace_refs")
        if self.truncation and not self.truncation_recovery:
            raise ValueError("truncation requires recovery path")


@dataclass(frozen=True)
class InformationCompletenessRule:
    completeness_id: str
    required_information_refs: List[str]
    height_behavior: str
    width_behavior: str
    information_access_path: str
    trace_refs: List[str]
    horizontal_scroll_exception: Optional[str] = None

    def require_complete(self) -> None:
        _require_text(self.completeness_id, "completeness_id")
        _require_non_empty(self.required_information_refs, "required_information_refs")
        _require_text(self.height_behavior, "height_behavior")
        _require_text(self.width_behavior, "width_behavior")
        _require_text(self.information_access_path, "information_access_path")
        _require_non_empty(self.trace_refs, "trace_refs")


@dataclass(frozen=True)
class ZAxisLayer:
    layer: int
    surface_ref: str
    layer_kind: LayerKind
    blocks_lower_layers: bool
    preserves_background_context: bool
    occlusion_rule: str

    def require_complete(self) -> None:
        _require_text(self.surface_ref, "surface_ref")
        _require_text(self.occlusion_rule, "occlusion_rule")


@dataclass(frozen=True)
class ZAxisLayering:
    z_axis_layer_id: str
    layers: List[ZAxisLayer]
    material_elevation_intent: Optional[str]
    focus_restoration: str
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.z_axis_layer_id, "z_axis_layer_id")
        if not self.layers:
            raise ValueError("layers must not be empty")
        for layer in self.layers:
            layer.require_complete()
        _require_text(self.focus_restoration, "focus_restoration")
        _require_non_empty(self.trace_refs, "trace_refs")


@dataclass(frozen=True)
class StatePlacementRecord:
    message_id: str
    state_type: str
    presentation_mode: str
    layout_placement: str
    surface_id: str
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.message_id, "message_id")
        _require_text(self.state_type, "state_type")
        _require_text(self.presentation_mode, "presentation_mode")
        _require_text(self.layout_placement, "layout_placement")
        _require_text(self.surface_id, "surface_id")
        _require_non_empty(self.trace_refs, "trace_refs")


@dataclass(frozen=True)
class StatePlacementIndex:
    index_id: str
    placements: List[StatePlacementRecord]

    def message_ids(self) -> set:
        return {placement.message_id for placement in self.placements}


@dataclass(frozen=True)
class NaturalLanguageLayout:
    layout_id: str
    surface_id: str
    layout_body_ref: str
    layout_text: str
    semantic_authority: str
    inventory_role: str
    carrier_profile_refs: List[str]
    section_index: List[str]
    containment_tree_ref: str
    pattern_refs: List[str]
    state_variants: List[str]
    content_growth_refs: List[str]
    z_axis_refs: List[str]
    information_completeness_refs: List[str]
    figma_metadata_ref: Optional[str]
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.layout_id, "layout_id")
        _require_text(self.surface_id, "surface_id")
        _require_text(self.layout_body_ref, "layout_body_ref")
        _require_text(self.layout_text, "layout_text")
        _require_text(self.semantic_authority, "semantic_authority")
        _require_text(self.inventory_role, "inventory_role")
        _require_non_empty(self.carrier_profile_refs, "carrier_profile_refs")
        _require_non_empty(self.section_index, "section_index")
        _require_text(self.containment_tree_ref, "containment_tree_ref")
        _require_non_empty(self.content_growth_refs, "content_growth_refs")
        _require_non_empty(self.information_completeness_refs, "information_completeness_refs")
        _require_non_empty(self.trace_refs, "trace_refs")


@dataclass(frozen=True)
class FigmaReconstructionMetadata:
    figma_metadata_id: str
    layout_id: str
    frame_hierarchy: List[str]
    selection_box_hierarchy: List[str]
    auto_layout_guidance: str
    component_instances: List[str]
    state_variants: List[str]
    carrier_variants: List[str]
    z_axis_layers: List[str]
    scroll_frames: List[str]
    constraints: List[str]
    non_goals: List[str]
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.figma_metadata_id, "figma_metadata_id")
        _require_text(self.layout_id, "layout_id")
        _require_non_empty(self.frame_hierarchy, "frame_hierarchy")
        _require_non_empty(self.selection_box_hierarchy, "selection_box_hierarchy")
        _require_text(self.auto_layout_guidance, "auto_layout_guidance")
        _require_non_empty(self.carrier_variants, "carrier_variants")
        _require_non_empty(self.scroll_frames, "scroll_frames")
        _require_non_empty(self.constraints, "constraints")
        _require_non_empty(self.non_goals, "non_goals")
        _require_non_empty(self.trace_refs, "trace_refs")


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")


def _require_non_empty(values: List[str], field: str) -> None:
    if not values or not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"{field} must be a non-empty list of text")
