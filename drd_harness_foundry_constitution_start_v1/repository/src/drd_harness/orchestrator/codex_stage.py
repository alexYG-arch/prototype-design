"""Codex-owned stage continuation for external PRD staged runs."""

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from drd_harness.kernel.hashline import sha256_file, sha256_text
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.runtimes.codex_cli import run_codex_runtime
from drd_harness.stages.contracts import (
    REQUIRED_UPSTREAM,
    SEMANTIC_SOURCE_STAGES,
    StageId,
    canonical_outputs_for_stage,
    candidate_outputs_for_stage,
    promotion_outputs_for_stage,
)


CODEX_STAGE_RUNTIMES = {"CODEX", "CODEX_PYTHON_LOOP", "CODEX_READ_ONLY"}


def run_codex_stage(
    *,
    work_dir: Path,
    run_state_ref: Path,
    stage_id: str,
    runtime_command: Optional[str] = None,
    codex_bin: Optional[str] = None,
    model: Optional[str] = None,
    timeout_seconds: int = 1800,
    dry_run: bool = False,
) -> dict:
    output_dir = run_state_ref.parent
    findings = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if not run_state_ref.is_file():
        findings.append(DriverFinding("CODEX-STAGE-INPUT-001", run_state_ref.as_posix(), "run_state_ref must exist"))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    try:
        run_state = _read_json(run_state_ref)
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(DriverFinding("CODEX-STAGE-INPUT-001", run_state_ref.as_posix(), str(exc)))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    plan_path = output_dir / "stage_execution_plan.json"
    try:
        stage_plan = _read_json(plan_path)
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(DriverFinding("CODEX-STAGE-INPUT-002", plan_path.as_posix(), str(exc)))
        return _stopped(stage_id, output_dir, findings, run_id=str(run_state.get("run_id", "")), dry_run=dry_run)

    stage_row = _stage_row(stage_plan, stage_id)
    if not stage_row:
        findings.append(DriverFinding("CODEX-STAGE-INPUT-003", stage_id, "stage_id is not present in stage_execution_plan"))
    elif stage_row.get("primary_runtime") not in CODEX_STAGE_RUNTIMES:
        findings.append(
            DriverFinding(
                "CODEX-STAGE-RUNTIME-001",
                stage_id,
                "stage primary_runtime must be CODEX, CODEX_PYTHON_LOOP, or CODEX_READ_ONLY",
            )
        )
    else:
        findings.extend(_upstream_findings(output_dir, stage_id))

    expected_outputs = _expected_outputs(stage_id, stage_row or {})
    planned_paths = _planned_paths(output_dir, stage_id, expected_outputs, include_prompt=not _existing_prompt(output_dir, stage_id).is_file())
    if findings:
        return _stopped(
            stage_id,
            output_dir,
            findings,
            run_id=str(run_state.get("run_id", "")),
            planned_written_paths=planned_paths,
            dry_run=dry_run,
        )

    prompt_path = _prompt_path(output_dir, stage_id)
    prompt_text = _prompt_text(
        output_dir=output_dir,
        run_state_ref=run_state_ref,
        plan_path=plan_path,
        stage_id=stage_id,
        stage_row=stage_row,
        expected_outputs=expected_outputs,
    )

    if dry_run:
        return build_status_payload(
            command="codex-stage",
            status="CODEX_STAGE_DRY_RUN",
            run_id=str(run_state.get("run_id", "")),
            written_paths=[],
            findings=[],
            exit_code=0,
            stage_id=stage_id,
            primary_runtime=stage_row.get("primary_runtime"),
            expected_outputs=expected_outputs,
            planned_written_paths=planned_paths,
            staged_execution_complete=False,
            dry_run=True,
        )

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    if not prompt_path.is_file():
        prompt_path.write_text(prompt_text, encoding="utf-8")
    else:
        prompt_text = prompt_path.read_text(encoding="utf-8")

    invocation_path = output_dir / "runtime_invocations" / f"{stage_id}_codex_runtime_invocation.json"
    result_path = output_dir / "runtime_results" / f"{stage_id}_codex_runtime_result.json"
    last_message_path = output_dir / "runtime_results" / f"{stage_id}_codex_last_message.md"
    invocation = _invocation_record(
        run_state=run_state,
        run_state_ref=run_state_ref,
        stage_id=stage_id,
        stage_row=stage_row,
        prompt_path=prompt_path,
        expected_outputs=expected_outputs,
        runtime_command=runtime_command,
        codex_bin=codex_bin,
        model=model,
    )
    _write_json(invocation_path, invocation)

    runtime_result = run_codex_runtime(
        prompt_text=prompt_text,
        work_dir=work_dir,
        prompt_file=prompt_path,
        output_dir=output_dir,
        stage_id=stage_id,
        expected_outputs=expected_outputs,
        run_state_ref=run_state_ref,
        runtime_command=runtime_command,
        codex_bin=codex_bin,
        model=model,
        timeout_seconds=timeout_seconds,
        output_last_message=last_message_path,
    )
    missing_outputs = _missing_outputs(output_dir, expected_outputs)
    status = _status_from_runtime(stage_id, runtime_result.status, missing_outputs)
    expected_hashes = _output_hashes(output_dir, expected_outputs) if not missing_outputs else {}
    candidate_subject_hash = _candidate_subject_hash(expected_hashes) if expected_hashes else ""
    result_record = {
        "artifact": "codex_runtime_result",
        "stage_id": stage_id,
        "status": status,
        "runtime": runtime_result.to_dict(),
        "expected_outputs": list(expected_outputs),
        "missing_outputs": missing_outputs,
        "candidate_subject_hash": candidate_subject_hash,
        "expected_output_hashes": expected_hashes,
        "staged_execution_complete": False,
        "forbidden_actions": ["review", "approve", "promote", "compile_final_drd", "create_lock", "release", "publish_package"],
    }
    _write_json(result_path, result_record)

    written_paths = [invocation_path.as_posix(), result_path.as_posix()]
    if prompt_path.as_posix() not in written_paths:
        written_paths.append(prompt_path.as_posix())
    if last_message_path.is_file():
        written_paths.append(last_message_path.as_posix())

    ready_statuses = {"CODEX_STAGE_CANDIDATE_READY", "CODEX_READ_ONLY_QA_READY"}
    exit_code = 0 if status in ready_statuses else 1
    if status in ready_statuses:
        if stage_id == "DRD-06":
            _mark_stage_read_only_qa_ready(stage_plan, stage_id, candidate_subject_hash)
        else:
            _mark_stage_candidate_ready(stage_plan, stage_id, candidate_subject_hash)
        _write_json(plan_path, stage_plan)
        written_paths.append(plan_path.as_posix())
        written_paths.extend((output_dir / rel_path).as_posix() for rel_path in expected_outputs)
        output_hashes = {path: sha256_file(Path(path)) for path in sorted(set(written_paths))}
        _update_run_state(
            run_state=run_state,
            run_state_ref=run_state_ref,
            stage_id=stage_id,
            candidate_subject_hash=candidate_subject_hash,
            written_paths=sorted(set(written_paths)),
            output_hashes=output_hashes,
            execution_plan_hash=sha256_file(plan_path),
        )
        written_paths.append(run_state_ref.as_posix())

    final_written = sorted(set(written_paths))
    payload_hashes = {path: sha256_file(Path(path)) for path in final_written if Path(path).is_file()}
    return build_status_payload(
        command="codex-stage",
        status=status,
        run_id=str(run_state.get("run_id", "")),
        written_paths=final_written,
        findings=_runtime_findings(stage_id, runtime_result.status, missing_outputs, runtime_result.unavailable_reason),
        exit_code=exit_code,
        stage_id=stage_id,
        primary_runtime=stage_row.get("primary_runtime"),
        expected_outputs=expected_outputs,
        candidate_subject_hash=candidate_subject_hash,
        output_hashes=dict(sorted(payload_hashes.items())),
        staged_execution_complete=False,
        dry_run=False,
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
        command="codex-stage",
        status="STOPPED",
        run_id=run_id,
        written_paths=[],
        findings=findings,
        exit_code=1,
        stage_id=stage_id,
        planned_written_paths=list(planned_written_paths),
        output_dir=output_dir.as_posix(),
        staged_execution_complete=False,
        dry_run=dry_run,
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stage_row(stage_plan: Mapping[str, Any], stage_id: str) -> Optional[Mapping[str, Any]]:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, Mapping) and row.get("stage_id") == stage_id:
            return row
    return None


