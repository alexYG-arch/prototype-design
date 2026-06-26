"""Traceability completeness, orphan code, test obligation, and Skill authority validators."""

import json
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.orchestrator.traceability import (
    TraceabilityFinding,
    detect_orphan_code_targets,
    invalidated_trace_rows,
    validate_skill_second_authority,
    validate_test_obligation_matrix,
    validate_traceability_rows,
)
from drd_harness.validators.compiler_conservation import validate_read_only_qa_boundary
from drd_harness.validators.workpack_scope import (
    validate_skill_binding_manifest,
    validate_workpack_readiness,
)


P3_ASSURANCE_ENVELOPE_FIELDS = {
    "artifact_id",
    "stage_id",
    "fixture_id",
    "path",
    "schema_ref",
    "schema_payload_key",
    "source_refs",
    "upstream_artifact_refs",
    "upstream_hashes",
    "validator_ref",
    "review_gate",
    "promotion_state",
    "invalidation_inputs",
}
P3_ASSURANCE_ARTIFACTS = {
    "assurance_input_index": (
        "p3.assurance.input_index",
        "index",
        "repository/fixtures/p3/assurance/assurance_input_index.json",
    ),
    "final_review_packet": (
        "p3.assurance.final_review_packet",
        "packet",
        "repository/fixtures/p3/assurance/final_review_packet.json",
    ),
    "trace_row_set": (
        "p3.assurance.trace_row_set",
        "records",
        "repository/fixtures/p3/assurance/code_target_map.json",
    ),
    "test_obligation_matrix": (
        "p3.assurance.test_obligation_matrix",
        "records",
        "repository/fixtures/p3/assurance/test_obligation_matrix.json",
    ),
    "implementation_workpack_index": (
        "p3.assurance.implementation_workpack_index",
        "index",
        "repository/fixtures/p3/assurance/implementation_workpack_index.json",
    ),
    "implementation_workpack_template": (
        "p3.assurance.implementation_workpack_template",
        "workpack",
        "repository/fixtures/p3/assurance/implementation_workpack_template.json",
    ),
    "skill_binding_manifest": (
        "p3.assurance.skill_binding_manifest",
        "manifest",
        "repository/fixtures/p3/assurance/skill_binding_manifest.json",
    ),
    "traceability_exception_ledger": (
        "p3.assurance.traceability_exception_ledger",
        "records",
        "repository/fixtures/p3/assurance/traceability_exception_ledger.json",
    ),
    "read_only_qa_boundary": (
        "p3.assurance.read_only_qa_boundary",
        "boundary",
        "repository/fixtures/p3/assurance/read_only_qa_boundary.json",
    ),
    "final_assurance_report": (
        "p3.assurance.final_assurance_report",
        "report",
        "repository/fixtures/p3/assurance/final_assurance_report.json",
    ),
}
P3_ASSURANCE_COMPILER_REVIEW_DECISION = "build_program/phases/P3/candidates/P3-IMPL-COMPILER/REVIEW_DECISION.json"
P3_ASSURANCE_COMPILER_REVIEW_SUBJECT_HASH = "05f7887f0e335de244edaa3ecdadb955dc5f6fc3da08261bdadb9021c8163834"
P3_ASSURANCE_COMPILER_REVIEW_DECISION_HASH = "aec392fb4f90c76cdd82fd40c031ab31f9dc4032cbae50d4a55d239abd62ebf4"
P3_ASSURANCE_REQUIRED_COMPILER_OUTPUTS = {
    "repository/fixtures/p3/compiler/FINAL_DRD.md",
    "repository/fixtures/p3/compiler/compiler_input_bundle.json",
    "repository/fixtures/p3/compiler/compiler_semantic_unit_inventory.json",
    "repository/fixtures/p3/compiler/compiler_conservation_report.json",
    "repository/fixtures/p3/compiler/final_drd_manifest.json",
    "repository/fixtures/p3/compiler/final_drd_toc.json",
    "repository/fixtures/p3/compiler/final_drd_reference_index.json",
    "repository/fixtures/p3/compiler/final_drd_hash_index.json",
    "repository/fixtures/p3/compiler/read_only_qa_boundary.json",
}
P3_ASSURANCE_PASS_STATUSES = {
    "compiler_gate_status",
    "qa_boundary_status",
    "traceability_status",
    "test_obligation_status",
    "workpack_scope_status",
    "skill_binding_status",
    "exception_status",
    "invalidation_status",
}


