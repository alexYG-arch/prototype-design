"""External PRD run and package governance driver primitives."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Union

from drd_harness.kernel.hashline import sha256_file, sha256_text
from drd_harness.orchestrator.recovery import current_hashes_for_paths, load_run_state, resolve_resume_decision


START_PACKAGE_ROOT = Path(__file__).resolve().parents[4]
EXTERNAL_PRD_OUTPUT_ROOT = Path("current_capsule") / "outputs"
P3_BUILD_LOCK_SHA256 = "52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e"
P3_BUILD_LOCK_ROOT_SHA256 = "0ef47227a39e3eb75923e7506523b734769485431c2a7c3a1e1265f9d937fa8f"
DOCUMENT_GENERATION_STAGE_ORDER = [
    {"stage_id": "DRD-00", "stage_order_index": 0, "purpose": "source snapshot"},
    {"stage_id": "DRD-01", "stage_order_index": 10, "purpose": "prd element inventory"},
    {"stage_id": "DRD-02", "stage_order_index": 20, "purpose": "structural completion review"},
    {"stage_id": "DRD-03", "stage_order_index": 30, "purpose": "interaction closure"},
    {"stage_id": "DRD-03B", "stage_order_index": 35, "purpose": "presentation and shared patterns"},
    {"stage_id": "DRD-04", "stage_order_index": 40, "purpose": "carrier layout and layering"},
    {"stage_id": "DRD-05", "stage_order_index": 50, "purpose": "final DRD compilation"},
    {"stage_id": "DRD-06", "stage_order_index": 60, "purpose": "read-only QA"},
]


@dataclass(frozen=True)
class DriverFinding:
    code: str
    subject_id: str
    message: str


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
    if lock_path is None:
        return [
            DriverFinding(
                "P4INT-GATE-001",
                "P3_BUILD_LOCK",
                "P3 build lock path must be supplied by the execution package",
            )
        ]
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


def plan_run(
    *,
    work_dir: Path,
    adapter_result_manifest: Mapping[str, Any],
    output_dir: Path,
    target_phase: Optional[str] = None,
    target_workpack: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    run_id = _stable_id("run", [str(work_dir.resolve()), str(output_dir), str(adapter_result_manifest.get("source_sha256", ""))])
    findings: List[DriverFinding] = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    findings.extend(validate_adapter_semantic_boundary(adapter_result_manifest))
    planned_paths = [(output_dir / "run_receipt.json").as_posix()]
    receipt = build_run_receipt(
        run_id=run_id,
        adapter_result_manifest=adapter_result_manifest,
        output_dir=output_dir,
        target_phase=target_phase,
        target_workpack=target_workpack,
    )
    status = "STOPPED" if findings else "DRY_RUN" if dry_run else "RECEIPT_READY"
    return build_status_payload(
        command="run",
        status=status,
        run_id=run_id,
        written_paths=[] if dry_run or findings else planned_paths,
        findings=findings,
        exit_code=1 if findings else 0,
        planned_written_paths=planned_paths,
        run_receipt=receipt,
        document_generation_stage_order=list(DOCUMENT_GENERATION_STAGE_ORDER),
        input_hashes=_source_hashes(adapter_result_manifest),
        source_sha256=adapter_result_manifest.get("source_sha256"),
        source_section_count=len(adapter_result_manifest.get("source_section_records", [])),
        source_ref_count=len(adapter_result_manifest.get("source_ref_records", [])),
        lock_in_external_prd_run=False,
        release_in_external_prd_run=False,
        package_publish_in_external_prd_run=False,
        dry_run=dry_run,
    )


def build_run_receipt(
    *,
    run_id: str,
    adapter_result_manifest: Mapping[str, Any],
    output_dir: Path,
    target_phase: Optional[str] = None,
    target_workpack: Optional[str] = None,
) -> dict:
    source_sections = adapter_result_manifest.get("source_section_records", [])
    source_refs = adapter_result_manifest.get("source_ref_records", [])
    return {
        "artifact": "external_prd_run_receipt",
        "run_id": run_id,
        "adapter_id": adapter_result_manifest.get("adapter_id"),
        "adapter_status": adapter_result_manifest.get("status"),
        "input_kind": adapter_result_manifest.get("input_kind"),
        "source_path": adapter_result_manifest.get("source_path"),
        "source_sha256": adapter_result_manifest.get("source_sha256"),
        "source_section_count": len(source_sections),
        "source_ref_count": len(source_refs),
        "input_hashes": _source_hashes(adapter_result_manifest),
        "document_generation_stage_order": list(DOCUMENT_GENERATION_STAGE_ORDER),
        "output_dir": output_dir.as_posix(),
        "write_scope": "current_capsule/outputs/**",
        "ignored_execution_package_labels": {
            "target_phase": target_phase,
            "target_workpack": target_workpack,
            "reason": "external PRD run does not enter execution-package workpack stages",
        },
        "lock_in_external_prd_run": False,
        "release_in_external_prd_run": False,
        "package_publish_in_external_prd_run": False,
        "resume_gate_in_external_prd_run": False,
        "evidence_chain_stage_in_external_prd_run": False,
    }


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
        "resume policy is reserved for execution-package recovery and is not part of external PRD run",
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


def plan_source_preserving_drd(
    *,
    work_dir: Path,
    source_ref: Path,
    output_dir: Path,
    dry_run: bool = False,
    command_name: str = "compile-source-preserving-drd",
) -> dict:
    from drd_harness.compiler.external_prd import generate_external_prd_drd

    return generate_external_prd_drd(
        work_dir=work_dir,
        source_ref=source_ref,
        output_dir=output_dir,
        dry_run=dry_run,
        command_name=command_name,
    )


def plan_generate_drd(*, work_dir: Path, source_ref: Path, output_dir: Path, dry_run: bool = False) -> dict:
    return plan_source_preserving_drd(
        work_dir=work_dir,
        source_ref=source_ref,
        output_dir=output_dir,
        dry_run=dry_run,
        command_name="generate-drd",
    )


def plan_staged_run(*, work_dir: Path, source_ref: Path, output_dir: Path, dry_run: bool = False) -> dict:
    from drd_harness.orchestrator.external_staged_run import run_external_prd_staged

    return run_external_prd_staged(
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


def validate_output_scope(work_dir: Path, output_dir: Path) -> List[DriverFinding]:
    try:
        output_dir.resolve().relative_to(work_dir.resolve())
    except ValueError:
        return [
            DriverFinding(
                "RUN-CHECK-OUTPUT-SCOPE",
                str(output_dir),
                "output_dir must stay inside the declared work_dir",
            )
        ]
    return []


def validate_external_prd_output_scope(work_dir: Path, output_dir: Path) -> List[DriverFinding]:
    findings = validate_output_scope(work_dir, output_dir)
    if findings:
        return findings
    resolved_output = output_dir.resolve()
    allowed_roots = {
        (work_dir.resolve() / EXTERNAL_PRD_OUTPUT_ROOT).resolve(),
        (START_PACKAGE_ROOT / EXTERNAL_PRD_OUTPUT_ROOT).resolve(),
    }
    if not any(_is_relative_to(resolved_output, allowed_root) for allowed_root in allowed_roots):
        return [
            DriverFinding(
                "RUN-CHECK-OUTPUT-SCOPE",
                str(output_dir),
                "external PRD output_dir must stay inside current_capsule/outputs",
            )
        ]
    return []


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_adapter_semantic_boundary(adapter_result_manifest: Mapping[str, Any]) -> List[DriverFinding]:
    forbidden = {"product_requirements", "page_elements", "layout_rules", "business_contracts", "deduced_product_requirements"}
    present = sorted(key for key in forbidden if key in adapter_result_manifest)
    if present:
        return [
            DriverFinding(
                "RUN-CHECK-SEMANTIC-BOUNDARY",
                str(adapter_result_manifest.get("adapter_id", "adapter")),
                "adapter result contains forbidden semantic keys: " + ", ".join(present),
            )
        ]
    return []


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
