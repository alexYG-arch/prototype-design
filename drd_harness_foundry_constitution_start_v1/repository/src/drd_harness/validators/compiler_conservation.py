"""Validators for compiler conservation and read-only QA boundaries."""

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

from drd_harness.compiler.conservation import (
    ConservationFinding,
    canonical_json,
    sha256_text,
    validate_atomic_inventory,
)
from drd_harness.compiler.final_drd import STAGE_ORDER


ALLOWED_INPUT_TYPES = {
    "APPROVED_SEMANTIC_ARTIFACT",
    "APPROVED_OPERATIONAL_INDEX",
    "REVIEW_DECISION",
    "SPEC_LOCK_REF",
    "CONTROL_INDEX",
    "VALIDATOR_RESULT",
    "SCHEMA",
}

FORBIDDEN_INPUT_TYPES = {
    "UNAPPROVED_CANDIDATE",
    "LOCAL_DRAFT",
    "MANUAL_FINAL_FRAGMENT",
    "CODEX_REWRITE_SUGGESTION",
    "DIRECT_SOURCE_PRD_SEMANTIC_READ",
    "UNHASHED_FILE",
    "HASH_DRIFTED_FILE",
    "SUPERSEDED_LOCK_WITHOUT_CURRENT_REF",
    "INVALIDATED_EVIDENCE",
}

ALLOWED_QA_WRITES = {"READ_ONLY_QA_REPORT.md", "qa_finding_index.json"}


@dataclass(frozen=True)
class CompilerFinding:
    code: str
    subject_id: str
    message: str


def validate_input_bundle(bundle: Mapping[str, Any]) -> List[CompilerFinding]:
    bundle_id = str(bundle.get("bundle_id") or "compiler_input_bundle")
    findings: List[CompilerFinding] = []
    required = [
        "bundle_id",
        "bundle_version",
        "compiler_stage_id",
        "source_snapshot_identity",
        "approved_semantic_artifacts",
        "approved_operational_indexes",
        "review_decisions",
        "lock_refs",
        "validator_results",
        "control_indexes",
        "schemas",
        "stage_order",
        "section_order",
        "closed_input_hash",
    ]
    for field in required:
        if field not in bundle or bundle.get(field) in (None, "", []):
            findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, f"{field} is required"))
    if bundle.get("compiler_stage_id") != "DRD-05":
        findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, "compiler_stage_id must be DRD-05"))

    records = input_records(bundle)
    for record in records:
        findings.extend(validate_input_record(record))
    findings.extend(validate_stage_order(bundle.get("stage_order", [])))
    expected_hash = compute_closed_input_hash(bundle)
    if bundle.get("closed_input_hash") != expected_hash:
        findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, "closed_input_hash does not match closed input records"))
    return findings


