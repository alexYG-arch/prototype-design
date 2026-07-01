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

INPUT_RECORD_GROUPS = (
    "approved_semantic_artifacts",
    "approved_operational_indexes",
    "review_decisions",
    "lock_refs",
    "validator_results",
    "control_indexes",
    "schemas",
)

ALLOWED_QA_WRITES = {"READ_ONLY_QA_REPORT.md", "qa_finding_index.json"}
FORBIDDEN_FINAL_DRD_TEXT_MARKERS = (
    "_Source:",
    " sha256:",
    "source_sha256",
    "source_prd:",
    "review_gates/",
    "REVIEW_DECISION.json",
    "approval:",
    "gate_id",
    "run_state",
    "run_id:",
    "CANDIDATE",
    "候选",
    "renderable_page_variants",
    "page_variant_code",
    "新增能力：False",
)

APPROVED_STAGE_SEMANTIC_ROLE = "approved_stage_semantic_body"
APPROVED_STAGE_ARTIFACT_KIND = "APPROVED_SEMANTIC_ARTIFACT"
APPROVED_STAGE_MANIFESTS_FIELD = "approved_semantic_artifact_manifests"


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
        "requires_approved_stage_semantic_artifacts",
        "closed_input_hash",
    ]
    for field in required:
        if field not in bundle or bundle.get(field) in (None, "", []):
            findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, f"{field} is required"))
    if not isinstance(bundle.get("requires_approved_stage_semantic_artifacts"), bool):
        findings.append(
            CompilerFinding(
                "COMP-CHECK-001",
                bundle_id,
                "requires_approved_stage_semantic_artifacts must be an explicit boolean",
            )
        )
    for field in INPUT_RECORD_GROUPS:
        if field in bundle and not isinstance(bundle.get(field), list):
            findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, f"{field} must be a list of input records"))
    if bundle.get("compiler_stage_id") != "DRD-05":
        findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, "compiler_stage_id must be DRD-05"))

    records = input_records(bundle)
    for record in records:
        findings.extend(validate_input_record(record))
    findings.extend(validate_stage_order(bundle.get("stage_order", [])))
    expected_hash = compute_closed_input_hash(bundle)
    if bundle.get("closed_input_hash") != expected_hash:
        findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, "closed_input_hash does not match closed input records"))
    if "semantic_content_hash" in bundle and bundle.get("semantic_content_hash") != compute_semantic_content_hash(bundle):
        findings.append(CompilerFinding("COMP-CHECK-001", bundle_id, "semantic_content_hash does not match sections and semantic units"))
    findings.extend(validate_approved_stage_semantic_artifacts(bundle))
    return findings


def input_records(bundle: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    records = []
    for field in INPUT_RECORD_GROUPS:
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
    if input_type == "APPROVED_SEMANTIC_ARTIFACT":
        if not (record.get("approval_ref") or record.get("review_decision_ref")):
            findings.append(CompilerFinding("COMP-CHECK-003", input_id, "semantic artifact requires approval or review decision reference"))
    if input_type == "APPROVED_OPERATIONAL_INDEX":
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
        "requires_approved_stage_semantic_artifacts": bundle.get("requires_approved_stage_semantic_artifacts"),
        "stage_order": bundle.get("stage_order"),
        "section_order": bundle.get("section_order"),
    }
    if APPROVED_STAGE_MANIFESTS_FIELD in bundle:
        payload[APPROVED_STAGE_MANIFESTS_FIELD] = bundle.get(APPROVED_STAGE_MANIFESTS_FIELD)
    return sha256_text(canonical_json(payload))


def compute_semantic_content_hash(bundle: Mapping[str, Any]) -> str:
    payload = {
        "bundle_id": bundle.get("bundle_id"),
        "sections": bundle.get("sections", []),
        "semantic_units": bundle.get("semantic_units", []),
        "compiled_semantic_units": bundle.get("compiled_semantic_units"),
    }
    return sha256_text(canonical_json(payload))


