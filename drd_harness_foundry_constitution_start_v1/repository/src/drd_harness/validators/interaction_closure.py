"""Interaction graph closure validators."""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Set

from drd_harness.rules.interaction import (
    AsyncApplicability,
    CancelApplicability,
    Clickable,
    DuplicateTriggerStrategy,
    EdgeType,
    FailureApplicability,
    HandoffApplicability,
    InteractionEdge,
    InteractionGraph,
    InteractionMessage,
    InteractionNode,
    MessageType,
    NodeType,
    ReactionRecord,
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
        validate_failure_path_edges,
        validate_failure_recovery,
        validate_overlay_closure,
        validate_message_coverage,
        validate_copy_scope,
    ]
    findings: List[InteractionFinding] = []
    for validator in validators:
        findings.extend(validator(graph))
    return findings


def interaction_graph_from_mapping(record: Mapping[str, object]) -> InteractionGraph:
    return InteractionGraph(
        graph_id=str(record["graph_id"]),
        entry_node_ids=_string_list(record["entry_node_ids"]),
        nodes=[interaction_node_from_mapping(node) for node in _mapping_list(record["nodes"])],
        edges=[interaction_edge_from_mapping(edge) for edge in _mapping_list(record["edges"])],
        clickables=[clickable_from_mapping(clickable) for clickable in _mapping_list(record["clickables"])],
        reactions=[reaction_record_from_mapping(reaction) for reaction in _mapping_list(record["reactions"])],
        messages=[interaction_message_from_mapping(message) for message in _mapping_list(record["messages"])],
    )


def interaction_node_from_mapping(record: Mapping[str, object]) -> InteractionNode:
    return InteractionNode(
        node_id=str(record["node_id"]),
        node_type=NodeType(str(record["node_type"])),
        source_refs=_string_list(record["source_refs"]),
        is_terminal=bool(record.get("is_terminal", False)),
        terminal_reason=_optional_string(record.get("terminal_reason")),
        message_refs=_optional_string_list(record.get("message_refs")),
        failure_reason=_optional_string(record.get("failure_reason")),
        recovery_targets=_optional_string_list(record.get("recovery_targets")),
        resume_source=_optional_string(record.get("resume_source")),
        trap_justification=_optional_string(record.get("trap_justification")),
    )


def interaction_edge_from_mapping(record: Mapping[str, object]) -> InteractionEdge:
    return InteractionEdge(
        edge_id=str(record["edge_id"]),
        source_node_id=str(record["source_node_id"]),
        target_ref=str(record["target_ref"]),
        edge_type=EdgeType(str(record["edge_type"])),
    )


def clickable_from_mapping(record: Mapping[str, object]) -> Clickable:
    return Clickable(
        clickable_id=str(record["clickable_id"]),
        source_node_id=str(record["source_node_id"]),
        label_or_affordance=str(record["label_or_affordance"]),
        clickable_type=str(record["clickable_type"]),
        source_refs=_string_list(record["source_refs"]),
        enabled_conditions=_string_list(record["enabled_conditions"]),
        disabled_behavior=_optional_string(record.get("disabled_behavior")),
        reaction_id=str(record["reaction_id"]),
    )


def reaction_record_from_mapping(record: Mapping[str, object]) -> ReactionRecord:
    repeat_trigger = record.get("repeat_trigger_strategy")
    return ReactionRecord(
        reaction_id=str(record["reaction_id"]),
        clickable_id=str(record["clickable_id"]),
        source_node_id=str(record["source_node_id"]),
        reaction_type=ReactionType(str(record["reaction_type"])),
        target_ref=str(record["target_ref"]),
        preconditions=_string_list(record["preconditions"]),
        failure_applicability=FailureApplicability(str(record["failure_applicability"])),
        cancel_applicability=CancelApplicability(str(record["cancel_applicability"])),
        async_applicability=AsyncApplicability(str(record["async_applicability"])),
        handoff_applicability=HandoffApplicability(str(record["handoff_applicability"])),
        success_behavior=str(record["success_behavior"]),
        failure_behavior=_optional_string(record.get("failure_behavior")),
        cancel_behavior=_optional_string(record.get("cancel_behavior")),
        exception_behavior=_optional_string(record.get("exception_behavior")),
        message_refs=_string_list(record["message_refs"]),
        trace_refs=_string_list(record["trace_refs"]),
        repeat_trigger_strategy=DuplicateTriggerStrategy(str(repeat_trigger)) if repeat_trigger else None,
        no_return_terminal=_optional_string(record.get("no_return_terminal")),
    )


