"""P3 compiler artifact-set validators."""

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.compiler.final_drd import CompilerFailure, compile_final_drd
from drd_harness.validators.compiler_conservation import (
    CompilerFinding,
    compute_semantic_content_hash,
    validate_compiler_output_package,
    validate_final_manifest,
    validate_input_bundle,
    validate_read_only_qa_boundary,
)


REQUIRED_ARTIFACT_ENVELOPE_FIELDS = {
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

P3_COMPILER_VALIDATOR_REF = "repository/src/drd_harness/validators/p3_compiler.py"
COMPILER_VALIDATOR_REF = "repository/src/drd_harness/validators/compiler_conservation.py"
FINAL_DRD_VALIDATOR_REF = "repository/src/drd_harness/compiler/final_drd.py"

P3_COMPILER_ARTIFACTS = {
    "compiler_input_bundle": (
        "p3.compiler.input_bundle",
        "bundle",
        "repository/schemas/compiler/compiler_input_bundle.schema.json",
        "f61eeeb0aee5576b438e32a78a73efbc31b5f226e79b47b0b0385c74bdc8d163",
        "repository/fixtures/p3/compiler/compiler_input_bundle.json",
        {P3_COMPILER_VALIDATOR_REF, COMPILER_VALIDATOR_REF},
    ),
    "compiler_semantic_unit_inventory": (
        "p3.compiler.semantic_unit_inventory",
        "inventory",
        "repository/schemas/compiler/compiler_semantic_unit_inventory.schema.json",
        "825baeaeeaf0b329cf7f67e0ec62668024e82172be08573b7605278405c862d2",
        "repository/fixtures/p3/compiler/compiler_semantic_unit_inventory.json",
        {P3_COMPILER_VALIDATOR_REF, COMPILER_VALIDATOR_REF},
    ),
    "compiler_conservation_report": (
        "p3.compiler.conservation_report",
        "report",
        "repository/schemas/compiler/compiler_conservation_report.schema.json",
        "05125c0f0314d07c9f021a064ab47bc77b73cd399f9748ca98cb1764635c56ab",
        "repository/fixtures/p3/compiler/compiler_conservation_report.json",
        {P3_COMPILER_VALIDATOR_REF, COMPILER_VALIDATOR_REF},
    ),
    "final_drd_manifest": (
        "p3.compiler.final_drd_manifest",
        "manifest",
        "repository/schemas/compiler/final_drd_manifest.schema.json",
        "f7ba25af69444091c8368f94bd6a3bfc3bd5fc75131c276ac168edac81cabcc1",
        "repository/fixtures/p3/compiler/final_drd_manifest.json",
        {P3_COMPILER_VALIDATOR_REF, COMPILER_VALIDATOR_REF},
    ),
    "final_drd_toc": (
        "p3.compiler.final_drd_toc",
        "records",
        "repository/schemas/compiler/final_drd_toc.schema.json",
        "893b3eae6362d9fdc6b03caa4233d39748b70c9a7ca4fa3f3d3097be4f613f08",
        "repository/fixtures/p3/compiler/final_drd_toc.json",
        {P3_COMPILER_VALIDATOR_REF, FINAL_DRD_VALIDATOR_REF},
    ),
    "final_drd_reference_index": (
        "p3.compiler.final_drd_reference_index",
        "records",
        "repository/schemas/compiler/final_drd_reference_index.schema.json",
        "b161948c58fe31f986ef0e32edc26b61c5407969d6db01500bb37237e9776b81",
        "repository/fixtures/p3/compiler/final_drd_reference_index.json",
        {P3_COMPILER_VALIDATOR_REF, FINAL_DRD_VALIDATOR_REF},
    ),
    "final_drd_hash_index": (
        "p3.compiler.final_drd_hash_index",
        "index",
        "repository/schemas/compiler/final_drd_hash_index.schema.json",
        "bde807f8a7f3ebdf6af001fbf608329f205e0411f0b2203740585b8ba81efa24",
        "repository/fixtures/p3/compiler/final_drd_hash_index.json",
        {P3_COMPILER_VALIDATOR_REF, FINAL_DRD_VALIDATOR_REF},
    ),
    "read_only_qa_boundary": (
        "p3.compiler.read_only_qa_boundary",
        "boundary",
        "repository/schemas/compiler/read_only_qa_boundary.schema.json",
        "c575117a7e20253151491455b09f91e3b64f6fb2e0ac5974275739f888015520",
        "repository/fixtures/p3/compiler/read_only_qa_boundary.json",
        {P3_COMPILER_VALIDATOR_REF, COMPILER_VALIDATOR_REF},
    ),
}

P3_REQUIRED_REVIEW_DECISIONS = {
    "P3-IMPL-SOURCE": "build_program/phases/P3/candidates/P3-IMPL-SOURCE/REVIEW_DECISION.json",
    "P3-IMPL-DISTILL": "build_program/phases/P3/candidates/P3-IMPL-DISTILL/REVIEW_DECISION.json",
    "P3-IMPL-CLOSURE": "build_program/phases/P3/candidates/P3-IMPL-CLOSURE/REVIEW_DECISION.json",
    "P3-IMPL-ELEMENTS": "build_program/phases/P3/candidates/P3-IMPL-ELEMENTS/REVIEW_DECISION.json",
    "P3-IMPL-PATTERNS": "build_program/phases/P3/candidates/P3-IMPL-PATTERNS/REVIEW_DECISION.json",
    "P3-IMPL-LAYOUT": "build_program/phases/P3/candidates/P3-IMPL-LAYOUT/REVIEW_DECISION.json",
}

P3_SCHEMA_HASHES = {
    "compiler_atomic_semantic_unit": "db67622879f11d5c1512ba803914584ae395ba7b928c4c06fec155f9dbcb0b7b",
    "compiler_conservation_report": "05125c0f0314d07c9f021a064ab47bc77b73cd399f9748ca98cb1764635c56ab",
    "compiler_input_bundle": "f61eeeb0aee5576b438e32a78a73efbc31b5f226e79b47b0b0385c74bdc8d163",
    "compiler_semantic_unit_inventory": "825baeaeeaf0b329cf7f67e0ec62668024e82172be08573b7605278405c862d2",
    "final_drd_hash_index": "bde807f8a7f3ebdf6af001fbf608329f205e0411f0b2203740585b8ba81efa24",
    "final_drd_manifest": "f7ba25af69444091c8368f94bd6a3bfc3bd5fc75131c276ac168edac81cabcc1",
    "final_drd_reference_index": "b161948c58fe31f986ef0e32edc26b61c5407969d6db01500bb37237e9776b81",
    "final_drd_toc": "893b3eae6362d9fdc6b03caa4233d39748b70c9a7ca4fa3f3d3097be4f613f08",
    "read_only_qa_boundary": "c575117a7e20253151491455b09f91e3b64f6fb2e0ac5974275739f888015520",
}

FINAL_DRD_PATH = "repository/fixtures/p3/compiler/FINAL_DRD.md"
FINAL_DRD_CODE_PATH = "repository/src/drd_harness/compiler/final_drd.py"
P3_COMPILER_PACKAGE_READ_PATHS = {
    FINAL_DRD_PATH,
    "repository/fixtures/p3/compiler/compiler_input_bundle.json",
    "repository/fixtures/p3/compiler/compiler_semantic_unit_inventory.json",
    "repository/fixtures/p3/compiler/compiler_conservation_report.json",
    "repository/fixtures/p3/compiler/final_drd_manifest.json",
    "repository/fixtures/p3/compiler/final_drd_toc.json",
    "repository/fixtures/p3/compiler/final_drd_reference_index.json",
    "repository/fixtures/p3/compiler/final_drd_hash_index.json",
}
P3_INPUT_GROUP_TYPES = {
    "approved_semantic_artifacts": "APPROVED_SEMANTIC_ARTIFACT",
    "approved_operational_indexes": "APPROVED_OPERATIONAL_INDEX",
    "review_decisions": "REVIEW_DECISION",
    "lock_refs": "SPEC_LOCK_REF",
    "validator_results": "VALIDATOR_RESULT",
    "control_indexes": "CONTROL_INDEX",
    "schemas": "SCHEMA",
}


def validate_p3_compiler_artifacts(
    *,
    compiler_input_bundle: Mapping[str, Any],
    compiler_semantic_unit_inventory: Mapping[str, Any],
    compiler_conservation_report: Mapping[str, Any],
    final_drd_manifest: Mapping[str, Any],
    final_drd_toc: Mapping[str, Any],
    final_drd_reference_index: Mapping[str, Any],
    final_drd_hash_index: Mapping[str, Any],
    read_only_qa_boundary: Mapping[str, Any],
    final_drd_text: str,
) -> List[CompilerFinding]:
    artifacts = {
        "compiler_input_bundle": compiler_input_bundle,
        "compiler_semantic_unit_inventory": compiler_semantic_unit_inventory,
        "compiler_conservation_report": compiler_conservation_report,
        "final_drd_manifest": final_drd_manifest,
        "final_drd_toc": final_drd_toc,
        "final_drd_reference_index": final_drd_reference_index,
        "final_drd_hash_index": final_drd_hash_index,
        "read_only_qa_boundary": read_only_qa_boundary,
    }
    findings: List[CompilerFinding] = []
    for name, artifact in artifacts.items():
        findings.extend(_validate_artifact_envelope(name, artifact))
        findings.extend(_validate_payload_shape(name, artifact))

    try:
        bundle = _payload_mapping(compiler_input_bundle, "bundle")
        inventory = _payload_mapping(compiler_semantic_unit_inventory, "inventory")
        report = _payload_mapping(compiler_conservation_report, "report")
        manifest = _payload_mapping(final_drd_manifest, "manifest")
        toc = _payload_records(final_drd_toc)
        reference_index = _payload_records(final_drd_reference_index)
        hash_index = _payload_mapping(final_drd_hash_index, "index")
        qa_boundary = _payload_mapping(read_only_qa_boundary, "boundary")
    except KeyError as exc:
        findings.append(CompilerFinding("COMP-CHECK-011", "p3.compiler", str(exc)))
        return findings

    findings.extend(validate_input_bundle(bundle))
    findings.extend(_validate_input_group_types(bundle))
    findings.extend(validate_compiler_output_package(bundle, inventory, report, final_drd_text))
    findings.extend(validate_final_manifest(manifest))
    findings.extend(validate_read_only_qa_boundary(qa_boundary))
    findings.extend(_validate_p3_required_fields(compiler_input_bundle, compiler_semantic_unit_inventory, compiler_conservation_report))
    findings.extend(_validate_review_decisions(bundle))
    findings.extend(_validate_schema_and_code_hashes(bundle, hash_index, manifest))
    findings.extend(_validate_output_sidecars(bundle, inventory, report, manifest, toc, reference_index, hash_index, final_drd_text))
    findings.extend(_validate_read_only_boundary(qa_boundary))
    return findings


def _validate_input_group_types(bundle: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    for group_name, expected_type in P3_INPUT_GROUP_TYPES.items():
        records = bundle.get(group_name, [])
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, Mapping):
                continue
            if record.get("input_type") != expected_type:
                subject_id = str(record.get("input_id") or record.get("path") or group_name)
                findings.append(
                    CompilerFinding(
                        "COMP-CHECK-002",
                        subject_id,
                        f"{group_name} records must use input_type {expected_type}",
                    )
                )
    return findings


def _validate_artifact_envelope(name: str, artifact: Mapping[str, Any]) -> List[CompilerFinding]:
    artifact_id, payload_key, schema_ref, schema_hash, path, validator_refs = P3_COMPILER_ARTIFACTS[name]
    findings: List[CompilerFinding] = []
    missing = sorted(REQUIRED_ARTIFACT_ENVELOPE_FIELDS - set(artifact))
    if missing:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "artifact envelope missing fields: " + ", ".join(missing)))
    if artifact.get("artifact_id") != artifact_id:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "artifact_id does not match P3 compiler contract"))
    if artifact.get("path") != path:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "path does not match P3 compiler contract"))
    if artifact.get("schema_payload_key") != payload_key:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "schema_payload_key does not match P3 compiler contract"))
    if artifact.get("schema_ref") != schema_ref:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "schema_ref does not match P3 compiler contract"))
    else:
        schema_path = Path(schema_ref)
        if not schema_path.is_file():
            findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, f"schema_ref path is missing: {schema_ref}"))
        elif _sha256_file(schema_path) != schema_hash:
            findings.append(CompilerFinding("COMP-CHECK-012", artifact_id, "schema_ref hash does not match P3 compiler contract"))
    if artifact.get("validator_ref") not in validator_refs:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "validator_ref does not match P3 compiler contract"))
    if not _non_empty_text_list(artifact.get("source_refs")):
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "source_refs must be a non-empty text list"))
    if not _non_empty_text_list(artifact.get("upstream_artifact_refs")):
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "upstream_artifact_refs must be a non-empty text list"))
    upstream_hashes = artifact.get("upstream_hashes")
    if not isinstance(upstream_hashes, Mapping) or not upstream_hashes:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "upstream_hashes must be a non-empty object"))
    elif any(not _is_sha256(value) for value in upstream_hashes.values()):
        findings.append(CompilerFinding("COMP-CHECK-012", artifact_id, "upstream_hashes values must be sha256"))
    if not _non_empty_text_list(artifact.get("invalidation_inputs")):
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "invalidation_inputs must be a non-empty text list"))
    return findings