def input_records(bundle: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    records = []
    for field in (
        "approved_semantic_artifacts",
        "approved_operational_indexes",
        "review_decisions",
        "lock_refs",
        "validator_results",
        "control_indexes",
        "schemas",
    ):
        values = bundle.get(field, [])
        if isinstance(values, list):
            records.extend(values)
    return records


def validate_input_record(record: Mapping[str, Any]) -> List[CompilerFinding]:
    input_id = str(record.get("input_id") or record.get("path") or "input")
    findings: List[CompilerFinding] = []
    input_type = record.get("input_type")
    if input_type in FORBIDDEN_INPUT_TYPES or input_type not in ALLOWED_INPUT_TYPES:
        findings.append(CompilerFinding("COMP-CHECK-002", input_id, "input_type is not allowed for DRD-05"))
    if not record.get("path") or not record.get("sha256"):
        findings.append(CompilerFinding("COMP-CHECK-001", input_id, "path and sha256 are required"))
    elif not _is_hash(record.get("sha256")):
        findings.append(CompilerFinding("COMP-CHECK-001", input_id, "sha256 must be sha256"))
    if input_type in {"APPROVED_SEMANTIC_ARTIFACT", "APPROVED_OPERATIONAL_INDEX"}:
        if not (record.get("approval_ref") or record.get("lock_ref") or record.get("review_decision_ref")):
            findings.append(CompilerFinding("COMP-CHECK-003", input_id, "structured approval or lock reference is required"))
    if record.get("approval_ref") == "approved in prose":
        findings.append(CompilerFinding("COMP-CHECK-003", input_id, "prose-only approval is not valid"))
    if record.get("invalidation_state") == "INVALIDATED":
        findings.append(CompilerFinding("COMP-CHECK-002", input_id, "invalidated evidence is not allowed"))
    return findings


def compute_closed_input_hash(bundle: Mapping[str, Any]) -> str:
    records = []
    for record in input_records(bundle):
        records.append(
            {
                "input_id": record.get("input_id"),
                "input_type": record.get("input_type"),
                "path": record.get("path"),
                "sha256": record.get("sha256"),
                "approval_ref": record.get("approval_ref") or record.get("review_decision_ref") or record.get("lock_ref"),
                "semantic_role": record.get("semantic_role"),
            }
        )
    payload = {
        "bundle_id": bundle.get("bundle_id"),
        "bundle_version": bundle.get("bundle_version"),
        "compiler_stage_id": bundle.get("compiler_stage_id"),
        "source_snapshot_identity": bundle.get("source_snapshot_identity"),
        "records": sorted(records, key=lambda row: (str(row.get("path")), str(row.get("input_id")))),
        "stage_order": bundle.get("stage_order"),
        "section_order": bundle.get("section_order"),
    }
    return sha256_text(canonical_json(payload))


def validate_hash_drift(records: Iterable[Mapping[str, Any]], current_hashes: Mapping[str, str]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    for record in records:
        path = str(record.get("path") or "")
        expected = record.get("sha256")
        if path in current_hashes and current_hashes[path] != expected:
            findings.append(CompilerFinding("COMP-CHECK-004", path, "current hash differs from bundled hash"))
    return findings


def validate_stage_order(stage_order: Iterable[Mapping[str, Any]]) -> List[CompilerFinding]:
    rows = list(stage_order)
    findings: List[CompilerFinding] = []
    ordered = [row.get("stage_id") for row in sorted(rows, key=lambda row: row.get("stage_order_index", 0))]
    if ordered != STAGE_ORDER:
        findings.append(CompilerFinding("COMP-CHECK-005", "stage_order", "stage_order must match DRD-01 through DRD-04"))
    seen_indexes = set()
    for row in rows:
        if "stage_order_index" not in row or not row.get("stage_id"):
            findings.append(CompilerFinding("COMP-CHECK-005", "stage_order", "stage_id and stage_order_index are required"))
        if row.get("stage_order_index") in seen_indexes:
            findings.append(CompilerFinding("COMP-CHECK-005", "stage_order", "stage_order_index must be unique"))
        seen_indexes.add(row.get("stage_order_index"))
    return findings


def validate_section_order(sections: Iterable[Mapping[str, Any]]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    for section in sections:
        subject = str(section.get("section_id") or "section")
        for field in ("stage_order_index", "section_order_index", "section_id"):
            if field not in section:
                findings.append(CompilerFinding("COMP-CHECK-005", subject, f"{field} is required"))
        if section.get("ordering_source") in {"filesystem", "mtime", "locale", "random", "git_status", "json_object_order"}:
            findings.append(CompilerFinding("COMP-CHECK-005", subject, "ordering source is nondeterministic"))
    return findings


def validate_conservation_report(report: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    status = report.get("status")
    if status == "FAIL_SEMANTIC_ADDITION" or report.get("added_semantic_units"):
        findings.append(CompilerFinding("COMP-CHECK-007", "conservation_report", "semantic additions are present"))
    if status == "FAIL_SEMANTIC_OMISSION" or report.get("omitted_semantic_units"):
        findings.append(CompilerFinding("COMP-CHECK-008", "conservation_report", "semantic omissions are present"))
    if report.get("hash_drift"):
        findings.append(CompilerFinding("COMP-CHECK-004", "conservation_report", "hash drift is present"))
    if status == "REQUIRES_HUMAN_REVIEW" and not report.get("human_review_required"):
        findings.append(CompilerFinding("COMP-CHECK-015", "conservation_report", "human review routing is required"))
    return findings


def validate_final_manifest(manifest: Mapping[str, Any]) -> List[CompilerFinding]:
    subject = str(manifest.get("final_drd_path") or "final_drd_manifest")
    findings: List[CompilerFinding] = []
    required = [
        "final_drd_path",
        "final_drd_hash",
        "semantic_hash",
        "mechanical_hash",
        "input_bundle_hash",
        "toc_hash",
        "reference_index_hash",
        "hash_index_hash",
        "conservation_report_hash",
        "conservation_status",
        "assembly_plan",
    ]
    for field in required:
        if field not in manifest or manifest.get(field) in (None, ""):
            findings.append(CompilerFinding("COMP-CHECK-011", subject, f"{field} is required"))
    for field in (
        "final_drd_hash",
        "semantic_hash",
        "mechanical_hash",
        "input_bundle_hash",
        "toc_hash",
        "reference_index_hash",
        "hash_index_hash",
        "conservation_report_hash",
    ):
        if not _is_hash(manifest.get(field)):
            findings.append(CompilerFinding("COMP-CHECK-012", subject, f"{field} must be sha256"))
    for field in (
        "approved_input_count",
        "compiled_section_count",
        "compiled_semantic_unit_count",
        "omitted_semantic_unit_count",
        "added_semantic_unit_count",
        "hash_drift_count",
        "unapproved_input_count",
    ):
        value = manifest.get(field)
        if not isinstance(value, int) or value < 0:
            findings.append(CompilerFinding("COMP-CHECK-011", subject, f"{field} must be a non-negative integer"))
    if manifest.get("conservation_status") == "PASS":
        blocking_counts = [
            manifest.get("omitted_semantic_unit_count", 0),
            manifest.get("added_semantic_unit_count", 0),
            manifest.get("hash_drift_count", 0),
            manifest.get("unapproved_input_count", 0),
        ]
        if any(blocking_counts):
            findings.append(CompilerFinding("COMP-CHECK-015", subject, "PASS manifest cannot contain blocking counts"))
    return findings


def validate_read_only_qa_boundary(record: Mapping[str, Any]) -> List[CompilerFinding]:
    subject = str(record.get("drd06_run_id") or "DRD-06")
    findings: List[CompilerFinding] = []
    written = set(record.get("written_paths", []))
    forbidden = sorted(written - ALLOWED_QA_WRITES)
    if forbidden:
        findings.append(CompilerFinding("COMP-CHECK-014", subject, "DRD-06 wrote forbidden paths: " + ", ".join(forbidden)))
    if record.get("mutated_artifacts"):
        findings.append(CompilerFinding("COMP-CHECK-014", subject, "DRD-06 mutated artifacts"))
    return findings


def validate_atomic_inventory_for_compiler(units: Iterable[Mapping[str, Any]]) -> List[CompilerFinding]:
    return [
        CompilerFinding(finding.code, finding.subject_id, finding.message)
        for finding in validate_atomic_inventory(units)
    ]


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
