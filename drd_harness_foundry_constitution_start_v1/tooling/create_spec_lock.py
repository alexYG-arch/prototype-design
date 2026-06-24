#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
import re
import sys
import tempfile
from pathlib import Path

from _common import ROOT, load_json, sha256


HASH_RE = re.compile(r"^[a-f0-9]{64}$")
PHASES = {"P1", "P2", "P3", "P4"}


class LockCreationError(Exception):
    pass


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def rel_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LockCreationError(message)


def require_hash(value: str, field: str) -> None:
    require(isinstance(value, str) and HASH_RE.match(value) is not None, f"invalid hash field: {field}")


def load_json_file(path: Path, label: str):
    require(path.exists(), f"missing {label}: {rel_repo(path)}")
    require(path.is_file(), f"{label} is not a file: {rel_repo(path)}")
    try:
        return load_json(path)
    except Exception as exc:
        raise LockCreationError(f"invalid json {label}: {rel_repo(path)}: {exc}") from exc


def candidate_dir(phase: str, spec_part: str) -> Path:
    return ROOT / "build_program" / "phases" / phase / "candidates" / spec_part


def candidate_subject(candidate: Path):
    manifest_path = candidate / "CANDIDATE_MANIFEST.json"
    manifest = load_json_file(manifest_path, "candidate manifest")
    outputs = manifest.get("generated_outputs")
    require(isinstance(outputs, list) and outputs, f"generated_outputs missing: {rel_repo(manifest_path)}")

    rows = []
    output_entries = []
    for rel in outputs:
        require(isinstance(rel, str) and rel, f"invalid generated output path in {rel_repo(manifest_path)}")
        path = candidate / rel
        require(path.exists() and path.is_file(), f"missing generated output: {rel_repo(path)}")
        digest = sha256(path)
        rows.append(f"{rel}\0{digest}")
        output_entries.append({"path": rel_repo(path), "sha256": digest})

    return sha256_text("\n".join(rows)), manifest, output_entries


def validate_candidate_binding(phase: str, approved_input: dict):
    spec_part = approved_input.get("spec_part")
    require(isinstance(spec_part, str) and spec_part, "approved input missing spec_part")
    subject_expected = approved_input.get("subject_hash")
    require_hash(subject_expected, f"{spec_part}.subject_hash")

    candidate = candidate_dir(phase, spec_part)
    subject_current, manifest, outputs = candidate_subject(candidate)
    require(subject_current == subject_expected, f"subject hash mismatch for {spec_part}")
    require(manifest.get("approval_state") == "APPROVED_BY_HUMAN", f"candidate is not human-approved: {spec_part}")

    review_rel = manifest.get("review_decision") or "REVIEW_DECISION.json"
    require(isinstance(review_rel, str) and review_rel, f"missing review_decision in manifest: {spec_part}")
    review_path = candidate / review_rel
    review = load_json_file(review_path, "review decision")
    require(review.get("decision") == "APPROVED", f"review decision is not APPROVED: {spec_part}")
    require(review.get("subject_hash") == subject_current, f"review subject hash mismatch: {spec_part}")

    expected_decision_id = approved_input.get("review_decision_id")
    if expected_decision_id is not None:
        require(review.get("decision_id") == expected_decision_id, f"review decision id mismatch: {spec_part}")

    return {
        "entry_type": "approved_spec_candidate",
        "spec_part": spec_part,
        "candidate_path": rel_repo(candidate),
        "subject_hash": subject_current,
        "review_decision": {
            "path": rel_repo(review_path),
            "decision_id": review.get("decision_id"),
            "sha256": sha256(review_path),
        },
        "generated_outputs": outputs,
    }


def phase_root(file_entries: list) -> str:
    rows = [f"{entry['spec_part']}\0{entry['subject_hash']}" for entry in file_entries]
    return sha256_text("\n".join(rows))


def review_file_root(file_entries: list) -> str:
    rows = [
        f"{entry['spec_part']}\0{entry['review_decision']['sha256']}"
        for entry in file_entries
    ]
    return sha256_text("\n".join(rows))


def validate_schema_minimum(lock: dict, schema: dict) -> None:
    required = schema.get("required", [])
    for field in required:
        require(field in lock, f"schema required field missing: {field}")

    phase_enum = schema.get("properties", {}).get("phase", {}).get("enum")
    if phase_enum:
        require(lock.get("phase") in phase_enum, f"schema phase enum mismatch: {lock.get('phase')}")

    for field in ("root_sha256", "review_decision_hash"):
        require_hash(lock.get(field), field)

    require(isinstance(lock.get("files"), list), "schema field files must be a list")


def validate_source_candidate(bundle: dict) -> dict:
    source_candidate = repo_path(bundle.get("source_candidate", ""))
    source_review = repo_path(bundle.get("source_candidate_review_decision", ""))
    source_subject, source_manifest, source_outputs = candidate_subject(source_candidate)

    require(source_subject == bundle.get("phase_readiness_subject_hash"), "phase readiness subject hash mismatch")
    require(source_manifest.get("approval_state") == "APPROVED_BY_HUMAN", "phase readiness candidate is not human-approved")
    require(sha256(source_review) == bundle.get("phase_review_decision_file_hash"), "phase review decision file hash mismatch")

    source_review_json = load_json_file(source_review, "phase review decision")
    require(source_review_json.get("decision") == "APPROVED", "phase review decision is not APPROVED")
    require(source_review_json.get("subject_hash") == source_subject, "phase review decision subject hash mismatch")

    return {
        "candidate_path": rel_repo(source_candidate),
        "subject_hash": source_subject,
        "review_decision_path": rel_repo(source_review),
        "review_decision_hash": sha256(source_review),
        "generated_outputs": source_outputs,
    }


