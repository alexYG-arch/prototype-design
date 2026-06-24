"""Interaction graph closure validators."""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

from drd_harness.rules.interaction import (
    AsyncApplicability,
    CancelApplicability,
    EdgeType,
    FailureApplicability,
    HandoffApplicability,
    InteractionGraph,
    InteractionNode,
    MessageType,
    NodeType,
    ReactionType,
    message_has_product_scope_expansion,
)


@dataclass(frozen=True)
class InteractionFinding:
    code: str
    subject_id: str
    message: str


CONTINUATION_EDGES = {
    EdgeType.NAVIGATES_TO,
    EdgeType.CLOSES_OVERLAY,
    EdgeType.SUBMITS_ACTION,
    EdgeType.STARTS_ASYNC,
    EdgeType.ASYNC_SUCCESS,
    EdgeType.ASYNC_FAILURE,
    EdgeType.HANDOFF_EXTERNAL,
    EdgeType.OPENS_OVERLAY,
    EdgeType.HANDOFF_SUCCESS,
    EdgeType.HANDOFF_CANCEL,
    EdgeType.HANDOFF_FAILURE,
    EdgeType.RETRIES,
    EdgeType.CANCELS,
    EdgeType.EXITS,
    EdgeType.TERMINATES,
}

REACTION_EDGE_TYPES = {
    ReactionType.NAVIGATE: {EdgeType.NAVIGATES_TO},
    ReactionType.OPEN_OVERLAY: {EdgeType.OPENS_OVERLAY},
    ReactionType.CLOSE_OVERLAY: {EdgeType.CLOSES_OVERLAY},
    ReactionType.SUBMIT: {EdgeType.SUBMITS_ACTION},
    ReactionType.START_ASYNC: {EdgeType.STARTS_ASYNC},
    ReactionType.SELECT: {EdgeType.NAVIGATES_TO, EdgeType.SUBMITS_ACTION},
    ReactionType.TOGGLE: {EdgeType.NAVIGATES_TO, EdgeType.SUBMITS_ACTION},
    ReactionType.RETRY: {EdgeType.RETRIES},
    ReactionType.CANCEL: {EdgeType.CANCELS},
    ReactionType.EXIT: {EdgeType.EXITS},
    ReactionType.HANDOFF: {EdgeType.HANDOFF_EXTERNAL},
    ReactionType.TERMINATE: {EdgeType.TERMINATES},
}


def validate_interaction_graph(graph: InteractionGraph) -> List[InteractionFinding]:
    validators = [
        validate_node_completeness,
        validate_reference_integrity,
        validate_clickable_reactions,
        validate_reaction_targets,
        validate_reaction_edge_alignment,
        validate_reachability,
        validate_non_terminal_exits,
        validate_async_behavior,
        validate_handoff_behavior,
        validate_failure_recovery,
        validate_overlay_closure,
        validate_message_coverage,
        validate_copy_scope,
    ]
    findings: List[InteractionFinding] = []
    for validator in validators:
        findings.extend(validator(graph))
    return findings


def validate_node_completeness(graph: InteractionGraph) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    for node in graph.nodes:
        findings.extend(_collect("INTERACTION001", node.node_id, node.require_complete))
    return findings