def _validate_payload_shape(name: str, artifact: Mapping[str, Any]) -> List[CompilerFinding]:
    artifact_id, payload_key, schema_ref, _, _, _ = P3_COMPILER_ARTIFACTS[name]
    payload = artifact.get(payload_key)
    if payload_key == "records":
        if not isinstance(payload, list):
            return [CompilerFinding("COMP-CHECK-011", artifact_id, "records payload must be a list")]
        return _validate_record_rows(payload, artifact_id, schema_ref)
    if not isinstance(payload, Mapping):
        return [CompilerFinding("COMP-CHECK-011", artifact_id, f"{payload_key} payload must be an object")]
    return _validate_schema_keys(payload, artifact_id, schema_ref)


def _validate_schema_keys(payload: Mapping[str, Any], artifact_id: str, schema_ref: str) -> List[CompilerFinding]:
    schema = _load_schema(schema_ref, artifact_id)
    if isinstance(schema, CompilerFinding):
        return [schema]
    object_schema = schema.get("items") if schema.get("type") == "array" else schema
    if not isinstance(object_schema, Mapping):
        return []
    required = set(_text_values(object_schema.get("required", [])))
    properties = object_schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) and not schema.get("additionalProperties", True) else None
    payload_keys = {str(key) for key in payload}
    findings: List[CompilerFinding] = []
    missing = sorted(required - payload_keys)
    if missing:
        findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "payload missing schema fields: " + ", ".join(missing)))
    if allowed is not None:
        extra = sorted(payload_keys - allowed)
        if extra:
            findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "payload has off-schema fields: " + ", ".join(extra)))
    return findings