def validate_code_target_map(rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    return validate_traceability_rows(rows)


def validate_trace_row_to_test_matrix(
    rows: Iterable[Mapping[str, Any]],
    matrix_rows: Iterable[Mapping[str, Any]],
) -> List[TraceabilityFinding]:
    return validate_test_obligation_matrix(rows, matrix_rows)


def validate_orphan_code_targets(code_targets: Iterable[str], rows: Iterable[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    return detect_orphan_code_targets(code_targets, rows)


def validate_skill_text_no_second_authority(skill_text: str) -> List[TraceabilityFinding]:
    return validate_skill_second_authority(skill_text)


def validate_traceability_invalidation(rows: Iterable[Mapping[str, Any]], changed_edge_type: str) -> List[TraceabilityFinding]:
    affected = invalidated_trace_rows(rows, changed_edge_type)
    if not affected:
        return [TraceabilityFinding("SW-CHECK-016", changed_edge_type, "changed dependency did not invalidate dependent rows")]
    return []


def validate_p3_assurance_artifacts(
    *,
    assurance_input_index: Mapping[str, Any],
    final_review_packet: Mapping[str, Any],
    trace_row_set: Mapping[str, Any],
    test_obligation_matrix: Mapping[str, Any],
    implementation_workpack_index: Mapping[str, Any],
    implementation_workpack_template: Mapping[str, Any],
    skill_binding_manifest: Mapping[str, Any],
    traceability_exception_ledger: Mapping[str, Any],
    read_only_qa_boundary: Mapping[str, Any],
    final_assurance_report: Mapping[str, Any],
) -> List[TraceabilityFinding]:
    artifacts = {
        "assurance_input_index": assurance_input_index,
        "final_review_packet": final_review_packet,
        "trace_row_set": trace_row_set,
        "test_obligation_matrix": test_obligation_matrix,
        "implementation_workpack_index": implementation_workpack_index,
        "implementation_workpack_template": implementation_workpack_template,
        "skill_binding_manifest": skill_binding_manifest,
        "traceability_exception_ledger": traceability_exception_ledger,
        "read_only_qa_boundary": read_only_qa_boundary,
        "final_assurance_report": final_assurance_report,
    }
    findings: List[TraceabilityFinding] = []
    for name, artifact in artifacts.items():
        findings.extend(_validate_p3_assurance_envelope(name, artifact))

    try:
        input_index = _payload_mapping(assurance_input_index, "index")
        packet = _payload_mapping(final_review_packet, "packet")
        trace_rows = _payload_records(trace_row_set)
        test_rows = _payload_records(test_obligation_matrix)
        workpack_index = _payload_mapping(implementation_workpack_index, "index")
        workpack = _payload_mapping(implementation_workpack_template, "workpack")
        skill_manifest = _payload_mapping(skill_binding_manifest, "manifest")
        exceptions = _payload_records(traceability_exception_ledger)
        qa_boundary = _payload_mapping(read_only_qa_boundary, "boundary")
        report = _payload_mapping(final_assurance_report, "report")
    except KeyError as exc:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", "p3.assurance", str(exc)))
        return findings

    findings.extend(_validate_p3_assurance_input_index(input_index))
    findings.extend(_validate_p3_assurance_qa_boundary(qa_boundary))
    findings.extend(validate_code_target_map(trace_rows))
    findings.extend(validate_trace_row_to_test_matrix(trace_rows, test_rows))
    findings.extend(_validate_p3_assurance_workpack_index(workpack_index, workpack, trace_rows))
    findings.extend(_scope_findings(validate_workpack_readiness(workpack)))
    findings.extend(_validate_p3_assurance_skill_binding(skill_manifest, trace_rows))
    findings.extend(_validate_p3_assurance_exceptions(exceptions))
    findings.extend(_validate_p3_final_assurance_report(report))
    findings.extend(_validate_p3_final_review_packet(packet, report))
    return findings


def _validate_p3_assurance_envelope(name: str, artifact: Mapping[str, Any]) -> List[TraceabilityFinding]:
    artifact_id, payload_key, path = P3_ASSURANCE_ARTIFACTS[name]
    findings: List[TraceabilityFinding] = []
    missing = sorted(P3_ASSURANCE_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, "artifact envelope missing fields: " + ", ".join(missing)))
    if artifact.get("artifact_id") != artifact_id:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, "artifact_id does not match P3 assurance contract"))
    if artifact.get("path") != path:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, "path does not match P3 assurance contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, "schema_payload_key does not match P3 assurance contract"))
    if payload_key not in artifact:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, f"{payload_key} payload is missing"))
    findings.extend(_validate_schema_payload(artifact, artifact_id, payload_key))
    for field in ("source_refs", "upstream_artifact_refs", "invalidation_inputs"):
        if not _non_empty_text_list(artifact.get(field)):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, f"{field} must be a non-empty text list"))
    upstream_hashes = artifact.get("upstream_hashes")
    if not isinstance(upstream_hashes, Mapping) or not upstream_hashes:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, "upstream_hashes must be a non-empty object"))
    elif any(not _is_sha256(value) for value in upstream_hashes.values()):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", artifact_id, "upstream_hashes sha256 values are malformed"))
    if artifact.get("promotion_state") != "candidate_only":
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", artifact_id, "assurance artifacts must remain candidate_only"))
    return findings