def _expected_outputs(stage_id: str, stage_row: Mapping[str, Any]) -> list[str]:
    if isinstance(stage_row.get("candidate_outputs"), list):
        return [str(path) for path in stage_row["candidate_outputs"]]
    if stage_id == "DRD-06":
        return canonical_outputs_for_stage(stage_id)
    return candidate_outputs_for_stage(stage_id)


def _existing_prompt(output_dir: Path, stage_id: str) -> Path:
    if stage_id == "DRD-01":
        existing = output_dir / "codex_prompts" / "DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md"
        if existing.is_file():
            return existing
    return output_dir / "codex_prompts" / f"{stage_id}_CODEX_RUNTIME_PROMPT.md"


def _prompt_path(output_dir: Path, stage_id: str) -> Path:
    return _existing_prompt(output_dir, stage_id)


def _planned_paths(output_dir: Path, stage_id: str, expected_outputs: Sequence[str], *, include_prompt: bool) -> list[str]:
    paths = [
        output_dir / "runtime_invocations" / f"{stage_id}_codex_runtime_invocation.json",
        output_dir / "runtime_results" / f"{stage_id}_codex_runtime_result.json",
        output_dir / "stage_execution_plan.json",
        output_dir / "run_state.json",
    ]
    if include_prompt:
        paths.append(output_dir / "codex_prompts" / f"{stage_id}_CODEX_RUNTIME_PROMPT.md")
    paths.extend(output_dir / rel_path for rel_path in expected_outputs)
    return sorted(path.as_posix() for path in paths)