def validate_reference_integrity(graph: InteractionGraph) -> List[InteractionFinding]:
    node_ids = graph.node_ids()
    clickable_ids = {clickable.clickable_id for clickable in graph.clickables}
    reaction_ids = graph.reaction_ids()
    message_ids = graph.message_ids()
    findings: List[InteractionFinding] = []

    for duplicate in _duplicates([node.node_id for node in graph.nodes]):
        findings.append(InteractionFinding("INTERACTION012", duplicate, "duplicate node_id"))
    for duplicate in _duplicates([edge.edge_id for edge in graph.edges]):
        findings.append(InteractionFinding("INTERACTION012", duplicate, "duplicate edge_id"))
    for duplicate in _duplicates([clickable.clickable_id for clickable in graph.clickables]):
        findings.append(InteractionFinding("INTERACTION012", duplicate, "duplicate clickable_id"))
    for duplicate in _duplicates([reaction.reaction_id for reaction in graph.reactions]):
        findings.append(InteractionFinding("INTERACTION012", duplicate, "duplicate reaction_id"))
    for duplicate in _duplicates([message.message_id for message in graph.messages]):
        findings.append(InteractionFinding("INTERACTION012", duplicate, "duplicate message_id"))

    for entry_node_id in graph.entry_node_ids:
        if entry_node_id not in node_ids:
            findings.append(InteractionFinding("INTERACTION012", entry_node_id, "entry node does not resolve"))

    for edge in graph.edges:
        if edge.source_node_id not in node_ids:
            findings.append(InteractionFinding("INTERACTION012", edge.edge_id, "edge source_node_id does not resolve"))
        if not _target_ref_resolves(edge.target_ref, node_ids):
            findings.append(InteractionFinding("INTERACTION012", edge.edge_id, "edge target_ref does not resolve"))

    for node in graph.nodes:
        for message_ref in node.message_refs or []:
            if message_ref not in message_ids:
                findings.append(InteractionFinding("INTERACTION012", node.node_id, "node message_ref does not resolve"))
        for recovery_target in node.recovery_targets or []:
            if not _recovery_ref_resolves(recovery_target, node_ids, reaction_ids):
                findings.append(InteractionFinding("INTERACTION012", node.node_id, "node recovery_target does not resolve"))

    for clickable in graph.clickables:
        if clickable.source_node_id not in node_ids:
            findings.append(InteractionFinding("INTERACTION012", clickable.clickable_id, "clickable source_node_id does not resolve"))

    for reaction in graph.reactions:
        if reaction.source_node_id not in node_ids:
            findings.append(InteractionFinding("INTERACTION012", reaction.reaction_id, "reaction source_node_id does not resolve"))
        if reaction.clickable_id not in clickable_ids:
            findings.append(InteractionFinding("INTERACTION012", reaction.reaction_id, "reaction clickable_id does not resolve"))
        for message_ref in reaction.message_refs:
            if message_ref not in message_ids:
                findings.append(InteractionFinding("INTERACTION012", reaction.reaction_id, "reaction message_ref does not resolve"))

    for message in graph.messages:
        if message.node_id not in node_ids:
            findings.append(InteractionFinding("INTERACTION012", message.message_id, "message node_id does not resolve"))
        if message.reaction_id is not None and message.reaction_id not in reaction_ids:
            findings.append(InteractionFinding("INTERACTION012", message.message_id, "message reaction_id does not resolve"))
        for recovery_target in message.recovery_targets:
            if not _recovery_ref_resolves(recovery_target, node_ids, reaction_ids):
                findings.append(InteractionFinding("INTERACTION012", message.message_id, "message recovery_target does not resolve"))

    return findings


def validate_clickable_reactions(graph: InteractionGraph) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    clickables_by_id = {clickable.clickable_id: clickable for clickable in graph.clickables}
    reactions_by_id = {reaction.reaction_id: reaction for reaction in graph.reactions}
    reaction_count: Dict[str, int] = defaultdict(int)
    for reaction in graph.reactions:
        reaction_count[reaction.clickable_id] += 1

    for clickable in graph.clickables:
        findings.extend(_collect("INTERACTION003", clickable.clickable_id, clickable.require_reaction))
        reaction = reactions_by_id.get(clickable.reaction_id)
        if not reaction:
            findings.append(InteractionFinding("INTERACTION003", clickable.clickable_id, "clickable reaction_id has no current Reaction"))
        else:
            if reaction.clickable_id != clickable.clickable_id:
                findings.append(InteractionFinding("INTERACTION003", clickable.clickable_id, "clickable reaction_id points to a Reaction for a different clickable"))
            if reaction.source_node_id != clickable.source_node_id:
                findings.append(InteractionFinding("INTERACTION003", clickable.clickable_id, "clickable and Reaction source_node_id do not match"))
        if reaction_count[clickable.clickable_id] != 1:
            findings.append(InteractionFinding("INTERACTION003", clickable.clickable_id, "clickable must bind exactly one current Reaction"))

    for reaction in graph.reactions:
        clickable = clickables_by_id.get(reaction.clickable_id)
        if clickable and clickable.reaction_id != reaction.reaction_id:
            findings.append(InteractionFinding("INTERACTION003", reaction.reaction_id, "Reaction clickable_id points to a clickable bound to a different Reaction"))
    return findings


