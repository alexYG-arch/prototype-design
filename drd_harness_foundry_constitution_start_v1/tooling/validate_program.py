#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from _common import ROOT, load_json, sha256


PROGRAM_MANIFEST = ROOT / "build_program/program/PROGRAM_MANIFEST.json"
PROGRAM_STATE = ROOT / "build_program/program/PROGRAM_STATE.json"


def validate_start(manifest: dict, state: dict) -> list[str]:
    errors = []
    ids = [phase["id"] for phase in manifest["phases"]]
    if ids != ["P1", "P2", "P3", "P4"]:
        errors.append(f"phase order invalid: {ids}")
    if state["current_workpack"] != "P1-SPEC-00":
        errors.append("current workpack must be P1-SPEC-00")
    if state["phases"]["P1"]["status"] != "ACTIVE":
        errors.append("P1 must be ACTIVE")
    for phase in ["P2", "P3", "P4"]:
        if state["phases"][phase]["status"] != "WAITING_UPSTREAM_LOCK":
            errors.append(f"{phase} must wait for upstream lock")
    errors.extend(_phase_manifest_errors(ids))
    return errors


def validate_complete(manifest: dict, state: dict) -> list[str]:
    errors = []
    ids = [phase["id"] for phase in manifest.get("phases", [])]
    if ids != ["P1", "P2", "P3", "P4"]:
        errors.append(f"phase order invalid: {ids}")
    if manifest.get("status") != "COMPLETE":
        errors.append("program manifest status must be COMPLETE")
    if state.get("program_state") != "COMPLETE":
        errors.append("program state must be COMPLETE")
    if state.get("current_phase") != "P4":
        errors.append("current phase must be P4")
    if state.get("current_lane") != "PROGRAM_CLOSURE":
        errors.append("current lane must be PROGRAM_CLOSURE")
    if state.get("current_workpack") != "P4-PROGRAM-CLOSURE-STATUS-SYNC":
        errors.append("current workpack must be P4-PROGRAM-CLOSURE-STATUS-SYNC")
    if state.get("target") != "DRD_HARNESS_RELEASE_LOCK":
        errors.append("target must be DRD_HARNESS_RELEASE_LOCK")
    if state.get("target_lock_state") != "CREATED_APPROVED_COMMITTED_AND_PUSHED":
        errors.append("target lock state must be CREATED_APPROVED_COMMITTED_AND_PUSHED")

    for phase in ids:
        manifest_phase = next(item for item in manifest["phases"] if item["id"] == phase)
        if manifest_phase.get("status") != "COMPLETE":
            errors.append(f"{phase} manifest status must be COMPLETE")
        if state.get("phases", {}).get(phase, {}).get("status") != "COMPLETE":
            errors.append(f"{phase} state status must be COMPLETE")

    errors.extend(_phase_manifest_errors(ids))
    for phase, phase_state in sorted(state.get("phases", {}).items()):
        errors.extend(_lock_errors(f"{phase}.spec_lock", phase_state.get("spec_lock", {})))
        errors.extend(_lock_errors(f"{phase}.build_lock", phase_state.get("build_lock", {})))
        if phase == "P4":
            errors.extend(_lock_errors("P4.release_lock", phase_state.get("release_lock", {})))
    errors.extend(_lock_errors("release_lock", state.get("release_lock", {})))
    errors.extend(_lock_errors("final_release_lock", manifest.get("final_release_lock", {})))
    return errors


def _phase_manifest_errors(ids: list[str]) -> list[str]:
    errors = []
    for phase in ids:
        if not (ROOT / f"build_program/phases/{phase}/PHASE_MANIFEST.json").exists():
            errors.append(f"missing phase manifest {phase}")
    return errors


def _lock_errors(label: str, ref: dict) -> list[str]:
    if not isinstance(ref, dict) or not ref.get("path") or not ref.get("sha256"):
        return [f"{label} lock ref incomplete"]
    path = ROOT / ref["path"]
    if not path.exists():
        return [f"{label} lock missing: {ref['path']}"]
    errors = []
    if sha256(path) != ref["sha256"]:
        errors.append(f"{label} lock sha256 mismatch: {ref['path']}")
    lock = load_json(path)
    if ref.get("root_sha256") and lock.get("root_sha256") != ref["root_sha256"]:
        errors.append(f"{label} root_sha256 mismatch: {ref['path']}")
    return errors


def selected_mode(requested: str, state: dict) -> str:
    if requested != "auto":
        return requested
    return "complete" if state.get("program_state") == "COMPLETE" else "start"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["auto", "start", "complete"], default="auto")
    args = parser.parse_args()
    manifest = load_json(PROGRAM_MANIFEST)
    state = load_json(PROGRAM_STATE)
    mode = selected_mode(args.mode, state)
    errors = validate_start(manifest, state) if mode == "start" else validate_complete(manifest, state)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PROGRAM VALIDATION: PASS ({mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
