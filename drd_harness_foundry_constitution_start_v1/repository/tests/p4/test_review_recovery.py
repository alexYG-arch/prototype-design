import json
from pathlib import Path

from drd_harness.orchestrator.review_recovery import build_review_recovery_packet
from drd_harness.validators.spec_validator import compute_candidate_subject_hash


def write_candidate(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "OUTPUT.md").write_text("# Candidate\n", encoding="utf-8")
    manifest = {
        "workpack_id": "P4-REVIEW-RECOVERY",
        "status": "CANDIDATE",
        "approval_state": "CANDIDATE",
        "seal_state": "NOT_SEALED",
        "generated_outputs": ["OUTPUT.md"],
    }
    (candidate / "CANDIDATE_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    subject = compute_candidate_subject_hash(candidate, manifest["generated_outputs"])
    (candidate / "REVIEW_TARGET.json").write_text(
        json.dumps({"review_subject_hash": subject, "review_sections": ["OUTPUT.md"]}),
        encoding="utf-8",
    )
    return candidate, subject


def test_review_recovery_accepts_matching_target_and_decision(tmp_path: Path):
    candidate, subject = write_candidate(tmp_path)
    review = {
        "decision_id": "P4-REVIEW-001",
        "subject_hash": subject,
        "decision": "APPROVED",
        "reviewer": "human-user",
        "open_blockers": [],
        "approved_sections": ["OUTPUT.md"],
    }
    review_path = candidate / "REVIEW_DECISION.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")

    packet = build_review_recovery_packet(candidate, review_decision_path=review_path)

    assert packet["review_target_status"] == "MATCHES_CURRENT_SUBJECT"
    assert packet["review_decision_status"] == "APPROVES_CURRENT_SUBJECT"
    assert packet["human_gate_required"] is False


def test_review_recovery_missing_decision_uses_nullable_path_shape(tmp_path: Path):
    candidate, _ = write_candidate(tmp_path)

    packet = build_review_recovery_packet(candidate)

    assert packet["review_decision_status"] == "MISSING"
    assert packet["review_decision_path"] is None
    assert packet["findings"]
    assert packet["human_gate_required"] is True


def test_review_recovery_detects_stale_review_decision(tmp_path: Path):
    candidate, _ = write_candidate(tmp_path)
    review_path = candidate / "REVIEW_DECISION.json"
    review_path.write_text(
        json.dumps(
            {
                "decision_id": "P4-REVIEW-001",
                "subject_hash": "a" * 64,
                "decision": "APPROVED",
                "reviewer": "human-user",
                "open_blockers": [],
                "approved_sections": ["OUTPUT.md"],
            }
        ),
        encoding="utf-8",
    )

    packet = build_review_recovery_packet(candidate, review_decision_path=review_path)

    assert packet["review_decision_status"] == "STALE"
    assert packet["human_gate_required"] is True
    assert "write_review_decision" in packet["forbidden_actions"]


def test_review_recovery_detects_review_file_hash_drift(tmp_path: Path):
    candidate, subject = write_candidate(tmp_path)
    review_path = candidate / "REVIEW_DECISION.json"
    review_path.write_text(
        json.dumps(
            {
                "decision_id": "P4-REVIEW-001",
                "subject_hash": subject,
                "decision": "APPROVED",
                "reviewer": "human-user",
                "open_blockers": [],
                "approved_sections": ["OUTPUT.md"],
            }
        ),
        encoding="utf-8",
    )

    packet = build_review_recovery_packet(
        candidate,
        review_decision_path=review_path,
        expected_review_decision_sha256="b" * 64,
    )

    assert packet["review_decision_status"] == "HASH_CHANGED"
    assert packet["human_gate_required"] is True