def validate_reaction_targets(graph: InteractionGraph) -> List[InteractionFinding]:
    node_ids = graph.node_ids()
    findings: List[InteractionFinding] = []
    for reaction in graph.reactions:
        findings.extend(_collect("INTERACTION005", reaction.reaction_id, reaction.require_complete))
        if reaction.target_ref not in node_ids and not reaction.target_ref.startswith(("TERMINAL:", "EXTERNAL:")):
            findings.append(InteractionFinding("INTERACTION004", reaction.reaction_id, "reaction target does not resolve"))
    return findings


def validate_reaction_edge_alignment(graph: InteractionGraph) -> List[InteractionFinding]:
    edges_by_source = _outgoing_edges(graph)
    findings: List[InteractionFinding] = []
    for reaction in graph.reactions:
        allowed_edge_types = REACTION_EDGE_TYPES[reaction.reaction_type]
        matching_edges = [
            edge for edge in edges_by_source[reaction.source_node_id]
            if edge.target_ref == reaction.target_ref and edge.edge_type in allowed_edge_types
        ]
        if not matching_edges:
            allowed_names = ", ".join(sorted(edge_type.value for edge_type in allowed_edge_types))
            findings.append(
                InteractionFinding(
                    "INTERACTION013",
                    reaction.reaction_id,
                    f"Reaction lacks matching graph edge from source to target with edge_type in {allowed_names}",
                )
            )
    return findings


def validate_reachability(graph: InteractionGraph) -> List[InteractionFinding]:
    reachable = _reachable_nodes(graph)
    findings = []
    for node in graph.nodes:
        if node.node_id not in reachable and not node.resume_source:
            findings.append(InteractionFinding("INTERACTION006", node.node_id, "node is not reachable from entry nodes"))
    return findings


def validate_non_terminal_exits(graph: InteractionGraph) -> List[InteractionFinding]:
    outgoing = _outgoing_edges(graph)
    findings = []
    for node in graph.nodes:
        if node.is_terminal or node.node_type == NodeType.TERMINAL:
            continue
        continuations = [edge for edge in outgoing[node.node_id] if edge.edge_type in CONTINUATION_EDGES]
        if not continuations:
            findings.append(InteractionFinding("INTERACTION007", node.node_id, "non-terminal node has no continuation, recovery, cancel, or exit path"))
    return findings