def _validate_record_rows(records: Sequence[object], artifact_id: str, schema_ref: str) -> List[CompilerFinding]:
    schema = _load_schema(schema_ref, artifact_id)
    if isinstance(schema, CompilerFinding):
        return [schema]
    object_schema = schema.get("items") if schema.get("type") == "array" else schema
    if not isinstance(object_schema, Mapping):
        return []
    required = set(_text_values(object_schema.get("required", [])))
    properties = object_schema.get("properties", {})
    allowed = {str(key) for key in properties} if isinstance(properties, Mapping) and not object_schema.get("additionalProperties", True) else None
    findings: List[CompilerFinding] = []
    for record in records:
        if not isinstance(record, Mapping):
            findings.append(CompilerFinding("COMP-CHECK-011", artifact_id, "record rows must be objects"))
            continue
        subject_id = str(record.get("toc_entry_id") or record.get("reference_id") or artifact_id)
        row_keys = {str(key) for key in record}
        missing = sorted(required - row_keys)
        if missing:
            findings.append(CompilerFinding("COMP-CHECK-011", subject_id, "record missing schema fields: " + ", ".join(missing)))
        if allowed is not None:
            extra = sorted(row_keys - allowed)
            if extra:
                findings.append(CompilerFinding("COMP-CHECK-011", subject_id, "record has off-schema fields: " + ", ".join(extra)))
    return findings


