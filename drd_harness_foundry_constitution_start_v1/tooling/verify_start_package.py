#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "START_PACKAGE_MANIFEST.json"
ROOT_HASH_PATH = ROOT / "ROOT.sha256"
PROGRAM_STATE_PATH = ROOT / "build_program/program/PROGRAM_STATE.json"
PROGRAM_MANIFEST_PATH = ROOT / "build_program/program/PROGRAM_MANIFEST.json"

IGNORED_PARTS = {".git", ".pytest_cache", "__pycache__"}
IGNORED_SUFFIXES = {".pyc"}
STRICT_EXCLUDED_FILES = {"START_PACKAGE_MANIFEST.json", "ROOT.sha256"}

COMPLETE_MUTABLE_PREFIXES = (
    "build_program/phases/",
    "build_program/program/",
    "control/locks/",
    "current_capsule/",
    "repository/",
    "tooling/",
)
COMPLETE_MUTABLE_FILES = {
    "CODEX_START_PROMPT.md",
    "START_HERE.md",
}
COMPLETE_IMMUTABLE_PREFIXES = (
    ".agents/skills/",
    "constitution/",
    "control/schemas/",
)
COMPLETE_IMMUTABLE_FILES = {
    "AGENTS.md",
    "PACKAGE_SCOPE.md",
    "control/CLAUSE_INVENTORY.json",
    "control/CONSTITUTION_LOCK.json",
    "control/DECISION_CATALOG.json",
    "control/ERROR_CODE_CATALOG.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_package_files() -> set[str]:
    files = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix in IGNORED_SUFFIXES:
            continue
        if rel in STRICT_EXCLUDED_FILES:
            continue
        files.add(rel)
    return files


def manifest_root_hash(entries: Iterable[dict]) -> str:
    lines = "\n".join(f"{entry['path']}\0{entry['sha256']}" for entry in entries).encode("utf-8")
    return hashlib.sha256(lines).hexdigest()


def strict_start_errors(manifest: dict) -> list[str]:
    errors = []
    expected = {entry["path"] for entry in manifest["files"]}
    actual = iter_package_files()
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        if not path.exists():
            errors.append("missing: " + entry["path"])
        elif sha256(path) != entry["sha256"]:
            errors.append("hash mismatch: " + entry["path"])
    for rel in sorted(actual - expected):
        errors.append("untracked: " + rel)
    for rel in sorted(expected - actual):
        errors.append("manifest-only: " + rel)
    root = manifest_root_hash(manifest["files"])
    recorded_root = ROOT_HASH_PATH.read_text(encoding="utf-8").strip() if ROOT_HASH_PATH.exists() else ""
    if root != manifest.get("root_sha256") or root != recorded_root:
        errors.append("root hash mismatch")
    return errors


def complete_state_errors(manifest: dict) -> list[str]:
    errors = []
    state = load_json(PROGRAM_STATE_PATH)
    program = load_json(PROGRAM_MANIFEST_PATH)
    manifest_entries = {entry["path"]: entry for entry in manifest["files"]}
    actual = iter_package_files()

    for rel, entry in sorted(manifest_entries.items()):
        if not _is_complete_immutable(rel):
            continue
        path = ROOT / rel
        if not path.exists():
            errors.append("missing immutable: " + rel)
        elif sha256(path) != entry["sha256"]:
            errors.append("immutable hash mismatch: " + rel)

    for rel in sorted(actual - set(manifest_entries)):
        if not _is_complete_mutable(rel):
            errors.append("unexpected complete-package file: " + rel)

    if program.get("status") != "COMPLETE":
        errors.append("program manifest status must be COMPLETE")
    if state.get("program_state") != "COMPLETE":
        errors.append("program state must be COMPLETE")
    if state.get("current_phase") != "P4" or state.get("current_lane") != "PROGRAM_CLOSURE":
        errors.append("program must be parked at P4 PROGRAM_CLOSURE")
    if state.get("target") != "DRD_HARNESS_RELEASE_LOCK":
        errors.append("program target must be DRD_HARNESS_RELEASE_LOCK")
    if state.get("target_lock_state") != "CREATED_APPROVED_COMMITTED_AND_PUSHED":
        errors.append("target lock state must be CREATED_APPROVED_COMMITTED_AND_PUSHED")

    for phase in ("P1", "P2", "P3", "P4"):
        if state.get("phases", {}).get(phase, {}).get("status") != "COMPLETE":
            errors.append(f"{phase} must be COMPLETE")
        manifest_phase = next((item for item in program.get("phases", []) if item.get("id") == phase), None)
        if not manifest_phase or manifest_phase.get("status") != "COMPLETE":
            errors.append(f"{phase} manifest status must be COMPLETE")

    for phase, data in sorted(state.get("phases", {}).items()):
        errors.extend(_lock_ref_errors(f"{phase}.spec_lock", data.get("spec_lock", {})))
        errors.extend(_lock_ref_errors(f"{phase}.build_lock", data.get("build_lock", {})))
        if phase == "P4":
            errors.extend(_lock_ref_errors("P4.release_lock", data.get("release_lock", {})))
    errors.extend(_lock_ref_errors("release_lock", state.get("release_lock", {})))
    errors.extend(_lock_ref_errors("final_release_lock", program.get("final_release_lock", {})))
    return errors


def _is_complete_immutable(rel: str) -> bool:
    return rel in COMPLETE_IMMUTABLE_FILES or any(rel.startswith(prefix) for prefix in COMPLETE_IMMUTABLE_PREFIXES)


def _is_complete_mutable(rel: str) -> bool:
    return rel in COMPLETE_MUTABLE_FILES or any(rel.startswith(prefix) for prefix in COMPLETE_MUTABLE_PREFIXES)


def _lock_ref_errors(label: str, ref: dict) -> list[str]:
    if not isinstance(ref, dict) or not ref.get("path") or not ref.get("sha256"):
        return [f"{label} lock ref incomplete"]
    path = ROOT / ref["path"]
    if not path.exists():
        return [f"{label} lock missing: {ref['path']}"]
    errors = []
    if sha256(path) != ref["sha256"]:
        errors.append(f"{label} lock sha256 mismatch: {ref['path']}")
    try:
        lock = load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{label} lock invalid JSON: {exc}"]
    if ref.get("root_sha256") and lock.get("root_sha256") != ref["root_sha256"]:
        errors.append(f"{label} root_sha256 mismatch: {ref['path']}")
    return errors


def selected_mode(requested: str) -> str:
    if requested != "auto":
        return requested
    if PROGRAM_STATE_PATH.exists():
        try:
            if load_json(PROGRAM_STATE_PATH).get("program_state") == "COMPLETE":
                return "complete"
        except json.JSONDecodeError:
            pass
    return "start"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["auto", "start", "complete"], default="auto")
    args = parser.parse_args()

    manifest = load_json(MANIFEST_PATH)
    mode = selected_mode(args.mode)
    errors = strict_start_errors(manifest) if mode == "start" else complete_state_errors(manifest)
    if errors:
        print("\n".join(errors))
        return 1
    if mode == "start":
        print(f"START PACKAGE INTEGRITY: PASS ({len(manifest['files'])} files)")
    else:
        print("COMPLETE PACKAGE INTEGRITY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