def _validate_schema_payload(artifact: Mapping[str, Any], artifact_id: str, payload_key: str) -> List[TraceabilityFinding]:
    schema_ref = artifact.get("schema_ref")
    if schema_ref is None:
        return []
    schema_path = Path(str(schema_ref))
    if not schema_path.is_file():
        return [TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, f"schema_ref path is missing: {schema_ref}")]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    item_schema = schema.get("items") if schema.get("type") == "array" else schema
    if not isinstance(item_schema, Mapping):
        return []
    required = set(_text_values(item_schema.get("required")))
    payload = artifact.get(payload_key)
    rows = payload if isinstance(payload, list) else [payload]
    findings: List[TraceabilityFinding] = []
    for row in rows:
        if not isinstance(row, Mapping):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", artifact_id, f"{payload_key} payload rows must be objects"))
            continue
        missing = sorted(required - set(row))
        if missing:
            subject_id = str(row.get("trace_row_id") or row.get("workpack_id") or row.get("skill_id") or artifact_id)
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", subject_id, "payload missing schema fields: " + ", ".join(missing)))
    return findings


def _validate_p3_assurance_input_index(index: Mapping[str, Any]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    if index.get("compiler_review_decision_ref") != P3_ASSURANCE_COMPILER_REVIEW_DECISION:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler review decision ref is not current implementation compiler review"))
    if index.get("compiler_review_subject_hash") != P3_ASSURANCE_COMPILER_REVIEW_SUBJECT_HASH:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler review subject hash mismatch"))
    if index.get("compiler_review_decision_sha256") != P3_ASSURANCE_COMPILER_REVIEW_DECISION_HASH:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler review decision sha256 mismatch"))
    decision_path = Path(P3_ASSURANCE_COMPILER_REVIEW_DECISION)
    if not decision_path.is_file() or _sha256_file(decision_path) != P3_ASSURANCE_COMPILER_REVIEW_DECISION_HASH:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler review decision file hash drift"))
    else:
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("decision") != "APPROVED" or decision.get("open_blockers"):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-001", "p3.assurance.input_index", "compiler review decision is not approved and clear"))
        if decision.get("subject_hash") != P3_ASSURANCE_COMPILER_REVIEW_SUBJECT_HASH:
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler review decision subject hash drift"))
    refs = index.get("compiler_output_refs")
    if not isinstance(refs, Mapping):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "compiler_output_refs must be an object"))
    else:
        missing = sorted(P3_ASSURANCE_REQUIRED_COMPILER_OUTPUTS - set(refs))
        if missing:
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "missing compiler output refs: " + ", ".join(missing)))
        extra = sorted(set(refs) - P3_ASSURANCE_REQUIRED_COMPILER_OUTPUTS)
        if extra:
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "unknown compiler output refs: " + ", ".join(extra)))
        for path, expected_hash in sorted(refs.items()):
            if not _is_sha256(expected_hash):
                findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, "compiler output ref hash must be sha256"))
            elif not Path(path).is_file():
                findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, "compiler output ref path is missing"))
            elif _sha256_file(Path(path)) != expected_hash:
                findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, "compiler output ref hash drift"))
    traceability_refs = index.get("traceability_refs")
    if not _non_empty_text_list(traceability_refs):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "traceability_refs must be non-empty"))
    else:
        for path in traceability_refs:
            if not Path(path).is_file():
                findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, "traceability ref path is missing"))
    schema_refs = index.get("schema_refs")
    schema_hashes = index.get("schema_hashes")
    if not _non_empty_text_list(schema_refs):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "schema_refs must be non-empty"))
    elif not isinstance(schema_hashes, Mapping):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "schema_hashes must be present"))
    else:
        for path in schema_refs:
            findings.extend(_validate_indexed_file_hash("schema", path, schema_hashes))
    validator_refs = index.get("validator_refs")
    validator_hashes = index.get("validator_hashes")
    if not _non_empty_text_list(validator_refs):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "validator_refs must be non-empty"))
    elif not isinstance(validator_hashes, Mapping):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "validator_hashes must be present"))
    else:
        for path in validator_refs:
            findings.extend(_validate_indexed_file_hash("validator", path, validator_hashes))
    if not _non_empty_text_list(index.get("invalidation_inputs")):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", "p3.assurance.input_index", "invalidation_inputs must be non-empty"))
    return findings


