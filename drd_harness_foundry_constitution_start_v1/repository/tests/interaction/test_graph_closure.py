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


def graph_with_nodes(nodes, edges):
    return InteractionGraph(
        graph_id="GRAPH",
        entry_node_ids=["ENTRY"],
        nodes=nodes,
        edges=edges,
        clickables=[],
        reactions=[],
        messages=[],
    )


def test_unreachable_required_node_fails():
    graph = graph_with_nodes(
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("ORPHAN", NodeType.STATE, ["SRC"]),
        ],
        [InteractionEdge("EDGE-END", "ENTRY", "TERMINAL:DONE", EdgeType.TERMINATES)],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION006" in {finding.code for finding in findings}


def test_non_terminal_dead_end_fails():
    graph = graph_with_nodes(
        [InteractionNode("ENTRY", NodeType.PAGE, ["SRC"])],
        [],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION007" in {finding.code for finding in findings}


def test_overlay_without_closure_fails():
    graph = graph_with_nodes(
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("MODAL", NodeType.OVERLAY, ["SRC"]),
        ],
        [InteractionEdge("EDGE-OPEN", "ENTRY", "MODAL", EdgeType.OPENS_OVERLAY)],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION011" in {finding.code for finding in findings}


def test_overlay_with_cancel_closure_passes_overlay_check():
    graph = graph_with_nodes(
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("MODAL", NodeType.OVERLAY, ["SRC"]),
            InteractionNode("END", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Closed."),
        ],
        [
            InteractionEdge("EDGE-OPEN", "ENTRY", "MODAL", EdgeType.OPENS_OVERLAY),
            InteractionEdge("EDGE-CLOSE", "MODAL", "ENTRY", EdgeType.CLOSES_OVERLAY),
            InteractionEdge("EDGE-END", "ENTRY", "END", EdgeType.TERMINATES),
        ],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION011" not in {finding.code for finding in findings}


def test_dangling_edge_target_fails_reference_integrity():
    graph = graph_with_nodes(
        [InteractionNode("ENTRY", NodeType.PAGE, ["SRC"])],
        [InteractionEdge("EDGE-MISSING", "ENTRY", "MISSING", EdgeType.NAVIGATES_TO)],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION012" in {finding.code for finding in findings}


def test_dangling_source_and_message_refs_fail_reference_integrity():
    graph = InteractionGraph(
        graph_id="GRAPH-REFS",
        entry_node_ids=["ENTRY"],
        nodes=[InteractionNode("ENTRY", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Done.")],
        edges=[],
        clickables=[Clickable("CLK-OPEN", "MISSING-NODE", "Open", "button", ["SRC"], [], None, "RX-OPEN")],
        reactions=[
            ReactionRecord(
                "RX-OPEN",
                "CLK-OPEN",
                "MISSING-NODE",
                ReactionType.NAVIGATE,
                "ENTRY",
                [],
                FailureApplicability.CANNOT_FAIL,
                CancelApplicability.NOT_CANCELLABLE,
                AsyncApplicability.IMMEDIATE,
                HandoffApplicability.INTERNAL_ONLY,
                "Open.",
                None,
                None,
                None,
                ["MSG-MISSING"],
                ["SRC"],
            )
        ],
        messages=[
            InteractionMessage(
                "MSG-ORPHAN",
                MessageType.SUCCESS_MESSAGE,
                "MISSING-NODE",
                "RX-MISSING",
                "Done.",
                "Done.",
                "none",
                ["MISSING-RECOVERY"],
                ["SRC"],
            )
        ],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION012" in {finding.code for finding in findings}
