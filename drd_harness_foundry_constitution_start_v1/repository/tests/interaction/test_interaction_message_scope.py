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


def test_interaction_copy_cannot_add_product_scope():
    graph = InteractionGraph(
        graph_id="GRAPH-COPY",
        entry_node_ids=["ENTRY"],
        nodes=[InteractionNode("ENTRY", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Done.")],
        edges=[],
        clickables=[],
        reactions=[],
        messages=[
            InteractionMessage(
                "MSG-EXPORT-FAILED",
                MessageType.FAILURE_MESSAGE,
                "ENTRY",
                None,
                "Export failed.",
                "Connect Salesforce to automatically sync future exports.",
                "connect_salesforce",
                [],
                ["RULE"],
            )
        ],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION020" in {finding.code for finding in findings}


def test_disabled_clickable_requires_disabled_reason_message():
    graph = InteractionGraph(
        graph_id="GRAPH-DISABLED",
        entry_node_ids=["ENTRY"],
        nodes=[
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("DONE", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Done."),
        ],
        edges=[InteractionEdge("EDGE-OPEN", "ENTRY", "DONE", EdgeType.NAVIGATES_TO)],
        clickables=[
            Clickable(
                "CLK-OPEN",
                "ENTRY",
                "Open",
                "button",
                ["SRC"],
                ["has_access"],
                "Disabled when access is missing.",
                "RX-OPEN",
            )
        ],
        reactions=[
            ReactionRecord(
                "RX-OPEN",
                "CLK-OPEN",
                "ENTRY",
                ReactionType.NAVIGATE,
                "DONE",
                [],
                FailureApplicability.CANNOT_FAIL,
                CancelApplicability.NOT_CANCELLABLE,
                AsyncApplicability.IMMEDIATE,
                HandoffApplicability.INTERNAL_ONLY,
                "Open done state.",
                None,
                None,
                None,
                [],
                ["RULE"],
            )
        ],
        messages=[],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION019" in {finding.code for finding in findings}