def validate_async_behavior(graph: InteractionGraph) -> List[InteractionFinding]:
    messages = {message.message_id: message for message in graph.messages}
    message_ids = set(messages)
    findings = []
    for reaction in graph.reactions:
        if reaction.async_applicability == AsyncApplicability.NON_IMMEDIATE:
            target_node = _node_by_id(graph, reaction.target_ref)
            if not target_node or target_node.node_type != NodeType.PROCESSING:
                findings.append(InteractionFinding("INTERACTION008", reaction.reaction_id, "non-immediate reaction must target a PROCESSING node"))
            if not reaction.repeat_trigger_strategy:
                findings.append(InteractionFinding("INTERACTION008", reaction.reaction_id, "async reaction lacks duplicate-trigger strategy"))
            if not reaction.failure_behavior or not reaction.exception_behavior:
                findings.append(InteractionFinding("INTERACTION008", reaction.reaction_id, "async reaction lacks failure or timeout handling"))
            bound_messages = [messages[message_ref] for message_ref in reaction.message_refs if message_ref in messages]
            if not any(message.message_type == MessageType.PROCESSING_MESSAGE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION016", reaction.reaction_id, "async reaction lacks processing message reference"))

    for node in graph.nodes:
        if node.node_type == NodeType.PROCESSING and not set(node.message_refs or []) & message_ids:
            findings.append(InteractionFinding("INTERACTION016", node.node_id, "PROCESSING node lacks user-visible processing copy"))
    return findings


def validate_handoff_behavior(graph: InteractionGraph) -> List[InteractionFinding]:
    outgoing = _outgoing_edges(graph)
    findings = []
    for reaction in graph.reactions:
        if reaction.handoff_applicability == HandoffApplicability.EXTERNAL_HANDOFF:
            target_node = _node_by_id(graph, reaction.target_ref)
            if reaction.reaction_type != ReactionType.HANDOFF:
                findings.append(InteractionFinding("INTERACTION015", reaction.reaction_id, "external handoff applicability contradicts reaction_type"))
            if not target_node or target_node.node_type != NodeType.EXTERNAL_HANDOFF:
                findings.append(InteractionFinding("INTERACTION009", reaction.reaction_id, "external handoff must target EXTERNAL_HANDOFF node"))
            if target_node:
                edge_types = {edge.edge_type for edge in outgoing[target_node.node_id]}
                required = {EdgeType.HANDOFF_SUCCESS, EdgeType.HANDOFF_CANCEL, EdgeType.HANDOFF_FAILURE}
                if not required <= edge_types and not reaction.no_return_terminal:
                    findings.append(InteractionFinding("INTERACTION009", target_node.node_id, "external handoff lacks success, cancel, failure, or no-return terminal behavior"))
    return findings


def validate_failure_recovery(graph: InteractionGraph) -> List[InteractionFinding]:
    outgoing = _outgoing_edges(graph)
    message_ids = graph.message_ids()
    findings = []
    for node in graph.nodes:
        if node.node_type != NodeType.FAILURE:
            continue
        if not node.failure_reason:
            findings.append(InteractionFinding("INTERACTION010", node.node_id, "failure node lacks user-visible reason"))
        if not (node.recovery_targets or [edge.target_ref for edge in outgoing[node.node_id]] or node.is_terminal):
            findings.append(InteractionFinding("INTERACTION010", node.node_id, "failure node lacks recovery, return, exit, or terminal justification"))
        if not set(node.message_refs or []) & message_ids:
            findings.append(InteractionFinding("INTERACTION017", node.node_id, "failure node lacks bound message record"))
    return findings


def validate_overlay_closure(graph: InteractionGraph) -> List[InteractionFinding]:
    outgoing = _outgoing_edges(graph)
    findings = []
    for node in graph.nodes:
        if node.node_type != NodeType.OVERLAY:
            continue
        close_edges = [
            edge for edge in outgoing[node.node_id]
            if edge.edge_type in {EdgeType.CLOSES_OVERLAY, EdgeType.CANCELS, EdgeType.SUBMITS_ACTION, EdgeType.EXITS}
        ]
        if not close_edges and not node.trap_justification:
            findings.append(InteractionFinding("INTERACTION011", node.node_id, "overlay lacks close, cancel, submit, exit, or trap justification"))
    return findings


def validate_message_coverage(graph: InteractionGraph) -> List[InteractionFinding]:
    messages = {message.message_id: message for message in graph.messages}
    findings: List[InteractionFinding] = []
    for message in graph.messages:
        findings.extend(_collect("INTERACTION017", message.message_id, message.require_complete))

    for node in graph.nodes:
        bound_messages = _messages_for_node(graph, node.node_id, messages)
        if node.node_type == NodeType.PROCESSING:
            if not any(message.message_type == MessageType.PROCESSING_MESSAGE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION016", node.node_id, "PROCESSING node lacks processing message"))
        if node.node_type == NodeType.FAILURE:
            if not any(message.message_type in {MessageType.FAILURE_MESSAGE, MessageType.RECOVERY_INSTRUCTION} for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION017", node.node_id, "FAILURE node lacks failure or recovery message"))
        if node.node_type == NodeType.EXTERNAL_HANDOFF:
            if not any(message.message_type == MessageType.HANDOFF_NOTICE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION018", node.node_id, "EXTERNAL_HANDOFF node lacks handoff notice copy"))
        if node.node_type == NodeType.SUCCESS:
            if not any(message.message_type == MessageType.SUCCESS_MESSAGE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION017", node.node_id, "SUCCESS node lacks success message"))

    for clickable in graph.clickables:
        if clickable.disabled_behavior:
            bound_messages = _messages_for_node(graph, clickable.source_node_id, messages)
            if not any(message.message_type == MessageType.DISABLED_REASON for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION019", clickable.clickable_id, "disabled clickable lacks disabled-reason message"))

    for reaction in graph.reactions:
        bound_messages = [messages[msg] for msg in reaction.message_refs if msg in messages]
        if reaction.failure_applicability == FailureApplicability.CAN_FAIL:
            if not any(message.message_type in {MessageType.FAILURE_MESSAGE, MessageType.RECOVERY_INSTRUCTION} for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION017", reaction.reaction_id, "failure-prone reaction lacks failure or recovery message"))
        if reaction.cancel_applicability == CancelApplicability.CANCELLABLE or reaction.reaction_type == ReactionType.CANCEL:
            if not any(message.message_type == MessageType.CANCEL_CONFIRMATION for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION019", reaction.reaction_id, "cancellable reaction lacks cancel confirmation copy"))
        if reaction.reaction_type == ReactionType.EXIT:
            if not any(message.message_type == MessageType.EXIT_CONSEQUENCE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION019", reaction.reaction_id, "exit reaction lacks exit consequence copy"))
        if reaction.handoff_applicability == HandoffApplicability.EXTERNAL_HANDOFF:
            if not any(message.message_type == MessageType.HANDOFF_NOTICE for message in bound_messages):
                findings.append(InteractionFinding("INTERACTION018", reaction.reaction_id, "external handoff lacks handoff notice copy"))
    return findings


def validate_copy_scope(graph: InteractionGraph) -> List[InteractionFinding]:
    findings = []
    for message in graph.messages:
        if message_has_product_scope_expansion(message):
            findings.append(InteractionFinding("INTERACTION020", message.message_id, "interaction copy appears to add product scope"))
    return findings


def _collect(code: str, subject_id: str, check: Callable[[], None]) -> List[InteractionFinding]:
    try:
        check()
    except ValueError as exc:
        return [InteractionFinding(code=code, subject_id=subject_id, message=str(exc))]
    return []


def _outgoing_edges(graph: InteractionGraph) -> Dict[str, List]:
    outgoing: Dict[str, List] = defaultdict(list)
    for edge in graph.edges:
        outgoing[edge.source_node_id].append(edge)
    return outgoing


def _reachable_nodes(graph: InteractionGraph) -> Set[str]:
    outgoing = _outgoing_edges(graph)
    node_ids = graph.node_ids()
    queue = deque(node_id for node_id in graph.entry_node_ids if node_id in node_ids)
    seen: Set[str] = set(queue)
    while queue:
        source = queue.popleft()
        for edge in outgoing[source]:
            if edge.target_ref in node_ids and edge.target_ref not in seen:
                seen.add(edge.target_ref)
                queue.append(edge.target_ref)
    return seen


def _node_by_id(graph: InteractionGraph, node_id: str) -> Optional[InteractionNode]:
    for node in graph.nodes:
        if node.node_id == node_id:
            return node
    return None


def _target_ref_resolves(target_ref: str, node_ids: Set[str]) -> bool:
    return target_ref in node_ids or target_ref.startswith(("TERMINAL:", "EXTERNAL:"))


def _recovery_ref_resolves(target_ref: str, node_ids: Set[str], reaction_ids: Set[str]) -> bool:
    return target_ref in node_ids or target_ref in reaction_ids or target_ref.startswith(("TERMINAL:", "EXTERNAL:"))


def _messages_for_node(graph: InteractionGraph, node_id: str, messages: Dict[str, object]) -> List:
    direct_messages = [message for message in graph.messages if message.node_id == node_id]
    referenced_messages = []
    node = _node_by_id(graph, node_id)
    if node:
        referenced_messages = [messages[message_ref] for message_ref in node.message_refs or [] if message_ref in messages]
    return direct_messages + [message for message in referenced_messages if message not in direct_messages]


def _duplicates(values: List[str]) -> List[str]:
    counts: Dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    return [value for value, count in counts.items() if count > 1]
