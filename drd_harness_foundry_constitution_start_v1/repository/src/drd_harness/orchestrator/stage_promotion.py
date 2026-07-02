"""Human-approved stage candidate promotion for external PRD staged runs."""

import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_file, sha256_text
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.stages.contracts import (
    SEMANTIC_SOURCE_STAGES,
    StageId,
    candidate_outputs_for_stage,
)
from drd_harness.validators.compiler_conservation import validate_approved_semantic_artifact_manifest


def run_stage_promotion(
    *,
    work_dir: Path,
    run_state_ref: Path,
    stage_id: str,
    approved_subject_hash: str,
    reviewer: str = "human-user",
    approval_note: str = "User approved candidate for promotion.",
) -> dict:
    output_dir = run_state_ref.parent
    findings = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if not run_state_ref.is_file():
        findings.append(DriverFinding("PROMOTE-STAGE-INPUT-001", run_state_ref.as_posix(), "run_state_ref must exist"))
        return _stopped(stage_id, output_dir, findings)
    try:
        run_state = _read_json(run_state_ref)
        stage_plan = _read_json(output_dir / "stage_execution_plan.json")
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(DriverFinding("PROMOTE-STAGE-INPUT-001", run_state_ref.as_posix(), str(exc)))
        return _stopped(stage_id, output_dir, findings)

    try:
        stage = StageId(stage_id)
    except ValueError:
        findings.append(DriverFinding("PROMOTE-STAGE-INPUT-002", stage_id, "stage_id is not canonical"))
        return _stopped(stage_id, output_dir, findings, run_id=str(run_state.get("run_id", "")))
    if stage not in SEMANTIC_SOURCE_STAGES:
        findings.append(DriverFinding("PROMOTE-STAGE-INPUT-003", stage_id, "only semantic source stages can be promoted"))

    run_candidate_hash = str(run_state.get("candidate_subject_hashes", {}).get(stage_id, ""))
    if run_candidate_hash != approved_subject_hash:
        findings.append(DriverFinding("PROMOTE-STAGE-REVIEW-001", stage_id, "approved_subject_hash does not match run_state candidate hash"))
    expected_outputs = candidate_outputs_for_stage(stage)
    missing = [rel_path for rel_path in expected_outputs if not (output_dir / rel_path).is_file()]
    for rel_path in missing:
        findings.append(DriverFinding("PROMOTE-STAGE-CANDIDATE-001", rel_path, "candidate output is missing"))

    candidate_hashes = _candidate_hashes(output_dir, expected_outputs) if not missing else {}
    current_subject_hash = _candidate_subject_hash(candidate_hashes) if candidate_hashes else ""
    if current_subject_hash and current_subject_hash != approved_subject_hash:
        findings.append(DriverFinding("PROMOTE-STAGE-REVIEW-002", stage_id, "candidate files no longer match approved subject hash"))
    if findings:
        return _stopped(stage_id, output_dir, findings, run_id=str(run_state.get("run_id", "")))

    review_path = output_dir / stage_id / "review_decision.json"
    approved_body_path = output_dir / stage_id / "APPROVED_SEMANTIC_ARTIFACT.md"
    approved_manifest_path = output_dir / stage_id / "approved_semantic_artifact.json"

    review_decision = _review_decision(
        run_id=str(run_state.get("run_id", "")),
        stage_id=stage_id,
        subject_hash=approved_subject_hash,
        approved_sections=expected_outputs,
        reviewer=reviewer,
        approval_note=approval_note,
    )
    _write_json(review_path, review_decision)
    review_hash = sha256_file(review_path)

    approved_body = _approved_body(output_dir, stage_id, expected_outputs)
    approved_body_path.write_text(approved_body, encoding="utf-8")
    approved_body_hash = sha256_file(approved_body_path)

    manifest = {
        "artifact": "approved_semantic_artifact",
        "artifact_kind": "APPROVED_SEMANTIC_ARTIFACT",
        "artifact_id": f"{stage_id}-approved-semantic-artifact-{approved_body_hash[:16]}",
        "stage_id": stage_id,
        "semantic_body_path": approved_body_path.as_posix(),
        "semantic_body_sha256": approved_body_hash,
        "review_decision_ref": review_path.as_posix(),
        "review_decision_sha256": review_hash,
        "source_candidate_refs": expected_outputs,
        "source_candidate_hashes": candidate_hashes,
        "final_drd_section_id": stage_id,
        "final_drd_section_title": _section_title(stage_id),
        "compiler_eligible": True,
        "product_capability_additions_allowed": False,
        "process_evidence_refs": [
            review_path.as_posix(),
            output_dir.joinpath("runtime_results", f"{stage_id}_codex_runtime_result.json").as_posix(),
        ],
    }
    manifest_findings = validate_approved_semantic_artifact_manifest(manifest)
    if manifest_findings:
        approved_body_path.unlink(missing_ok=True)
        return _stopped(
            stage_id,
            output_dir,
            [
                DriverFinding(finding.code, finding.subject_id, finding.message)
                for finding in manifest_findings
            ],
            run_id=str(run_state.get("run_id", "")),
        )

    _write_json(approved_manifest_path, manifest)
    _mark_stage_promoted(stage_plan, stage_id, approved_subject_hash, approved_body_hash)
    _write_json(output_dir / "stage_execution_plan.json", stage_plan)

    written_paths = [
        review_path.as_posix(),
        approved_body_path.as_posix(),
        approved_manifest_path.as_posix(),
        (output_dir / "stage_execution_plan.json").as_posix(),
    ]
    output_hashes = {path: sha256_file(Path(path)) for path in sorted(written_paths)}
    _update_run_state(
        run_state=run_state,
        run_state_ref=run_state_ref,
        stage_id=stage_id,
        review_hash=review_hash,
        approved_body_hash=approved_body_hash,
        approved_manifest_hash=sha256_file(approved_manifest_path),
        written_paths=written_paths,
        output_hashes=output_hashes,
    )
    written_paths.append(run_state_ref.as_posix())
    return build_status_payload(
        command="promote-stage",
        status="STAGE_PROMOTED",
        run_id=str(run_state.get("run_id", "")),
        written_paths=sorted(set(written_paths)),
        findings=[],
        exit_code=0,
        stage_id=stage_id,
        approved_subject_hash=approved_subject_hash,
        review_decision_sha256=review_hash,
        approved_semantic_artifact_sha256=approved_body_hash,
        staged_execution_complete=False,
        output_hashes={path: sha256_file(Path(path)) for path in sorted(set(written_paths)) if Path(path).is_file()},
    )