def validate_hash_drift(records: Iterable[Mapping[str, Any]], current_hashes: Mapping[str, str]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    for record in records:
        path = str(record.get("path") or "")
        expected = record.get("sha256")
        if path not in current_hashes:
            findings.append(CompilerFinding("COMP-CHECK-004", path, "current hash is missing for bundled input"))
        elif current_hashes[path] != expected:
            findings.append(CompilerFinding("COMP-CHECK-004", path, "current hash differs from bundled hash"))
    return findings


def validate_section_semantic_unit_refs(bundle: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    unit_ids = {str(unit.get("semantic_unit_id")) for unit in bundle.get("semantic_units", []) if unit.get("semantic_unit_id")}
    seen_refs = {}
    for section in bundle.get("sections", []):
        section_id = str(section.get("section_id") or "section")
        refs = [str(unit_id) for unit_id in section.get("semantic_unit_ids", [])]
        if not refs:
            findings.append(CompilerFinding("COMP-CHECK-011", section_id, "section must reference semantic_unit_ids"))
        missing = sorted(set(refs) - unit_ids)
        if missing:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-011",
                    section_id,
                    "section references unknown semantic_unit_ids: " + ", ".join(missing),
                )
            )
        duplicate_refs = sorted({unit_id for unit_id in refs if refs.count(unit_id) > 1})
        if duplicate_refs:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-011",
                    section_id,
                    "section references semantic_unit_ids more than once: " + ", ".join(duplicate_refs),
                )
            )
        for unit_id in refs:
            if unit_id in seen_refs and unit_id in unit_ids:
                findings.append(
                    CompilerFinding(
                        "COMP-CHECK-011",
                        unit_id,
                        f"semantic_unit_id is referenced by multiple sections: {seen_refs[unit_id]}, {section_id}",
                    )
                )
            seen_refs.setdefault(unit_id, section_id)
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
    rows = list(sections)
    section_keys = [
        (section.get("stage_id"), section.get("section_id"))
        for section in rows
        if section.get("stage_id") and section.get("section_id")
    ]
    for key in sorted({key for key in section_keys if section_keys.count(key) > 1}):
        findings.append(CompilerFinding("COMP-CHECK-005", str(key[1]), "section_id must be unique within a stage"))
    order_slots = [
        (section.get("stage_order_index"), section.get("section_order_index"))
        for section in rows
        if "stage_order_index" in section and "section_order_index" in section
    ]
    for slot in sorted({slot for slot in order_slots if order_slots.count(slot) > 1}):
        findings.append(CompilerFinding("COMP-CHECK-005", "section_order", f"section order slot must be unique: {slot[0]}.{slot[1]}"))
    for section in rows:
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


def validate_final_drd_reader_structure(final_drd_text: str) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    lines = final_drd_text.splitlines()
    h1_lines = [line for line in lines if line.startswith("# ")]
    if not h1_lines:
        findings.append(CompilerFinding("COMP-CHECK-021", "FINAL_DRD.md", "reader-facing final DRD requires exactly one H1 title"))
    elif h1_lines != [lines[0]]:
        findings.append(CompilerFinding("COMP-CHECK-021", "FINAL_DRD.md", "reader-facing final DRD must not contain nested or repeated H1 headings"))

    for marker in FORBIDDEN_FINAL_DRD_TEXT_MARKERS:
        if marker in final_drd_text:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-021",
                    "FINAL_DRD.md",
                    f"reader-facing final DRD contains process evidence or index dump marker: {marker}",
                )
            )
    return findings