def _validate_p3_assurance_qa_boundary(boundary: Mapping[str, Any]) -> List[TraceabilityFinding]:
    findings = [
        TraceabilityFinding(finding.code, finding.subject_id, finding.message)
        for finding in validate_read_only_qa_boundary(boundary)
    ]
    if boundary.get("mutation_claim") != "NO_MUTATION":
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-003", "p3.assurance.read_only_qa_boundary", "mutation_claim must be NO_MUTATION"))
    written_paths = boundary.get("written_paths", [])
    if not isinstance(written_paths, list) or set(written_paths) - {"READ_ONLY_QA_REPORT.md", "qa_finding_index.json"}:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-003", "p3.assurance.read_only_qa_boundary", "DRD-06 wrote outside allowed QA outputs"))
    return findings


def _validate_p3_assurance_workpack_index(
    index: Mapping[str, Any],
    workpack: Mapping[str, Any],
    trace_rows: Sequence[Mapping[str, Any]],
) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    trace_ids = {str(row.get("trace_row_id")) for row in trace_rows if row.get("trace_row_id")}
    generated_at = str(index.get("generated_at") or "")
    if not generated_at.startswith("P3-ASSURANCE-RUN-"):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-010", str(index.get("index_id") or "workpack_index"), "generated_at must be deterministic from assurance run id"))
    indexed_workpack_ids = {
        str(row.get("workpack_id"))
        for row in index.get("workpacks", [])
        if isinstance(row, Mapping) and row.get("workpack_id")
    }
    workpack_id = str(workpack.get("workpack_id") or "workpack")
    if workpack_id not in indexed_workpack_ids:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-008", workpack_id, "workpack template is missing from implementation workpack index"))
    indexed_rows = set()
    for row in index.get("workpacks", []) if isinstance(index.get("workpacks"), list) else []:
        for trace_id in row.get("traceability_rows", []):
            indexed_rows.add(str(trace_id))
    missing = sorted(trace_ids - indexed_rows)
    if missing:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-008", str(index.get("index_id") or "workpack_index"), "trace rows missing from workpack index: " + ", ".join(missing)))
    orphan = sorted(set(workpack.get("traceability_rows", [])) - trace_ids)
    if orphan:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-008", str(workpack.get("workpack_id") or "workpack"), "workpack template references unknown trace rows: " + ", ".join(orphan)))
    findings.extend(validate_orphan_code_targets(workpack.get("code_targets", []), trace_rows))
    return findings


