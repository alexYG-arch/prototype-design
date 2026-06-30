from pathlib import Path

from drd_harness.kernel.hashline import sha256_file
from drd_harness.orchestrator.lock_rebuild import (
    build_lock_rebuild_request_packet,
    validate_request_only,
)


def test_lock_rebuild_packet_is_request_only_and_hash_bound(tmp_path: Path):
    source_lock = tmp_path / "P4_SPEC_LOCK.json"
    source_lock.write_text('{"lock_id":"P4"}\n', encoding="utf-8")
    requested = tmp_path / "P4_SPEC_LOCK.next.json"

    packet = build_lock_rebuild_request_packet(
        lock_kind="SPEC_LOCK",
        source_lock_path=source_lock,
        requested_lock_path=requested,
        candidate_inputs=[{"path": "candidate-b"}, {"path": "candidate-a"}],
        review_decision_inputs=[{"path": "review-b"}, {"path": "review-a"}],
        drift_report=[{"reason_code": "CANDIDATE_SUBJECT_HASH_CHANGED", "affected_path": "candidate-a"}],
    )

    assert packet["source_lock_sha256"] == sha256_file(source_lock)
    assert packet["candidate_inputs"] == [{"path": "candidate-a"}, {"path": "candidate-b"}]
    assert packet["review_decision_inputs"] == [{"path": "review-a"}, {"path": "review-b"}]
    assert packet["dry_run_result"]["would_create_lock"] is False
    assert packet["dry_run_result"]["would_rewrite_lock"] is False
    assert packet["required_human_authorization"] is True
    assert validate_request_only(packet) is True
    assert not requested.exists()


def test_lock_rebuild_packet_rejects_unknown_lock_kind(tmp_path: Path):
    source_lock = tmp_path / "LOCK.json"
    source_lock.write_text("{}\n", encoding="utf-8")

    try:
        build_lock_rebuild_request_packet(
            lock_kind="UNKNOWN",
            source_lock_path=source_lock,
            requested_lock_path=tmp_path / "next.json",
            candidate_inputs=[],
            review_decision_inputs=[],
            drift_report=[],
        )
    except ValueError as exc:
        assert "unsupported lock_kind" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_lock_rebuild_packet_requires_existing_source_lock(tmp_path: Path):
    try:
        build_lock_rebuild_request_packet(
            lock_kind="SPEC_LOCK",
            source_lock_path=tmp_path / "missing.json",
            requested_lock_path=tmp_path / "next.json",
            candidate_inputs=[],
            review_decision_inputs=[],
            drift_report=[],
        )
    except FileNotFoundError as exc:
        assert "source lock is required" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")