def validate_approved_stage_semantic_artifacts(bundle: Mapping[str, Any]) -> List[CompilerFinding]:
    """Validate the staged-run boundary between review candidates and compiler input.

    When enabled, DRD-05 may only compile reader-facing approved semantic bodies
    promoted after review. Raw DRD-01 through DRD-04 candidate documents remain
    review evidence and must stay out of FINAL_DRD.md.
    """

    if not bundle.get("requires_approved_stage_semantic_artifacts"):
        return []

    findings: List[CompilerFinding] = []
    bundle_id = str(bundle.get("bundle_id") or "compiler_input_bundle")
    approved_records = [
        record
        for record in bundle.get("approved_semantic_artifacts", [])
        if isinstance(record, Mapping)
        and record.get("input_type") == "APPROVED_SEMANTIC_ARTIFACT"
        and record.get("stage_id") in STAGE_ORDER
    ]
    records_by_path = {str(record.get("path")): record for record in approved_records}
    record_paths = [str(record.get("path")) for record in approved_records]
    for duplicate_path in sorted({path for path in record_paths if record_paths.count(path) > 1}):
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                duplicate_path,
                "approved semantic artifact body path must be unique",
            )
        )
    if not approved_records:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                bundle_id,
                "staged DRD-05 requires approved semantic artifact records for DRD-01 through DRD-04",
            )
        )
    record_stage_ids = {str(record.get("stage_id")) for record in approved_records}
    missing_record_stages = [stage_id for stage_id in STAGE_ORDER if stage_id not in record_stage_ids]
    if missing_record_stages:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                bundle_id,
                "staged DRD-05 requires approved semantic artifact records for every stage: "
                + ", ".join(missing_record_stages),
            )
        )

    section_stage_ids = {
        str(section.get("stage_id"))
        for section in bundle.get("sections", [])
        if isinstance(section, Mapping) and section.get("stage_id") in STAGE_ORDER
    }
    section_source_paths = {
        str(section.get("source_path"))
        for section in bundle.get("sections", [])
        if isinstance(section, Mapping) and section.get("stage_id") in STAGE_ORDER and section.get("source_path")
    }
    missing_section_stages = [stage_id for stage_id in STAGE_ORDER if stage_id not in section_stage_ids]
    if missing_section_stages:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                bundle_id,
                "staged DRD-05 requires compiler sections for every approved stage: "
                + ", ".join(missing_section_stages),
            )
        )

    manifests = bundle.get(APPROVED_STAGE_MANIFESTS_FIELD, [])
    if not isinstance(manifests, list) or not manifests:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                bundle_id,
                "staged DRD-05 requires approved_semantic_artifact_manifests",
            )
        )
        manifests = []
    manifest_by_id = {
        str(manifest.get("artifact_id")): manifest
        for manifest in manifests
        if isinstance(manifest, Mapping) and manifest.get("artifact_id")
    }
    review_hash_by_path = {
        str(record.get("path")): record.get("sha256")
        for record in bundle.get("review_decisions", [])
        if isinstance(record, Mapping)
    }

    for record in approved_records:
        input_id = str(record.get("input_id") or record.get("path") or "approved_semantic_artifact")
        if str(record.get("path")) not in section_source_paths:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must be referenced by a compiler section",
                )
            )
        if record.get("artifact_kind") != APPROVED_STAGE_ARTIFACT_KIND:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must declare artifact_kind=APPROVED_SEMANTIC_ARTIFACT",
                )
            )
        if record.get("semantic_role") != APPROVED_STAGE_SEMANTIC_ROLE:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    f"approved semantic artifact record must use semantic_role={APPROVED_STAGE_SEMANTIC_ROLE}",
                )
            )
        if not record.get("approved_semantic_artifact_ref"):
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must bind approved_semantic_artifact_ref",
                )
            )
        elif record.get("approved_semantic_artifact_ref") not in manifest_by_id:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must reference a bundled approved semantic artifact manifest",
                )
            )
        if record.get("semantic_body_path") != record.get("path"):
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "semantic_body_path must match the compiled approved semantic body path",
                )
            )
        if not record.get("semantic_body_sha256"):
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must bind semantic_body_sha256",
                )
            )
        elif record.get("semantic_body_sha256") != record.get("sha256"):
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "semantic_body_sha256 must match the compiled semantic body sha256",
                )
            )
        source_candidates = record.get("source_candidate_refs")
        if not isinstance(source_candidates, list) or not source_candidates:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    input_id,
                    "approved semantic artifact record must name source_candidate_refs",
                )
            )
        manifest = manifest_by_id.get(str(record.get("approved_semantic_artifact_ref")))
        if isinstance(manifest, Mapping):
            findings.extend(validate_approved_semantic_artifact_manifest(manifest))
            findings.extend(
                _validate_manifest_matches_record(
                    manifest=manifest,
                    record=record,
                    review_hash_by_path=review_hash_by_path,
                )
            )

    for section in bundle.get("sections", []):
        if not isinstance(section, Mapping) or section.get("stage_id") not in STAGE_ORDER:
            continue
        section_id = str(section.get("section_id") or "section")
        findings.extend(validate_reader_facing_semantic_body(str(section.get("heading_text") or ""), section_id))
        source_path = str(section.get("source_path") or "")
        record = records_by_path.get(source_path)
        if record is None:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    section_id,
                    "compiled section source_path must point to an approved semantic artifact body, not a review candidate",
                )
            )
        else:
            if section.get("approved_semantic_artifact_ref") != record.get("approved_semantic_artifact_ref"):
                findings.append(
                    CompilerFinding(
                        "COMP-CHECK-022",
                        section_id,
                        "compiled section must bind the approved semantic artifact manifest used by its input record",
                    )
                )
            if section.get("source_hash") != record.get("semantic_body_sha256"):
                findings.append(
                    CompilerFinding(
                        "COMP-CHECK-022",
                        section_id,
                        "compiled section source_hash must match approved semantic body sha256",
                    )
                )
        findings.extend(validate_reader_facing_semantic_body(str(section.get("body") or ""), section_id))

    return findings


