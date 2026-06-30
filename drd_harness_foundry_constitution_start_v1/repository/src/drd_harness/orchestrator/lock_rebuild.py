"""P4 lock rebuild request packets.

This module prepares dry-run request evidence only. It never creates, rewrites,
deletes, or publishes locks.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from drd_harness.kernel.hashline import sha256_file, sha256_text


LOCK_KINDS = {"SPEC_LOCK", "BUILD_LOCK", "RELEASE_LOCK"}


def build_lock_rebuild_request_packet(
    *,
    lock_kind: str,
    source_lock_path: Path,
    requested_lock_path: Path,
    candidate_inputs: Iterable[Mapping[str, Any]],
    review_decision_inputs: Iterable[Mapping[str, Any]],
    drift_report: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    if lock_kind not in LOCK_KINDS:
        raise ValueError(f"unsupported lock_kind: {lock_kind}")
    if not source_lock_path.is_file():
        raise FileNotFoundError(f"source lock is required for rebuild evidence: {source_lock_path}")

    candidate_rows = _sorted_rows(candidate_inputs)
    review_rows = _sorted_rows(review_decision_inputs)
    drift_rows = _sorted_rows(drift_report)
    source_sha256 = sha256_file(source_lock_path)
    request_id = "lock-rebuild-" + sha256_text(
        json.dumps(
            {
                "lock_kind": lock_kind,
                "source_lock_path": str(source_lock_path),
                "requested_lock_path": str(requested_lock_path),
                "candidate_inputs": candidate_rows,
                "review_decision_inputs": review_rows,
                "drift_report": drift_rows,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )[:16]
    return {
        "request_id": request_id,
        "lock_kind": lock_kind,
        "source_lock_path": str(source_lock_path),
        "source_lock_sha256": source_sha256,
        "requested_lock_path": str(requested_lock_path),
        "candidate_inputs": candidate_rows,
        "review_decision_inputs": review_rows,
        "drift_report": drift_rows,
        "dry_run_result": {
            "status": "REQUEST_ONLY",
            "would_create_lock": False,
            "would_rewrite_lock": False,
            "would_delete_lock": False,
            "would_publish_package": False,
            "requested_lock_exists": requested_lock_path.exists(),
        },
        "required_human_authorization": True,
        "forbidden_without_authorization": [
            "create_lock",
            "rewrite_lock",
            "delete_lock",
            "publish_package",
        ],
    }


def validate_request_only(packet: Mapping[str, Any]) -> bool:
    dry_run = packet.get("dry_run_result", {})
    return (
        packet.get("required_human_authorization") is True
        and dry_run.get("would_create_lock") is False
        and dry_run.get("would_rewrite_lock") is False
        and dry_run.get("would_delete_lock") is False
        and dry_run.get("would_publish_package") is False
    )


def _sorted_rows(rows: Iterable[Mapping[str, Any]]) -> list:
    normalized = [dict(row) for row in rows]
    return sorted(normalized, key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))