def _validate_p3_assurance_skill_binding(
    manifest: Mapping[str, Any],
    trace_rows: Sequence[Mapping[str, Any]],
) -> List[TraceabilityFinding]:
    findings = _scope_findings(validate_skill_binding_manifest(manifest))
    trace_ids = {str(row.get("trace_row_id")) for row in trace_rows if row.get("trace_row_id")}
    missing = sorted(set(manifest.get("traceability_rows", [])) - trace_ids)
    if missing:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-011", str(manifest.get("skill_id") or "skill"), "skill binding references unknown trace rows: " + ", ".join(missing)))
    source_path = Path(str(manifest.get("skill_source_path") or ""))
    if source_path.is_file():
        if _sha256_file(source_path) != manifest.get("skill_source_hash"):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-011", str(manifest.get("skill_id") or "skill"), "skill source hash drift"))
        findings.extend(validate_skill_text_no_second_authority(source_path.read_text(encoding="utf-8")))
    else:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-011", str(manifest.get("skill_id") or "skill"), "skill source path is missing"))
    return findings


def _validate_p3_assurance_exceptions(records: Sequence[Mapping[str, Any]]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    for record in records:
        exception_id = str(record.get("exception_id") or "traceability_exception")
        if not record.get("human_gate_decision_ref"):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-012", exception_id, "traceability exception lacks human gate decision"))
        if not record.get("scope_delta"):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-012", exception_id, "traceability exception lacks scope_delta"))
    return findings


def _validate_p3_final_assurance_report(report: Mapping[str, Any]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    subject = str(report.get("report_id") or "final_assurance_report")
    if report.get("status") == "PASS":
        for field in sorted(P3_ASSURANCE_PASS_STATUSES):
            if report.get(field) != "PASS":
                findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, f"{field} must be PASS when final report passes"))
        if report.get("blocking_findings"):
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "final assurance cannot pass with blocking findings"))
        if report.get("human_gate_required") is not True:
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "human_gate_required must be true"))
        if report.get("lock_creation_allowed") is not False:
            findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "assurance cannot allow lock creation inside this candidate"))
    return findings


def _validate_p3_final_review_packet(packet: Mapping[str, Any], report: Mapping[str, Any]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    subject = str(packet.get("packet_id") or "final_review_packet")
    if packet.get("promotion_claim") != "NOT_PROMOTED":
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "final review packet must not claim promotion"))
    if packet.get("lock_readiness") != "READY_FOR_SEPARATE_EXPLICIT_REQUEST":
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "lock readiness must remain a separate explicit request"))
    if report.get("blocking_findings") and not packet.get("unresolved_findings"):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-013", subject, "packet must expose unresolved report findings"))
    return findings


def _scope_findings(findings: Iterable[Any]) -> List[TraceabilityFinding]:
    return [TraceabilityFinding(finding.code, finding.subject_id, finding.message) for finding in findings]


def _validate_indexed_file_hash(kind: str, path: str, expected_hashes: Mapping[str, Any]) -> List[TraceabilityFinding]:
    findings: List[TraceabilityFinding] = []
    expected_hash = expected_hashes.get(path)
    if not _is_sha256(expected_hash):
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, f"{kind} hash must be sha256"))
    elif not Path(path).is_file():
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, f"{kind} ref path is missing"))
    elif _sha256_file(Path(path)) != expected_hash:
        findings.append(TraceabilityFinding("P3ASSURE-CHECK-002", path, f"{kind} hash drift"))
    return findings


def _payload_mapping(artifact: Mapping[str, Any], payload_key: str) -> Mapping[str, Any]:
    payload = artifact.get(payload_key)
    if not isinstance(payload, Mapping):
        raise KeyError(f"{payload_key} payload must be an object")
    return payload


def _payload_records(artifact: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    records = artifact.get("records")
    if not isinstance(records, list):
        raise KeyError("records payload must be a list")
    return [record for record in records if isinstance(record, Mapping)]


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _non_empty_text_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _text_values(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []
