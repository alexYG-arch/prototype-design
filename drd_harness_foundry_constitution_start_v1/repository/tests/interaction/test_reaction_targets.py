from drd_harness.rules.interaction import (
    AsyncApplicability,
    CancelApplicability,
    Clickable,
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
)
from drd_harness.validators.interaction_closure import validate_interaction_graph


def basic_graph(reaction_target="NODE-DETAIL"):
    return InteractionGraph(
        graph_id="GRAPH-001",
        entry_node_ids=["NODE-LIST"],
        nodes=[
            InteractionNode("NODE-LIST", NodeType.PAGE, ["ADOPT-LIST"]),
            InteractionNode("NODE-DETAIL", NodeType.PAGE, ["ADOPT-DETAIL"]),
            InteractionNode("NODE-END", NodeType.TERMINAL, ["RULE"], is_terminal=True, terminal_reason="Task is complete."),
        ],
        edges=[
            InteractionEdge("EDGE-OPEN", "NODE-LIST", "NODE-DETAIL", EdgeType.NAVIGATES_TO),
            InteractionEdge("EDGE-END", "NODE-DETAIL", "NODE-END", EdgeType.TERMINATES),
        ],
        clickables=[
            Clickable("CLK-ROW", "NODE-LIST", "Project row", "row", ["ADOPT-LIST"], ["has_project"], None, "RX-OPEN")
        ],
        reactions=[
            ReactionRecord(
                reaction_id="RX-OPEN",
                clickable_id="CLK-ROW",
                source_node_id="NODE-LIST",
                reaction_type=ReactionType.NAVIGATE,
                target_ref=reaction_target,
                preconditions=["project selected"],
                failure_applicability=FailureApplicability.CANNOT_FAIL,
                cancel_applicability=CancelApplicability.NOT_CANCELLABLE,
                async_applicability=AsyncApplicability.IMMEDIATE,
                handoff_applicability=HandoffApplicability.INTERNAL_ONLY,
                success_behavior="Open detail.",
                failure_behavior=None,
                cancel_behavior=None,
                exception_behavior=None,
                message_refs=[],
                trace_refs=["INF-OPEN"],
            )
        ],
        messages=[],
    )


def test_valid_reaction_target_passes():
    assert validate_interaction_graph(basic_graph()) == []


def test_dangling_reaction_target_fails():
    findings = validate_interaction_graph(basic_graph("NODE-MISSING"))

    assert "INTERACTION004" in {finding.code for finding in findings}


def test_clickable_without_reaction_fails():
    graph = basic_graph()
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        [Clickable("CLK-MISSING", "NODE-LIST", "Export", "button", ["ADOPT"], [], None, "RX-MISSING")],
        graph.reactions,
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION003" in {finding.code for finding in findings}


def test_unknown_applicability_blocks_canonical_reaction():
    graph = basic_graph()
    reaction = graph.reactions[0]
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        graph.clickables,
        [
            ReactionRecord(
                **{**reaction.__dict__, "failure_applicability": FailureApplicability.UNKNOWN_REQUIRES_REVIEW}
            )
        ],
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION005" in {finding.code for finding in findings}


def test_cross_wired_clickable_and_reaction_fails():
    graph = basic_graph()
    reactions = [
        ReactionRecord(
            **{**graph.reactions[0].__dict__, "reaction_id": "RX-OPEN-A", "clickable_id": "CLK-B"}
        ),
        ReactionRecord(
            **{**graph.reactions[0].__dict__, "reaction_id": "RX-OPEN-B", "clickable_id": "CLK-A"}
        ),
    ]
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        [
            Clickable("CLK-A", "NODE-LIST", "Project row A", "row", ["ADOPT-LIST"], [], None, "RX-OPEN-A"),
            Clickable("CLK-B", "NODE-LIST", "Project row B", "row", ["ADOPT-LIST"], [], None, "RX-OPEN-B"),
        ],
        reactions,
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION003" in {finding.code for finding in findings}


def test_clickable_and_reaction_source_mismatch_fails():
    graph = basic_graph()
    reaction = graph.reactions[0]
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        graph.clickables,
        [ReactionRecord(**{**reaction.__dict__, "source_node_id": "NODE-DETAIL"})],
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION003" in {finding.code for finding in findings}


def test_reaction_without_matching_graph_edge_fails():
    graph = basic_graph()
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        [InteractionEdge("EDGE-END", "NODE-DETAIL", "NODE-END", EdgeType.TERMINATES)],
        graph.clickables,
        graph.reactions,
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION013" in {finding.code for finding in findings}
