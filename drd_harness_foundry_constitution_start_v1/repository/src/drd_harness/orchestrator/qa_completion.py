"""DRD-06 read-only QA validation and staged-run completion."""

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_file
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.stages.contracts import canonical_outputs_for_stage
from drd_harness.validators.compiler_conservation import validate_read_only_qa_boundary


def run_qa_completion(
    *,
    work_dir: Path,
    run_state_ref: Path,
    stage_id: str = "DRD-06",
    dry_run: bool = False,
) -> dict:
    output_dir = run_state_ref.parent
    findings = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if stage_id != "DRD-06":
        findings.append(DriverFinding("QA-COMPLETE-INPUT-001", stage_id, "qa-complete-stage only supports DRD-06"))
    if not run_state_ref.is_file():
        findings.append(DriverFinding("QA-COMPLETE-INPUT-002", run_state_ref.as_posix(), "run_state_ref must exist"))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    try:
        run_state = _read_json(run_state_ref)
        stage_plan = _read_json(output_dir / "stage_execution_plan.json")
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(DriverFinding("QA-COMPLETE-INPUT-002", run_state_ref.as_posix(), str(exc)))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    expected_outputs = canonical_outputs_for_stage("DRD-06")
    planned_paths = _planned_paths(output_dir)
    missing = [rel_path for rel_path in expected_outputs if not (output_dir / rel_path).is_file()]
    for rel_path in missing:
        findings.append(DriverFinding("QA-COMPLETE-OUTPUT-001", rel_path, "DRD-06 read-only QA output is missing"))
    if not missing:
        findings.extend(_qa_status_findings(output_dir))
    if run_state.get("node_states", {}).get("DRD-06", {}).get("state") != "NODE_CODEX_READ_ONLY_QA_READY":
        findings.append(DriverFinding("QA-COMPLETE-STATE-001", "DRD-06", "DRD-06 must be CODEX_READ_ONLY_QA_READY before completion"))

    mutated = _mutated_drd05_artifacts(output_dir, run_state)
    boundary_record = {
        "drd06_run_id": run_state.get("run_id", ""),
        "written_paths": [Path(path).name for path in expected_outputs],
        "mutated_artifacts": mutated,
    }
    findings.extend(DriverFinding(finding.code, finding.subject_id, finding.message) for finding in validate_read_only_qa_boundary(boundary_record))

    if findings:
        return _stopped(
            stage_id,
            output_dir,
            findings,
            run_id=str(run_state.get("run_id", "")),
            planned_written_paths=planned_paths,
            dry_run=dry_run,
        )
    if dry_run:
        return build_status_payload(
            command="qa-complete-stage",
            status="QA_COMPLETE_DRY_RUN",
            run_id=str(run_state.get("run_id", "")),
            written_paths=[],
            findings=[],
            exit_code=0,
            stage_id=stage_id,
            planned_written_paths=planned_paths,
            expected_outputs=expected_outputs,
            staged_execution_complete=False,
            dry_run=True,
        )

    qa_hashes = {rel_path: sha256_file(output_dir / rel_path) for rel_path in expected_outputs}
    _mark_stage_complete(stage_plan, qa_hashes)
    _write_json(output_dir / "stage_execution_plan.json", stage_plan)
    written_paths = [(output_dir / "stage_execution_plan.json").as_posix()]
    output_hashes = {path: sha256_file(Path(path)) for path in written_paths}
    _update_run_state(
        run_state=run_state,
        run_state_ref=run_state_ref,
        qa_hashes=qa_hashes,
        written_paths=written_paths,
        output_hashes=output_hashes,
        execution_plan_hash=sha256_file(output_dir / "stage_execution_plan.json"),
    )
    written_paths.append(run_state_ref.as_posix())
    final_written = sorted(set(written_paths))
    return build_status_payload(
        command="qa-complete-stage",
        status="STAGED_EXECUTION_COMPLETE",
        run_id=str(run_state.get("run_id", "")),
        written_paths=final_written,
        findings=[],
        exit_code=0,
        stage_id=stage_id,
        qa_output_hashes=qa_hashes,
        final_drd_path=(output_dir / "DRD-05" / "FINAL_DRD.md").as_posix(),
        final_drd_hash=sha256_file(output_dir / "DRD-05" / "FINAL_DRD.md"),
        staged_execution_complete=True,
        creates_control_lock=False,
        creates_release_lock=False,
        publishes_package=False,
        dry_run=False,
        output_hashes={path: sha256_file(Path(path)) for path in final_written if Path(path).is_file()},
    )


def _mutated_drd05_artifacts(output_dir: Path, run_state: Mapping[str, Any]) -> list[str]:
    expected_hashes = run_state.get("output_hashes", {})
    mutated = []
    for rel_path in canonical_outputs_for_stage("DRD-05"):
        path = output_dir / rel_path
        recorded_hash = expected_hashes.get(path.as_posix())
        if not path.is_file():
            mutated.append(path.as_posix())
        elif recorded_hash and sha256_file(path) != recorded_hash:
            mutated.append(path.as_posix())
    return sorted(mutated)


