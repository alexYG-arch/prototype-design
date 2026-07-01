"""External PRD staged-run boundary.

This module owns the honest executable boundary for arbitrary external PRDs.
Python can freeze source evidence, then it must stop before DRD-01 because
experience fact extraction is Codex-owned by the charter runtime model.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_bytes, sha256_file, sha256_text
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.stages.contracts import (
    candidate_outputs_for_stage,
    canonical_outputs_for_stage,
    promotion_outputs_for_stage,
)


def _semantic_stage_output_fields(stage_id: str) -> dict:
    candidate_outputs = candidate_outputs_for_stage(stage_id)
    promotion_outputs = promotion_outputs_for_stage(stage_id)
    return {
        "candidate_outputs": candidate_outputs,
        "promotion_outputs": promotion_outputs,
        "canonical_outputs": candidate_outputs + promotion_outputs,
    }


STAGE_CHAIN = [
    {
        "stage_id": "DRD-00",
        "stage_order_index": 0,
        "purpose": "Source freeze",
        "primary_runtime": "PYTHON",
        "canonical_outputs": canonical_outputs_for_stage("DRD-00"),
    },
    {
        "stage_id": "DRD-01",
        "stage_order_index": 10,
        "purpose": "PRD experience fact extraction",
        "primary_runtime": "CODEX",
        **_semantic_stage_output_fields("DRD-01"),
    },
    {
        "stage_id": "DRD-02",
        "stage_order_index": 20,
        "purpose": "User task and interaction closure",
        "primary_runtime": "CODEX_PYTHON_LOOP",
        **_semantic_stage_output_fields("DRD-02"),
    },
    {
        "stage_id": "DRD-03",
        "stage_order_index": 30,
        "purpose": "PRD element validation, adoption, and necessary completion",
        "primary_runtime": "CODEX",
        **_semantic_stage_output_fields("DRD-03"),
    },
    {
        "stage_id": "DRD-03B",
        "stage_order_index": 35,
        "purpose": "Shared components and information presentation patterns",
        "primary_runtime": "CODEX_PYTHON_LOOP",
        **_semantic_stage_output_fields("DRD-03B"),
    },
    {
        "stage_id": "DRD-04",
        "stage_order_index": 40,
        "purpose": "Natural-language layout and Figma compatibility",
        "primary_runtime": "CODEX",
        **_semantic_stage_output_fields("DRD-04"),
    },
    {
        "stage_id": "DRD-05",
        "stage_order_index": 50,
        "purpose": "Deterministic DRD compilation",
        "primary_runtime": "PYTHON",
        "canonical_outputs": canonical_outputs_for_stage("DRD-05"),
        "requires_approved_stage_semantic_artifacts": True,
    },
    {
        "stage_id": "DRD-06",
        "stage_order_index": 60,
        "purpose": "Read-only consistency QA",
        "primary_runtime": "CODEX_READ_ONLY",
        "canonical_outputs": canonical_outputs_for_stage("DRD-06"),
    },
]

WRITTEN_RELATIVE_PATHS = [
    "stage_execution_plan.json",
    "DRD-00/source_prd_snapshot.md",
    "DRD-00/source_snapshot_manifest.json",
    "DRD-00/stage_receipt.json",
    "review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json",
    "codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md",
    "run_state.json",
]


def run_external_prd_staged(
    *,
    work_dir: Path,
    source_ref: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict:
    planned_paths = [(output_dir / rel_path).as_posix() for rel_path in WRITTEN_RELATIVE_PATHS]
    findings: List[Any] = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if not source_ref.is_file():
        findings.append(DriverFinding("STAGED-RUN-INPUT-001", str(source_ref), "source_ref must be a readable Markdown PRD"))

    source_hash = ""
    source_bytes = b""
    source_text = ""
    sections: List[dict] = []
    if not findings:
        try:
            source_bytes = source_ref.read_bytes()
            source_hash = sha256_bytes(source_bytes)
            source_text = source_bytes.decode("utf-8")
            sections = _split_markdown_sections(source_text, source_hash, source_ref)
            if not source_text.strip():
                findings.append(DriverFinding("STAGED-RUN-INPUT-002", str(source_ref), "source_ref must contain non-empty Markdown content"))
            findings.extend(_unsupported_markdown_findings(source_text))
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(DriverFinding("STAGED-RUN-INPUT-001", str(source_ref), str(exc)))

    run_id = _stable_id("staged-run", [str(source_ref), str(output_dir), source_hash])
    if findings:
        return build_status_payload(
            command="staged-run",
            status="STOPPED",
            run_id=run_id,
            written_paths=[],
            findings=findings,
            exit_code=1,
            planned_written_paths=planned_paths,
            dry_run=dry_run,
            staged_execution_complete=False,
        )

    if dry_run:
        return build_status_payload(
            command="staged-run",
            status="DRY_RUN",
            run_id=run_id,
            written_paths=[],
            findings=[],
            exit_code=0,
            planned_written_paths=planned_paths,
            source_sha256=source_hash,
            stage_execution_order=[row["stage_id"] for row in STAGE_CHAIN],
            blocked_stage_id="DRD-01",
            blocked_gate_id="CODEX_RUNTIME_GATE",
            next_required_runtime="CODEX",
            staged_execution_complete=False,
            dry_run=True,
        )

    artifacts = _build_artifacts(run_id, source_ref, source_hash, source_bytes, source_text, sections, output_dir)
    _write_artifacts(artifacts)
    written_paths = sorted(path.as_posix() for path in artifacts)
    output_hashes = {path: sha256_file(Path(path)) for path in written_paths}
    run_state_path = output_dir / "run_state.json"
    run_state = _run_state(run_id, source_ref, source_hash, sections, output_dir, artifacts, output_hashes)
    run_state_path.write_text(json.dumps(run_state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_hashes[run_state_path.as_posix()] = sha256_file(run_state_path)

    return build_status_payload(
        command="staged-run",
        status="STAGE_GATE_STOPPED",
        run_id=run_id,
        written_paths=sorted(output_hashes),
        findings=[],
        exit_code=0,
        planned_written_paths=planned_paths,
        output_hashes=dict(sorted(output_hashes.items())),
        source_sha256=source_hash,
        source_section_count=len(sections),
        stage_execution_order=[row["stage_id"] for row in STAGE_CHAIN],
        completed_stage_ids=["DRD-00"],
        blocked_stage_id="DRD-01",
        blocked_gate_id="CODEX_RUNTIME_GATE",
        next_required_runtime="CODEX",
        staged_execution_complete=False,
        creates_control_lock=False,
        creates_release_lock=False,
        publishes_package=False,
        run_state_path=run_state_path.as_posix(),
        dry_run=False,
    )


def _build_artifacts(
    run_id: str,
    source_ref: Path,
    source_hash: str,
    source_bytes: bytes,
    source_text: str,
    sections: Sequence[Mapping[str, Any]],
    output_dir: Path,
) -> Dict[Path, Any]:
    snapshot_path = output_dir / "DRD-00" / "source_prd_snapshot.md"
    source_snapshot_manifest = _source_snapshot_manifest(source_ref, source_hash, source_bytes, snapshot_path)

    stage_plan = _stage_execution_plan(run_id, source_ref, source_hash, sections, output_dir)
    drd00_output_paths = [snapshot_path, output_dir / "DRD-00" / "source_snapshot_manifest.json"]
    drd00_receipt = _stage_receipt(
        run_id=run_id,
        stage_id="DRD-00",
        status="PASS",
        input_hashes={str(source_ref): source_hash},
        output_paths=drd00_output_paths,
        output_hashes={
            snapshot_path.as_posix(): source_hash,
            (output_dir / "DRD-00" / "source_snapshot_manifest.json").as_posix(): _json_file_sha256(source_snapshot_manifest),
        },
        next_stage_id="DRD-01",
    )
    gate_request = _drd01_runtime_gate_request(run_id, source_ref, source_hash, sections, output_dir)
    codex_prompt = _drd01_prompt(source_ref, source_hash, output_dir)

    return {
        output_dir / "stage_execution_plan.json": stage_plan,
        snapshot_path: source_bytes,
        output_dir / "DRD-00" / "source_snapshot_manifest.json": source_snapshot_manifest,
        output_dir / "DRD-00" / "stage_receipt.json": drd00_receipt,
        output_dir / "review_gates" / "DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json": gate_request,
        output_dir / "codex_prompts" / "DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md": codex_prompt,
    }


def _source_snapshot_manifest(source_ref: Path, source_hash: str, source_bytes: bytes, snapshot_path: Path) -> dict:
    return {
        "artifact": "source_snapshot_manifest",
        "stage_id": "DRD-00",
        "stage_order_index": 0,
        "primary_runtime": "PYTHON",
        "manifest": {
            "source_prd_snapshot_id": "external-prd-source-snapshot-" + source_hash[:16],
            "source_path": str(source_ref),
            "snapshot_path": snapshot_path.as_posix(),
            "snapshot_hash": source_hash,
            "created_at": "deterministic-staged-run",
            "byte_size": len(source_bytes),
            "content_type": "text/markdown",
            "normalization_method": "none",
            "source_identity": source_ref.name,
        },
    }


def _stage_execution_plan(run_id: str, source_ref: Path, source_hash: str, sections: Sequence[Mapping[str, Any]], output_dir: Path) -> dict:
    stage_rows = []
    for row in STAGE_CHAIN:
        status = "NOT_STARTED_PENDING_UPSTREAM"
        if row["stage_id"] == "DRD-00":
            status = "COMPLETE"
        elif row["stage_id"] == "DRD-01":
            status = "BLOCKED_CODEX_RUNTIME_REQUIRED"
        stage_rows.append({**row, "status": status})
    return {
        "artifact": "stage_execution_plan",
        "run_id": run_id,
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "source_section_count": len(sections),
        "stage_chain": stage_rows,
        "completed_stage_ids": ["DRD-00"],
        "blocked_stage_id": "DRD-01",
        "blocked_gate_id": "CODEX_RUNTIME_GATE",
        "next_required_runtime": "CODEX",
        "staged_execution_complete": False,
        "external_prd_output_scope": output_dir.as_posix(),
        "lock_or_release_stage_included": False,
        "source_preserving_compile_substitute": False,
    }


def _stage_receipt(
    *,
    run_id: str,
    stage_id: str,
    status: str,
    input_hashes: Mapping[str, str],
    output_paths: Sequence[Path],
    output_hashes: Mapping[str, str],
    next_stage_id: str,
) -> dict:
    return {
        "artifact": "stage_receipt",
        "run_id": run_id,
        "stage_id": stage_id,
        "status": status,
        "input_hashes": dict(sorted(input_hashes.items())),
        "output_artifacts": [path.as_posix() for path in output_paths],
        "output_hashes": dict(sorted(output_hashes.items())),
        "validator_result_hash": sha256_text(json.dumps({"stage_id": stage_id, "status": status}, sort_keys=True)),
        "next_stage_id": next_stage_id,
    }


def _drd01_runtime_gate_request(
    run_id: str,
    source_ref: Path,
    source_hash: str,
    sections: Sequence[Mapping[str, Any]],
    output_dir: Path,
) -> dict:
    return {
        "artifact": "runtime_gate_request",
        "gate_id": "CODEX_RUNTIME_GATE",
        "run_id": run_id,
        "blocked_stage_id": "DRD-01",
        "status": "CODEX_RUNTIME_REQUIRED",
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "source_section_count": len(sections),
        "reason": "DRD-01 requires Codex experience fact extraction, classification, and experience impact explanation; Python staged-run may only freeze source evidence.",
        "required_inputs": [
            (output_dir / "DRD-00" / "source_snapshot_manifest.json").as_posix(),
        ],
        "expected_candidate_outputs": [
            *candidate_outputs_for_stage("DRD-01"),
        ],
        "post_review_promotion_outputs": promotion_outputs_for_stage("DRD-01"),
        "promotion_required_before_successor": True,
        "compiler_eligible_artifact_kind": "APPROVED_SEMANTIC_ARTIFACT",
        "product_capability_additions_allowed": False,
        "lock_or_release_allowed": False,
    }


def _drd01_prompt(source_ref: Path, source_hash: str, output_dir: Path) -> str:
    return (
        "# DRD-01 Codex Candidate Prompt\n\n"
        "Use the immutable source PRD snapshot to extract PRD experience facts, classify them, and explain experience impact.\n\n"
        f"- source_path: {source_ref}\n"
        f"- source_sha256: {source_hash}\n"
        f"- source_snapshot_manifest: {(output_dir / 'DRD-00' / 'source_snapshot_manifest.json').as_posix()}\n"
        f"- source_snapshot: {(output_dir / 'DRD-00' / 'source_prd_snapshot.md').as_posix()}\n\n"
        "Rules:\n"
        "- Do not add product capabilities absent from the PRD.\n"
        "- Re-read the immutable source snapshot; do not rely on a summary as authority.\n"
        "- Output only DRD-01 candidate artifacts and wait for validation or conditional Human Gate.\n"
    )


def _run_state(
    run_id: str,
    source_ref: Path,
    source_hash: str,
    sections: Sequence[Mapping[str, Any]],
    output_dir: Path,
    artifacts: Mapping[Path, Any],
    output_hashes: Mapping[str, str],
) -> dict:
    plan_path = output_dir / "stage_execution_plan.json"
    source_refs = [str(source_ref)] + [str(section["section_id"]) for section in sections]
    return {
        "run_id": run_id,
        "program_id": "external-prd-staged-run",
        "driver_version": "external-staged-run-v1",
        "original_command": "staged-run",
        "adapter_id": "markdown_prd_adapter",
        "source_refs": source_refs,
        "input_hashes": {str(source_ref): source_hash},
        "upstream_lock_refs": {},
        "candidate_subject_hashes": {},
        "review_decision_hashes": {},
        "dag_snapshot_hash": sha256_text(json.dumps(STAGE_CHAIN, sort_keys=True, separators=(",", ":"))),
        "execution_plan_hash": output_hashes.get(plan_path.as_posix(), ""),
        "node_states": {
            "DRD-00": {"state": "NODE_COMPLETED"},
            "DRD-01": {"state": "NODE_BLOCKED_CODEX_RUNTIME"},
        },
        "written_paths": sorted(path.as_posix() for path in artifacts),
        "output_hashes": {path: digest for path, digest in sorted(output_hashes.items()) if path != (output_dir / "run_state.json").as_posix()},
        "gate_states": {
            "DRD-01": {
                "gate_type": "CODEX_RUNTIME_GATE",
                "human_gate_required": True,
                "gate_id": "CODEX_RUNTIME_GATE",
            }
        },
        "failure_records": {},
        "recovery_history": [],
    }


def _split_markdown_sections(source_text: str, source_hash: str, source_ref: Path) -> List[dict]:
    lines = source_text.splitlines()
    starts = [index for index, line in enumerate(lines, 1) if line.startswith("#")]
    if not starts and lines:
        starts = [1]
    sections = []
    for position, start in enumerate(starts):
        end = starts[position + 1] - 1 if position + 1 < len(starts) else len(lines)
        heading_line = lines[start - 1] if lines else ""
        heading = heading_line.lstrip("#").strip() if heading_line.startswith("#") else "preamble"
        body = "\n".join(lines[start - 1 : end])
        sections.append(
            {
                "section_id": "md-section-" + sha256_text(f"{source_hash}\0{position}\0{heading}\0{start}")[:16],
                "source_path": str(source_ref),
                "source_sha256": source_hash,
                "heading": heading or "untitled",
                "line_start": start,
                "line_end": end,
                "body": body,
                "content_sha256": sha256_text(body),
            }
        )
    return sections


def _unsupported_markdown_findings(source_text: str) -> List[DriverFinding]:
    findings = []
    for index, line in enumerate(source_text.splitlines(), 1):
        stripped = line.strip()
        if "\x00" in line:
            findings.append(DriverFinding("STAGED-RUN-HUMAN-GATE", str(index), "NUL byte marker requires Human Gate review"))
        if stripped.startswith("<script") or stripped.startswith("<iframe"):
            findings.append(DriverFinding("STAGED-RUN-HUMAN-GATE", str(index), "active embedded HTML requires Human Gate review"))
    return findings


def _write_artifacts(artifacts: Mapping[Path, Any]) -> None:
    for path, value in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            path.write_bytes(value)
        elif isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_file_sha256(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _stable_id(prefix: str, parts: Iterable[str]) -> str:
    normalized = json.dumps([str(part) for part in parts], sort_keys=True, separators=(",", ":"))
    return f"{prefix}-{sha256_text(normalized)[:16]}"
