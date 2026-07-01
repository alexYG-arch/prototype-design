"""P4 integration program driver primitives.

The driver coordinates locked harness capabilities. It records deterministic
plans and gate stops, but does not create review decisions, locks, packages, or
product semantics.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Union

from drd_harness.kernel.hashline import sha256_file, sha256_text
from drd_harness.orchestrator.recovery import current_hashes_for_paths, load_run_state, resolve_resume_decision


START_PACKAGE_ROOT = Path(__file__).resolve().parents[4]
P3_BUILD_LOCK_PATH = Path() / "control" / "locks" / "P3_BUILD_LOCK.json"
P3_BUILD_LOCK_SHA256 = "52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e"
P3_BUILD_LOCK_ROOT_SHA256 = "0ef47227a39e3eb75923e7506523b734769485431c2a7c3a1e1265f9d937fa8f"
DRIVER_VERSION = "p4-impl-01"
LOCK_GATE_STATUSES = {"LOCK_GATE", "HUMAN_REVIEW_GATE", "RELEASE_REQUEST"}


@dataclass(frozen=True)
class DriverFinding:
    code: str
    subject_id: str
    message: str


@dataclass(frozen=True)
class ProgramNode:
    node_id: str
    node_type: str
    label: str
    reads: List[str]
    writes: List[str]
    gate: bool = False


@dataclass(frozen=True)
class ProgramEdge:
    edge_id: str
    edge_type: str
    source_node_id: str
    target_node_id: str


def build_status_payload(
    *,
    command: str,
    status: str,
    run_id: str,
    written_paths: Iterable[str] = (),
    findings: Iterable[Union[Mapping[str, Any], DriverFinding]] = (),
    exit_code: int = 0,
    **extra: Any,
) -> dict:
    payload = {
        "command": command,
        "status": status,
        "run_id": run_id,
        "written_paths": sorted(str(path) for path in written_paths),
        "findings": _finding_dicts(findings),
        "exit_code": exit_code,
    }
    payload.update(extra)
    return payload


def bind_upstream_p3_build_lock(lock_path: Optional[Path] = None) -> List[DriverFinding]:
    lock_path = lock_path or START_PACKAGE_ROOT / P3_BUILD_LOCK_PATH
    subject_id = _display_path(lock_path)
    if not lock_path.is_file():
        return [DriverFinding("P4INT-GATE-001", subject_id, "required P3 build lock is missing")]

    lock_hash = sha256_file(lock_path)
    findings: List[DriverFinding] = []
    if lock_hash != P3_BUILD_LOCK_SHA256:
        findings.append(DriverFinding("P4INT-GATE-001", subject_id, "P3 build lock sha256 drift"))

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [DriverFinding("P4INT-GATE-001", subject_id, f"P3 build lock is invalid JSON: {exc}")]

    if lock.get("root_sha256") != P3_BUILD_LOCK_ROOT_SHA256:
        findings.append(DriverFinding("P4INT-GATE-001", subject_id, "P3 build lock root_sha256 drift"))
    if lock.get("phase") != "P3":
        findings.append(DriverFinding("P4INT-GATE-001", subject_id, "P3 build lock phase mismatch"))
    return findings


def build_program_dag(
    *,
    adapter_result_manifest: Mapping[str, Any],
    upstream_lock_refs: Iterable[str],
    target_phase: Optional[str] = None,
    target_workpack: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> dict:
    source_refs = _source_refs(adapter_result_manifest)
    read_refs = sorted(set(source_refs + list(upstream_lock_refs)))
    output_root = output_dir or ""
    stage_label = target_workpack or target_phase or "bounded-stage"

    nodes = [
        ProgramNode(
            node_id=_stable_id("node", ["INPUT_ADAPTER", adapter_result_manifest.get("adapter_id", "")] + read_refs),
            node_type="INPUT_ADAPTER",
            label=str(adapter_result_manifest.get("adapter_id", "input_adapter")),
            reads=read_refs,
            writes=_planned_path(output_root, "adapter_result_manifest.json"),
        ),
        ProgramNode(
            node_id=_stable_id("node", ["SOURCE_INTAKE"] + source_refs),
            node_type="SOURCE_INTAKE",
            label="source_intake",
            reads=source_refs,
            writes=_planned_path(output_root, "source_intake_plan.json"),
        ),
        ProgramNode(
            node_id=_stable_id("node", ["STAGE_EXECUTION", stage_label] + source_refs),
            node_type="STAGE_EXECUTION",
            label=stage_label,
            reads=source_refs,
            writes=_planned_path(output_root, "stage_execution_plan.json"),
        ),
        ProgramNode(
            node_id=_stable_id("node", ["CANDIDATE_VALIDATION", stage_label]),
            node_type="CANDIDATE_VALIDATION",
            label="candidate_validation",
            reads=_planned_path(output_root, "stage_execution_plan.json"),
            writes=_planned_path(output_root, "validation_report.json"),
        ),
        ProgramNode(
            node_id=_stable_id("node", ["HUMAN_REVIEW_GATE", stage_label]),
            node_type="HUMAN_REVIEW_GATE",
            label="human_review_gate",
            reads=_planned_path(output_root, "validation_report.json"),
            writes=[],
            gate=True,
        ),
        ProgramNode(
            node_id=_stable_id("node", ["LOCK_GATE", stage_label]),
            node_type="LOCK_GATE",
            label="lock_gate",
            reads=[],
            writes=[],
            gate=True,
        ),
    ]
    edges = [
        ProgramEdge(_stable_id("edge", ["SOURCE_TO_STAGE", nodes[0].node_id, nodes[1].node_id]), "SOURCE_TO_STAGE", nodes[0].node_id, nodes[1].node_id),
        ProgramEdge(_stable_id("edge", ["STAGE_TO_STAGE", nodes[1].node_id, nodes[2].node_id]), "STAGE_TO_STAGE", nodes[1].node_id, nodes[2].node_id),
        ProgramEdge(_stable_id("edge", ["STAGE_TO_STAGE", nodes[2].node_id, nodes[3].node_id]), "STAGE_TO_STAGE", nodes[2].node_id, nodes[3].node_id),
        ProgramEdge(_stable_id("edge", ["CANDIDATE_TO_REVIEW", nodes[3].node_id, nodes[4].node_id]), "CANDIDATE_TO_REVIEW", nodes[3].node_id, nodes[4].node_id),
        ProgramEdge(_stable_id("edge", ["REVIEW_TO_LOCK", nodes[4].node_id, nodes[5].node_id]), "REVIEW_TO_LOCK", nodes[4].node_id, nodes[5].node_id),
    ]
    node_dicts = [asdict(node) for node in nodes]
    edge_dicts = [asdict(edge) for edge in edges]
    return {
        "program_id": _stable_id("program", [target_phase or "", target_workpack or ""] + read_refs),
        "driver_version": DRIVER_VERSION,
        "dag_nodes": node_dicts,
        "dag_edges": edge_dicts,
        "execution_plan": [node["node_id"] for node in node_dicts],
        "review_gate_refs": [node["node_id"] for node in node_dicts if node["node_type"] == "HUMAN_REVIEW_GATE"],
        "lock_gate_refs": [node["node_id"] for node in node_dicts if node["node_type"] == "LOCK_GATE"],
        "findings": [asdict(finding) for finding in validate_acyclic(node_dicts, edge_dicts)],
    }


def plan_run(
    *,
    work_dir: Path,
    adapter_result_manifest: Mapping[str, Any],
    output_dir: Path,
    target_phase: Optional[str] = None,
    target_workpack: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    run_id = _stable_id("run", [str(work_dir.resolve()), str(output_dir), target_phase or "", target_workpack or ""])
    findings: List[DriverFinding] = []
    findings.extend(bind_upstream_p3_build_lock())
    findings.extend(validate_output_scope(work_dir, output_dir))
    findings.extend(validate_adapter_semantic_boundary(adapter_result_manifest))

    dag = build_program_dag(
        adapter_result_manifest=adapter_result_manifest,
        upstream_lock_refs=[str(P3_BUILD_LOCK_PATH)],
        target_phase=target_phase,
        target_workpack=target_workpack,
        output_dir=str(output_dir),
    )
    findings.extend(DriverFinding(**item) for item in dag["findings"])
    planned_paths = sorted(
        path
        for node in dag["dag_nodes"]
        for path in node["writes"]
    )
    status = "STOPPED" if findings else "DRY_RUN" if dry_run else "PLANNED"
    return build_status_payload(
        command="run",
        status=status,
        run_id=run_id,
        written_paths=[] if dry_run or findings else planned_paths,
        findings=findings,
        exit_code=1 if findings else 0,
        adapter_result_manifest=adapter_result_manifest,
        program_dag_snapshot=dag,
        stage_execution_plan=dag["execution_plan"],
        planned_written_paths=planned_paths,
        evidence_paths=planned_paths,
        dry_run=dry_run,
        **_run_state_fields(
            adapter_result_manifest=adapter_result_manifest,
            dag=dag,
            dry_run=dry_run,
        ),
    )


def plan_resume(run_state_ref: str, requested_resume_node: str, *, dry_run: bool = False) -> dict:
    run_state_path = Path(run_state_ref)
    if run_state_path.is_file():
        run_state = load_run_state(run_state_path)
        current_evidence = {
            "written_paths": run_state.get("written_paths", []),
            "output_hashes": current_hashes_for_paths(run_state.get("written_paths", [])),
        }
        report = resolve_resume_decision(run_state, requested_resume_node, current_evidence=current_evidence)
        decision = report["decision"]
        return build_status_payload(
            command="resume",
            status="STOPPED" if decision.startswith("BLOCK_") else decision,
            run_id=str(report.get("run_id", "")),
            findings=[],
            exit_code=1 if decision.startswith("BLOCK_") else 0,
            resume_eligibility=decision,
            invalidation_state="DRIFT" if report["invalidation_records"] else "CLEAR",
            skipped_nodes=report["skipped_nodes"],
            replayed_nodes=report["replayed_nodes"],
            blocked_nodes=report["blocked_nodes"],
            next_command_plan=report["next_allowed_actions"],
            resume_decision_report=report,
            dry_run=dry_run,
        )
    finding = DriverFinding(
        "P4INT-GATE-RESUME",
        requested_resume_node,
        "resume policy is reserved for P4-IMPL-02 recovery implementation",
    )
    return build_status_payload(
        command="resume",
        status="STOPPED",
        run_id=_stable_id("resume", [run_state_ref, requested_resume_node]),
        findings=[finding],
        exit_code=1,
        resume_eligibility="BLOCKED_PENDING_RECOVERY_POLICY",
        invalidation_state="UNKNOWN_UNTIL_P4_IMPL_02",
        skipped_nodes=[],
        replayed_nodes=[],
        next_command_plan=[],
        dry_run=dry_run,
    )


def output_hashes_for_written_paths(payload: Mapping[str, Any]) -> dict:
    return {
        str(path): sha256_file(Path(path))
        for path in sorted(str(path) for path in payload.get("written_paths", []))
    }


def plan_generate_drd(*, work_dir: Path, source_ref: Path, output_dir: Path, dry_run: bool = False) -> dict:
    from drd_harness.compiler.external_prd import generate_external_prd_drd

    return generate_external_prd_drd(
        work_dir=work_dir,
        source_ref=source_ref,
        output_dir=output_dir,
        dry_run=dry_run,
    )


def plan_release_request(build_lock_refs: Iterable[str], release_scope_ref: str, evidence_bundle_ref: str) -> dict:
    finding = DriverFinding(
        "P4INT-GATE-RELEASE",
        release_scope_ref,
        "release readiness is declaration-only until later P4 release workpacks",
    )
    return build_status_payload(
        command="release",
        status="STOPPED",
        run_id=_stable_id("release", list(build_lock_refs) + [release_scope_ref, evidence_bundle_ref]),
        findings=[finding],
        exit_code=1,
        release_readiness_packet=None,
        missing_gate_list=["P4_RELEASE_READINESS_IMPLEMENTATION", "DRD_HARNESS_RELEASE_LOCK_AUTHORIZATION"],
        release_lock_eligibility_state="NOT_ELIGIBLE",
        will_create_release_lock=False,
        will_publish_package=False,
    )


def validate_acyclic(nodes: Iterable[Mapping[str, Any]], edges: Iterable[Mapping[str, Any]]) -> List[DriverFinding]:
    node_ids = {str(node["node_id"]) for node in nodes}
    incoming = {node_id: 0 for node_id in node_ids}
    outgoing = {node_id: [] for node_id in node_ids}
    findings: List[DriverFinding] = []
    for edge in edges:
        source = str(edge["source_node_id"])
        target = str(edge["target_node_id"])
        if source not in node_ids or target not in node_ids:
            findings.append(DriverFinding("P4INT-DAG-001", str(edge.get("edge_id", "edge")), "edge references unknown node"))
            continue
        outgoing[source].append(target)
        incoming[target] += 1

    ready = sorted(node_id for node_id, count in incoming.items() if count == 0)
    visited = []
    while ready:
        node_id = ready.pop(0)
        visited.append(node_id)
        for target in sorted(outgoing[node_id]):
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
                ready.sort()
    if len(visited) != len(node_ids):
        findings.append(DriverFinding("P4INT-DAG-002", "program_dag", "program DAG contains a cycle"))
    return findings


def validate_output_scope(work_dir: Path, output_dir: Path) -> List[DriverFinding]:
    try:
        output_dir.resolve().relative_to(work_dir.resolve())
    except ValueError:
        return [
            DriverFinding(
                "P4INT-GATE-OUTPUT-SCOPE",
                str(output_dir),
                "output_dir must stay inside the declared work_dir",
            )
        ]
    return []


def validate_adapter_semantic_boundary(adapter_result_manifest: Mapping[str, Any]) -> List[DriverFinding]:
    forbidden = {"product_requirements", "page_elements", "layout_rules", "business_contracts", "deduced_product_requirements"}
    present = sorted(key for key in forbidden if key in adapter_result_manifest)
    if present:
        return [
            DriverFinding(
                "P4INT-GATE-SEMANTIC-BOUNDARY",
                str(adapter_result_manifest.get("adapter_id", "adapter")),
                "adapter result contains forbidden semantic keys: " + ", ".join(present),
            )
        ]
    return []


def _source_refs(adapter_result_manifest: Mapping[str, Any]) -> List[str]:
    records = adapter_result_manifest.get("source_ref_records") or adapter_result_manifest.get("source_section_records") or []
    refs = []
    for record in records:
        if isinstance(record, Mapping):
            refs.append(str(record.get("source_ref") or record.get("source_path") or record.get("section_id") or record))
        else:
            refs.append(str(record))
    return sorted(refs)


def _run_state_fields(*, adapter_result_manifest: Mapping[str, Any], dag: Mapping[str, Any], dry_run: bool) -> dict:
    return {
        "program_id": dag.get("program_id", ""),
        "driver_version": dag.get("driver_version", DRIVER_VERSION),
        "original_command": "run",
        "adapter_id": str(adapter_result_manifest.get("adapter_id", "")),
        "source_refs": _source_refs(adapter_result_manifest),
        "input_hashes": _source_hashes(adapter_result_manifest),
        "upstream_lock_refs": {str(P3_BUILD_LOCK_PATH): P3_BUILD_LOCK_SHA256},
        "candidate_subject_hashes": {},
        "review_decision_hashes": {},
        "dag_snapshot_hash": _canonical_hash(dag),
        "execution_plan_hash": _canonical_hash(dag.get("execution_plan", [])),
        "node_states": _node_states(dag, dry_run=dry_run),
        "output_hashes": {},
        "gate_states": _gate_states(dag),
        "failure_records": {},
        "recovery_history": [],
    }


def _source_hashes(adapter_result_manifest: Mapping[str, Any]) -> dict:
    hashes = {}
    for record in adapter_result_manifest.get("source_section_records", []):
        if not isinstance(record, Mapping):
            continue
        key = record.get("section_id") or record.get("source_ref") or record.get("source_path")
        digest = record.get("content_sha256") or record.get("source_sha256")
        if key and digest:
            hashes[str(key)] = str(digest)
    for record in adapter_result_manifest.get("source_ref_records", []):
        if not isinstance(record, Mapping):
            continue
        key = record.get("source_ref") or record.get("section_id") or record.get("source_path")
        digest = record.get("content_sha256") or record.get("source_sha256")
        if key and digest and str(key) not in hashes:
            hashes[str(key)] = str(digest)
    handoff = adapter_result_manifest.get("handoff_manifest", {})
    if isinstance(handoff, Mapping) and handoff.get("source_path") and handoff.get("source_sha256"):
        hashes[str(handoff["source_path"])] = str(handoff["source_sha256"])
    return dict(sorted(hashes.items()))


def _node_states(dag: Mapping[str, Any], *, dry_run: bool) -> dict:
    states = {}
    for node in dag.get("dag_nodes", []):
        if not isinstance(node, Mapping) or not node.get("node_id"):
            continue
        node_type = str(node.get("node_type", ""))
        if dry_run:
            state = "NODE_PLANNED"
        elif node_type == "HUMAN_REVIEW_GATE":
            state = "NODE_BLOCKED_HUMAN_REVIEW"
        elif node_type == "LOCK_GATE":
            state = "NODE_BLOCKED_LOCK_BOUNDARY"
        else:
            state = "NODE_COMPLETED"
        states[str(node["node_id"])] = {
            "state": state,
            "node_type": node_type,
            "label": str(node.get("label", "")),
        }
    return states


def _gate_states(dag: Mapping[str, Any]) -> dict:
    states = {}
    for node in dag.get("dag_nodes", []):
        if not isinstance(node, Mapping) or not node.get("node_id") or not node.get("gate"):
            continue
        node_type = str(node.get("node_type", ""))
        states[str(node["node_id"])] = {
            "gate_type": node_type,
            "human_gate_required": node_type == "HUMAN_REVIEW_GATE",
            "lock_requested": node_type == "LOCK_GATE",
        }
    return states


def _canonical_hash(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _planned_path(output_root: str, name: str) -> List[str]:
    if not output_root:
        return [name]
    return [(Path(output_root) / name).as_posix()]


def _stable_id(prefix: str, parts: Iterable[str]) -> str:
    normalized = json.dumps([str(part) for part in parts], sort_keys=True, separators=(",", ":"))
    return f"{prefix}-{sha256_text(normalized)[:16]}"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(START_PACKAGE_ROOT).as_posix()
    except ValueError:
        return str(path)


def _finding_dicts(findings: Iterable[Union[Mapping[str, Any], DriverFinding]]) -> List[dict]:
    result = []
    for finding in findings:
        if isinstance(finding, DriverFinding):
            result.append(asdict(finding))
        else:
            result.append(dict(finding))
    return sorted(result, key=lambda item: (item.get("code", ""), item.get("subject_id", ""), item.get("message", "")))
