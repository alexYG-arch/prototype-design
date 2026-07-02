"""Deterministic DRD-05 compilation continuation for staged runs."""

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from drd_harness.compiler.conservation import compute_unit_hash
from drd_harness.compiler.final_drd import CompilerFailure, compile_final_drd
from drd_harness.kernel.hashline import sha256_file
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.stages.contracts import StageId, canonical_outputs_for_stage
from drd_harness.validators.compiler_conservation import compute_closed_input_hash, compute_semantic_content_hash


SEMANTIC_COMPILER_STAGES = ("DRD-01", "DRD-02", "DRD-03", "DRD-03B", "DRD-04")
SEMANTIC_UNIT_TYPES = ("TRACE_BINDING", "ARRANGEMENT_RULE", "CTA", "COPY_STRING")


def run_stage_compilation(
    *,
    work_dir: Path,
    run_state_ref: Path,
    stage_id: str = "DRD-05",
    dry_run: bool = False,
) -> dict:
    output_dir = run_state_ref.parent
    findings = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if stage_id != StageId.DRD_05.value:
        findings.append(DriverFinding("COMPILE-STAGE-INPUT-001", stage_id, "compile-stage only supports DRD-05"))
    if not run_state_ref.is_file():
        findings.append(DriverFinding("COMPILE-STAGE-INPUT-002", run_state_ref.as_posix(), "run_state_ref must exist"))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    try:
        run_state = _read_json(run_state_ref)
        stage_plan = _read_json(output_dir / "stage_execution_plan.json")
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(DriverFinding("COMPILE-STAGE-INPUT-002", run_state_ref.as_posix(), str(exc)))
        return _stopped(stage_id, output_dir, findings, dry_run=dry_run)

    planned_paths = _planned_paths(output_dir)
    findings.extend(_upstream_findings(output_dir, run_state))
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
            command="compile-stage",
            status="COMPILE_STAGE_DRY_RUN",
            run_id=str(run_state.get("run_id", "")),
            written_paths=[],
            findings=[],
            exit_code=0,
            stage_id=stage_id,
            primary_runtime="PYTHON",
            planned_written_paths=planned_paths,
            expected_outputs=canonical_outputs_for_stage("DRD-05"),
            requires_approved_stage_semantic_artifacts=True,
            staged_execution_complete=False,
            dry_run=True,
        )

    try:
        bundle = _compiler_input_bundle(
            work_dir=work_dir,
            output_dir=output_dir,
            run_state_ref=run_state_ref,
            run_state=run_state,
            stage_plan=stage_plan,
        )
        compiled = compile_final_drd(bundle)
    except (CompilerFailure, OSError, json.JSONDecodeError, ValueError) as exc:
        compiler_findings = getattr(exc, "findings", None)
        if compiler_findings:
            findings.extend(DriverFinding(finding.code, finding.subject_id, finding.message) for finding in compiler_findings)
        else:
            findings.append(DriverFinding("COMPILE-STAGE-COMPILE-001", stage_id, str(exc)))
        return _stopped(
            stage_id,
            output_dir,
            findings,
            run_id=str(run_state.get("run_id", "")),
            planned_written_paths=planned_paths,
            dry_run=dry_run,
        )

    output_map = {
        output_dir / "DRD-05" / "FINAL_DRD.md": compiled["FINAL_DRD.md"],
        output_dir / "DRD-05" / "final_drd_manifest.json": compiled["final_drd_manifest.json"],
        output_dir / "DRD-05" / "final_drd_toc.json": compiled["final_drd_toc.json"],
        output_dir / "DRD-05" / "final_drd_reference_index.json": compiled["final_drd_reference_index.json"],
        output_dir / "DRD-05" / "final_drd_hash_index.json": compiled["final_drd_hash_index.json"],
        output_dir / "DRD-05" / "compiler_conservation_report.json": compiled["compiler_conservation_report.json"],
        output_dir / "DRD-05" / "compiler_semantic_unit_inventory.json": compiled["compiler_semantic_unit_inventory.json"],
        output_dir / "DRD-05" / "compiler_input_bundle.json": bundle,
    }
    _write_outputs(output_map)
    _mark_stage_compiled(stage_plan, compiled)
    _write_json(output_dir / "stage_execution_plan.json", stage_plan)

    written_paths = sorted(path.as_posix() for path in output_map)
    written_paths.append((output_dir / "stage_execution_plan.json").as_posix())
    output_hashes = {path: sha256_file(Path(path)) for path in sorted(set(written_paths))}
    _update_run_state(
        run_state=run_state,
        run_state_ref=run_state_ref,
        written_paths=written_paths,
        output_hashes=output_hashes,
        final_drd_hash=sha256_file(output_dir / "DRD-05" / "FINAL_DRD.md"),
        compiler_input_bundle_hash=sha256_file(output_dir / "DRD-05" / "compiler_input_bundle.json"),
        execution_plan_hash=sha256_file(output_dir / "stage_execution_plan.json"),
    )
    written_paths.append(run_state_ref.as_posix())

    final_written = sorted(set(written_paths))
    return build_status_payload(
        command="compile-stage",
        status="COMPILE_STAGE_COMPLETE",
        run_id=str(run_state.get("run_id", "")),
        written_paths=final_written,
        findings=[],
        exit_code=0,
        stage_id=stage_id,
        primary_runtime="PYTHON",
        expected_outputs=canonical_outputs_for_stage("DRD-05"),
        final_drd_path=(output_dir / "DRD-05" / "FINAL_DRD.md").as_posix(),
        final_drd_hash=sha256_file(output_dir / "DRD-05" / "FINAL_DRD.md"),
        compiler_input_bundle_hash=sha256_file(output_dir / "DRD-05" / "compiler_input_bundle.json"),
        conservation_status=compiled["compiler_conservation_report.json"]["status"],
        staged_execution_complete=False,
        creates_control_lock=False,
        creates_release_lock=False,
        publishes_package=False,
        dry_run=False,
        output_hashes={path: sha256_file(Path(path)) for path in final_written if Path(path).is_file()},
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
        command="compile-stage",
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


def _compiler_input_bundle(
    *,
    work_dir: Path,
    output_dir: Path,
    run_state_ref: Path,
    run_state: Mapping[str, Any],
    stage_plan: Mapping[str, Any],
) -> dict:
    source_manifest_path = output_dir / "DRD-00" / "source_snapshot_manifest.json"
    source_manifest = _read_json(source_manifest_path)
    source_identity = dict(source_manifest.get("manifest", source_manifest))
    source_hash = str(source_identity.get("snapshot_hash") or source_identity.get("sha256") or "")
    source_section_count = int(stage_plan.get("source_section_count") or 0)
    stage_rows = _semantic_stage_order(stage_plan)
    approved_records = []
    approved_manifests = []
    operational_indexes = []
    review_decisions = []
    validator_results = []
    sections = []
    section_order = []
    semantic_units = []

    for stage_index, stage_id in enumerate(SEMANTIC_COMPILER_STAGES, 1):
        stage_dir = output_dir / stage_id
        body_path = stage_dir / "APPROVED_SEMANTIC_ARTIFACT.md"
        manifest_path = stage_dir / "approved_semantic_artifact.json"
        review_path = stage_dir / "review_decision.json"
        manifest = _read_json(manifest_path)
        body_hash = sha256_file(body_path)
        review_hash = sha256_file(review_path)
        body_text = _section_body(body_path, str(manifest.get("final_drd_section_title") or stage_id))
        unit_ids = []
        for unit_index, unit_type in enumerate(SEMANTIC_UNIT_TYPES, 1):
            unit = _semantic_unit(
                stage_id=stage_id,
                unit_type=unit_type,
                unit_index=unit_index,
                source_path=body_path.as_posix(),
                source_hash=body_hash,
                approval_ref=review_path.as_posix(),
                lock_ref=source_manifest_path.as_posix(),
                canonical_value=f"{stage_id} approved semantic body is preserved for DRD-05 as {unit_type}.",
            )
            semantic_units.append(unit)
            unit_ids.append(unit["semantic_unit_id"])
        section_order.append({"stage_id": stage_id, "section_id": stage_id, "section_order_index": 1})
        sections.append(
            {
                "section_id": stage_id,
                "stage_id": stage_id,
                "stage_order_index": _stage_order_index(stage_rows, stage_id),
                "section_order_index": 1,
                "heading_text": str(manifest.get("final_drd_section_title") or stage_id),
                "source_path": body_path.as_posix(),
                "source_hash": body_hash,
                "approved_hash_ref": review_path.as_posix(),
                "approved_semantic_artifact_ref": manifest.get("artifact_id"),
                "body": body_text,
                "semantic_unit_ids": unit_ids,
            }
        )
        approved_records.append(
            {
                "input_id": f"{stage_id}-APPROVED-SEMANTIC-BODY",
                "input_type": "APPROVED_SEMANTIC_ARTIFACT",
                "stage_id": stage_id,
                "artifact_kind": "APPROVED_SEMANTIC_ARTIFACT",
                "path": body_path.as_posix(),
                "sha256": body_hash,
                "approval_ref": review_path.as_posix(),
                "review_decision_ref": review_path.as_posix(),
                "semantic_body_path": body_path.as_posix(),
                "semantic_body_sha256": body_hash,
                "semantic_role": "approved_stage_semantic_body",
                "approved_semantic_artifact_ref": manifest.get("artifact_id"),
                "source_candidate_refs": list(manifest.get("source_candidate_refs", [])),
            }
        )
        approved_manifests.append(manifest)
        operational_indexes.append(
            {
                "input_id": f"{stage_id}-APPROVED-SEMANTIC-MANIFEST",
                "input_type": "APPROVED_OPERATIONAL_INDEX",
                "stage_id": stage_id,
                "path": manifest_path.as_posix(),
                "sha256": sha256_file(manifest_path),
                "review_decision_ref": review_path.as_posix(),
                "semantic_role": "approved_semantic_artifact_manifest",
            }
        )
        review_decisions.append(
            {
                "input_id": f"{stage_id}-REVIEW-DECISION",
                "input_type": "REVIEW_DECISION",
                "stage_id": stage_id,
                "path": review_path.as_posix(),
                "sha256": review_hash,
            }
        )
        runtime_result_path = output_dir / "runtime_results" / f"{stage_id}_codex_runtime_result.json"
        if runtime_result_path.is_file():
            validator_results.append(
                {
                    "input_id": f"{stage_id}-CODEX-RUNTIME-RESULT",
                    "input_type": "VALIDATOR_RESULT",
                    "stage_id": stage_id,
                    "path": runtime_result_path.as_posix(),
                    "sha256": sha256_file(runtime_result_path),
                }
            )

    schema_paths = [
        Path("repository/schemas/compiler/final_drd_manifest.schema.json"),
        Path("repository/schemas/compiler/compiler_input_bundle.schema.json"),
    ]
    schemas = [
        {
            "input_id": path.stem.upper().replace("-", "_") + "-SCHEMA",
            "input_type": "SCHEMA",
            "path": path.as_posix(),
            "sha256": sha256_file(_resolve_path(work_dir, path.as_posix())),
        }
        for path in schema_paths
    ]
    control_path = Path("repository/src/drd_harness/stages/contracts.py")
    control_indexes = [
        {
            "input_id": "STAGE-CONTRACTS",
            "input_type": "CONTROL_INDEX",
            "path": control_path.as_posix(),
            "sha256": sha256_file(_resolve_path(work_dir, control_path.as_posix())),
        }
    ]
    lock_refs = [
        {
            "input_id": "SOURCE-SNAPSHOT-BINDING",
            "input_type": "SPEC_LOCK_REF",
            "path": source_manifest_path.as_posix(),
            "sha256": sha256_file(source_manifest_path),
        }
    ]
    bundle = {
        "bundle_id": "staged-drd-compiler-bundle-" + str(run_state.get("run_id", "")),
        "bundle_version": "1.0",
        "compiler_id": "drd_harness.compiler.final_drd",
        "compiler_version": "1.0.0",
        "compiler_code_hash": sha256_file(Path(__file__).parents[1] / "compiler" / "final_drd.py"),
        "compiler_stage_id": "DRD-05",
        "requires_approved_stage_semantic_artifacts": True,
        "source_snapshot_identity": {
            "snapshot_id": source_identity.get("source_prd_snapshot_id") or "DRD-00",
            "source_path": source_identity.get("source_path"),
            "snapshot_path": source_identity.get("snapshot_path") or source_manifest_path.as_posix(),
            "sha256": source_hash,
            "section_count": source_section_count,
        },
        "approved_semantic_artifacts": approved_records,
        "approved_semantic_artifact_manifests": approved_manifests,
        "approved_operational_indexes": operational_indexes,
        "review_decisions": review_decisions,
        "lock_refs": lock_refs,
        "validator_results": validator_results,
        "control_indexes": control_indexes,
        "schemas": schemas,
        "stage_order": stage_rows,
        "section_order": section_order,
        "sections": sections,
        "semantic_units": semantic_units,
        "compiled_semantic_units": semantic_units,
        "schema_hashes": {record["path"]: record["sha256"] for record in schemas},
        "validator_result_refs": [record["path"] for record in validator_results],
        "default_lock_ref": source_manifest_path.as_posix(),
        "semantic_content_hash": "",
        "current_hashes": {},
        "closed_input_hash": "",
    }
    bundle["semantic_content_hash"] = compute_semantic_content_hash(bundle)
    bundle["current_hashes"] = _current_hashes(work_dir, bundle)
    bundle["closed_input_hash"] = compute_closed_input_hash(bundle)
    return bundle


def _upstream_findings(output_dir: Path, run_state: Mapping[str, Any]) -> list[DriverFinding]:
    findings = []
    for stage_id in SEMANTIC_COMPILER_STAGES:
        state = run_state.get("node_states", {}).get(stage_id, {}).get("state")
        if state != "NODE_PROMOTED_APPROVED_SEMANTIC_ARTIFACT":
            findings.append(
                DriverFinding(
                    "COMPILE-STAGE-UPSTREAM-001",
                    stage_id,
                    "DRD-05 requires promoted approved semantic artifacts for every semantic source stage",
                )
            )
        for rel_path in (
            f"{stage_id}/APPROVED_SEMANTIC_ARTIFACT.md",
            f"{stage_id}/approved_semantic_artifact.json",
            f"{stage_id}/review_decision.json",
        ):
            path = output_dir / rel_path
            if not path.is_file():
                findings.append(DriverFinding("COMPILE-STAGE-UPSTREAM-002", path.as_posix(), "required approved stage input is missing"))
    return findings


def _semantic_stage_order(stage_plan: Mapping[str, Any]) -> list[dict]:
    rows = []
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, Mapping) and row.get("stage_id") in SEMANTIC_COMPILER_STAGES:
            rows.append({"stage_id": row.get("stage_id"), "stage_order_index": row.get("stage_order_index")})
    return sorted(rows, key=lambda row: row["stage_order_index"])


