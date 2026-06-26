"""Validators for P3 source intake artifacts."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from drd_harness.stages.source_snapshot import validate_source_snapshot_manifest


ELIGIBILITY_STATES = {"eligible", "review_required", "rejected"}
SECRET_RISK_FLAGS = {"credential", "private_personal_data", "payment_detail", "third_party_restricted"}
VISUAL_MEDIA_KINDS = {"image", "screenshot", "visual_artifact"}
TEXT_MEDIA_KINDS = {"prd_markdown", "brief_markdown"}


@dataclass(frozen=True)
class SourceIntakeFinding:
    code: str
    subject_id: str
    message: str


def validate_source_intake_artifacts(
    *,
    input_register: Mapping[str, Any],
    intake_decisions: Mapping[str, Any],
    source_snapshot_manifests: Mapping[str, Any],
    source_authority_index: Mapping[str, Any],
    redaction_and_exclusion_log: Mapping[str, Any],
    downstream_handoff_manifest: Mapping[str, Any],
) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    register_rows = _rows(input_register, "sources")
    decision_rows = _rows(intake_decisions, "decisions")
    snapshot_rows = _rows(source_snapshot_manifests, "snapshots")
    authority_rows = _rows(source_authority_index, "sources")
    redaction_rows = _rows(redaction_and_exclusion_log, "records")

    registered = _by_id(register_rows, "source_item_id")
    decisions = _by_id(decision_rows, "source_item_id")
    snapshots = _by_id(snapshot_rows, "source_item_id")
    authorities = _by_id(authority_rows, "source_item_id")
    redactions_by_source = _group_by_id(redaction_rows, "source_item_id")

    findings.extend(_require_unique_ids(register_rows, "source_item_id", "SOURCEINTAKE001", "input_register"))
    findings.extend(_require_unique_ids(decision_rows, "source_item_id", "SOURCEINTAKE001", "intake_decisions"))

    for source_id, row in registered.items():
        findings.extend(_validate_register_row(source_id, row))
        decision = decisions.get(source_id)
        if decision is None:
            findings.append(SourceIntakeFinding("SOURCEINTAKE002", source_id, "registered source lacks intake decision"))
            continue
        authority = authorities.get(source_id)
        if authority is None:
            findings.append(SourceIntakeFinding("SOURCEINTAKE002", source_id, "registered source lacks authority record"))
        else:
            findings.extend(_validate_authority_record(source_id, row, authority))
        snapshot = snapshots.get(source_id)
        findings.extend(_validate_decision(source_id, row, decision, snapshot, redactions_by_source.get(source_id, [])))

    for source_id in sorted(set(decisions) - set(registered)):
        findings.append(SourceIntakeFinding("SOURCEINTAKE002", source_id, "intake decision has no registered source"))
    for source_id in sorted(set(snapshots) - set(registered)):
        findings.append(SourceIntakeFinding("SOURCEINTAKE002", source_id, "snapshot manifest has no registered source"))

    findings.extend(_validate_snapshot_rows(snapshot_rows))
    findings.extend(_validate_handoff_manifest(downstream_handoff_manifest, registered, decisions))
    return findings


def _validate_register_row(source_id: str, row: Mapping[str, Any]) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    for field in (
        "source_item_id",
        "source_path",
        "media_kind",
        "origin",
        "submitted_at",
        "source_role",
        "access_boundary",
        "permission_boundary",
    ):
        if not _text(row.get(field)):
            findings.append(SourceIntakeFinding("SOURCEINTAKE001", source_id, f"{field} must be non-empty text"))
    return findings


def _validate_authority_record(
    source_id: str, register_row: Mapping[str, Any], authority: Mapping[str, Any]
) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    if not _text(authority.get("authority_role")):
        findings.append(SourceIntakeFinding("SOURCEINTAKE003", source_id, "authority_role must be non-empty text"))
    if not _text(authority.get("conflict_policy")):
        findings.append(SourceIntakeFinding("SOURCEINTAKE003", source_id, "conflict_policy must be non-empty text"))
    if register_row.get("media_kind") in TEXT_MEDIA_KINDS:
        if authority.get("natural_language_primary") is not True:
            findings.append(
                SourceIntakeFinding(
                    "SOURCEINTAKE003",
                    source_id,
                    "text PRD or brief sources must keep natural language as primary semantics",
                )
            )
        if authority.get("inventory_role") != "index_verification_only":
            findings.append(
                SourceIntakeFinding(
                    "SOURCEINTAKE003",
                    source_id,
                    "structured inventory may only be an index and verification skeleton",
                )
            )
    return findings


def _validate_decision(
    source_id: str,
    register_row: Mapping[str, Any],
    decision: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    redaction_records: Sequence[Mapping[str, Any]],
) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    state = decision.get("state")
    downstream = decision.get("downstream_eligibility")
    media_kind = str(register_row.get("media_kind", ""))
    source_path = str(register_row.get("source_path", ""))
    risk_flags = set(_text_list(decision.get("risk_flags", [])))

    if state not in ELIGIBILITY_STATES:
        findings.append(SourceIntakeFinding("SOURCEINTAKE004", source_id, "state must be eligible, review_required, or rejected"))
    if downstream not in ELIGIBILITY_STATES:
        findings.append(
            SourceIntakeFinding(
                "SOURCEINTAKE004",
                source_id,
                "downstream_eligibility must be eligible, review_required, or rejected",
            )
        )
    if state != downstream:
        findings.append(SourceIntakeFinding("SOURCEINTAKE004", source_id, "state and downstream_eligibility must match"))

    has_snapshot = bool(snapshot)
    if state == "eligible" and not has_snapshot:
        findings.append(SourceIntakeFinding("SOURCEINTAKE005", source_id, "eligible source requires local snapshot manifest"))
    if state == "eligible" and source_path.startswith(("http://", "https://")):
        findings.append(SourceIntakeFinding("SOURCEINTAKE005", source_id, "external link metadata is not source content"))
    if state == "eligible" and media_kind in VISUAL_MEDIA_KINDS and not decision.get("extraction_evidence_refs"):
        findings.append(
            SourceIntakeFinding(
                "SOURCEINTAKE006",
                source_id,
                "visual source cannot become semantic authority before extraction evidence exists",
            )
        )
    if state == "eligible" and decision.get("requires_product_capability_expansion") is True:
        findings.append(
            SourceIntakeFinding(
                "SOURCEINTAKE007",
                source_id,
                "source requiring product capability expansion must be routed to human review",
            )
        )
    if state == "eligible" and risk_flags & SECRET_RISK_FLAGS:
        findings.append(SourceIntakeFinding("SOURCEINTAKE008", source_id, "secret-bearing source cannot be eligible"))
    if state in {"review_required", "rejected"} and not redaction_records:
        findings.append(
            SourceIntakeFinding(
                "SOURCEINTAKE009",
                source_id,
                "review_required or rejected source must have a redaction or exclusion reason record",
            )
        )
    return findings


def _validate_snapshot_rows(snapshot_rows: Sequence[Mapping[str, Any]]) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    for row in snapshot_rows:
        source_id = str(row.get("source_item_id", "SOURCE"))
        manifest = row.get("manifest")
        if not isinstance(manifest, Mapping):
            findings.append(SourceIntakeFinding("SOURCEINTAKE005", source_id, "snapshot row requires manifest mapping"))
            continue
        for finding in validate_source_snapshot_manifest(manifest):
            findings.append(SourceIntakeFinding(finding.code, source_id, finding.message))
    return findings


def _validate_handoff_manifest(
    handoff: Mapping[str, Any],
    registered: Mapping[str, Mapping[str, Any]],
    decisions: Mapping[str, Mapping[str, Any]],
) -> List[SourceIntakeFinding]:
    findings: List[SourceIntakeFinding] = []
    for field in ("stage_id", "run_id", "input_artifacts", "input_hashes", "source_prd_snapshot_hash", "output_artifacts", "output_hashes", "validator_result_hash"):
        if field not in handoff:
            findings.append(SourceIntakeFinding("SOURCEINTAKE010", "downstream_handoff_manifest", f"{field} is required"))
    for source_id, decision in decisions.items():
        if decision.get("state") == "rejected" and _mentions_source(handoff, source_id):
            findings.append(
                SourceIntakeFinding(
                    "SOURCEINTAKE011",
                    source_id,
                    "rejected source cannot be named as downstream semantic authority",
                )
            )
    return findings


def _rows(payload: Mapping[str, Any], key: str) -> List[Mapping[str, Any]]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _by_id(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, Mapping[str, Any]]:
    result: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if isinstance(value, str) and value:
            result[value] = row
    return result


def _group_by_id(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, List[Mapping[str, Any]]]:
    result: Dict[str, List[Mapping[str, Any]]] = {}
    for row in rows:
        value = row.get(key)
        if isinstance(value, str) and value:
            result.setdefault(value, []).append(row)
    return result


def _require_unique_ids(rows: Sequence[Mapping[str, Any]], key: str, code: str, subject_id: str) -> List[SourceIntakeFinding]:
    values = [row.get(key) for row in rows if isinstance(row.get(key), str)]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    return [SourceIntakeFinding(code, subject_id, "duplicate source ids: " + ", ".join(duplicates))] if duplicates else []


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _mentions_source(payload: Any, source_id: str) -> bool:
    if isinstance(payload, str):
        return source_id in payload
    if isinstance(payload, Mapping):
        return any(_mentions_source(value, source_id) for value in payload.values())
    if isinstance(payload, list):
        return any(_mentions_source(item, source_id) for item in payload)
    return False