def interaction_message_from_mapping(record: Mapping[str, object]) -> InteractionMessage:
    return InteractionMessage(
        message_id=str(record["message_id"]),
        message_type=MessageType(str(record["message_type"])),
        node_id=str(record["node_id"]),
        reaction_id=_optional_string(record.get("reaction_id")),
        trigger_condition=str(record["trigger_condition"]),
        user_visible_summary=str(record["user_visible_summary"]),
        required_user_next_step=str(record["required_user_next_step"]),
        recovery_targets=_string_list(record["recovery_targets"]),
        trace_refs=_string_list(record["trace_refs"]),
    )


def validate_required_clickable_coverage(
    graph: InteractionGraph,
    required_clickable_ids: Sequence[str],
) -> List[InteractionFinding]:
    present_ids = {clickable.clickable_id for clickable in graph.clickables}
    findings: List[InteractionFinding] = []
    for clickable_id in sorted(set(required_clickable_ids) - present_ids):
        findings.append(InteractionFinding("INTERACTION003", clickable_id, "required clickable is missing"))
    return findings


def validate_spec_edge_table_coverage(
    graph: InteractionGraph,
    edge_rows: Sequence[Mapping[str, object]],
) -> List[InteractionFinding]:
    edges_by_id = {edge.edge_id: edge for edge in graph.edges}
    clickable_ids = {clickable.clickable_id for clickable in graph.clickables}
    node_ids = graph.node_ids()
    spec_edge_ids = {str(row.get("edge_id", "")) for row in edge_rows}
    traced_edge_ids = {
        trace_ref
        for reaction in graph.reactions
        for trace_ref in reaction.trace_refs
        if trace_ref in edges_by_id
    }
    findings: List[InteractionFinding] = []
    for row in edge_rows:
        edge_id = str(row.get("edge_id", ""))
        edge = edges_by_id.get(edge_id)
        if not edge:
            findings.append(InteractionFinding("INTERACTION013", edge_id, "required spec edge is missing"))
            continue
        if edge.source_node_id != row.get("from_state"):
            findings.append(InteractionFinding("INTERACTION013", edge_id, "spec edge source does not match from_state"))
        if edge.target_ref != row.get("to_state"):
            findings.append(InteractionFinding("INTERACTION013", edge_id, "spec edge target does not match to_state"))
        if row.get("product_expansion_allowed") is not False:
            findings.append(InteractionFinding("INTERACTION020", edge_id, "spec edge allows product expansion"))
        trigger_element = str(row.get("trigger_element", ""))
        trigger_type = str(row.get("trigger_type", ""))
        if trigger_type in {"click", "select_change"} and trigger_element not in clickable_ids:
            findings.append(InteractionFinding("INTERACTION003", edge_id, "spec edge trigger_element does not resolve to a graph clickable"))
        if trigger_element in clickable_ids:
            matching_reactions = [
                reaction
                for reaction in graph.reactions
                if reaction.clickable_id == trigger_element and edge_id in reaction.trace_refs
            ]
            if not matching_reactions:
                findings.append(
                    InteractionFinding(
                        "INTERACTION013",
                        edge_id,
                        "spec edge trigger_element is not traced by its clickable reaction",
                    )
                )
        overlay = row.get("overlay")
        if overlay is not None:
            overlay_id = str(overlay)
            if overlay_id not in node_ids:
                findings.append(InteractionFinding("INTERACTION011", edge_id, "spec edge overlay node does not resolve"))
            elif not any(
                graph_edge.source_node_id == overlay_id or graph_edge.target_ref == overlay_id
                for graph_edge in graph.edges
            ):
                findings.append(InteractionFinding("INTERACTION011", edge_id, "spec edge overlay is not connected in graph"))
    for edge in graph.edges:
        if edge.edge_id in spec_edge_ids:
            continue
        if edge.edge_id not in traced_edge_ids:
            findings.append(InteractionFinding("INTERACTION013", edge.edge_id, "extra graph edge is not traced by a reaction"))
            continue
        if not _extra_edge_has_spec_basis(graph, edge, edge_rows):
            findings.append(InteractionFinding("INTERACTION013", edge.edge_id, "extra graph edge lacks spec basis"))
    return findings