def _prompt_text(
    *,
    output_dir: Path,
    run_state_ref: Path,
    plan_path: Path,
    stage_id: str,
    stage_row: Mapping[str, Any],
    expected_outputs: Sequence[str],
) -> str:
    upstream_refs = _approved_upstream_refs(output_dir, stage_id)
    compiler_refs = _compiler_output_refs(output_dir) if stage_id == "DRD-06" else []
    lines = [
        f"# {stage_id} Codex Runtime Continuation",
        "",
        "You are the Codex runtime for this governed DRD Harness stage.",
        "",
        "Inputs:",
        f"- run_state: {run_state_ref.as_posix()}",
        f"- stage_execution_plan: {plan_path.as_posix()}",
        f"- source_snapshot: {(output_dir / 'DRD-00' / 'source_prd_snapshot.md').as_posix()}",
        f"- source_snapshot_manifest: {(output_dir / 'DRD-00' / 'source_snapshot_manifest.json').as_posix()}",
        *[f"- approved_upstream: {ref}" for ref in upstream_refs],
        *[f"- compiler_output: {ref}" for ref in compiler_refs],
        "",
        "Stage:",
        f"- stage_id: {stage_id}",
        f"- purpose: {stage_row.get('purpose')}",
        f"- primary_runtime: {stage_row.get('primary_runtime')}",
        "",
        "Required outputs:",
        *[f"- {rel_path}" for rel_path in expected_outputs],
        "",
        "Rules:",
        "- Re-read the immutable source snapshot; do not rely on summaries as authority.",
        "- Produce only the required candidate/read-only outputs for this stage.",
        "- Do not approve, promote, compile FINAL_DRD.md, create locks, release, or publish packages.",
        "- Do not add product capabilities absent from the PRD; route gaps or uncertain inferences to review.",
        "- Record audit-friendly premises, rules, conclusions, and source references; do not expose private chain-of-thought.",
        "- Write files under the configured output directory only.",
    ]
    if stage_id == "DRD-06":
        lines.extend(
            [
                "- DRD-06 is read-only QA: inspect DRD-05 outputs and write only DRD-06/READ_ONLY_QA_REPORT.md and DRD-06/qa_finding_index.json.",
                "- Do not edit DRD-05/FINAL_DRD.md, compiler sidecars, source snapshots, approved semantic artifacts, run_state, stage plan, locks, or release/package files.",
            ]
        )
    return "\n".join(lines) + "\n"


