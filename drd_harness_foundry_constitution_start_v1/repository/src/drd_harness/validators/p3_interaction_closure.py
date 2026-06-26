"""P3 interaction closure artifact-set validators."""

from typing import Dict, List, Mapping, Sequence, Set

from drd_harness.rules.interaction import EdgeType, HandoffApplicability, InteractionGraph, NodeType, ReactionRecord
from drd_harness.validators.interaction_closure import (
    InteractionFinding,
    interaction_graph_from_mapping,
    validate_interaction_artifact_slices,
    validate_interaction_graph,
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

P3_VALIDATOR_REF = "repository/src/drd_harness/validators/p3_interaction_closure.py"

P3_CLOSURE_ARTIFACTS = {
    "interaction_graph": ("p3.closure.interaction_graph", "graph"),
    "interaction_nodes": ("p3.closure.interaction_nodes", "records"),
    "interaction_edges": ("p3.closure.interaction_edges", "records"),
    "clickable_inventory": ("p3.closure.clickable_inventory", "records"),
    "reaction_records": ("p3.closure.reaction_records", "records"),
    "reaction_applicability": ("p3.closure.reaction_applicability", "records"),
    "async_behavior": ("p3.closure.async_behavior", "records"),
    "handoff_behavior": ("p3.closure.handoff_behavior", "records"),
    "failure_recovery": ("p3.closure.failure_recovery", "records"),
    "overlay_closure": ("p3.closure.overlay_closure", "records"),
    "interaction_messages": ("p3.closure.interaction_messages", "records"),
    "message_coverage_index": ("p3.closure.message_coverage_index", "coverage_index"),
    "closure_handoff_manifest": ("p3.closure.closure_handoff_manifest", "records"),
}

P3_PAYLOAD_SHAPES = {
    "interaction_graph": "mapping",
    "reaction_applicability": "mapping",
    "message_coverage_index": "mapping",
}


def validate_interaction_closure_artifacts(
    *,
    interaction_graph: Mapping[str, object],
    interaction_nodes: Mapping[str, object],
    interaction_edges: Mapping[str, object],
    clickable_inventory: Mapping[str, object],
    reaction_records: Mapping[str, object],
    reaction_applicability: Mapping[str, object],
    async_behavior: Mapping[str, object],
    handoff_behavior: Mapping[str, object],
    failure_recovery: Mapping[str, object],
    overlay_closure: Mapping[str, object],
    interaction_messages: Mapping[str, object],
    message_coverage_index: Mapping[str, object],
    closure_handoff_manifest: Mapping[str, object],
    distill_closure_handoff_manifest: Mapping[str, object],
    distill_product_expansion_gaps: Mapping[str, object],
) -> List[InteractionFinding]:
    artifacts = {
        "interaction_graph": interaction_graph,
        "interaction_nodes": interaction_nodes,
        "interaction_edges": interaction_edges,
        "clickable_inventory": clickable_inventory,
        "reaction_records": reaction_records,
        "reaction_applicability": reaction_applicability,
        "async_behavior": async_behavior,
        "handoff_behavior": handoff_behavior,
        "failure_recovery": failure_recovery,
        "overlay_closure": overlay_closure,
        "interaction_messages": interaction_messages,
        "message_coverage_index": message_coverage_index,
        "closure_handoff_manifest": closure_handoff_manifest,
    }
    findings: List[InteractionFinding] = []
    for name, artifact in artifacts.items():
        artifact_id, payload_key = P3_CLOSURE_ARTIFACTS[name]
        findings.extend(_validate_artifact_envelope(artifact, artifact_id, payload_key))
        findings.extend(_validate_payload_shape(name, artifact))

    graph_payload = interaction_graph.get("graph")
    if not isinstance(graph_payload, Mapping):
        findings.append(InteractionFinding("INTERACTION021", "p3.closure.interaction_graph", "graph payload is missing"))
        return findings

    try:
        graph = interaction_graph_from_mapping(graph_payload)
    except (KeyError, ValueError) as exc:
        findings.append(InteractionFinding("INTERACTION021", "p3.closure.interaction_graph", str(exc)))
        return findings

    findings.extend(validate_interaction_graph(graph))
    findings.extend(
        validate_interaction_artifact_slices(
            graph,
            clickable_records=_payload_records(clickable_inventory, "records"),
            async_records=_payload_records(async_behavior, "records"),
            failure_records=_payload_records(failure_recovery, "records"),
            message_records=_payload_records(interaction_messages, "records"),
        )
    )
    findings.extend(_validate_node_slice(graph, _payload_records(interaction_nodes, "records")))
    findings.extend(_validate_edge_slice(graph, _payload_records(interaction_edges, "records")))
    findings.extend(_validate_reaction_slice(graph, _payload_records(reaction_records, "records")))
    findings.extend(_validate_reaction_applicability(graph, _payload_mapping(reaction_applicability, "records")))
    findings.extend(_validate_handoff_slice(graph, _payload_records(handoff_behavior, "records")))
    findings.extend(_validate_overlay_slice(graph, _payload_records(overlay_closure, "records")))
    findings.extend(_validate_message_coverage_index(graph, _payload_object(message_coverage_index, "coverage_index")))
    findings.extend(
        _validate_closure_handoff_manifest(
            graph,
            closure_handoff_manifest,
            distill_closure_handoff_manifest,
            distill_product_expansion_gaps,
        )
    )
    return findings


def _validate_node_slice(
    graph: InteractionGraph,
    node_records: List[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    graph_nodes = {node.node_id: _node_payload(node) for node in graph.nodes}
    slice_ids = [str(record.get("node_id", "")) for record in node_records]
    for duplicate_id in _duplicates(slice_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate interaction_node record"))
    if graph.node_ids() != set(slice_ids):
        findings.append(InteractionFinding("INTERACTION001", graph.graph_id, "interaction_nodes does not match graph nodes"))
    for record in node_records:
        node_id = str(record.get("node_id", ""))
        if node_id in graph_nodes and dict(record) != graph_nodes[node_id]:
            findings.append(InteractionFinding("INTERACTION001", node_id, "interaction_node record drifts from graph node"))
    return findings


def _validate_edge_slice(
    graph: InteractionGraph,
    edge_records: List[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    graph_edges = {edge.edge_id: _edge_payload(edge) for edge in graph.edges}
    slice_ids = [str(record.get("edge_id", "")) for record in edge_records]
    for duplicate_id in _duplicates(slice_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate interaction_edge record"))
    if set(graph_edges) != set(slice_ids):
        findings.append(InteractionFinding("INTERACTION013", graph.graph_id, "interaction_edges does not match graph edges"))
    for record in edge_records:
        edge_id = str(record.get("edge_id", ""))
        if edge_id in graph_edges and dict(record) != graph_edges[edge_id]:
            findings.append(InteractionFinding("INTERACTION013", edge_id, "interaction_edge record drifts from graph edge"))
    return findings


def _validate_reaction_slice(
    graph: InteractionGraph,
    reaction_records: List[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    graph_reactions = {reaction.reaction_id: _reaction_payload(reaction) for reaction in graph.reactions}
    slice_ids = [str(record.get("reaction_id", "")) for record in reaction_records]
    for duplicate_id in _duplicates(slice_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate reaction_record record"))
    if graph.reaction_ids() != set(slice_ids):
        findings.append(InteractionFinding("INTERACTION005", graph.graph_id, "reaction_records does not match graph reactions"))
    for record in reaction_records:
        reaction_id = str(record.get("reaction_id", ""))
        if reaction_id in graph_reactions and dict(record) != graph_reactions[reaction_id]:
            findings.append(InteractionFinding("INTERACTION005", reaction_id, "reaction_record drifts from graph reaction"))
    return findings


def _validate_reaction_applicability(
    graph: InteractionGraph,
    records: Mapping[str, Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    if graph.reaction_ids() != set(records):
        findings.append(InteractionFinding("INTERACTION005", graph.graph_id, "reaction_applicability does not cover all reactions exactly"))
    reactions = {reaction.reaction_id: reaction for reaction in graph.reactions}
    for reaction_id, record in records.items():
        reaction = reactions.get(str(reaction_id))
        if reaction is None:
            findings.append(InteractionFinding("INTERACTION005", str(reaction_id), "reaction_applicability references unknown reaction"))
            continue
        if dict(record) != _reaction_applicability_payload(reaction):
            findings.append(InteractionFinding("INTERACTION005", str(reaction_id), "reaction_applicability drifts from graph reaction"))
    return findings


def _validate_handoff_slice(
    graph: InteractionGraph,
    records: List[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    expected_ids = {
        reaction.reaction_id
        for reaction in graph.reactions
        if reaction.handoff_applicability == HandoffApplicability.EXTERNAL_HANDOFF
    }
    actual_ids = [str(record.get("reaction_id", "")) for record in records]
    for duplicate_id in _duplicates(actual_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate handoff_behavior record"))
    if expected_ids != set(actual_ids):
        findings.append(InteractionFinding("INTERACTION009", graph.graph_id, "handoff_behavior does not cover external handoffs exactly"))
    reactions = {reaction.reaction_id: reaction for reaction in graph.reactions}
    for record in records:
        reaction_id = str(record.get("reaction_id", ""))
        reaction = reactions.get(reaction_id)
        if reaction is None:
            findings.append(InteractionFinding("INTERACTION009", reaction_id, "handoff behavior reaction_id does not resolve"))
            continue
        if record.get("external_target") != reaction.target_ref:
            findings.append(InteractionFinding("INTERACTION009", reaction_id, "handoff external_target must equal reaction target_ref"))
        if record.get("no_return_terminal") != reaction.no_return_terminal:
            findings.append(InteractionFinding("INTERACTION009", reaction_id, "handoff no_return_terminal must match reaction"))
    return findings


def _validate_overlay_slice(
    graph: InteractionGraph,
    records: List[Mapping[str, object]],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    expected_ids = {node.node_id for node in graph.nodes if node.node_type == NodeType.OVERLAY}
    actual_ids = [str(record.get("overlay_node_id", "")) for record in records]
    for duplicate_id in _duplicates(actual_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate overlay_closure record"))
    if expected_ids != set(actual_ids):
        findings.append(InteractionFinding("INTERACTION011", graph.graph_id, "overlay_closure does not cover overlays exactly"))
    nodes = {node.node_id: node for node in graph.nodes}
    outgoing = _outgoing_edges(graph)
    for record in records:
        overlay_id = str(record.get("overlay_node_id", ""))
        node = nodes.get(overlay_id)
        if not node or node.node_type != NodeType.OVERLAY:
            findings.append(InteractionFinding("INTERACTION011", overlay_id, "overlay_closure record does not resolve to overlay node"))
            continue
        closure_targets = {
            edge.target_ref
            for edge in outgoing[overlay_id]
            if edge.edge_type in {EdgeType.CLOSES_OVERLAY, EdgeType.CANCELS, EdgeType.SUBMITS_ACTION, EdgeType.EXITS}
        }
        if set(record.get("closure_targets", [])) != closure_targets:
            findings.append(InteractionFinding("INTERACTION011", overlay_id, "overlay_closure targets drift from graph edges"))
        if record.get("return_context") != node.resume_source:
            findings.append(InteractionFinding("INTERACTION011", overlay_id, "overlay_closure return_context must match overlay resume_source"))
        if record.get("trap_justification") != node.trap_justification:
            findings.append(InteractionFinding("INTERACTION011", overlay_id, "overlay_closure trap_justification must match overlay node"))
    return findings


def _validate_message_coverage_index(
    graph: InteractionGraph,
    coverage_index: Mapping[str, object],
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    coverage_rows = _payload_records(coverage_index, "coverage")
    messages = {message.message_id: message for message in graph.messages}
    coverage_message_ids = [str(row.get("message_id", "")) for row in coverage_rows]
    for duplicate_id in _duplicates(coverage_message_ids):
        findings.append(InteractionFinding("INTERACTION012", duplicate_id, "duplicate message coverage row"))
    if set(messages) != set(coverage_message_ids):
        findings.append(InteractionFinding("INTERACTION017", graph.graph_id, "message_coverage_index does not cover graph messages exactly"))
    for row in coverage_rows:
        message_id = str(row.get("message_id", ""))
        message = messages.get(message_id)
        if not message:
            findings.append(InteractionFinding("INTERACTION017", message_id, "message coverage row references unknown message"))
            continue
        if row.get("source_node_id") != message.node_id:
            findings.append(InteractionFinding("INTERACTION017", message_id, "message coverage source_node_id must match message node_id"))
        if row.get("reaction_id") != message.reaction_id:
            findings.append(InteractionFinding("INTERACTION017", message_id, "message coverage reaction_id must match message reaction_id"))
    return findings


def _validate_closure_handoff_manifest(
    graph: InteractionGraph,
    closure_handoff_manifest: Mapping[str, object],
    distill_closure_handoff_manifest: Mapping[str, object],
    distill_product_expansion_gaps: Mapping[str, object],
) -> List[InteractionFinding]:
    records = _payload_records(closure_handoff_manifest, "records")
    if len(records) != 1:
        return [InteractionFinding("INTERACTION022", "p3.closure.closure_handoff_manifest", "closure handoff manifest requires exactly one record")]

    findings: List[InteractionFinding] = []
    record = records[0]
    eligible_graph_units = set(_text_values(record.get("eligible_graph_units", [])))
    blocked_graph_units = set(_text_values(record.get("blocked_graph_units", [])))
    review_blockers = set(_text_values(record.get("review_blockers", [])))
    graph_units = _graph_unit_ids(graph)
    if record.get("source_artifact_hashes") != closure_handoff_manifest.get("upstream_hashes"):
        findings.append(InteractionFinding("INTERACTION022", str(record.get("handoff_id", "handoff")), "handoff source_artifact_hashes must match artifact upstream_hashes"))

    for graph_unit in sorted(graph_units - eligible_graph_units):
        findings.append(InteractionFinding("INTERACTION022", graph_unit, "closure handoff omits eligible graph unit"))
    for graph_unit in sorted(eligible_graph_units - graph_units):
        findings.append(InteractionFinding("INTERACTION022", graph_unit, "closure handoff eligible_graph_units references unknown graph unit"))

    blocked_units = set(_text_values(distill_closure_handoff_manifest.get("blocked_unit_refs", [])))
    blocked_gaps = set(_text_values(distill_closure_handoff_manifest.get("blocked_product_gap_refs", [])))
    open_gaps = {
        str(row.get("gap_id"))
        for row in _payload_records(distill_product_expansion_gaps, "records")
        if row.get("gap_id") and row.get("status") == "OPEN"
    }
    graph_source_refs = _graph_source_refs(graph)

    for unit_id in sorted(blocked_units):
        if unit_id in eligible_graph_units or unit_id in graph_source_refs:
            findings.append(InteractionFinding("INTERACTION022", unit_id, "blocked distilled unit cannot become eligible graph authority"))
        if unit_id not in blocked_graph_units:
            findings.append(InteractionFinding("INTERACTION022", unit_id, "blocked distilled unit is missing from closure blocked_graph_units"))

    for gap_id in sorted(blocked_gaps | open_gaps):
        if gap_id in eligible_graph_units or gap_id in graph_source_refs:
            findings.append(InteractionFinding("INTERACTION022", gap_id, "open product gap cannot become eligible graph authority"))
        if gap_id not in review_blockers:
            findings.append(InteractionFinding("INTERACTION022", gap_id, "open product gap is missing from closure review_blockers"))
    return findings


def _validate_artifact_envelope(
    artifact: Mapping[str, object],
    artifact_id: str,
    payload_key: str,
) -> List[InteractionFinding]:
    findings: List[InteractionFinding] = []
    missing = sorted(REQUIRED_ARTIFACT_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "artifact envelope missing fields: " + ", ".join(missing)))
    if artifact.get("artifact_id") != artifact_id:
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "artifact_id does not match contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "schema_payload_key does not match contract"))
    if payload_key not in artifact:
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "payload key is missing"))
    if artifact.get("validator_ref") != P3_VALIDATOR_REF:
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "validator_ref does not bind p3_interaction_closure.py"))
    upstream_refs = artifact.get("upstream_artifact_refs")
    upstream_hashes = artifact.get("upstream_hashes")
    if not _is_text_list(upstream_refs):
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "upstream_artifact_refs must be a text list"))
    if not isinstance(upstream_hashes, Mapping):
        findings.append(InteractionFinding("INTERACTION021", artifact_id, "upstream_hashes must be an object"))
    if _is_text_list(upstream_refs) and isinstance(upstream_hashes, Mapping):
        refs = set(_text_values(upstream_refs))
        hash_keys = {str(key) for key in upstream_hashes}
        if refs != hash_keys:
            findings.append(InteractionFinding("INTERACTION021", artifact_id, "upstream_artifact_refs and upstream_hashes keys must match"))
        for ref in sorted(refs & hash_keys):
            if not _is_sha256(upstream_hashes.get(ref)):
                findings.append(InteractionFinding("INTERACTION021", artifact_id, "upstream_hashes values must be sha256"))
    return findings


def _validate_payload_shape(
    artifact_name: str,
    artifact: Mapping[str, object],
) -> List[InteractionFinding]:
    artifact_id, payload_key = P3_CLOSURE_ARTIFACTS[artifact_name]
    payload = artifact.get(payload_key)
    expected_shape = P3_PAYLOAD_SHAPES.get(artifact_name, "list")
    if expected_shape == "mapping" and not isinstance(payload, Mapping):
        return [InteractionFinding("INTERACTION021", artifact_id, f"{payload_key} payload must be an object")]
    if expected_shape == "list" and not isinstance(payload, list):
        return [InteractionFinding("INTERACTION021", artifact_id, f"{payload_key} payload must be a list")]
    if expected_shape == "list" and isinstance(payload, list):
        return [
            InteractionFinding("INTERACTION021", artifact_id, f"{payload_key} payload rows must be objects")
            for item in payload
            if not isinstance(item, Mapping)
        ]
    if artifact_name == "reaction_applicability" and isinstance(payload, Mapping):
        return [
            InteractionFinding("INTERACTION021", artifact_id, f"{payload_key} payload values must be objects")
            for item in payload.values()
            if not isinstance(item, Mapping)
        ]
    if artifact_name == "message_coverage_index" and isinstance(payload, Mapping):
        coverage = payload.get("coverage")
        if not isinstance(coverage, list):
            return [InteractionFinding("INTERACTION021", artifact_id, "coverage payload must be a list")]
        return [
            InteractionFinding("INTERACTION021", artifact_id, "coverage rows must be objects")
            for item in coverage
            if not isinstance(item, Mapping)
        ]
    return []


def _node_payload(node) -> Dict[str, object]:
    return {
        "node_id": node.node_id,
        "node_type": node.node_type.value,
        "source_refs": node.source_refs,
        "is_terminal": node.is_terminal,
        "terminal_reason": node.terminal_reason,
        "message_refs": node.message_refs or [],
        "failure_reason": node.failure_reason,
        "recovery_targets": node.recovery_targets or [],
        "resume_source": node.resume_source,
        "trap_justification": node.trap_justification,
    }


def _edge_payload(edge) -> Dict[str, object]:
    return {
        "edge_id": edge.edge_id,
        "source_node_id": edge.source_node_id,
        "target_ref": edge.target_ref,
        "edge_type": edge.edge_type.value,
    }


def _reaction_payload(reaction: ReactionRecord) -> Dict[str, object]:
    return {
        "reaction_id": reaction.reaction_id,
        "clickable_id": reaction.clickable_id,
        "source_node_id": reaction.source_node_id,
        "reaction_type": reaction.reaction_type.value,
        "target_ref": reaction.target_ref,
        "preconditions": reaction.preconditions,
        "failure_applicability": reaction.failure_applicability.value,
        "cancel_applicability": reaction.cancel_applicability.value,
        "async_applicability": reaction.async_applicability.value,
        "handoff_applicability": reaction.handoff_applicability.value,
        "success_behavior": reaction.success_behavior,
        "failure_behavior": reaction.failure_behavior,
        "cancel_behavior": reaction.cancel_behavior,
        "exception_behavior": reaction.exception_behavior,
        "message_refs": reaction.message_refs,
        "trace_refs": reaction.trace_refs,
        "repeat_trigger_strategy": reaction.repeat_trigger_strategy.value if reaction.repeat_trigger_strategy else None,
        "no_return_terminal": reaction.no_return_terminal,
    }


def _reaction_applicability_payload(reaction: ReactionRecord) -> Dict[str, object]:
    return {
        "failure_applicability": reaction.failure_applicability.value,
        "cancel_applicability": reaction.cancel_applicability.value,
        "async_applicability": reaction.async_applicability.value,
        "handoff_applicability": reaction.handoff_applicability.value,
    }


def _payload_records(artifact: Mapping[str, object], key: str) -> List[Mapping[str, object]]:
    value = artifact.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _payload_mapping(artifact: Mapping[str, object], key: str) -> Dict[str, Mapping[str, object]]:
    value = artifact.get(key, {})
    if not isinstance(value, Mapping):
        return {}
    return {str(item_key): item_value for item_key, item_value in value.items() if isinstance(item_value, Mapping)}


def _payload_object(artifact: Mapping[str, object], key: str) -> Dict[str, object]:
    value = artifact.get(key, {})
    if not isinstance(value, Mapping):
        return {}
    return dict(value)


def _outgoing_edges(graph: InteractionGraph) -> Dict[str, List]:
    outgoing: Dict[str, List] = {}
    for edge in graph.edges:
        outgoing.setdefault(edge.source_node_id, []).append(edge)
    return outgoing


def _graph_unit_ids(graph: InteractionGraph) -> Set[str]:
    return (
        graph.node_ids()
        | {edge.edge_id for edge in graph.edges}
        | {clickable.clickable_id for clickable in graph.clickables}
        | graph.reaction_ids()
        | graph.message_ids()
    )


def _graph_source_refs(graph: InteractionGraph) -> Set[str]:
    refs: Set[str] = set()
    for node in graph.nodes:
        refs.update(node.source_refs)
    for clickable in graph.clickables:
        refs.update(clickable.source_refs)
    for reaction in graph.reactions:
        refs.update(reaction.trace_refs)
    for message in graph.messages:
        refs.update(message.trace_refs)
    return refs


def _text_values(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]


def _is_text_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(char in "0123456789abcdef" for char in value)


def _duplicates(values: Sequence[str]) -> List[str]:
    result: List[str] = []
    seen: Set[str] = set()
    emitted: Set[str] = set()
    for value in values:
        if value in seen and value not in emitted:
            result.append(value)
            emitted.add(value)
        seen.add(value)
    return result