def validate_approved_semantic_artifact_manifest(manifest: Mapping[str, Any]) -> List[CompilerFinding]:
    subject_id = str(manifest.get("artifact_id") or "approved_semantic_artifact")
    findings: List[CompilerFinding] = []
    required = [
        "artifact",
        "artifact_kind",
        "artifact_id",
        "stage_id",
        "semantic_body_path",
        "semantic_body_sha256",
        "review_decision_ref",
        "review_decision_sha256",
        "source_candidate_refs",
        "source_candidate_hashes",
        "final_drd_section_id",
        "final_drd_section_title",
        "compiler_eligible",
        "product_capability_additions_allowed",
        "process_evidence_refs",
    ]
    for field in required:
        if field not in manifest or manifest.get(field) in (None, "", []):
            findings.append(CompilerFinding("COMP-CHECK-023", subject_id, f"{field} is required"))
    if manifest.get("artifact") != "approved_semantic_artifact":
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "artifact must be approved_semantic_artifact"))
    if manifest.get("artifact_kind") != APPROVED_STAGE_ARTIFACT_KIND:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "artifact_kind must be APPROVED_SEMANTIC_ARTIFACT"))
    if manifest.get("stage_id") not in STAGE_ORDER:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "stage_id must be DRD-01 through DRD-04/03B"))
    if manifest.get("compiler_eligible") is not True:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "compiler_eligible must be true"))
    if manifest.get("product_capability_additions_allowed") is not False:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "product_capability_additions_allowed must be false"))
    if not _is_hash(manifest.get("semantic_body_sha256")):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "semantic_body_sha256 must be sha256"))
    if not _is_hash(manifest.get("review_decision_sha256")):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "review_decision_sha256 must be sha256"))
    source_candidate_refs = manifest.get("source_candidate_refs")
    source_candidate_hashes = manifest.get("source_candidate_hashes")
    if not isinstance(source_candidate_refs, list) or not source_candidate_refs:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "source_candidate_refs must be non-empty"))
    if not isinstance(source_candidate_hashes, Mapping) or not source_candidate_hashes:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "source_candidate_hashes must be non-empty"))
    elif isinstance(source_candidate_refs, list):
        missing_hashes = [str(ref) for ref in source_candidate_refs if str(ref) not in source_candidate_hashes]
        if missing_hashes:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-023",
                    subject_id,
                    "source_candidate_hashes must cover every source_candidate_ref: " + ", ".join(missing_hashes),
                )
            )
        for ref, digest in source_candidate_hashes.items():
            if not _is_hash(digest):
                findings.append(CompilerFinding("COMP-CHECK-023", str(ref), "source candidate hash must be sha256"))
    process_evidence_refs = manifest.get("process_evidence_refs")
    if not isinstance(process_evidence_refs, list) or not process_evidence_refs:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "process_evidence_refs must be non-empty"))
    elif manifest.get("review_decision_ref") not in process_evidence_refs:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "process_evidence_refs must include review_decision_ref"))
    return findings


def _validate_manifest_matches_record(
    *,
    manifest: Mapping[str, Any],
    record: Mapping[str, Any],
    review_hash_by_path: Mapping[str, Any],
) -> List[CompilerFinding]:
    subject_id = str(manifest.get("artifact_id") or record.get("input_id") or "approved_semantic_artifact")
    findings: List[CompilerFinding] = []
    if manifest.get("stage_id") != record.get("stage_id"):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest stage_id must match input record"))
    if manifest.get("semantic_body_path") != record.get("path"):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest semantic_body_path must match input record path"))
    if manifest.get("semantic_body_sha256") != record.get("semantic_body_sha256"):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest semantic_body_sha256 must match input record"))
    review_ref = record.get("review_decision_ref") or record.get("approval_ref")
    if manifest.get("review_decision_ref") != review_ref:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest review_decision_ref must match input record"))
    if review_ref and str(review_ref) not in review_hash_by_path:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest review_decision_ref must be present in bundled review_decisions"))
    if review_ref and review_hash_by_path.get(str(review_ref)) and manifest.get("review_decision_sha256") != review_hash_by_path[str(review_ref)]:
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest review_decision_sha256 must match bundled review decision"))
    if sorted(manifest.get("source_candidate_refs", [])) != sorted(record.get("source_candidate_refs", [])):
        findings.append(CompilerFinding("COMP-CHECK-023", subject_id, "manifest source_candidate_refs must match input record"))
    return findings


