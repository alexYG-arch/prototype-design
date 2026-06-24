"""Command-line entrypoint that delegates to governed validators."""

import argparse
import json
from dataclasses import asdict
from json import JSONDecodeError
from pathlib import Path
from typing import Iterable, Optional

from drd_harness.kernel.import_boundaries import (
    find_forbidden_imports,
    find_forbidden_runtime_reads,
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


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
