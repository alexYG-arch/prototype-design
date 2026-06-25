import hashlib
import json
from pathlib import Path

from drd_harness.rules.interaction import (
    AsyncApplicability,
    MessageType,
    NodeType,
    message_has_product_scope_expansion,
)
from drd_harness.validators.interaction_closure import (
    interaction_graph_from_mapping,
    validate_interaction_artifact_slices,
    validate_interaction_graph,
    validate_required_clickable_coverage,
    validate_spec_edge_table_coverage,
)


FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")
SPEC_INVENTORY = Path("build_program/phases/P2/candidates/P2-SPEC-01/P2_PRD_ELEMENT_INVENTORY.json")
SPEC_EDGES = Path("build_program/phases/P2/candidates/P2-SPEC-01/P2_INTERACTION_EDGE_TABLE.json")
REQUIRED_ARTIFACT_FIELDS = {
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
P2_IMPL_02_REASONING_ARTIFACT_FILES = {
    "p2.tiny_brief.inference_records": FIXTURE_ROOT / "inference_records.json",
    "p2.tiny_brief.structural_completion_review": FIXTURE_ROOT / "structural_completion_review.json",
}


def test_interaction_graph_passes_full_closure_validation():
    graph_artifact = _load("interaction_graph.json")
    graph = interaction_graph_from_mapping(graph_artifact["graph"])

    _assert_artifact_contract(graph_artifact, "p2.tiny_brief.interaction_graph", "graph")
    assert validate_interaction_graph(graph) == []
    assert {node.node_type for node in graph.nodes} >= {
        NodeType.OVERLAY,
        NodeType.PROCESSING,
        NodeType.FAILURE,
        NodeType.SUCCESS,
    }


def test_clickable_inventory_covers_approved_prd_clickables_and_edge_table():
    graph = _graph()
    spec = json.loads(SPEC_INVENTORY.read_text(encoding="utf-8"))
    required_clickables = {
        element["element_id"] for element in spec["elements"] if element["category"] == "clickable"
    }
    edge_table = json.loads(SPEC_EDGES.read_text(encoding="utf-8"))
    required_edges = {edge["edge_id"] for edge in edge_table["edges"]}

    clickable_artifact = _load("clickable_inventory.json")
    _assert_artifact_contract(clickable_artifact, "p2.tiny_brief.clickable_inventory", "records")
    assert {record["clickable_id"] for record in clickable_artifact["records"]} == required_clickables
    assert validate_required_clickable_coverage(graph, sorted(required_clickables)) == []
    assert validate_spec_edge_table_coverage(graph, edge_table["edges"]) == []
    assert required_edges <= {edge.edge_id for edge in graph.edges}


def test_interaction_split_artifacts_match_the_graph_payload():
    graph = _graph()
    async_artifact = _load("async_behavior.json")
    failure_artifact = _load("failure_recovery.json")
    messages_artifact = _load("interaction_messages.json")

    _assert_artifact_contract(async_artifact, "p2.tiny_brief.async_behavior", "records")
    _assert_artifact_contract(failure_artifact, "p2.tiny_brief.failure_recovery", "records")
    _assert_artifact_contract(messages_artifact, "p2.tiny_brief.interaction_messages", "records")

    assert validate_interaction_artifact_slices(
        graph,
        clickable_records=_load("clickable_inventory.json")["records"],
        async_records=async_artifact["records"],
        failure_records=failure_artifact["records"],
        message_records=messages_artifact["records"],
    ) == []


def test_async_failure_and_disabled_copy_are_explicit_and_same_task_scoped():
    graph = _graph()
    async_reactions = {
        reaction.reaction_id: reaction
        for reaction in graph.reactions
        if reaction.async_applicability == AsyncApplicability.NON_IMMEDIATE
    }
    messages = {message.message_id: message for message in graph.messages}

    assert set(async_reactions) == {
        "reaction.brief.validate",
        "reaction.brief.generate",
        "reaction.overlay.retry",
    }
    for reaction in async_reactions.values():
        assert any(messages[message_id].message_type == MessageType.PROCESSING_MESSAGE for message_id in reaction.message_refs)
        assert any(
            messages[message_id].message_type in {MessageType.FAILURE_MESSAGE, MessageType.RECOVERY_INSTRUCTION}
            for message_id in reaction.message_refs
        )

    assert messages["msg.generate_disabled"].message_type == MessageType.DISABLED_REASON
    assert messages["msg.failure.transient"].recovery_targets == [
        "reaction.overlay.retry",
        "reaction.overlay.edit_brief",
    ]
    assert not any(message_has_product_scope_expansion(message) for message in graph.messages)


def test_failure_prone_save_draft_has_recoverable_failure_graph_path():
    graph = _graph()
    failure_edges = {
        edge.edge_id
        for edge in graph.edges
        if edge.source_node_id == "state.editing" and edge.target_ref == "state.recoverable_failure"
    }

    assert "edge.editing.save_draft.failure_to_recoverable_failure" in failure_edges


def test_interaction_slice_validator_rejects_broken_async_processing_binding():
    graph = _graph()
    async_records = [dict(record) for record in _load("async_behavior.json")["records"]]
    async_records[0]["processing_node_id"] = "state.editing"

    findings = validate_interaction_artifact_slices(
        graph,
        clickable_records=_load("clickable_inventory.json")["records"],
        async_records=async_records,
        failure_records=_load("failure_recovery.json")["records"],
        message_records=_load("interaction_messages.json")["records"],
    )

    assert [finding.code for finding in findings] == ["INTERACTION008", "INTERACTION008"]


def test_interaction_slice_validator_rejects_missing_async_record():
    graph = _graph()
    async_records = [
        record
        for record in _load("async_behavior.json")["records"]
        if record["reaction_id"] != "reaction.brief.generate"
    ]

    findings = validate_interaction_artifact_slices(
        graph,
        clickable_records=_load("clickable_inventory.json")["records"],
        async_records=async_records,
        failure_records=_load("failure_recovery.json")["records"],
        message_records=_load("interaction_messages.json")["records"],
    )

    assert [finding.code for finding in findings] == ["INTERACTION008"]


def test_interaction_slice_validator_rejects_failure_recovery_target_drift():
    graph = _graph()
    failure_records = [dict(record) for record in _load("failure_recovery.json")["records"]]
    failure_records[0]["recovery_targets"] = ["reaction.overlay.retry"]

    findings = validate_interaction_artifact_slices(
        graph,
        clickable_records=_load("clickable_inventory.json")["records"],
        async_records=_load("async_behavior.json")["records"],
        failure_records=failure_records,
        message_records=_load("interaction_messages.json")["records"],
    )

    assert [finding.code for finding in findings] == ["INTERACTION010"]


def test_interaction_slice_validator_rejects_clickable_record_drift():
    graph = _graph()
    clickable_records = [dict(record) for record in _load("clickable_inventory.json")["records"]]
    clickable_records[0]["label_or_affordance"] = "Drifted label"

    findings = validate_interaction_artifact_slices(
        graph,
        clickable_records=clickable_records,
        async_records=_load("async_behavior.json")["records"],
        failure_records=_load("failure_recovery.json")["records"],
        message_records=_load("interaction_messages.json")["records"],
    )

    assert [finding.code for finding in findings] == ["INTERACTION003"]


def test_interaction_slice_validator_rejects_message_record_drift():
    graph = _graph()
    message_records = [dict(record) for record in _load("interaction_messages.json")["records"]]
    message_records[0]["user_visible_summary"] = "Drifted copy"

    findings = validate_interaction_artifact_slices(
        graph,
        clickable_records=_load("clickable_inventory.json")["records"],
        async_records=_load("async_behavior.json")["records"],
        failure_records=_load("failure_recovery.json")["records"],
        message_records=message_records,
    )

    assert [finding.code for finding in findings] == ["INTERACTION017"]


def test_spec_edge_table_validator_rejects_product_expansion_edge():
    graph = _graph()
    edge_rows = json.loads(SPEC_EDGES.read_text(encoding="utf-8"))["edges"]
    broken = [dict(row) for row in edge_rows]
    broken[0]["product_expansion_allowed"] = True

    findings = validate_spec_edge_table_coverage(graph, broken)

    assert [finding.code for finding in findings] == ["INTERACTION020"]


def test_spec_edge_table_validator_rejects_clickable_trigger_drift():
    graph = _graph()
    edge_rows = json.loads(SPEC_EDGES.read_text(encoding="utf-8"))["edges"]
    broken = [dict(row) for row in edge_rows]
    broken[2]["trigger_element"] = "brief.generate"

    findings = validate_spec_edge_table_coverage(graph, broken)

    assert [finding.code for finding in findings] == ["INTERACTION013"]


def test_spec_edge_table_validator_rejects_unjustified_extra_graph_edge():
    payload = _load("interaction_graph.json")
    payload["graph"]["edges"].append(
        {
            "edge_id": "edge.editing.unreviewed.to_final_ready",
            "source_node_id": "state.editing",
            "target_ref": "state.final_ready",
            "edge_type": "NAVIGATES_TO",
        }
    )
    graph = interaction_graph_from_mapping(payload["graph"])
    edge_rows = json.loads(SPEC_EDGES.read_text(encoding="utf-8"))["edges"]

    findings = validate_spec_edge_table_coverage(graph, edge_rows)

    assert [finding.code for finding in findings] == ["INTERACTION013"]


def test_spec_edge_table_validator_rejects_extra_edge_traced_by_unrelated_reaction():
    payload = _load("interaction_graph.json")
    for reaction in payload["graph"]["reactions"]:
        if reaction["reaction_id"] in {"reaction.brief.validate", "reaction.brief.generate"}:
            reaction["trace_refs"] = [
                trace_ref
                for trace_ref in reaction["trace_refs"]
                if trace_ref != "edge.editing.opens_validation_overlay"
            ]
        if reaction["reaction_id"] == "reaction.brief.save_draft":
            reaction["trace_refs"].append("edge.editing.opens_validation_overlay")
    graph = interaction_graph_from_mapping(payload["graph"])
    edge_rows = json.loads(SPEC_EDGES.read_text(encoding="utf-8"))["edges"]

    findings = validate_spec_edge_table_coverage(graph, edge_rows)

    assert [finding.code for finding in findings] == ["INTERACTION013"]


def test_failure_prone_reaction_requires_graph_failure_path():
    payload = _load("interaction_graph.json")
    payload["graph"]["edges"] = [
        edge
        for edge in payload["graph"]["edges"]
        if edge["edge_id"] != "edge.editing.save_draft.failure_to_recoverable_failure"
    ]
    graph = interaction_graph_from_mapping(payload["graph"])

    findings = validate_interaction_graph(graph)

    assert any(
        finding.code == "INTERACTION010"
        and finding.subject_id == "reaction.brief.save_draft"
        and "failure-prone reaction lacks graph edge" in finding.message
        for finding in findings
    )


def test_required_clickable_validator_reports_missing_prd_clickable():
    graph = _graph()

    findings = validate_required_clickable_coverage(graph, ["brief.generate", "brief.unknown"])

    assert [finding.code for finding in findings] == ["INTERACTION003"]


def test_interaction_artifacts_bind_reasoning_upstream_hashes():
    for filename in [
        "interaction_graph.json",
        "clickable_inventory.json",
        "async_behavior.json",
        "failure_recovery.json",
        "interaction_messages.json",
    ]:
        artifact = _load(filename)
        for artifact_id, path in P2_IMPL_02_REASONING_ARTIFACT_FILES.items():
            assert artifact_id in artifact["upstream_artifact_refs"]
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(path)


def _graph():
    return interaction_graph_from_mapping(_load("interaction_graph.json")["graph"])


def _load(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _assert_artifact_contract(payload, artifact_id: str, payload_key: str):
    assert REQUIRED_ARTIFACT_FIELDS <= set(payload)
    assert payload["artifact_id"] == artifact_id
    assert payload["stage_id"] == "DRD-03-INTERACTION"
    assert payload["fixture_id"] == "tiny_brief_intake"
    assert payload["schema_payload_key"] == payload_key
    assert payload["validator_ref"] == "repository/src/drd_harness/validators/interaction_closure.py"
    assert payload["promotion_state"] == "CANDIDATE"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
