"""Evidence-driven P4 recovery and resume decisions."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from drd_harness.kernel.hashline import sha256_file, sha256_text


REQUIRED_RUN_STATE_FIELDS = [
    "run_id",
    "program_id",
    "driver_version",
    "original_command",
    "adapter_id",
    "source_refs",
    "input_hashes",
    "upstream_lock_refs",
    "candidate_subject_hashes",
    "review_decision_hashes",
    "dag_snapshot_hash",
    "execution_plan_hash",
    "node_states",
    "written_paths",
    "output_hashes",
    "gate_states",
    "failure_records",
    "recovery_history",
]

DECISIONS = {
    "SKIP",
    "REPLAY",
    "BLOCK_HUMAN_GATE",
    "BLOCK_INVALIDATION",
    "BLOCK_LOCK_BOUNDARY",
    "BLOCK_UNSAFE_STATE",
}

REASON_CODES = {
    "INPUT_HASH_CHANGED",
    "INPUT_SOURCE_MISSING",
    "ADAPTER_NORMALIZATION_CHANGED",
    "UPSTREAM_LOCK_HASH_CHANGED",
    "CANDIDATE_SUBJECT_HASH_CHANGED",
    "REVIEW_DECISION_HASH_CHANGED",
    "DAG_SNAPSHOT_CHANGED",
    "EXECUTION_PLAN_CHANGED",
    "OUTPUT_HASH_CHANGED",
    "OUTPUT_MISSING",
    "WRITE_SCOPE_CHANGED",
    "FAILURE_RECORD_INCOMPLETE",
    "REQUESTED_NODE_NOT_IN_DAG",
}

HUMAN_GATE_REASONS = {
    "CANDIDATE_SUBJECT_HASH_CHANGED",
    "REVIEW_DECISION_HASH_CHANGED",
    "UPSTREAM_LOCK_HASH_CHANGED",
}
INVALIDATION_REASONS = {
    "INPUT_HASH_CHANGED",
    "INPUT_SOURCE_MISSING",
    "ADAPTER_NORMALIZATION_CHANGED",
    "DAG_SNAPSHOT_CHANGED",
    "EXECUTION_PLAN_CHANGED",
}
REPLAYABLE_OUTPUT_REASONS = {"OUTPUT_HASH_CHANGED", "OUTPUT_MISSING"}


@dataclass(frozen=True)
class InvalidationRecord:
    reason_code: str
    affected_node_id: str
    affected_path: str
    prior_value: str
    current_value: str
    required_stop_rule: str
    human_gate_required: bool


def load_run_state(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_run_state_shape(run_state: Mapping[str, Any]) -> List[str]:
    return sorted(field for field in REQUIRED_RUN_STATE_FIELDS if field not in run_state)


def resolve_resume_decision(
    run_state: Mapping[str, Any],
    requested_resume_node: str,
    *,
    current_evidence: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    current = dict(current_evidence or {})
    prior_hash = sha256_text(json.dumps(run_state, sort_keys=True, separators=(",", ":")))
    missing = validate_run_state_shape(run_state)
    if missing:
        return _unsafe_report(run_state, requested_resume_node, prior_hash, missing)

    node_states = _node_map(run_state.get("node_states", {}))
    if requested_resume_node not in node_states:
        record = InvalidationRecord(
            reason_code="REQUESTED_NODE_NOT_IN_DAG",
            affected_node_id=requested_resume_node,
            affected_path="node_states",
            prior_value="MISSING",
            current_value=requested_resume_node,
            required_stop_rule="BLOCK_UNSAFE_STATE",
            human_gate_required=True,
        )
        return _report(run_state, requested_resume_node, prior_hash, "BLOCK_UNSAFE_STATE", [record], [])

    invalidations = classify_invalidation(run_state, requested_resume_node, current)
    failure_findings = _failure_record_invalidations(run_state, requested_resume_node)
    invalidations.extend(failure_findings)
    invalidations = _sort_invalidations(invalidations)

    gate_decision = _gate_decision(run_state, requested_resume_node)
    if gate_decision:
        return _report(run_state, requested_resume_node, prior_hash, gate_decision, invalidations, [])

    if any(record.reason_code in HUMAN_GATE_REASONS for record in invalidations):
        return _report(run_state, requested_resume_node, prior_hash, "BLOCK_HUMAN_GATE", invalidations, [])
    if any(record.reason_code == "WRITE_SCOPE_CHANGED" for record in invalidations):
        return _report(run_state, requested_resume_node, prior_hash, "BLOCK_INVALIDATION", invalidations, [])
    if any(record.reason_code in INVALIDATION_REASONS for record in invalidations):
        return _report(run_state, requested_resume_node, prior_hash, "BLOCK_INVALIDATION", invalidations, [])
    if any(record.reason_code == "FAILURE_RECORD_INCOMPLETE" for record in invalidations):
        return _report(run_state, requested_resume_node, prior_hash, "BLOCK_UNSAFE_STATE", invalidations, [])
    if invalidations and all(record.reason_code in REPLAYABLE_OUTPUT_REASONS for record in invalidations):
        return _report(run_state, requested_resume_node, prior_hash, "REPLAY", invalidations, [requested_resume_node])
    return _report(run_state, requested_resume_node, prior_hash, "SKIP", [], [])


def classify_invalidation(
    run_state: Mapping[str, Any],
    requested_resume_node: str,
    current_evidence: Mapping[str, Any],
) -> List[InvalidationRecord]:
    records: List[InvalidationRecord] = []
    records.extend(_compare_hash_map(run_state, current_evidence, "input_hashes", "INPUT_HASH_CHANGED", "INPUT_SOURCE_MISSING", requested_resume_node))
    records.extend(_compare_hash_map(run_state, current_evidence, "upstream_lock_refs", "UPSTREAM_LOCK_HASH_CHANGED", "UPSTREAM_LOCK_HASH_CHANGED", requested_resume_node))
    records.extend(_compare_hash_map(run_state, current_evidence, "candidate_subject_hashes", "CANDIDATE_SUBJECT_HASH_CHANGED", "CANDIDATE_SUBJECT_HASH_CHANGED", requested_resume_node))
    records.extend(_compare_hash_map(run_state, current_evidence, "review_decision_hashes", "REVIEW_DECISION_HASH_CHANGED", "REVIEW_DECISION_HASH_CHANGED", requested_resume_node))
    records.extend(_compare_scalar(run_state, current_evidence, "dag_snapshot_hash", "DAG_SNAPSHOT_CHANGED", requested_resume_node))
    records.extend(_compare_scalar(run_state, current_evidence, "execution_plan_hash", "EXECUTION_PLAN_CHANGED", requested_resume_node))
    records.extend(_compare_hash_map(run_state, current_evidence, "output_hashes", "OUTPUT_HASH_CHANGED", "OUTPUT_MISSING", requested_resume_node))
    records.extend(_write_scope_invalidations(run_state, current_evidence, requested_resume_node))
    return _sort_invalidations(records)


def current_hashes_for_paths(paths: Iterable[str]) -> Dict[str, str]:
    result = {}
    for raw_path in sorted(paths):
        path = Path(raw_path)
        result[raw_path] = sha256_file(path) if path.is_file() else "MISSING"
    return result


def reject_semantic_recovery_fields(packet: Mapping[str, Any]) -> List[str]:
    forbidden = {"product_requirements", "page_elements", "layout_rules", "business_contracts", "inferred_product_requirement"}
    return sorted(key for key in forbidden if key in packet)


def _unsafe_report(run_state: Mapping[str, Any], requested_resume_node: str, prior_hash: str, missing: List[str]) -> Dict[str, Any]:
    records = [
        InvalidationRecord(
            reason_code="FAILURE_RECORD_INCOMPLETE",
            affected_node_id=requested_resume_node,
            affected_path=field,
            prior_value="REQUIRED",
            current_value="MISSING",
            required_stop_rule="BLOCK_UNSAFE_STATE",
            human_gate_required=True,
        )
        for field in missing
    ]
    return _report(run_state, requested_resume_node, prior_hash, "BLOCK_UNSAFE_STATE", records, [])


def _report(
    run_state: Mapping[str, Any],
    requested_resume_node: str,
    prior_hash: str,
    decision: str,
    invalidations: List[InvalidationRecord],
    replayed_nodes: List[str],
) -> Dict[str, Any]:
    skipped_nodes = [requested_resume_node] if decision == "SKIP" else []
    blocked_nodes = [requested_resume_node] if decision.startswith("BLOCK_") else []
    node_decision = {
        "node_id": requested_resume_node,
        "decision": decision,
        "dependency_hash_status": "PASS" if not invalidations else "DRIFT",
        "output_hash_status": "PASS" if not any(item.reason_code in REPLAYABLE_OUTPUT_REASONS for item in invalidations) else "DRIFT",
        "write_scope_status": "PASS" if not any(item.reason_code == "WRITE_SCOPE_CHANGED" for item in invalidations) else "FAIL",
        "gate_status": decision if decision.startswith("BLOCK_") else "PASS",
        "reason_codes": sorted({item.reason_code for item in invalidations}),
    }
    return {
        "run_id": str(run_state.get("run_id", "")),
        "requested_resume_node": requested_resume_node,
        "prior_run_state_hash": prior_hash,
        "decision": decision,
        "node_decisions": [node_decision],
        "invalidation_records": [asdict(item) for item in _sort_invalidations(invalidations)],
        "skipped_nodes": skipped_nodes,
        "replayed_nodes": sorted(replayed_nodes),
        "blocked_nodes": blocked_nodes,
        "next_allowed_actions": _next_actions(decision),
    }


def _next_actions(decision: str) -> List[str]:
    if decision == "SKIP":
        return ["CONTINUE_WITH_NEXT_NODE"]
    if decision == "REPLAY":
        return ["REPLAY_DECLARED_NODE_OUTPUTS"]
    if decision == "BLOCK_HUMAN_GATE":
        return ["REQUEST_HUMAN_REVIEW"]
    if decision == "BLOCK_LOCK_BOUNDARY":
        return ["REQUEST_EXPLICIT_LOCK_AUTHORIZATION"]
    return ["REPAIR_EVIDENCE_AND_RETRY"]


def _node_map(value: Any) -> Dict[str, Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items() if isinstance(item, Mapping)}
    if isinstance(value, list):
        return {str(item.get("node_id")): item for item in value if isinstance(item, Mapping) and item.get("node_id")}
    return {}


def _normalize_hash_map(value: Any) -> Dict[str, str]:
    if isinstance(value, Mapping):
        return {str(key): str(item) for key, item in value.items()}
    if isinstance(value, list):
        result = {}
        for item in value:
            if isinstance(item, Mapping):
                key = item.get("path") or item.get("ref") or item.get("id")
                digest = item.get("sha256") or item.get("hash")
                if key and digest:
                    result[str(key)] = str(digest)
        return result
    return {}


def _compare_hash_map(
    run_state: Mapping[str, Any],
    current_evidence: Mapping[str, Any],
    field: str,
    changed_reason: str,
    missing_reason: str,
    node_id: str,
) -> List[InvalidationRecord]:
    prior = _normalize_hash_map(run_state.get(field, {}))
    current = _normalize_hash_map(current_evidence.get(field, prior))
    records = []
    for path, prior_hash in prior.items():
        current_hash = current.get(path)
        if current_hash is None or current_hash == "MISSING":
            records.append(_record(missing_reason, node_id, path, prior_hash, "MISSING"))
        elif current_hash != prior_hash:
            records.append(_record(changed_reason, node_id, path, prior_hash, current_hash))
    return records


def _compare_scalar(
    run_state: Mapping[str, Any],
    current_evidence: Mapping[str, Any],
    field: str,
    reason_code: str,
    node_id: str,
) -> List[InvalidationRecord]:
    if field not in current_evidence:
        return []
    prior = str(run_state.get(field, ""))
    current = str(current_evidence.get(field, ""))
    if prior != current:
        return [_record(reason_code, node_id, field, prior, current)]
    return []


def _write_scope_invalidations(
    run_state: Mapping[str, Any],
    current_evidence: Mapping[str, Any],
    node_id: str,
) -> List[InvalidationRecord]:
    declared = set(str(path) for path in run_state.get("written_paths", []))
    current = set(str(path) for path in current_evidence.get("written_paths", declared))
    extra = sorted(current - declared)
    return [_record("WRITE_SCOPE_CHANGED", node_id, path, "UNDECLARED", "DECLARED_FOR_REPLAY") for path in extra]


def _failure_record_invalidations(run_state: Mapping[str, Any], node_id: str) -> List[InvalidationRecord]:
    node = _node_map(run_state.get("node_states", {})).get(node_id, {})
    if node.get("state") != "NODE_FAILED":
        return []
    failure_records = run_state.get("failure_records", {})
    record = failure_records.get(node_id) if isinstance(failure_records, Mapping) else None
    if not isinstance(record, Mapping):
        return [_record("FAILURE_RECORD_INCOMPLETE", node_id, "failure_records", "REQUIRED", "MISSING")]
    missing = [field for field in ("failure_type", "failed_command", "exit_code") if field not in record]
    return [_record("FAILURE_RECORD_INCOMPLETE", node_id, f"failure_records.{field}", "REQUIRED", "MISSING") for field in missing]


def _gate_decision(run_state: Mapping[str, Any], node_id: str) -> Optional[str]:
    gates = run_state.get("gate_states", {})
    gate = gates.get(node_id) if isinstance(gates, Mapping) else None
    if not isinstance(gate, Mapping):
        return None
    if gate.get("lock_requested") or gate.get("gate_type") == "LOCK_GATE":
        return "BLOCK_LOCK_BOUNDARY"
    if gate.get("human_gate_required") or gate.get("gate_type") == "HUMAN_REVIEW_GATE":
        return "BLOCK_HUMAN_GATE"
    return None


def _record(reason_code: str, node_id: str, path: str, prior: str, current: str) -> InvalidationRecord:
    human_gate = reason_code in HUMAN_GATE_REASONS or reason_code in {"WRITE_SCOPE_CHANGED", "REQUESTED_NODE_NOT_IN_DAG", "FAILURE_RECORD_INCOMPLETE"}
    stop_rule = "BLOCK_HUMAN_GATE" if reason_code in HUMAN_GATE_REASONS else "BLOCK_INVALIDATION"
    if reason_code in {"REQUESTED_NODE_NOT_IN_DAG", "FAILURE_RECORD_INCOMPLETE"}:
        stop_rule = "BLOCK_UNSAFE_STATE"
    if reason_code == "WRITE_SCOPE_CHANGED":
        stop_rule = "BLOCK_INVALIDATION"
    return InvalidationRecord(
        reason_code=reason_code,
        affected_node_id=node_id,
        affected_path=path,
        prior_value=prior,
        current_value=current,
        required_stop_rule=stop_rule,
        human_gate_required=human_gate,
    )


def _sort_invalidations(records: Iterable[InvalidationRecord]) -> List[InvalidationRecord]:
    return sorted(records, key=lambda item: (item.reason_code, item.affected_node_id, item.affected_path))