def _upstream_findings(output_dir: Path, stage_id: str) -> list[DriverFinding]:
    findings = []
    try:
        stage = StageId(stage_id)
    except ValueError:
        return [DriverFinding("CODEX-STAGE-INPUT-003", stage_id, "stage_id is not canonical")]
    for upstream in REQUIRED_UPSTREAM.get(stage, []):
        if upstream == StageId.DRD_00:
            required = [output_dir / "DRD-00" / "source_prd_snapshot.md", output_dir / "DRD-00" / "source_snapshot_manifest.json"]
        elif upstream in SEMANTIC_SOURCE_STAGES:
            required = [output_dir / rel_path for rel_path in promotion_outputs_for_stage(upstream)]
        elif upstream == StageId.DRD_05:
            required = [output_dir / "DRD-05" / "FINAL_DRD.md"]
        else:
            required = [output_dir / rel_path for rel_path in canonical_outputs_for_stage(upstream)]
        for path in required:
            if not path.is_file():
                findings.append(DriverFinding("CODEX-STAGE-UPSTREAM-001", path.as_posix(), "required upstream artifact is missing"))
    return findings


def _approved_upstream_refs(output_dir: Path, stage_id: str) -> list[str]:
    try:
        stage = StageId(stage_id)
    except ValueError:
        return []
    refs = []
    for upstream in REQUIRED_UPSTREAM.get(stage, []):
        if upstream in SEMANTIC_SOURCE_STAGES:
            refs.extend((output_dir / rel_path).as_posix() for rel_path in promotion_outputs_for_stage(upstream))
    return refs


def _invocation_record(
    *,
    run_state: Mapping[str, Any],
    run_state_ref: Path,
    stage_id: str,
    stage_row: Mapping[str, Any],
    prompt_path: Path,
    expected_outputs: Sequence[str],
    runtime_command: Optional[str],
    codex_bin: Optional[str],
    model: Optional[str],
) -> dict:
    return {
        "artifact": "codex_runtime_invocation",
        "run_id": run_state.get("run_id", ""),
        "stage_id": stage_id,
        "primary_runtime": stage_row.get("primary_runtime"),
        "run_state_ref": run_state_ref.as_posix(),
        "prompt_path": prompt_path.as_posix(),
        "prompt_sha256": sha256_file(prompt_path),
        "expected_outputs": list(expected_outputs),
        "runtime_command": runtime_command,
        "codex_bin": codex_bin,
        "model": model,
        "forbidden_actions": ["review", "approve", "promote", "compile_final_drd", "create_lock", "release", "publish_package"],
    }


def _missing_outputs(output_dir: Path, expected_outputs: Sequence[str]) -> list[str]:
    return sorted(rel_path for rel_path in expected_outputs if not (output_dir / rel_path).is_file())


def _output_hashes(output_dir: Path, expected_outputs: Sequence[str]) -> dict[str, str]:
    return {rel_path: sha256_file(output_dir / rel_path) for rel_path in sorted(expected_outputs)}


def _candidate_subject_hash(expected_hashes: Mapping[str, str]) -> str:
    return sha256_text(json.dumps(expected_hashes, sort_keys=True, separators=(",", ":")))


def _compiler_output_refs(output_dir: Path) -> list[str]:
    return [
        (output_dir / rel_path).as_posix()
        for rel_path in canonical_outputs_for_stage("DRD-05")
        if (output_dir / rel_path).is_file()
    ]


