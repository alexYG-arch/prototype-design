"""Review recovery packets for P4 resume flows."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from drd_harness.validators.spec_validator import compute_candidate_subject_hash


def build_review_recovery_packet(
    candidate_dir: Path,
    *,
    review_target_path: Optional[Path] = None,
    review_decision_path: Optional[Path] = None,
    expected_review_decision_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    manifest = _read_json(candidate_dir / "CANDIDATE_MANIFEST.json")
    current_subject_hash = compute_candidate_subject_hash(candidate_dir, manifest.get("generated_outputs", []))
    target_path = review_target_path or candidate_dir / "REVIEW_TARGET.json"
    target_status, target_findings = _review_target_status(target_path, current_subject_hash)
    decision_status, decision_findings, decision_path_value = _review_decision_status(
        review_decision_path,
        current_subject_hash,
        expected_review_decision_sha256,
    )
    findings = target_findings + decision_findings
    human_gate_required = target_status != "MATCHES_CURRENT_SUBJECT" or decision_status != "APPROVES_CURRENT_SUBJECT"
    return {
        "candidate_dir": str(candidate_dir),
        "current_subject_hash": current_subject_hash,
        "review_target_path": str(target_path),
        "review_target_status": target_status,
        "review_decision_path": decision_path_value,
        "review_decision_status": decision_status,
        "findings": findings,
        "human_gate_required": human_gate_required,
        "forbidden_actions": [
            "write_review_decision",
            "edit_review_decision",
            "approve_candidate",
            "promote_candidate",
        ],
    }


def _review_target_status(path: Path, current_subject_hash: str):
    if not path.exists():
        return "MISSING", [_finding("P4REC-REVIEW-TARGET-MISSING", str(path), "review target is missing")]
    try:
        target = _read_json(path)
    except json.JSONDecodeError as exc:
        return "INVALID", [_finding("P4REC-REVIEW-TARGET-INVALID", str(path), str(exc))]
    if target.get("review_subject_hash") != current_subject_hash:
        return "STALE", [
            _finding(
                "P4REC-REVIEW-TARGET-STALE",
                str(path),
                "review target subject hash does not match current candidate subject",
            )
        ]
    return "MATCHES_CURRENT_SUBJECT", []


def _review_decision_status(
    path: Optional[Path],
    current_subject_hash: str,
    expected_sha256: Optional[str],
):
    if path is None or not path.exists():
        return "MISSING", [
            _finding("P4REC-REVIEW-DECISION-MISSING", str(path) if path else "", "review decision is missing")
        ], None
    try:
        raw = path.read_bytes()
        review = json.loads(raw)
    except json.JSONDecodeError as exc:
        return "INVALID", [_finding("P4REC-REVIEW-DECISION-INVALID", str(path), str(exc))], str(path)
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and actual_sha256 != expected_sha256:
        return "HASH_CHANGED", [
            _finding("P4REC-REVIEW-DECISION-HASH-CHANGED", str(path), "review decision file hash changed")
        ], str(path)
    if review.get("decision") != "APPROVED":
        return "DECISION_NOT_APPROVED", [
            _finding("P4REC-REVIEW-DECISION-NOT-APPROVED", str(path), "review decision is not APPROVED")
        ], str(path)
    if review.get("subject_hash") != current_subject_hash:
        return "STALE", [
            _finding("P4REC-REVIEW-DECISION-STALE", str(path), "review decision subject hash is stale")
        ], str(path)
    return "APPROVES_CURRENT_SUBJECT", [], str(path)


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _finding(code: str, subject_id: str, message: str) -> Dict[str, str]:
    return {"code": code, "subject_id": subject_id, "message": message}
