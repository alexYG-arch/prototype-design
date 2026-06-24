"""Presentation consistency and shared pattern rule primitives."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class PatternKind(str, Enum):
    COMPONENT = "COMPONENT"
    PRESENTATION_PATTERN = "PRESENTATION_PATTERN"
    LAYOUT_PATTERN = "LAYOUT_PATTERN"
    INTERACTION_PATTERN = "INTERACTION_PATTERN"


class PresentationMode(str, Enum):
    INLINE_MESSAGE = "INLINE_MESSAGE"
    BANNER = "BANNER"
    TOAST = "TOAST"
    MODAL_DIALOG = "MODAL_DIALOG"
    EMPTY_STATE = "EMPTY_STATE"
    TABLE_OR_LIST_STATE = "TABLE_OR_LIST_STATE"
    DETAIL_PANEL = "DETAIL_PANEL"
    HELP_TEXT = "HELP_TEXT"
    STATUS_BADGE = "STATUS_BADGE"
    ERROR_SUMMARY = "ERROR_SUMMARY"


VISUAL_ONLY_TERMS = {
    "blue",
    "red",
    "green",
    "rounded",
    "icon",
    "shadow",
    "gradient",
    "looks similar",
    "same color",
    "visual",
}

TRANSIENT_ONLY_MODES = {PresentationMode.TOAST}
SUSTAINED_LIFECYCLES = {"until resolved", "session", "persistent", "audit"}


@dataclass(frozen=True)
class SharedComponentPattern:
    pattern_id: str
    pattern_kind: PatternKind
    semantic_role: str
    data_structure: List[str]
    operation_set: List[str]
    state_model: List[str]
    information_hierarchy: List[str]
    interaction_model: List[str]
    surface_constraints: List[str]
    reuse_scope: List[str]
    trace_refs: List[str]
    reuse_reason: Optional[str] = None
    non_reuse_reason: Optional[str] = None

    def require_complete(self) -> None:
        _require_text(self.pattern_id, "pattern_id")
        _require_text(self.semantic_role, "semantic_role")
        _require_non_empty(self.data_structure, "data_structure")
        _require_non_empty(self.operation_set, "operation_set")
        _require_non_empty(self.state_model, "state_model")
        _require_non_empty(self.information_hierarchy, "information_hierarchy")
        _require_non_empty(self.interaction_model, "interaction_model")
        _require_non_empty(self.surface_constraints, "surface_constraints")
        _require_non_empty(self.reuse_scope, "reuse_scope")
        _require_non_empty(self.trace_refs, "trace_refs")

    def reject_visual_only_reuse(self) -> None:
        text = " ".join([self.semantic_role, self.reuse_reason or "", " ".join(self.reuse_scope)]).lower()
        has_visual_reason = any(term in text for term in VISUAL_ONLY_TERMS)
        has_semantic_support = all(
            [
                self.data_structure,
                self.operation_set,
                self.state_model,
                self.information_hierarchy,
                self.interaction_model,
            ]
        )
        if has_visual_reason and not has_semantic_support:
            raise ValueError("shared pattern cannot be justified by visual similarity only")


@dataclass(frozen=True)
class InformationPresentationDecision:
    presentation_id: str
    semantic_intent: str
    trigger_condition: str
    scope: str
    information_lifecycle: str
    presentation_mode: PresentationMode
    recoverability: str
    trace_refs: List[str]
    user_decision_need: bool = False
    sustained_processing_required: bool = False
    message_ref: Optional[str] = None
    reason_for_difference: Optional[str] = None

    def consistency_key(self) -> Tuple[str, str, str, str]:
        return (
            self.semantic_intent.strip().lower(),
            self.trigger_condition.strip().lower(),
            self.scope.strip().lower(),
            self.information_lifecycle.strip().lower(),
        )

    def require_complete(self) -> None:
        _require_text(self.presentation_id, "presentation_id")
        _require_text(self.semantic_intent, "semantic_intent")
        _require_text(self.trigger_condition, "trigger_condition")
        _require_text(self.scope, "scope")
        _require_text(self.information_lifecycle, "information_lifecycle")
        _require_text(self.recoverability, "recoverability")
        _require_non_empty(self.trace_refs, "trace_refs")

    def reject_transient_only_sustained_information(self) -> None:
        sustained = (
            self.user_decision_need
            or self.sustained_processing_required
            or self.information_lifecycle.strip().lower() in SUSTAINED_LIFECYCLES
        )
        unrecoverable = "unrecoverable" in self.recoverability.lower() or "not recoverable" in self.recoverability.lower()
        if sustained and self.presentation_mode in TRANSIENT_ONLY_MODES and unrecoverable:
            raise ValueError("sustained or decision information cannot be transient-only and unrecoverable")


@dataclass(frozen=True)
class PresentationConsistencyException:
    exception_id: str
    semantic_intent: str
    trigger_condition: str
    scope: str
    information_lifecycle: str
    allowed_modes: List[PresentationMode]
    reason: str
    trace_refs: List[str]

    def consistency_key(self) -> Tuple[str, str, str, str]:
        return (
            self.semantic_intent.strip().lower(),
            self.trigger_condition.strip().lower(),
            self.scope.strip().lower(),
            self.information_lifecycle.strip().lower(),
        )

    def require_complete(self) -> None:
        _require_text(self.exception_id, "exception_id")
        _require_text(self.reason, "reason")
        _require_non_empty([mode.value for mode in self.allowed_modes], "allowed_modes")
        _require_non_empty(self.trace_refs, "trace_refs")


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")


def _require_non_empty(values: List[str], field: str) -> None:
    if not values or not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"{field} must be a non-empty list of text")