def build_lock(phase: str, bundle_path: Path) -> dict:
    bundle = load_json_file(bundle_path, "input bundle")
    require(bundle.get("phase") == phase, "input bundle phase mismatch")
    require(phase in PHASES, f"unsupported phase: {phase}")
    require(bundle.get("not_a_spec_lock") is True, "input bundle must be marked not_a_spec_lock")

    schema_info = bundle.get("canonical_spec_lock_schema", {})
    schema_path = repo_path(schema_info.get("path", ""))
    schema = load_json_file(schema_path, "spec lock schema")
    schema_hash = sha256(schema_path)
    require_hash(schema_info.get("sha256"), "canonical_spec_lock_schema.sha256")
    require(schema_hash == schema_info.get("sha256"), "spec lock schema hash mismatch")

    source = validate_source_candidate(bundle)
    fields = bundle.get("proposed_canonical_lock_fields", {})
    require(fields.get("phase") == phase, "proposed lock phase mismatch")
    require_hash(fields.get("root_sha256"), "proposed_canonical_lock_fields.root_sha256")
    require_hash(fields.get("review_decision_hash"), "proposed_canonical_lock_fields.review_decision_hash")
    require_hash(fields.get("review_decision_file_root_sha256"), "proposed_canonical_lock_fields.review_decision_file_root_sha256")

    approved_inputs = bundle.get("approved_spec_inputs")
    require(isinstance(approved_inputs, list) and approved_inputs, "approved_spec_inputs missing")
    file_entries = [validate_candidate_binding(phase, item) for item in approved_inputs]

    computed_phase_root = phase_root(file_entries)
    computed_review_file_root = review_file_root(file_entries)
    require(computed_phase_root == fields.get("root_sha256"), "computed phase root mismatch")
    require(computed_review_file_root == fields.get("review_decision_file_root_sha256"), "computed review decision file root mismatch")
    require(fields.get("review_decision_hash") == bundle.get("phase_review_decision_file_hash"), "phase review hash mismatch")

    lock = {
        "lock_id": fields.get("lock_id"),
        "phase": phase,
        "root_sha256": computed_phase_root,
        "files": file_entries,
        "review_decision_hash": fields.get("review_decision_hash"),
        "review_decision_file_root_sha256": computed_review_file_root,
        "source_candidate": source,
        "schema": {
            "path": rel_repo(schema_path),
            "sha256": schema_hash,
        },
        "input_bundle": {
            "path": rel_repo(bundle_path),
            "sha256": sha256(bundle_path),
        },
        "created_by_runtime": {
            "kind": "python",
            "version": platform.python_version(),
        },
        "created_by_tool": {
            "path": rel_repo(Path(__file__)),
            "sha256": sha256(Path(__file__)),
        },
        "root_algorithm": "sha256(join_lines(spec_part + NUL + subject_hash))",
        "review_file_root_algorithm": "sha256(join_lines(spec_part + NUL + review_decision_file_sha256))",
        "validation": {
            "candidate_subject_bindings": "PASS",
            "phase_review_binding": "PASS",
            "schema_minimum": "PASS",
        },
    }

    validate_schema_minimum(lock, schema)
    return lock


def write_json_new(path: Path, payload: dict) -> None:
    require(not path.exists(), f"output already exists: {rel_repo(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            tmp_name = handle.name
            json.dump(payload, handle, ensure_ascii=True, indent=2)
            handle.write("\n")
        os.link(tmp_name, path)
    except FileExistsError as exc:
        raise LockCreationError(f"output already exists: {rel_repo(path)}") from exc
    finally:
        if tmp_name and Path(tmp_name).exists():
            Path(tmp_name).unlink()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a canonical SPEC_LOCK from approved Candidate inputs.")
    parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    parser.add_argument("--input-bundle", required=True, help="Path to SPEC_LOCK_INPUT_BUNDLE.json.")
    parser.add_argument("--output", help="Output path for the canonical SPEC_LOCK JSON. Must not already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Print the lock JSON to stdout and do not write a file.")
    args = parser.parse_args(argv)
    if args.dry_run and args.output:
        parser.error("--dry-run cannot be combined with --output")
    if not args.dry_run and not args.output:
        parser.error("one of --dry-run or --output is required")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        bundle_path = repo_path(args.input_bundle)
        lock = build_lock(args.phase, bundle_path)
        if args.dry_run:
            json.dump(lock, sys.stdout, ensure_ascii=True, indent=2)
            sys.stdout.write("\n")
        if args.output:
            write_json_new(repo_path(args.output), lock)
            print(f"SPEC_LOCK CREATED: {args.output}")
        return 0
    except LockCreationError as exc:
        print(f"SPEC_LOCK CREATION FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
