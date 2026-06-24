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
)
from drd_harness.validators.interaction_closure import validate_interaction_graph


def async_graph(with_message=True):
    messages = [
        InteractionMessage("MSG-SAVING", MessageType.PROCESSING_MESSAGE, "SAVING", "RX-SAVE", "Save in progress.", "Saving. Wait.", "wait", [], ["RULE"])
    ] if with_message else []
    cancel_messages = [
        InteractionMessage("MSG-CANCEL", MessageType.CANCEL_CONFIRMATION, "EDIT", "RX-SAVE", "Save cancelled.", "Save cancelled. Continue editing.", "continue_editing", ["EDIT"], ["RULE"])
    ] if with_message else []
    return InteractionGraph(
        "GRAPH-ASYNC",
        ["EDIT"],
        [
            InteractionNode("EDIT", NodeType.PAGE, ["SRC"]),
            InteractionNode("SAVING", NodeType.PROCESSING, ["SRC"], message_refs=["MSG-SAVING"] if with_message else []),
            InteractionNode("SAVED", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Saved."),
            InteractionNode("FAILED", NodeType.FAILURE, ["SRC"], message_refs=["MSG-FAIL"], failure_reason="Save failed.", recovery_targets=["EDIT"]),
        ],
        [
            InteractionEdge("EDGE-SAVE", "EDIT", "SAVING", EdgeType.STARTS_ASYNC),
            InteractionEdge("EDGE-OK", "SAVING", "SAVED", EdgeType.ASYNC_SUCCESS),
            InteractionEdge("EDGE-FAIL", "SAVING", "FAILED", EdgeType.ASYNC_FAILURE),
            InteractionEdge("EDGE-RETRY", "FAILED", "EDIT", EdgeType.RETRIES),
        ],
        [Clickable("CLK-SAVE", "EDIT", "Save", "button", ["SRC"], [], None, "RX-SAVE")],
        [
            ReactionRecord(
                "RX-SAVE",
                "CLK-SAVE",
                "EDIT",
                ReactionType.START_ASYNC,
                "SAVING",
                [],
                FailureApplicability.CAN_FAIL,
                CancelApplicability.CANCELLABLE,
                AsyncApplicability.NON_IMMEDIATE,
                HandoffApplicability.INTERNAL_ONLY,
                "Enter saving state.",
                "Show save failed state.",
                "Return to edit without saving.",
                "Timeout allows retry.",
                ["MSG-SAVING", "MSG-FAIL", "MSG-CANCEL"] if with_message else [],
                ["RULE"],
                DuplicateTriggerStrategy.DISABLE_DUPLICATE_TRIGGER,
            )
        ],
        messages + cancel_messages + [
            InteractionMessage("MSG-FAIL", MessageType.FAILURE_MESSAGE, "FAILED", "RX-SAVE", "Save failed.", "Save failed. Retry or edit.", "retry_or_edit", ["EDIT"], ["RULE"])
        ],
    )


def test_async_action_requires_processing_message():
    findings = validate_interaction_graph(async_graph(with_message=False))

    assert "INTERACTION016" in {finding.code for finding in findings}


def test_async_action_with_processing_and_failure_copy_passes():
    assert validate_interaction_graph(async_graph(with_message=True)) == []


def test_async_reaction_must_bind_processing_message_type():
    graph = async_graph(with_message=True)
    reaction = graph.reactions[0]
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        graph.clickables,
        [ReactionRecord(**{**reaction.__dict__, "message_refs": ["MSG-FAIL", "MSG-CANCEL"]})],
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION016" in {finding.code for finding in findings}


def test_external_handoff_requires_return_cancel_failure():
    graph = InteractionGraph(
        "GRAPH-HANDOFF",
        ["ENTRY"],
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("OAUTH", NodeType.EXTERNAL_HANDOFF, ["SRC"], message_refs=["MSG-HANDOFF"]),
        ],
        [InteractionEdge("EDGE-HANDOFF", "ENTRY", "OAUTH", EdgeType.HANDOFF_EXTERNAL)],
        [Clickable("CLK-CONNECT", "ENTRY", "Connect CRM", "button", ["SRC"], [], None, "RX-HANDOFF")],
        [
            ReactionRecord(
                "RX-HANDOFF",
                "CLK-CONNECT",
                "ENTRY",
                ReactionType.HANDOFF,
                "OAUTH",
                [],
                FailureApplicability.CAN_FAIL,
                CancelApplicability.CANCELLABLE,
                AsyncApplicability.IMMEDIATE,
                HandoffApplicability.EXTERNAL_HANDOFF,
                "Open external auth.",
                "Show auth failure.",
                "Return to entry.",
                "External auth timeout.",
                ["MSG-HANDOFF"],
                ["RULE"],
            )
        ],
        [InteractionMessage("MSG-HANDOFF", MessageType.HANDOFF_NOTICE, "OAUTH", "RX-HANDOFF", "Leaving app.", "You are opening an external authorization flow.", "continue", [], ["RULE"])],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION009" in {finding.code for finding in findings}


def test_failure_node_requires_reason_recovery_and_message():
    graph = InteractionGraph(
        "GRAPH-FAIL",
        ["ENTRY"],
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("FAILED", NodeType.FAILURE, ["SRC"]),
        ],
        [InteractionEdge("EDGE-FAIL", "ENTRY", "FAILED", EdgeType.NAVIGATES_TO)],
        [],
        [],
        [],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION010" in {finding.code for finding in findings}
    assert "INTERACTION017" in {finding.code for finding in findings}


def test_cancellable_reaction_requires_cancel_copy():
    graph = async_graph(with_message=True)
    reaction = graph.reactions[0]
    graph = InteractionGraph(
        graph.graph_id,
        graph.entry_node_ids,
        graph.nodes,
        graph.edges,
        graph.clickables,
        [ReactionRecord(**{**reaction.__dict__, "message_refs": ["MSG-SAVING", "MSG-FAIL"]})],
        graph.messages,
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION019" in {finding.code for finding in findings}


def test_exit_reaction_requires_exit_consequence_copy():
    graph = InteractionGraph(
        "GRAPH-EXIT",
        ["ENTRY"],
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("END", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Exited."),
        ],
        [InteractionEdge("EDGE-EXIT", "ENTRY", "END", EdgeType.EXITS)],
        [Clickable("CLK-EXIT", "ENTRY", "Exit", "button", ["SRC"], [], None, "RX-EXIT")],
        [
            ReactionRecord(
                "RX-EXIT",
                "CLK-EXIT",
                "ENTRY",
                ReactionType.EXIT,
                "END",
                [],
                FailureApplicability.CANNOT_FAIL,
                CancelApplicability.NOT_CANCELLABLE,
                AsyncApplicability.IMMEDIATE,
                HandoffApplicability.INTERNAL_ONLY,
                "Exit flow.",
                None,
                None,
                None,
                [],
                ["RULE"],
            )
        ],
        [],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION019" in {finding.code for finding in findings}


def test_success_node_requires_success_message():
    graph = InteractionGraph(
        "GRAPH-SUCCESS",
        ["ENTRY"],
        [
            InteractionNode("ENTRY", NodeType.PAGE, ["SRC"]),
            InteractionNode("DONE", NodeType.SUCCESS, ["SRC"]),
            InteractionNode("END", NodeType.TERMINAL, ["SRC"], is_terminal=True, terminal_reason="Done."),
        ],
        [
            InteractionEdge("EDGE-SUBMIT", "ENTRY", "DONE", EdgeType.SUBMITS_ACTION),
            InteractionEdge("EDGE-END", "DONE", "END", EdgeType.TERMINATES),
        ],
        [Clickable("CLK-SUBMIT", "ENTRY", "Submit", "button", ["SRC"], [], None, "RX-SUBMIT")],
        [
            ReactionRecord(
                "RX-SUBMIT",
                "CLK-SUBMIT",
                "ENTRY",
                ReactionType.SUBMIT,
                "DONE",
                [],
                FailureApplicability.CANNOT_FAIL,
                CancelApplicability.NOT_CANCELLABLE,
                AsyncApplicability.IMMEDIATE,
                HandoffApplicability.INTERNAL_ONLY,
                "Show done state.",
                None,
                None,
                None,
                [],
                ["RULE"],
            )
        ],
        [],
    )

    findings = validate_interaction_graph(graph)

    assert "INTERACTION017" in {finding.code for finding in findings}