def _stage_order_index(stage_rows: Sequence[Mapping[str, Any]], stage_id: str) -> int:
    for row in stage_rows:
        if row.get("stage_id") == stage_id:
            return int(row.get("stage_order_index"))
    return SEMANTIC_COMPILER_STAGES.index(stage_id) * 10 + 10


def _semantic_unit(
    *,
    stage_id: str,
    unit_type: str,
    unit_index: int,
    source_path: str,
    source_hash: str,
    approval_ref: str,
    lock_ref: str,
    canonical_value: str,
) -> dict:
    unit = {
        "semantic_unit_id": f"UNIT-{stage_id}-{unit_type}",
        "unit_type": unit_type,
        "unit_class": "Approved stage semantic body",
        "stage_id": stage_id,
        "source_path": source_path,
        "source_section_id": stage_id,
        "source_span_ref": f"approved_body:{stage_id}:{unit_index}",
        "source_hash": source_hash,
        "approval_ref": approval_ref,
        "lock_ref": lock_ref,
        "parent_unit_id": None,
        "relationship_kind": "TRACE",
        "canonical_value": canonical_value,
        "unit_hash": "",
        "inventory_version": "1.0",
    }
    unit["unit_hash"] = compute_unit_hash(unit)
    return unit


def _section_body(body_path: Path, heading: str) -> str:
    lines = body_path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == heading:
        lines = lines[1:]
        if lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def _current_hashes(work_dir: Path, bundle: Mapping[str, Any]) -> dict[str, str]:
    hashes = {}
    for group in ("approved_semantic_artifacts", "approved_operational_indexes", "review_decisions", "lock_refs", "validator_results", "control_indexes", "schemas"):
        for record in bundle.get(group, []):
            path = str(record.get("path") or "")
            hashes[path] = sha256_file(_resolve_path(work_dir, path))
    return dict(sorted(hashes.items()))


