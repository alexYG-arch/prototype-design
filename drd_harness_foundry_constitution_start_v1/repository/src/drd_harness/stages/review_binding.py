"""Review decision hash binding helpers."""

from typing import Mapping


def require_review_binds_subject(review_decision: Mapping[str, object], subject_hash: str) -> None:
    if review_decision.get("decision") != "APPROVED":
        raise ValueError("review decision must be APPROVED")
    if review_decision.get("subject_hash") != subject_hash:
        raise ValueError("review decision subject_hash does not match reviewed subject")
    blockers = review_decision.get("open_blockers", [])
    if blockers:
        raise ValueError("review decision has open blockers")
