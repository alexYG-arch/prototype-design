import pytest

from drd_harness.stages.review_binding import require_review_binds_subject


def test_review_decision_binds_reviewed_subject_hash():
    require_review_binds_subject(
        {
            "decision": "APPROVED",
            "subject_hash": "a" * 64,
            "open_blockers": [],
        },
        "a" * 64,
    )


def test_review_decision_rejects_subject_hash_mismatch():
    with pytest.raises(ValueError, match="subject_hash"):
        require_review_binds_subject(
            {
                "decision": "APPROVED",
                "subject_hash": "a" * 64,
                "open_blockers": [],
            },
            "b" * 64,
        )


def test_review_decision_rejects_open_blockers():
    with pytest.raises(ValueError, match="open blockers"):
        require_review_binds_subject(
            {
                "decision": "APPROVED",
                "subject_hash": "a" * 64,
                "open_blockers": ["missing validation"],
            },
            "a" * 64,
        )