def _resolve_path(work_dir: Path, path: str) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    work_dir_path = work_dir / value
    if work_dir_path.exists():
        return work_dir_path
    parts = value.parts
    if parts and parts[0] == "repository":
        return Path(__file__).parents[3].joinpath(*parts[1:])
    return work_dir_path


def _planned_paths(output_dir: Path) -> list[str]:
    return sorted([(output_dir / rel_path).as_posix() for rel_path in canonical_outputs_for_stage("DRD-05")] + [
        (output_dir / "stage_execution_plan.json").as_posix(),
        (output_dir / "run_state.json").as_posix(),
    ])


def _mark_stage_compiled(stage_plan: Mapping[str, Any], compiled: Mapping[str, Any]) -> None:
    for row in stage_plan.get("stage_chain", []):
        if isinstance(row, dict) and row.get("stage_id") == "DRD-05":
            row["status"] = "COMPILED_FINAL_DRD"
            row["final_drd_sha256"] = compiled["final_drd_manifest.json"]["final_drd_hash"]
            row["conservation_status"] = compiled["compiler_conservation_report.json"]["status"]
    stage_plan["completed_stage_ids"] = sorted(set(stage_plan.get("completed_stage_ids", [])) | {"DRD-05"})
    stage_plan["blocked_stage_id"] = "DRD-06"
    stage_plan["blocked_gate_id"] = "CODEX_READ_ONLY_RUNTIME_GATE"
    stage_plan["next_required_runtime"] = "CODEX_READ_ONLY"
    stage_plan["staged_execution_complete"] = False


