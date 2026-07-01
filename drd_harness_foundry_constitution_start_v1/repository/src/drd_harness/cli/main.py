"""Command-line entrypoint that delegates to governed validators."""

import argparse
import json
from dataclasses import asdict
from json import JSONDecodeError
from pathlib import Path
from typing import Iterable, Optional

from drd_harness.adapters.markdown_prd import adapt_markdown_prd
from drd_harness.adapters.prd_harness import adapt_prd_harness_bundle
from drd_harness.kernel.import_boundaries import (
    find_forbidden_imports,
    find_forbidden_runtime_reads,
)
from drd_harness.orchestrator.program_driver import (
    build_status_payload,
    output_hashes_for_written_paths,
    plan_generate_drd,
    plan_release_request,
    plan_resume,
    plan_run,
)
from drd_harness.orchestrator.workpacks import compute_workpack_readiness_state
from drd_harness.validators.spec_validator import (
    compute_candidate_subject_hash,
    validate_candidate_only_state,
    validate_required_outputs,
    validate_review_binding,
)
from drd_harness.validators.workpack_scope import validate_workpack_readiness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="drd-harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    candidate = subparsers.add_parser("candidate-check")
    candidate.add_argument("candidate_dir")
    candidate.add_argument("--review-decision")
    candidate.set_defaults(func=_run_candidate_check)

    boundary = subparsers.add_parser("runtime-boundary-check")
    boundary.add_argument("source_root")
    boundary.set_defaults(func=_run_runtime_boundary_check)

    workpack = subparsers.add_parser("workpack-readiness")
    workpack.add_argument("workpack_json")
    workpack.set_defaults(func=_run_workpack_readiness)

    run = subparsers.add_parser("run")
    run.add_argument("--work-dir", required=True)
    run.add_argument("--adapter-id", required=True, choices=["markdown_prd_adapter", "prd_harness_adapter"])
    run.add_argument("--source-ref", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--target-phase")
    run.add_argument("--target-workpack")
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=_run_p4_run)

    generate_drd = subparsers.add_parser("generate-drd")
    generate_drd.add_argument("--work-dir", required=True)
    generate_drd.add_argument("--source-ref", required=True)
    generate_drd.add_argument("--output-dir", required=True)
    generate_drd.add_argument("--dry-run", action="store_true")
    generate_drd.set_defaults(func=_run_generate_drd)

    review = subparsers.add_parser("review")
    review.add_argument("candidate_dir")
    review.add_argument("--review-target")
    review.add_argument("--review-decision")
    review.set_defaults(func=_run_p4_review)

    resume = subparsers.add_parser("resume")
    resume.add_argument("--run-state-ref", required=True)
    resume.add_argument("--requested-resume-node", required=True)
    resume.add_argument("--dry-run", action="store_true")
    resume.set_defaults(func=_run_p4_resume)

    release = subparsers.add_parser("release")
    release.add_argument("--lock-ref", action="append", default=[])
    release.add_argument("--release-scope-ref", required=True)
    release.add_argument("--evidence-bundle-ref", required=True)
    release.add_argument("--package-target")
    release.add_argument("--dry-run", action="store_true")
    release.set_defaults(func=_run_p4_release)
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    return args.func(args)


def _run_candidate_check(args) -> int:
    candidate_dir = Path(args.candidate_dir)
    try:
        manifest = _read_json(candidate_dir / "CANDIDATE_MANIFEST.json")
    except (OSError, JSONDecodeError) as exc:
        return _emit_failure("candidate-check", "CLI-INPUT", str(candidate_dir), str(exc))
    outputs = manifest.get("generated_outputs", [])
    findings = []
    findings.extend(validate_candidate_only_state(manifest))
    output_findings = validate_required_outputs(candidate_dir, manifest)
    findings.extend(output_findings)
    subject_hash = ""
    if not findings and isinstance(outputs, list):
        try:
            subject_hash = compute_candidate_subject_hash(candidate_dir, outputs)
        except (OSError, ValueError) as exc:
            findings.append(_finding("VLOCK-CHECK-002", str(candidate_dir), str(exc)))
    if args.review_decision:
        try:
            review = _read_json(Path(args.review_decision))
        except (OSError, JSONDecodeError) as exc:
            findings.append(_finding("CLI-INPUT", str(args.review_decision), str(exc)))
            review = None
        if review is not None and not output_findings:
            findings.extend(validate_review_binding(candidate_dir, manifest, review))
    _emit(
        {
            "command": "candidate-check",
            "status": _status(findings),
            "subject_hash": subject_hash,
            "findings": _finding_dicts(findings),
        }
    )
    return 0 if not findings else 1


def _run_runtime_boundary_check(args) -> int:
    source_root = Path(args.source_root)
    findings = []
    findings.extend(find_forbidden_imports(source_root))
    findings.extend(find_forbidden_runtime_reads(source_root))
    _emit(
        {
            "command": "runtime-boundary-check",
            "status": _status(findings),
            "findings": _finding_dicts(findings),
        }
    )
    return 0 if not findings else 1


def _run_workpack_readiness(args) -> int:
    try:
        workpack = _read_json(Path(args.workpack_json))
    except (OSError, JSONDecodeError) as exc:
        return _emit_failure("workpack-readiness", "CLI-INPUT", str(args.workpack_json), str(exc))
    findings = validate_workpack_readiness(workpack)
    _emit(
        {
            "command": "workpack-readiness",
            "status": _status(findings),
            "readiness_state": compute_workpack_readiness_state(workpack),
            "findings": _finding_dicts(findings),
        }
    )
    return 0 if not findings else 1