def _qa_status_findings(output_dir: Path) -> list[DriverFinding]:
    index_path = output_dir / "DRD-06" / "qa_finding_index.json"
    try:
        index = _read_json(index_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [DriverFinding("QA-COMPLETE-QA-001", index_path.as_posix(), str(exc))]
    status = index.get("status") or index.get("qa_status") or index.get("summary", {}).get("status")
    pass_statuses = {"PASS", "PASSED", "QA_PASS", "NO_BLOCKERS"}
    if status not in pass_statuses:
        return [
            DriverFinding(
                "QA-COMPLETE-QA-001",
                index_path.as_posix(),
                f"DRD-06 QA status must pass before staged completion; got {status!r}",
            )
        ]
    return []


def _mark_stage_complete(stage_plan: Mapping[str, Any], qa_hashes: Mapping[str, str]) -> None:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, dict) and row.get("stage_id") == "DRD-06":
            row["status"] = "READ_ONLY_QA_PASSED"
            row["qa_output_hashes"] = dict(sorted(qa_hashes.items()))
    completed = {
        str(row.get("stage_id"))
        for row in stage_plan.get("stage_chain", [])
        if isinstance(row, Mapping)
        and row.get("stage_id")
        and row.get("status")
        in {
            "COMPLETE",
            "PROMOTED_APPROVED_SEMANTIC_ARTIFACT",
            "COMPILED_FINAL_DRD",
            "READ_ONLY_QA_PASSED",
        }
    }
    stage_plan["completed_stage_ids"] = sorted(completed, key=_stage_sort_key)
    stage_plan["blocked_stage_id"] = None
    stage_plan["blocked_gate_id"] = None
    stage_plan["next_required_runtime"] = None
    stage_plan["staged_execution_complete"] = True


def _stage_sort_key(stage_id: str) -> int:
    order = {
        "DRD-00": 0,
        "DRD-01": 10,
        "DRD-02": 20,
        "DRD-03": 30,
        "DRD-03B": 35,
        "DRD-04": 40,
        "DRD-05": 50,
        "DRD-06": 60,
    }
    return order.get(stage_id, 999)


def _update_run_state(
    *,
    run_state: dict,
    run_state_ref: Path,
    qa_hashes: Mapping[str, str],
    written_paths: Sequence[str],
    output_hashes: Mapping[str, str],
    execution_plan_hash: str,
) -> None:
    existing_written = set(str(path) for path in run_state.get("written_paths", []))
    existing_written.update(written_paths)
    run_state["written_paths"] = sorted(existing_written)
    existing_hashes = dict(run_state.get("output_hashes", {}))
    existing_hashes.update(output_hashes)
    existing_hashes.pop(run_state_ref.as_posix(), None)
    run_state["output_hashes"] = dict(sorted(existing_hashes.items()))
    run_state["execution_plan_hash"] = execution_plan_hash
    node_states = dict(run_state.get("node_states", {}))
    node_states["DRD-06"] = {
        "state": "NODE_COMPLETED",
        "qa_output_hashes": dict(sorted(qa_hashes.items())),
    }
    run_state["node_states"] = node_states
    gate_states = dict(run_state.get("gate_states", {}))
    gate_states["DRD-06"] = {
        "gate_type": "READ_ONLY_QA_VALIDATION_GATE",
        "gate_id": "DRD-06_READ_ONLY_QA_VALIDATION_GATE",
        "human_gate_required": False,
        "validation_status": "PASS",
    }
    run_state["gate_states"] = gate_states
    history = list(run_state.get("recovery_history", []))
    history.append({"command": "qa-complete-stage", "stage_id": "DRD-06", "status": "STAGED_EXECUTION_COMPLETE"})
    run_state["recovery_history"] = history
    run_state["staged_execution_complete"] = True
    _write_json(run_state_ref, run_state)


def _planned_paths(output_dir: Path) -> list[str]:
    return sorted(
        [
            (output_dir / "stage_execution_plan.json").as_posix(),
            (output_dir / "run_state.json").as_posix(),
        ]
    )


def _stopped(
    stage_id: str,
    output_dir: Path,
    findings: Iterable[DriverFinding],
    *,
    run_id: str = "",
    planned_written_paths: Sequence[str] = (),
    dry_run: bool,
) -> dict:
    return build_status_payload(
        command="qa-complete-stage",
        status="STOPPED",
        run_id=run_id,
        written_paths=[],
        findings=findings,
        exit_code=1,
        stage_id=stage_id,
        output_dir=output_dir.as_posix(),
        planned_written_paths=list(planned_written_paths),
        staged_execution_complete=False,
        dry_run=dry_run,
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
