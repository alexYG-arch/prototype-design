"""Interaction graph and Reaction rule primitives."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class NodeType(str, Enum):
    PAGE = "PAGE"
    STATE = "STATE"
    OVERLAY = "OVERLAY"
    PROCESSING = "PROCESSING"
    EXTERNAL_HANDOFF = "EXTERNAL_HANDOFF"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TERMINAL = "TERMINAL"


class EdgeType(str, Enum):
    NAVIGATES_TO = "NAVIGATES_TO"
    OPENS_OVERLAY = "OPENS_OVERLAY"
    CLOSES_OVERLAY = "CLOSES_OVERLAY"
    SUBMITS_ACTION = "SUBMITS_ACTION"
    STARTS_ASYNC = "STARTS_ASYNC"
    ASYNC_SUCCESS = "ASYNC_SUCCESS"
    ASYNC_FAILURE = "ASYNC_FAILURE"
    HANDOFF_EXTERNAL = "HANDOFF_EXTERNAL"
    HANDOFF_SUCCESS = "HANDOFF_SUCCESS"
    HANDOFF_CANCEL = "HANDOFF_CANCEL"
    HANDOFF_FAILURE = "HANDOFF_FAILURE"
    RETRIES = "RETRIES"
    CANCELS = "CANCELS"
    EXITS = "EXITS"
    TERMINATES = "TERMINATES"


class ReactionType(str, Enum):
    NAVIGATE = "NAVIGATE"
    OPEN_OVERLAY = "OPEN_OVERLAY"
    CLOSE_OVERLAY = "CLOSE_OVERLAY"
    SUBMIT = "SUBMIT"
    START_ASYNC = "START_ASYNC"
    SELECT = "SELECT"
    TOGGLE = "TOGGLE"
    RETRY = "RETRY"
    CANCEL = "CANCEL"
    EXIT = "EXIT"
    HANDOFF = "HANDOFF"
    TERMINATE = "TERMINATE"


class FailureApplicability(str, Enum):
    CAN_FAIL = "CAN_FAIL"
    CANNOT_FAIL = "CANNOT_FAIL"
    UNKNOWN_REQUIRES_REVIEW = "UNKNOWN_REQUIRES_REVIEW"


class CancelApplicability(str, Enum):
    CANCELLABLE = "CANCELLABLE"
    NOT_CANCELLABLE = "NOT_CANCELLABLE"
    UNKNOWN_REQUIRES_REVIEW = "UNKNOWN_REQUIRES_REVIEW"


class AsyncApplicability(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    NON_IMMEDIATE = "NON_IMMEDIATE"
    UNKNOWN_REQUIRES_REVIEW = "UNKNOWN_REQUIRES_REVIEW"


class HandoffApplicability(str, Enum):
    INTERNAL_ONLY = "INTERNAL_ONLY"
    EXTERNAL_HANDOFF = "EXTERNAL_HANDOFF"
    UNKNOWN_REQUIRES_REVIEW = "UNKNOWN_REQUIRES_REVIEW"


class MessageType(str, Enum):
    PROCESSING_MESSAGE = "PROCESSING_MESSAGE"
    SUCCESS_MESSAGE = "SUCCESS_MESSAGE"
    FAILURE_MESSAGE = "FAILURE_MESSAGE"
    VALIDATION_MESSAGE = "VALIDATION_MESSAGE"
    DISABLED_REASON = "DISABLED_REASON"
    CANCEL_CONFIRMATION = "CANCEL_CONFIRMATION"
    EXIT_CONSEQUENCE = "EXIT_CONSEQUENCE"
    HANDOFF_NOTICE = "HANDOFF_NOTICE"
    RECOVERY_INSTRUCTION = "RECOVERY_INSTRUCTION"
    EMPTY_STATE_MESSAGE = "EMPTY_STATE_MESSAGE"
    PERMISSION_BLOCK_MESSAGE = "PERMISSION_BLOCK_MESSAGE"


class DuplicateTriggerStrategy(str, Enum):
    DISABLE_DUPLICATE_TRIGGER = "DISABLE_DUPLICATE_TRIGGER"
    IGNORE_WITH_VISIBLE_STATE = "IGNORE_WITH_VISIBLE_STATE"
    QUEUE_DUPLICATE_TRIGGER = "QUEUE_DUPLICATE_TRIGGER"
    IDEMPOTENT_RETRY = "IDEMPOTENT_RETRY"
    CANCEL_AND_RESTART = "CANCEL_AND_RESTART"


UNKNOWN_APPLICABILITY = "UNKNOWN_REQUIRES_REVIEW"

PRODUCT_SCOPE_TERMS = {
    "integration",
    "salesforce",
    "sync",
    "pricing",
    "billing",
    "automation",
    "new role",
    "data retention",
    "export to",
}


@dataclass(frozen=True)
class InteractionNode:
    node_id: str
    node_type: NodeType
    source_refs: List[str]
    is_terminal: bool = False
    terminal_reason: Optional[str] = None
    message_refs: Optional[List[str]] = None
    failure_reason: Optional[str] = None
    recovery_targets: Optional[List[str]] = None
    resume_source: Optional[str] = None
    trap_justification: Optional[str] = None

    def require_complete(self) -> None:
        _require_text(self.node_id, "node_id")
        _require_non_empty(self.source_refs, "source_refs")
        if self.is_terminal and not self.terminal_reason:
            raise ValueError("terminal node requires terminal_reason")


@dataclass(frozen=True)
class InteractionEdge:
    edge_id: str
    source_node_id: str
    target_ref: str
    edge_type: EdgeType


@dataclass(frozen=True)
class Clickable:
    clickable_id: str
    source_node_id: str
    label_or_affordance: str
    clickable_type: str
    source_refs: List[str]
    enabled_conditions: List[str]
    disabled_behavior: Optional[str]
    reaction_id: str

    def require_reaction(self) -> None:
        _require_text(self.clickable_id, "clickable_id")
        _require_text(self.reaction_id, "reaction_id")
        _require_text(self.source_node_id, "source_node_id")
        _require_text(self.label_or_affordance, "label_or_affordance")
        _require_non_empty(self.source_refs, "source_refs")


@dataclass(frozen=True)
class ReactionRecord:
    reaction_id: str
    clickable_id: str
    source_node_id: str
    reaction_type: ReactionType
    target_ref: str
    preconditions: List[str]
    failure_applicability: FailureApplicability
    cancel_applicability: CancelApplicability
    async_applicability: AsyncApplicability
    handoff_applicability: HandoffApplicability
    success_behavior: str
    failure_behavior: Optional[str]
    cancel_behavior: Optional[str]
    exception_behavior: Optional[str]
    message_refs: List[str]
    trace_refs: List[str]
    repeat_trigger_strategy: Optional[DuplicateTriggerStrategy] = None
    no_return_terminal: Optional[str] = None

    def require_complete(self) -> None:
        _require_text(self.reaction_id, "reaction_id")
        _require_text(self.clickable_id, "clickable_id")
        _require_text(self.source_node_id, "source_node_id")
        _require_text(self.target_ref, "target_ref")
        _require_text(self.success_behavior, "success_behavior")
        _require_non_empty(self.trace_refs, "trace_refs")
        for value in (
            self.failure_applicability.value,
            self.cancel_applicability.value,
            self.async_applicability.value,
            self.handoff_applicability.value,
        ):
            if value == UNKNOWN_APPLICABILITY:
                raise ValueError("reaction applicability cannot be UNKNOWN_REQUIRES_REVIEW in canonical input")
        if self.failure_applicability == FailureApplicability.CAN_FAIL and not self.failure_behavior:
            raise ValueError("failure-prone reaction requires failure_behavior")
        if self.cancel_applicability == CancelApplicability.CANCELLABLE and not self.cancel_behavior:
            raise ValueError("cancellable reaction requires cancel_behavior")
        if self.async_applicability == AsyncApplicability.NON_IMMEDIATE and not self.repeat_trigger_strategy:
            raise ValueError("non-immediate reaction requires repeat_trigger_strategy")


@dataclass(frozen=True)
class InteractionMessage:
    message_id: str
    message_type: MessageType
    node_id: str
    reaction_id: Optional[str]
    trigger_condition: str
    user_visible_summary: str
    required_user_next_step: str
    recovery_targets: List[str]
    trace_refs: List[str]

    def require_complete(self) -> None:
        _require_text(self.message_id, "message_id")
        _require_text(self.node_id, "node_id")
        _require_text(self.trigger_condition, "trigger_condition")
        _require_text(self.user_visible_summary, "user_visible_summary")
        _require_text(self.required_user_next_step, "required_user_next_step")
        _require_non_empty(self.trace_refs, "trace_refs")


@dataclass(frozen=True)
class InteractionGraph:
    graph_id: str
    entry_node_ids: List[str]
    nodes: List[InteractionNode]
    edges: List[InteractionEdge]
    clickables: List[Clickable]
    reactions: List[ReactionRecord]
    messages: List[InteractionMessage]

    def node_ids(self) -> set:
        return {node.node_id for node in self.nodes}

    def reaction_ids(self) -> set:
        return {reaction.reaction_id for reaction in self.reactions}

    def message_ids(self) -> set:
        return {message.message_id for message in self.messages}


def message_has_product_scope_expansion(message: InteractionMessage) -> bool:
    text = f"{message.user_visible_summary} {message.required_user_next_step}".lower()
    return any(term in text for term in PRODUCT_SCOPE_TERMS)


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")


def _require_non_empty(values: List[str], field: str) -> None:
    if not values or not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"{field} must be a non-empty list of text")