def _run_p4_run(args) -> int:
    try:
        adapter_result = _adapt_source(args.adapter_id, Path(args.source_ref))
        payload = plan_run(
            work_dir=Path(args.work_dir),
            adapter_result_manifest=adapter_result,
            output_dir=Path(args.output_dir),
            target_phase=args.target_phase,
            target_workpack=args.target_workpack,
            dry_run=args.dry_run,
        )
        if _should_materialize_run_outputs(payload):
            try:
                _materialize_run_outputs(payload)
                payload["output_hashes"] = output_hashes_for_written_paths(payload)
            except OSError as exc:
                payload = build_status_payload(
                    command="run",
                    status="FAIL",
                    run_id=str(payload.get("run_id", "")),
                    findings=[_finding("CLI-OUTPUT", str(args.output_dir), str(exc))],
                    exit_code=1,
                    planned_written_paths=payload.get("planned_written_paths", []),
                    dry_run=args.dry_run,
                )
    except (OSError, UnicodeDecodeError, JSONDecodeError) as exc:
        payload = build_status_payload(
            command="run",
            status="FAIL",
            run_id="",
            findings=[_finding("CLI-INPUT", str(args.source_ref), str(exc))],
            exit_code=1,
        )
    _emit(payload)
    return int(payload["exit_code"])


def _run_generate_drd(args) -> int:
    payload = plan_generate_drd(
        work_dir=Path(args.work_dir),
        source_ref=Path(args.source_ref),
        output_dir=Path(args.output_dir),
        dry_run=args.dry_run,
    )
    _emit(payload)
    return int(payload["exit_code"])


def _run_p4_review(args) -> int:
    candidate_dir = Path(args.candidate_dir)
    findings = []
    try:
        manifest = _read_json(candidate_dir / "CANDIDATE_MANIFEST.json")
        outputs = manifest.get("generated_outputs", [])
        subject_hash = compute_candidate_subject_hash(candidate_dir, outputs)
    except (OSError, JSONDecodeError, ValueError) as exc:
        payload = build_status_payload(
            command="review",
            status="FAIL",
            run_id="",
            findings=[_finding("CLI-INPUT", str(candidate_dir), str(exc))],
            exit_code=1,
        )
        _emit(payload)
        return 1

    review_target_status = "NOT_SUPPLIED"
    if args.review_target:
        try:
            _read_json(Path(args.review_target))
            review_target_status = "PRESENT"
        except (OSError, JSONDecodeError) as exc:
            findings.append(_finding("CLI-INPUT", str(args.review_target), str(exc)))
            review_target_status = "INVALID"

    review_decision_binding_status = "NOT_SUPPLIED"
    if args.review_decision:
        try:
            review_decision = _read_json(Path(args.review_decision))
            binding_findings = validate_review_binding(candidate_dir, manifest, review_decision)
            findings.extend(binding_findings)
            review_decision_binding_status = "PASS" if not binding_findings else "FAIL"
        except (OSError, JSONDecodeError) as exc:
            findings.append(_finding("CLI-INPUT", str(args.review_decision), str(exc)))
            review_decision_binding_status = "INVALID"

    payload = build_status_payload(
        command="review",
        status="PASS" if not findings else "FAIL",
        run_id=f"review-{subject_hash[:16]}",
        findings=findings,
        exit_code=0 if not findings else 1,
        candidate_subject_hash=subject_hash,
        review_sections=outputs,
        review_target_status=review_target_status,
        review_decision_binding_status=review_decision_binding_status,
    )
    _emit(payload)
    return int(payload["exit_code"])


def _run_p4_resume(args) -> int:
    payload = plan_resume(
        args.run_state_ref,
        args.requested_resume_node,
        dry_run=args.dry_run,
    )
    _emit(payload)
    return int(payload["exit_code"])


def _run_p4_release(args) -> int:
    payload = plan_release_request(args.lock_ref, args.release_scope_ref, args.evidence_bundle_ref)
    _emit(payload)
    return int(payload["exit_code"])


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _adapt_source(adapter_id: str, source_ref: Path) -> dict:
    if adapter_id == "markdown_prd_adapter":
        return adapt_markdown_prd(source_ref)
    if adapter_id == "prd_harness_adapter":
        return adapt_prd_harness_bundle(source_ref)
    raise ValueError(f"unknown adapter_id: {adapter_id}")


def _should_materialize_run_outputs(payload: dict) -> bool:
    return payload.get("command") == "run" and payload.get("status") == "RECEIPT_READY" and not payload.get("dry_run")


def _materialize_run_outputs(payload: dict) -> None:
    paths_by_name = {Path(path).name: Path(path) for path in payload.get("planned_written_paths", [])}
    artifacts = _run_output_artifacts(payload)
    missing = sorted(set(artifacts) - set(paths_by_name))
    if missing:
        raise OSError(f"missing planned output path(s): {', '.join(missing)}")
    for name, artifact in artifacts.items():
        path = paths_by_name[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_output_artifacts(payload: dict) -> dict:
    return {
        "run_receipt.json": payload.get("run_receipt", {}),
    }


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _status(findings) -> str:
    return "PASS" if not findings else "FAIL"


def _finding_dicts(findings) -> list:
    return [finding if isinstance(finding, dict) else asdict(finding) for finding in findings]


def _finding(code: str, subject_id: str, message: str) -> dict:
    return {"code": code, "subject_id": subject_id, "message": message}


def _emit_failure(command: str, code: str, subject_id: str, message: str) -> int:
    _emit({"command": command, "status": "FAIL", "findings": [_finding(code, subject_id, message)]})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