def _status_from_runtime(stage_id: str, runtime_status: str, missing_outputs: Sequence[str]) -> str:
    if runtime_status == "CODEX_RUNTIME_UNAVAILABLE":
        return "CODEX_RUNTIME_UNAVAILABLE"
    if runtime_status != "CODEX_RUNTIME_COMPLETED":
        return "CODEX_STAGE_FAILED"
    if missing_outputs:
        return "CODEX_STAGE_FAILED"
    if stage_id == "DRD-06":
        return "CODEX_READ_ONLY_QA_READY"
    return "CODEX_STAGE_CANDIDATE_READY"


def _runtime_findings(stage_id: str, runtime_status: str, missing_outputs: Sequence[str], unavailable_reason: str) -> list[DriverFinding]:
    findings = []
    if runtime_status == "CODEX_RUNTIME_UNAVAILABLE":
        findings.append(DriverFinding("CODEX-STAGE-RUNTIME-002", stage_id, unavailable_reason or "Codex runtime unavailable"))
    elif runtime_status != "CODEX_RUNTIME_COMPLETED":
        findings.append(DriverFinding("CODEX-STAGE-RUNTIME-003", stage_id, "Codex runtime returned a failure"))
    for rel_path in missing_outputs:
        findings.append(DriverFinding("CODEX-STAGE-OUTPUT-001", rel_path, "expected Codex stage output is missing"))
    return findings


def _mark_stage_candidate_ready(stage_plan: Mapping[str, Any], stage_id: str, candidate_subject_hash: str) -> None:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, dict) and row.get("stage_id") == stage_id:
            row["status"] = "CODEX_CANDIDATE_READY_PENDING_HUMAN_REVIEW"
            row["candidate_subject_hash"] = candidate_subject_hash


def _mark_stage_read_only_qa_ready(stage_plan: Mapping[str, Any], stage_id: str, qa_subject_hash: str) -> None:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, dict) and row.get("stage_id") == stage_id:
            row["status"] = "CODEX_READ_ONLY_QA_READY_PENDING_VALIDATION"
            row["qa_subject_hash"] = qa_subject_hash


def _update_run_state(
    *,
    run_state: dict,
    run_state_ref: Path,
    stage_id: str,
    candidate_subject_hash: str,
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

    candidate_hashes = dict(run_state.get("candidate_subject_hashes", {}))
    candidate_hashes[stage_id] = candidate_subject_hash
    run_state["candidate_subject_hashes"] = candidate_hashes

    node_states = dict(run_state.get("node_states", {}))
    if stage_id == "DRD-06":
        node_states[stage_id] = {
            "state": "NODE_CODEX_READ_ONLY_QA_READY",
            "qa_subject_hash": candidate_subject_hash,
        }
    else:
        node_states[stage_id] = {
            "state": "NODE_CODEX_CANDIDATE_READY",
            "candidate_subject_hash": candidate_subject_hash,
        }
    run_state["node_states"] = node_states

    gate_states = dict(run_state.get("gate_states", {}))
    if stage_id == "DRD-06":
        gate_states[stage_id] = {
            "gate_type": "READ_ONLY_QA_VALIDATION_GATE",
            "gate_id": "DRD-06_READ_ONLY_QA_VALIDATION_GATE",
            "human_gate_required": False,
            "qa_subject_hash": candidate_subject_hash,
        }
    else:
        gate_states[stage_id] = {
            "gate_type": "HUMAN_REVIEW_GATE",
            "gate_id": f"{stage_id}_HUMAN_REVIEW_GATE",
            "human_gate_required": True,
            "candidate_subject_hash": candidate_subject_hash,
        }
    run_state["gate_states"] = gate_states

    history = list(run_state.get("recovery_history", []))
    history_status = "CODEX_READ_ONLY_QA_READY" if stage_id == "DRD-06" else "CODEX_STAGE_CANDIDATE_READY"
    history.append(
        {
            "command": "codex-stage",
            "stage_id": stage_id,
            "status": history_status,
            "candidate_subject_hash": candidate_subject_hash,
        }
    )
    run_state["recovery_history"] = history
    _write_json(run_state_ref, run_state)