def validate_reader_facing_semantic_body(body_text: str, subject_id: str = "approved_semantic_body") -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    if any(line.startswith("# ") for line in body_text.splitlines()):
        findings.append(
            CompilerFinding(
                "COMP-CHECK-022",
                subject_id,
                "approved semantic artifact body must not contain H1 headings; DRD-05 owns final heading structure",
            )
        )
    for marker in FORBIDDEN_FINAL_DRD_TEXT_MARKERS:
        if marker in body_text:
            findings.append(
                CompilerFinding(
                    "COMP-CHECK-022",
                    subject_id,
                    f"approved semantic artifact body contains process evidence marker: {marker}",
                )
            )
    return findings


def validate_compiler_output_package(
    bundle: Mapping[str, Any],
    semantic_unit_inventory: Mapping[str, Any],
    conservation_report: Mapping[str, Any],
    final_drd_text: str,
) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    findings.extend(validate_final_drd_reader_structure(final_drd_text))
    units = semantic_unit_inventory.get("semantic_units", [])
    findings.extend(validate_input_bundle(bundle))
    findings.extend(validate_section_semantic_unit_refs(bundle))
    findings.extend(validate_atomic_inventory_for_compiler(units))
    findings.extend(validate_conservation_report(conservation_report))
    current_hashes = bundle.get("current_hashes")
    if not isinstance(current_hashes, Mapping) or not current_hashes:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-004",
                str(bundle.get("bundle_id") or "compiler_input_bundle"),
                "current_hashes is required for compiler output package",
            )
        )
    else:
        findings.extend(validate_hash_drift(input_records(bundle), current_hashes))
    expected_semantic_hash = compute_semantic_content_hash(bundle)
    if not bundle.get("semantic_content_hash"):
        findings.append(
            CompilerFinding(
                "COMP-CHECK-001",
                str(bundle.get("bundle_id") or "compiler_input_bundle"),
                "semantic_content_hash is required for compiler output package",
            )
        )
    elif bundle.get("semantic_content_hash") != expected_semantic_hash:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-001",
                str(bundle.get("bundle_id") or "compiler_input_bundle"),
                "semantic_content_hash does not match sections and semantic units",
            )
        )
    if semantic_unit_inventory.get("source_artifact_hash") != expected_semantic_hash:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-011",
                str(semantic_unit_inventory.get("inventory_id") or "compiler_semantic_unit_inventory"),
                "semantic unit inventory source_artifact_hash does not bind semantic content hash",
            )
        )

    try:
        from drd_harness.compiler.final_drd import CompilerFailure, compile_final_drd

        compiled = compile_final_drd(bundle)
    except CompilerFailure as exc:
        findings.extend(CompilerFinding(finding.code, finding.subject_id, finding.message) for finding in exc.findings)
        return findings

    if final_drd_text != compiled["FINAL_DRD.md"]:
        findings.append(CompilerFinding("COMP-CHECK-011", "FINAL_DRD.md", "FINAL_DRD does not match deterministic compiler output"))
    if units != compiled["compiler_semantic_unit_inventory.json"]:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-011",
                str(semantic_unit_inventory.get("inventory_id") or "compiler_semantic_unit_inventory"),
                "semantic unit inventory does not match deterministic compiler output",
            )
        )
    if dict(conservation_report) != compiled["compiler_conservation_report.json"]:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-011",
                "compiler_conservation_report",
                "conservation report does not match deterministic compiler output",
            )
        )
    if conservation_report.get("status") != "PASS":
        findings.append(CompilerFinding("COMP-CHECK-015", "compiler_conservation_report", "compiled package must pass conservation"))
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
