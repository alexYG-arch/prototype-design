"""P4 v3.1 migration coverage validation."""

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_text


REQUIRED_REPORT_FIELDS = [
    "coverage_id",
    "source_version",
    "target_version",
    "capability_rows",
    "coverage_summary",
    "blocked_rows",
    "human_review_required",
    "report_hash",
]
REQUIRED_ROW_FIELDS = [
    "legacy_capability_id",
    "legacy_capability_name",
    "legacy_source_ref",
    "target_status",
    "target_evidence_ref",
    "rationale",
    "review_required",
]
ALLOWED_TARGET_STATUS = {
    "MIGRATED",
    "REPLACED_BY_LOCKED_CAPABILITY",
    "DROPPED_WITH_RATIONALE",
    "BLOCKED_REQUIRES_HUMAN_REVIEW",
}
REQUIRED_SUMMARY_FIELDS = [
    "total_legacy_capabilities",
    "migrated_count",
    "replaced_count",
    "dropped_count",
    "blocked_count",
    "unmapped_count",
    "release_blocking",
]
FORBIDDEN_SEMANTIC_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


@dataclass(frozen=True)
class MigrationFinding:
    code: str
    subject_id: str
    message: str


def compute_migration_report_hash(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("report_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)


def build_migration_coverage_report(
    *,
    coverage_id: str,
    source_version: str,
    target_version: str,
    capability_rows: Iterable[Mapping[str, Any]],
) -> dict:
    rows = sorted((dict(row) for row in capability_rows), key=lambda row: str(row.get("legacy_capability_id", "")))
    blocked_rows = [
        str(row.get("legacy_capability_id", ""))
        for row in rows
        if row.get("target_status") == "BLOCKED_REQUIRES_HUMAN_REVIEW"
    ]
    summary = _coverage_summary(rows)
    report = {
        "coverage_id": coverage_id,
        "source_version": source_version,
        "target_version": target_version,
        "capability_rows": rows,
        "coverage_summary": summary,
        "blocked_rows": blocked_rows,
        "human_review_required": bool(blocked_rows),
    }
    report["report_hash"] = compute_migration_report_hash(report)
    return report


def validate_migration_coverage_report(report: Mapping[str, Any]) -> List[MigrationFinding]:
    findings: List[MigrationFinding] = []
    subject = str(report.get("coverage_id", "migration_coverage_report"))
    findings.extend(_required_field_findings(report, REQUIRED_REPORT_FIELDS, subject, "P4MIG-CHECK-001"))
    findings.extend(_semantic_key_findings(report, subject))

    rows = report.get("capability_rows", [])
    if not isinstance(rows, list):
        findings.append(MigrationFinding("P4MIG-CHECK-002", subject, "capability_rows must be a list"))
        rows = []
    findings.extend(_row_findings(rows))
    findings.extend(_duplicate_row_findings(rows))

    summary = report.get("coverage_summary", {})
    if not isinstance(summary, Mapping):
        findings.append(MigrationFinding("P4MIG-CHECK-003", subject, "coverage_summary must be an object"))
        summary = {}
    findings.extend(_summary_findings(summary, rows, subject))

    blocked_ids = sorted(str(row.get("legacy_capability_id", "")) for row in rows if row.get("target_status") == "BLOCKED_REQUIRES_HUMAN_REVIEW")
    blocked_rows = report.get("blocked_rows", [])
    if not isinstance(blocked_rows, list):
        findings.append(MigrationFinding("P4MIG-CHECK-004", subject, "blocked_rows must be a list"))
        declared_blocked: List[str] = []
    else:
        declared_blocked = sorted(str(item) for item in blocked_rows)
    if declared_blocked != blocked_ids:
        findings.append(MigrationFinding("P4MIG-CHECK-004", subject, "blocked_rows must match blocked capability ids"))
    if blocked_ids and report.get("human_review_required") is not True:
        findings.append(MigrationFinding("P4MIG-CHECK-005", subject, "blocked rows require human_review_required=true"))
    if not _is_sha256(report.get("report_hash")):
        findings.append(MigrationFinding("P4MIG-CHECK-006", subject, "report_hash must be sha256"))
    elif report.get("report_hash") != compute_migration_report_hash(report):
        findings.append(MigrationFinding("P4MIG-CHECK-006", subject, "report_hash mismatch"))
    return sorted(findings, key=lambda item: (item.code, item.subject_id, item.message))


def _coverage_summary(rows: Sequence[Mapping[str, Any]]) -> dict:
    migrated = sum(1 for row in rows if row.get("target_status") == "MIGRATED")
    replaced = sum(1 for row in rows if row.get("target_status") == "REPLACED_BY_LOCKED_CAPABILITY")
    dropped = sum(1 for row in rows if row.get("target_status") == "DROPPED_WITH_RATIONALE")
    blocked = sum(1 for row in rows if row.get("target_status") == "BLOCKED_REQUIRES_HUMAN_REVIEW")
    unmapped = sum(1 for row in rows if row.get("target_status") not in ALLOWED_TARGET_STATUS)
    release_blocking = (
        blocked > 0
        or unmapped > 0
        or any(not row.get("target_evidence_ref") for row in rows)
        or any(row.get("target_status") == "DROPPED_WITH_RATIONALE" and not row.get("rationale") for row in rows)
    )
    return {
        "total_legacy_capabilities": len(rows),
        "migrated_count": migrated,
        "replaced_count": replaced,
        "dropped_count": dropped,
        "blocked_count": blocked,
        "unmapped_count": unmapped,
        "release_blocking": release_blocking,
    }


def _required_field_findings(report: Mapping[str, Any], fields: Sequence[str], subject: str, code: str) -> List[MigrationFinding]:
    return [MigrationFinding(code, subject, f"{field} is required") for field in fields if field not in report]


def _row_findings(rows: Sequence[object]) -> List[MigrationFinding]:
    findings: List[MigrationFinding] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(MigrationFinding("P4MIG-CHECK-002", str(index), "capability row must be an object"))
            continue
        subject = str(row.get("legacy_capability_id", index))
        findings.extend(_required_field_findings(row, REQUIRED_ROW_FIELDS, subject, "P4MIG-CHECK-002"))
        findings.extend(_semantic_key_findings(row, subject))
        if row.get("target_status") not in ALLOWED_TARGET_STATUS:
            findings.append(MigrationFinding("P4MIG-CHECK-007", subject, "target_status is unsupported"))
        if not row.get("target_evidence_ref"):
            findings.append(MigrationFinding("P4MIG-CHECK-008", subject, "target_evidence_ref is required"))
        if row.get("target_status") == "DROPPED_WITH_RATIONALE" and not row.get("rationale"):
            findings.append(MigrationFinding("P4MIG-CHECK-009", subject, "dropped rows require rationale"))
        if row.get("target_status") == "BLOCKED_REQUIRES_HUMAN_REVIEW" and row.get("review_required") is not True:
            findings.append(MigrationFinding("P4MIG-CHECK-010", subject, "blocked rows require review_required=true"))
    return findings


def _duplicate_row_findings(rows: Sequence[object]) -> List[MigrationFinding]:
    ids = [str(row.get("legacy_capability_id")) for row in rows if isinstance(row, Mapping) and row.get("legacy_capability_id")]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    return [MigrationFinding("P4MIG-CHECK-011", item, "duplicate legacy_capability_id") for item in duplicates]


def _summary_findings(summary: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], subject: str) -> List[MigrationFinding]:
    findings = _required_field_findings(summary, REQUIRED_SUMMARY_FIELDS, subject, "P4MIG-CHECK-003")
    expected = _coverage_summary(rows)
    for key, value in expected.items():
        if key in summary and summary.get(key) != value:
            findings.append(MigrationFinding("P4MIG-CHECK-003", subject, f"{key} does not match capability rows"))
    return findings


def _semantic_key_findings(report: Mapping[str, Any], subject: str) -> List[MigrationFinding]:
    return [
        MigrationFinding("P4MIG-SEMANTIC-BOUNDARY", subject, f"{key} is outside migration coverage authority")
        for key in sorted(FORBIDDEN_SEMANTIC_KEYS & set(report))
    ]


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def finding_dicts(findings: Iterable[MigrationFinding | Mapping[str, Any]]) -> List[dict]:
    rows = [asdict(finding) if isinstance(finding, MigrationFinding) else dict(finding) for finding in findings]
    return sorted(rows, key=lambda row: (row.get("code", ""), row.get("subject_id", ""), row.get("message", "")))