def _stopped(stage_id: str, output_dir: Path, findings: Iterable[DriverFinding], *, run_id: str = "") -> dict:
    return build_status_payload(
        command="promote-stage",
        status="STOPPED",
        run_id=run_id,
        written_paths=[],
        findings=findings,
        exit_code=1,
        stage_id=stage_id,
        output_dir=output_dir.as_posix(),
        staged_execution_complete=False,
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _candidate_hashes(output_dir: Path, expected_outputs: Sequence[str]) -> dict[str, str]:
    return {rel_path: sha256_file(output_dir / rel_path) for rel_path in sorted(expected_outputs)}


def _candidate_subject_hash(candidate_hashes: Mapping[str, str]) -> str:
    return sha256_text(json.dumps(candidate_hashes, sort_keys=True, separators=(",", ":")))


def _review_decision(
    *,
    run_id: str,
    stage_id: str,
    subject_hash: str,
    approved_sections: Sequence[str],
    reviewer: str,
    approval_note: str,
) -> dict:
    return {
        "artifact": "stage_review_decision",
        "decision_id": f"{stage_id}-review-{subject_hash[:16]}",
        "run_id": run_id,
        "stage_id": stage_id,
        "subject_hash": subject_hash,
        "decision": "APPROVED",
        "reviewer": reviewer,
        "reviewed_at": date.today().isoformat(),
        "approved_sections": list(approved_sections),
        "open_blockers": [],
        "basis": approval_note,
    }


def _approved_body(output_dir: Path, stage_id: str, expected_outputs: Sequence[str]) -> str:
    sections = [_section_title(stage_id), ""]
    for rel_path in expected_outputs:
        path = output_dir / rel_path
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        cleaned = _clean_candidate_markdown(text)
        if cleaned.strip():
            sections.append(cleaned.strip())
            sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def _clean_candidate_markdown(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    skip_source_binding = False
    metadata_prefixes = (
        "Status:",
        "Run ID:",
        "Stage:",
        "Artifact kind:",
        "Source snapshot:",
        "Source SHA-256:",
        "Source snapshot SHA-256:",
        "Approved upstream:",
        "Boundary:",
    )
    process_only_headings = {
        "## Artifact Handoff",
        "## Artifact Status",
        "## Candidate Handoff",
        "## Candidate Status",
    }
    for line in lines:
        if line.startswith("# "):
            continue
        stripped = line.strip()
        unbulleted = stripped[2:].lstrip() if stripped.startswith("- ") else stripped
        if any(unbulleted.startswith(prefix) for prefix in metadata_prefixes):
            continue
        if stripped in process_only_headings:
            skip_source_binding = True
            continue
        if stripped == "## Source Binding":
            skip_source_binding = True
            continue
        if skip_source_binding and line.startswith("## "):
            skip_source_binding = False
        if skip_source_binding:
            continue
        if "Candidate artifact" in line or "candidate artifact" in line:
            continue
        line = line.replace("CANDIDATE", "ARTIFACT")
        line = line.replace("Candidate order", "Semantic order")
        line = line.replace("candidate order", "semantic order")
        line = line.replace("The candidate", "The artifact")
        line = line.replace("this candidate", "this artifact")
        line = line.replace("Candidate", "Artifact")
        line = line.replace("candidate", "artifact")
        line = line.replace("APPROVED_SEMANTIC_ARTIFACT.md", "approved upstream semantics")
        line = line.replace("APPROVED_SEMANTIC_ARTIFACT", "approved upstream semantics")
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def _section_title(stage_id: str) -> str:
    return {
        "DRD-01": "DRD-01 Experience Facts",
        "DRD-02": "DRD-02 User Task And Interaction Closure",
        "DRD-03": "DRD-03 Page Element Blueprint",
        "DRD-03B": "DRD-03B Shared Components And Presentation Patterns",
        "DRD-04": "DRD-04 Natural Language Layout",
    }[stage_id]


def _mark_stage_promoted(stage_plan: Mapping[str, Any], stage_id: str, approved_subject_hash: str, approved_body_hash: str) -> None:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, dict) and row.get("stage_id") == stage_id:
            row["status"] = "PROMOTED_APPROVED_SEMANTIC_ARTIFACT"
            row["approved_subject_hash"] = approved_subject_hash
            row["approved_semantic_artifact_sha256"] = approved_body_hash


def _update_run_state(
    *,
    run_state: dict,
    run_state_ref: Path,
    stage_id: str,
    review_hash: str,
    approved_body_hash: str,
    approved_manifest_hash: str,
    written_paths: Sequence[str],
    output_hashes: Mapping[str, str],
) -> None:
    existing_written = set(str(path) for path in run_state.get("written_paths", []))
    existing_written.update(written_paths)
    run_state["written_paths"] = sorted(existing_written)
    existing_hashes = dict(run_state.get("output_hashes", {}))
    existing_hashes.update(output_hashes)
    existing_hashes.pop(run_state_ref.as_posix(), None)
    run_state["output_hashes"] = dict(sorted(existing_hashes.items()))
    review_hashes = dict(run_state.get("review_decision_hashes", {}))
    review_hashes[stage_id] = review_hash
    run_state["review_decision_hashes"] = review_hashes
    node_states = dict(run_state.get("node_states", {}))
    node_states[stage_id] = {
        "state": "NODE_PROMOTED_APPROVED_SEMANTIC_ARTIFACT",
        "review_decision_sha256": review_hash,
        "approved_semantic_artifact_sha256": approved_body_hash,
        "approved_semantic_artifact_manifest_sha256": approved_manifest_hash,
    }
    run_state["node_states"] = node_states
    gate_states = dict(run_state.get("gate_states", {}))
    gate_states[stage_id] = {
        "gate_type": "HUMAN_REVIEW_GATE",
        "gate_id": f"{stage_id}_HUMAN_REVIEW_GATE",
        "human_gate_required": False,
        "review_decision_sha256": review_hash,
    }
    run_state["gate_states"] = gate_states
    history = list(run_state.get("recovery_history", []))
    history.append(
        {
            "command": "promote-stage",
            "stage_id": stage_id,
            "status": "STAGE_PROMOTED",
            "review_decision_sha256": review_hash,
        }
    )
    run_state["recovery_history"] = history
    _write_json(run_state_ref, run_state)