def validate_interaction_artifact_slices(
    graph: InteractionGraph,
    *,
    clickable_records: Sequence[Mapping[str, object]],
    async_records: Sequence[Mapping[str, object]],
    failure_records: Sequence[Mapping[str, object]],
    message_records: Sequence[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    graph_clickable_ids = {clickable.clickable_id for clickable in graph.clickables}
    slice_clickable_ids = [str(record.get("clickable_id", "")) for record in clickable_records]
    for duplicate_id in _duplicates(slice_clickable_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate clickable_inventory record"))
    slice_clickable_id_set = set(slice_clickable_ids)
    if graph_clickable_ids != slice_clickable_id_set:
        findings.append(InteractionFinding("INTERACTION003", graph.graph_id, "clickable_inventory does not match graph clickables"))
    graph_clickables = {clickable.clickable_id: _clickable_payload(clickable) for clickable in graph.clickables}
    for record in clickable_records:
        clickable_id = str(record.get("clickable_id", ""))
        if clickable_id in graph_clickables and dict(record) != graph_clickables[clickable_id]:
            findings.append(InteractionFinding("INTERACTION003", clickable_id, "clickable_inventory record drifts from graph clickable"))

    graph_message_ids = graph.message_ids()
    slice_message_ids = [str(record.get("message_id", "")) for record in message_records]
    for duplicate_id in _duplicates(slice_message_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate interaction_message record"))
    slice_message_id_set = set(slice_message_ids)
    if graph_message_ids != slice_message_id_set:
        findings.append(InteractionFinding("INTERACTION017", graph.graph_id, "interaction_messages does not match graph messages"))
    graph_messages = {message.message_id: _message_payload(message) for message in graph.messages}
    for record in message_records:
        message_id = str(record.get("message_id", ""))
        if message_id in graph_messages and dict(record) != graph_messages[message_id]:
            findings.append(InteractionFinding("INTERACTION017", message_id, "interaction_message record drifts from graph message"))

    expected_async_ids = {
        reaction.reaction_id
        for reaction in graph.reactions
        if reaction.async_applicability == AsyncApplicability.NON_IMMEDIATE
    }
    slice_async_ids = [str(record.get("reaction_id", "")) for record in async_records]
    for duplicate_id in _duplicates(slice_async_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate async_behavior record"))
    slice_async_id_set = set(slice_async_ids)
    if expected_async_ids != slice_async_id_set:
        findings.append(InteractionFinding("INTERACTION008", graph.graph_id, "async_behavior does not cover all non-immediate reactions exactly"))

    expected_failure_nodes = {node.node_id for node in graph.nodes if node.node_type == NodeType.FAILURE}
    slice_failure_nodes = [str(record.get("failure_node_id", "")) for record in failure_records]
    for duplicate_id in _duplicates(slice_failure_nodes):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate failure_recovery record"))
    slice_failure_node_set = set(slice_failure_nodes)
    if expected_failure_nodes != slice_failure_node_set:
        findings.append(InteractionFinding("INTERACTION010", graph.graph_id, "failure_recovery does not cover all failure nodes exactly"))

    reactions = {reaction.reaction_id: reaction for reaction in graph.reactions}
    nodes = {node.node_id: node for node in graph.nodes}
    for record in async_records:
        reaction_id = str(record.get("reaction_id", ""))
        processing_node_id = str(record.get("processing_node_id", ""))
        reaction = reactions.get(reaction_id)
        node = nodes.get(processing_node_id)
        if not reaction:
            findings.append(InteractionFinding("INTERACTION012", reaction_id, "async behavior reaction_id does not resolve"))
            continue
        if reaction.async_applicability != AsyncApplicability.NON_IMMEDIATE:
            findings.append(InteractionFinding("INTERACTION008", reaction_id, "async behavior references an immediate reaction"))
        if reaction.target_ref != processing_node_id:
            findings.append(InteractionFinding("INTERACTION008", reaction_id, "async behavior processing_node_id must equal reaction target_ref"))
        if not node or node.node_type != NodeType.PROCESSING:
            findings.append(InteractionFinding("INTERACTION008", reaction_id, "async behavior processing_node_id must resolve to a PROCESSING node"))
        if reaction.repeat_trigger_strategy and record.get("duplicate_trigger_strategy") != reaction.repeat_trigger_strategy.value:
            findings.append(InteractionFinding("INTERACTION008", reaction_id, "async duplicate_trigger_strategy does not match reaction"))

    for record in failure_records:
        failure_node_id = str(record.get("failure_node_id", ""))
        node = nodes.get(failure_node_id)
        if not node or node.node_type != NodeType.FAILURE:
            findings.append(InteractionFinding("INTERACTION010", failure_node_id, "failure_recovery node must resolve to a FAILURE node"))
        elif record.get("reason") != node.failure_reason:
            findings.append(InteractionFinding("INTERACTION010", failure_node_id, "failure_recovery reason must match failure node failure_reason"))
        elif set(record.get("recovery_targets", [])) != set(node.recovery_targets or []):
            findings.append(InteractionFinding("INTERACTION010", failure_node_id, "failure_recovery targets must match failure node recovery_targets"))
        elif set(record.get("message_refs", [])) != set(node.message_refs or []):
            findings.append(InteractionFinding("INTERACTION017", failure_node_id, "failure_recovery message_refs must match failure node message_refs"))
        for message_ref in record.get("message_refs", []):
            if message_ref not in graph_message_ids:
                findings.append(InteractionFinding("INTERACTION017", failure_node_id, "failure_recovery message_ref does not resolve"))
        for target in record.get("recovery_targets", []):
            if not _recovery_ref_resolves(str(target), set(nodes), graph.reaction_ids()):
                findings.append(InteractionFinding("INTERACTION010", failure_node_id, "failure_recovery target does not resolve"))
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


def validate_failure_path_edges(graph: InteractionGraph) -> List[InteractionFinding]:
    outgoing = _outgoing_edges(graph)
    nodes = {node.node_id: node for node in graph.nodes}
    findings: List[InteractionFinding] = []
    for reaction in graph.reactions:
        if reaction.failure_applicability != FailureApplicability.CAN_FAIL:
            continue
        candidate_sources = [reaction.source_node_id]
        if reaction.target_ref in nodes:
            candidate_sources.append(reaction.target_ref)
        has_failure_path = any(
            edge.target_ref in nodes and nodes[edge.target_ref].node_type == NodeType.FAILURE
            for source in candidate_sources
            for edge in outgoing[source]
        )
        if not has_failure_path:
            findings.append(
                InteractionFinding(
                    "INTERACTION010",
                    reaction.reaction_id,
                    "failure-prone reaction lacks graph edge to a FAILURE node",
                )
            )
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


def _clickable_payload(clickable: Clickable) -> Dict[str, object]:
    return {
        "clickable_id": clickable.clickable_id,
        "source_node_id": clickable.source_node_id,
        "label_or_affordance": clickable.label_or_affordance,
        "clickable_type": clickable.clickable_type,
        "source_refs": clickable.source_refs,
        "enabled_conditions": clickable.enabled_conditions,
        "disabled_behavior": clickable.disabled_behavior,
        "reaction_id": clickable.reaction_id,
    }


def _message_payload(message: InteractionMessage) -> Dict[str, object]:
    return {
        "message_id": message.message_id,
        "message_type": message.message_type.value,
        "node_id": message.node_id,
        "reaction_id": message.reaction_id,
        "trigger_condition": message.trigger_condition,
        "user_visible_summary": message.user_visible_summary,
        "required_user_next_step": message.required_user_next_step,
        "recovery_targets": message.recovery_targets,
        "trace_refs": message.trace_refs,
    }


def _extra_edge_has_spec_basis(
    graph: InteractionGraph,
    edge: InteractionEdge,
    edge_rows: Sequence[Mapping[str, object]],
) -> bool:
    nodes = {node.node_id: node for node in graph.nodes}
    if edge.edge_type == EdgeType.ASYNC_FAILURE:
        target_node = nodes.get(edge.target_ref)
        if not target_node or target_node.node_type != NodeType.FAILURE:
            return False
        for reaction in graph.reactions:
            if reaction.failure_applicability != FailureApplicability.CAN_FAIL:
                continue
            reaction_sources = {reaction.source_node_id}
            if reaction.target_ref in nodes:
                reaction_sources.add(reaction.target_ref)
            if edge.source_node_id in reaction_sources and edge.edge_id in reaction.trace_refs:
                return True
        return False

    for row in edge_rows:
        overlay = row.get("overlay")
        if overlay is None:
            continue
        overlay_id = str(overlay)
        if (
            edge.edge_type == EdgeType.OPENS_OVERLAY
            and edge.source_node_id == row.get("from_state")
            and edge.target_ref == overlay_id
        ):
            return _same_reaction_traces_edges(graph, edge.edge_id, str(row.get("edge_id", "")))
        if (
            edge.edge_type == EdgeType.STARTS_ASYNC
            and edge.source_node_id == overlay_id
            and edge.target_ref == row.get("to_state")
        ):
            return _same_reaction_traces_edges(graph, edge.edge_id, str(row.get("edge_id", "")))
    return False


def _same_reaction_traces_edges(graph: InteractionGraph, edge_id: str, spec_edge_id: str) -> bool:
    return any(
        edge_id in reaction.trace_refs and spec_edge_id in reaction.trace_refs
        for reaction in graph.reactions
    )


def _mapping_list(value: object) -> List[Mapping[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise ValueError("expected list of mapping records")
    return value


def _optional_string(value: object) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _optional_string_list(value: object) -> Optional[List[str]]:
    if value is None:
        return None
    return _string_list(value)


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        raise ValueError("expected list")
    return [str(item) for item in value]