def _validate_p3_required_fields(
    compiler_input_bundle: Mapping[str, Any],
    compiler_semantic_unit_inventory: Mapping[str, Any],
    compiler_conservation_report: Mapping[str, Any],
) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    bundle = _payload_mapping(compiler_input_bundle, "bundle")
    for field in ("semantic_content_hash", "sections", "semantic_units", "current_hashes"):
        if not bundle.get(field):
            findings.append(CompilerFinding("COMP-CHECK-011", "p3.compiler.input_bundle", f"{field} is P3-required"))
    if compiler_semantic_unit_inventory.get("atomic_unit_validation") != "PASS":
        findings.append(CompilerFinding("COMP-CHECK-019", "p3.compiler.semantic_unit_inventory", "atomic_unit_validation must be PASS"))
    if not _non_empty_text_list(compiler_semantic_unit_inventory.get("prose_authority_refs")):
        findings.append(CompilerFinding("COMP-CHECK-011", "p3.compiler.semantic_unit_inventory", "prose_authority_refs is P3-required"))
    if compiler_conservation_report.get("status_is_blocking_when_not_pass") is not True:
        findings.append(CompilerFinding("COMP-CHECK-015", "p3.compiler.conservation_report", "non-PASS status must be blocking"))
    if not compiler_conservation_report.get("manual_review_route_for_upstream_conflict_only"):
        findings.append(CompilerFinding("COMP-CHECK-015", "p3.compiler.conservation_report", "manual review route must be limited to upstream conflict"))
    return findings