def _update_run_state(
    *,
    run_state: dict,
    run_state_ref: Path,
    written_paths: Sequence[str],
    output_hashes: Mapping[str, str],
    final_drd_hash: str,
    compiler_input_bundle_hash: str,
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
    node_states["DRD-05"] = {
        "state": "NODE_COMPLETED",
        "final_drd_sha256": final_drd_hash,
        "compiler_input_bundle_sha256": compiler_input_bundle_hash,
    }
    run_state["node_states"] = node_states
    gate_states = dict(run_state.get("gate_states", {}))
    gate_states["DRD-05"] = {
        "gate_type": "DETERMINISTIC_COMPILER_GATE",
        "gate_id": "DRD-05_DETERMINISTIC_COMPILER_GATE",
        "human_gate_required": False,
        "final_drd_sha256": final_drd_hash,
    }
    run_state["gate_states"] = gate_states
    history = list(run_state.get("recovery_history", []))
    history.append(
        {
            "command": "compile-stage",
            "stage_id": "DRD-05",
            "status": "COMPILE_STAGE_COMPLETE",
            "final_drd_sha256": final_drd_hash,
        }
    )
    run_state["recovery_history"] = history
    _write_json(run_state_ref, run_state)


def _write_outputs(outputs: Mapping[Path, Any]) -> None:
    for path, value in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            _write_json(path, value)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
