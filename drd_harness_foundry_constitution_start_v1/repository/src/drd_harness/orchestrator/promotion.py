"""Promotion audit helpers."""

from dataclasses import asdict, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from drd_harness.validators.phase_gate import PhaseGateFinding, validate_promotion_readiness


@dataclass(frozen=True)
class PromotionAudit:
    promotion_id: str
    subject_id: str
    subject_hash: str
    validator_result_hashes: List[str]
    review_decision_hash: str
    upstream_hashes: List[str]
    output_state: str
    invalidation_effects: List[str]
    created_by_runtime: str

    def to_dict(self) -> dict:
        return asdict(self)


def create_promotion_audit(
    promotion_id: str,
    subject_id: str,
    subject_hash: str,
    validator_result_hashes: List[str],
    review_decision_hash: str,
    upstream_hashes: List[str],
    output_state: str = "PROMOTION_READY",
    invalidation_effects: Optional[List[str]] = None,
    created_by_runtime: str = "python",
) -> PromotionAudit:
    return PromotionAudit(
        promotion_id=promotion_id,
        subject_id=subject_id,
        subject_hash=subject_hash,
        validator_result_hashes=validator_result_hashes,
        review_decision_hash=review_decision_hash,
        upstream_hashes=upstream_hashes,
        output_state=output_state,
        invalidation_effects=invalidation_effects or [],
        created_by_runtime=created_by_runtime,
    )


def validate_promotion_audit(audit: PromotionAudit) -> List[PhaseGateFinding]:
    findings: List[PhaseGateFinding] = []
    for field_name in (
        "promotion_id",
        "subject_id",
        "subject_hash",
        "review_decision_hash",
        "output_state",
        "created_by_runtime",
    ):
        if not getattr(audit, field_name):
            findings.append(PhaseGateFinding("VLOCK-CHECK-007", audit.promotion_id or "promotion", f"{field_name} is required"))
    for field_name in ("subject_hash", "review_decision_hash"):
        if not _is_hash(getattr(audit, field_name)):
            findings.append(PhaseGateFinding("VLOCK-CHECK-007", audit.promotion_id, f"{field_name} must be sha256"))
    for field_name in ("validator_result_hashes", "upstream_hashes"):
        values = getattr(audit, field_name)
        if not values:
            findings.append(PhaseGateFinding("VLOCK-CHECK-007", audit.promotion_id, f"{field_name} is required"))
        for value in values:
            if not _is_hash(value):
                findings.append(PhaseGateFinding("VLOCK-CHECK-007", audit.promotion_id, f"{field_name} entries must be sha256"))
    if audit.created_by_runtime != "python":
        findings.append(PhaseGateFinding("VLOCK-CHECK-007", audit.promotion_id, "promotion audit must be python-created"))
    return findings


def promotion_readiness_findings(
    validation_results: Iterable[Mapping[str, Any]],
    review_decision: Mapping[str, Any],
    subject_hash: str,
    upstream_bindings_present: bool,
    forbidden_write_paths: Iterable[str],
    invalidation_state: str,
) -> List[PhaseGateFinding]:
    return validate_promotion_readiness(
        validation_results,
        review_decision,
        subject_hash,
        upstream_bindings_present,
        forbidden_write_paths,
        invalidation_state,
    )


def _is_hash(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