def _validate_review_decisions(bundle: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    records = {
        str(record.get("path")): record
        for record in bundle.get("review_decisions", [])
        if isinstance(record, Mapping)
    }
    missing = sorted(set(P3_REQUIRED_REVIEW_DECISIONS.values()) - set(records))
    if missing:
        findings.append(CompilerFinding("COMP-CHECK-003", "p3.compiler.review_decisions", "missing required P3 review decisions: " + ", ".join(missing)))
    for workpack_id, path in sorted(P3_REQUIRED_REVIEW_DECISIONS.items()):
        record = records.get(path)
        if record is None:
            continue
        decision_path = Path(path)
        if not decision_path.is_file():
            findings.append(CompilerFinding("COMP-CHECK-003", workpack_id, f"review decision file is missing: {path}"))
            continue
        actual_hash = _sha256_file(decision_path)
        if record.get("sha256") != actual_hash:
            findings.append(CompilerFinding("COMP-CHECK-004", workpack_id, "review decision sha256 drift"))
        try:
            decision = json.loads(decision_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(CompilerFinding("COMP-CHECK-003", workpack_id, f"review decision JSON invalid: {exc}"))
            continue
        if decision.get("decision") != "APPROVED":
            findings.append(CompilerFinding("COMP-CHECK-003", workpack_id, "review decision must be APPROVED"))
        if decision.get("subject_hash") != record.get("subject_hash"):
            findings.append(CompilerFinding("COMP-CHECK-003", workpack_id, "review decision subject_hash does not match bundle record"))
    return findings


def _validate_schema_and_code_hashes(bundle: Mapping[str, Any], hash_index: Mapping[str, Any], manifest: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    schema_hashes = bundle.get("schema_hashes")
    if not isinstance(schema_hashes, Mapping):
        return [CompilerFinding("COMP-CHECK-012", "p3.compiler.schema_hashes", "schema_hashes must be present")]
    for schema_id, expected_hash in sorted(P3_SCHEMA_HASHES.items()):
        if schema_hashes.get(schema_id) != expected_hash:
            findings.append(CompilerFinding("COMP-CHECK-012", schema_id, "bundle schema_hashes do not match current schema contract"))
        if hash_index.get("schema_hashes", {}).get(schema_id) != expected_hash:
            findings.append(CompilerFinding("COMP-CHECK-012", schema_id, "hash index schema_hashes do not match current schema contract"))
    code_path = Path(FINAL_DRD_CODE_PATH)
    if not code_path.is_file():
        findings.append(CompilerFinding("COMP-CHECK-012", "compiler_code_hash", f"compiler code path is missing: {FINAL_DRD_CODE_PATH}"))
        current_code_hash = None
    else:
        current_code_hash = _sha256_file(code_path)
    if current_code_hash and bundle.get("compiler_code_hash") != current_code_hash:
        findings.append(CompilerFinding("COMP-CHECK-012", "compiler_code_hash", "bundle compiler_code_hash does not match final_drd.py"))
    if current_code_hash and hash_index.get("compiler_code_hash") != current_code_hash:
        findings.append(CompilerFinding("COMP-CHECK-012", "compiler_code_hash", "hash index compiler_code_hash does not match final_drd.py"))
    assembly_plan = manifest.get("assembly_plan", {})
    if not isinstance(assembly_plan, Mapping):
        findings.append(CompilerFinding("COMP-CHECK-011", "final_drd_manifest", "assembly_plan must be an object"))
    else:
        if current_code_hash and assembly_plan.get("compiler_code_hash") != current_code_hash:
            findings.append(CompilerFinding("COMP-CHECK-012", "compiler_code_hash", "manifest compiler_code_hash does not match final_drd.py"))
        if assembly_plan.get("compiler_id") != bundle.get("compiler_id"):
            findings.append(CompilerFinding("COMP-CHECK-011", "final_drd_manifest", "assembly_plan compiler_id must match bundle"))
        if set(assembly_plan.get("output_files", [])) != {
            "FINAL_DRD.md",
            "final_drd_manifest.json",
            "final_drd_toc.json",
            "final_drd_reference_index.json",
            "final_drd_hash_index.json",
            "compiler_conservation_report.json",
        }:
            findings.append(CompilerFinding("COMP-CHECK-011", "final_drd_manifest", "assembly_plan output_files are incomplete"))
    return findings


def _validate_output_sidecars(
    bundle: Mapping[str, Any],
    inventory: Mapping[str, Any],
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
    toc: Sequence[Mapping[str, Any]],
    reference_index: Sequence[Mapping[str, Any]],
    hash_index: Mapping[str, Any],
    final_drd_text: str,
) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    if inventory.get("source_artifact_hash") != compute_semantic_content_hash(bundle):
        findings.append(CompilerFinding("COMP-CHECK-011", "p3.compiler.semantic_unit_inventory", "source_artifact_hash does not bind semantic content hash"))
    try:
        compiled = compile_final_drd(bundle)
    except CompilerFailure as exc:
        return [CompilerFinding(finding.code, finding.subject_id, finding.message) for finding in exc.findings]
    expected = {
        "FINAL_DRD.md": final_drd_text,
        "compiler_semantic_unit_inventory.json": inventory.get("semantic_units"),
        "compiler_conservation_report.json": dict(report),
        "final_drd_manifest.json": dict(manifest),
        "final_drd_toc.json": list(toc),
        "final_drd_reference_index.json": list(reference_index),
        "final_drd_hash_index.json": dict(hash_index),
    }
    for output_name, expected_value in expected.items():
        if expected_value != compiled[output_name]:
            findings.append(CompilerFinding("COMP-CHECK-011", output_name, "compiler sidecar does not match deterministic output"))
    if _sha256_text(final_drd_text) != hash_index.get("full_output_hash"):
        findings.append(CompilerFinding("COMP-CHECK-012", "FINAL_DRD.md", "final DRD hash does not match hash index"))
    return findings


def _validate_read_only_boundary(boundary: Mapping[str, Any]) -> List[CompilerFinding]:
    findings: List[CompilerFinding] = []
    if boundary.get("mutation_claim") != "NO_MUTATION":
        findings.append(CompilerFinding("COMP-CHECK-014", "p3.compiler.read_only_qa_boundary", "mutation_claim must be NO_MUTATION"))
    read_paths = set(_text_values(boundary.get("read_paths")))
    missing_read_paths = sorted(P3_COMPILER_PACKAGE_READ_PATHS - read_paths)
    if missing_read_paths:
        findings.append(
            CompilerFinding(
                "COMP-CHECK-014",
                "p3.compiler.read_only_qa_boundary",
                "QA read_paths missing compiler package outputs: " + ", ".join(missing_read_paths),
            )
        )
    for path in read_paths:
        if path not in P3_COMPILER_PACKAGE_READ_PATHS:
            findings.append(CompilerFinding("COMP-CHECK-014", "p3.compiler.read_only_qa_boundary", f"QA read path is outside compiler package: {path}"))
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


def _load_schema(schema_ref: str, artifact_id: str):
    path = Path(schema_ref)
    if not path.is_file():
        return CompilerFinding("COMP-CHECK-011", artifact_id, f"schema missing: {schema_ref}")
    return json.loads(path.read_text(encoding="utf-8"))


def _text_values(value: object) -> List[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
        return [str(item) for item in value if item is not None and str(item)]
    return []


def _non_empty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(_text_values(value))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
