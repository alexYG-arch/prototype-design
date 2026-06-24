"""Validation helpers for candidate state, output coverage, and review binding."""

import hashlib
import json
import platform
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Sequence


HASH_RE = re.compile(r"^[a-f0-9]{64}$")
PLACEHOLDER_MARKERS = ("T" + "BD", "TO" + "DO", "FIXME", "PLACEHOLDER", "TO_BE_FILLED")
SELF_APPROVAL_STATES = {"APPROVED_BY_CODEX", "SELF_APPROVED", "CODEX_APPROVED"}
LOCKED_STATES = {"LOCKED", "SEALED"}
PROMOTED_STATES = {"PROMOTED"}


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    subject_id: str
    message: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_candidate_subject_hash(candidate_dir: Path, generated_outputs: Sequence[str]) -> str:
    rows = []
    for rel_path in generated_outputs:
        file_hash = sha256_file(_candidate_output_path(candidate_dir, rel_path))
        rows.append(f"{rel_path}\0{file_hash}")
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def validate_candidate_only_state(manifest: Mapping[str, Any]) -> List[ValidationFinding]:
    subject_id = str(manifest.get("workpack_id") or manifest.get("candidate_id") or "candidate")
    findings: List[ValidationFinding] = []

    approval_state = str(manifest.get("approval_state", "CANDIDATE"))
    if approval_state in SELF_APPROVAL_STATES:
        findings.append(
            ValidationFinding("VLOCK-CHECK-001", subject_id, "candidate claims Codex or self approval")
        )

    status = str(manifest.get("status", "CANDIDATE"))
    if status in PROMOTED_STATES:
        findings.append(ValidationFinding("VLOCK-CHECK-001", subject_id, "candidate claims promoted state"))

    seal_state = str(manifest.get("seal_state", manifest.get("build_lock_state", "NOT_LOCKED")))
    if seal_state in LOCKED_STATES:
        findings.append(ValidationFinding("VLOCK-CHECK-008", subject_id, "candidate claims locked state"))

    if approval_state == "APPROVED_BY_HUMAN" and not manifest.get("review_decision"):
        findings.append(
            ValidationFinding("VLOCK-CHECK-005", subject_id, "human approval must name a review decision")
        )

    return findings


def validate_required_outputs(candidate_dir: Path, manifest: Mapping[str, Any]) -> List[ValidationFinding]:
    subject_id = str(manifest.get("workpack_id") or manifest.get("candidate_id") or "candidate")
    outputs = manifest.get("generated_outputs")
    findings: List[ValidationFinding] = []
    if not isinstance(outputs, list) or not outputs:
        return [ValidationFinding("VLOCK-CHECK-002", subject_id, "generated_outputs must be a non-empty list")]

    for rel_path in outputs:
        if not isinstance(rel_path, str) or not rel_path:
            findings.append(ValidationFinding("VLOCK-CHECK-002", subject_id, "generated output path is empty"))
            continue
        try:
            path = _candidate_output_path(candidate_dir, rel_path)
        except ValueError as exc:
            findings.append(ValidationFinding("VLOCK-CHECK-002", rel_path, str(exc)))
            continue
        if not path.is_file():
            findings.append(ValidationFinding("VLOCK-CHECK-002", rel_path, "generated output is missing"))
            continue
        if path.stat().st_size == 0:
            findings.append(ValidationFinding("VLOCK-CHECK-002", rel_path, "generated output is empty"))
            continue
        text = path.read_text(encoding="utf-8")
        markers = [marker for marker in PLACEHOLDER_MARKERS if marker in text.upper()]
        if markers:
            findings.append(
                ValidationFinding("VLOCK-CHECK-002", rel_path, "generated output contains placeholder markers")
            )
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                findings.append(ValidationFinding("VLOCK-CHECK-002", rel_path, f"invalid JSON: {exc}"))
    return findings


def validate_review_binding(
    candidate_dir: Path,
    manifest: Mapping[str, Any],
    review_decision: Mapping[str, Any],
) -> List[ValidationFinding]:
    subject_id = str(manifest.get("workpack_id") or manifest.get("candidate_id") or "candidate")
    outputs = manifest.get("generated_outputs", [])
    if not isinstance(outputs, list):
        return [ValidationFinding("VLOCK-CHECK-005", subject_id, "generated_outputs must be a list")]

    try:
        current_hash = compute_candidate_subject_hash(candidate_dir, outputs)
    except (FileNotFoundError, ValueError) as exc:
        return [ValidationFinding("VLOCK-CHECK-005", subject_id, f"review subject cannot be hashed: {exc}")]
    findings: List[ValidationFinding] = []
    if review_decision.get("decision") != "APPROVED":
        findings.append(ValidationFinding("VLOCK-CHECK-005", subject_id, "review decision must be APPROVED"))
    if review_decision.get("subject_hash") != current_hash:
        findings.append(ValidationFinding("VLOCK-CHECK-005", subject_id, "review subject_hash is stale"))
    if review_decision.get("open_blockers"):
        findings.append(ValidationFinding("VLOCK-CHECK-005", subject_id, "approved review has open blockers"))
    if not review_decision.get("reviewer"):
        findings.append(ValidationFinding("VLOCK-CHECK-005", subject_id, "review decision lacks reviewer"))
    approved_sections = review_decision.get("approved_sections")
    if review_decision.get("decision") == "APPROVED" and not approved_sections:
        findings.append(ValidationFinding("VLOCK-CHECK-005", subject_id, "approval lacks approved sections"))
    return findings


def validate_validator_identity(identity: Mapping[str, Any]) -> List[ValidationFinding]:
    validator_id = str(identity.get("validator_id") or "validator")
    findings: List[ValidationFinding] = []
    required_text_fields = [
        "validator_id",
        "validator_kind",
        "validator_version",
        "validator_code_hash",
        "runtime_identity",
        "result_hash",
    ]
    for field in required_text_fields:
        if not identity.get(field):
            findings.append(ValidationFinding("VLOCK-CHECK-004", validator_id, f"{field} is required"))

    for field in ("validator_code_hash", "result_hash"):
        value = identity.get(field)
        if value and not _is_hash(value):
            findings.append(ValidationFinding("VLOCK-CHECK-004", validator_id, f"{field} must be sha256"))

    schema_hashes = identity.get("schema_hashes")
    if not isinstance(schema_hashes, Mapping) or not schema_hashes:
        findings.append(ValidationFinding("VLOCK-CHECK-004", validator_id, "schema_hashes must be non-empty"))
    else:
        for schema_name, schema_hash in schema_hashes.items():
            if not schema_name or not _is_hash(schema_hash):
                findings.append(ValidationFinding("VLOCK-CHECK-004", validator_id, "schema hash must be sha256"))
    return findings


def validate_validation_result(result: Mapping[str, Any], subject_hash: str) -> List[ValidationFinding]:
    result_id = str(result.get("result_id") or "validation_result")
    findings: List[ValidationFinding] = []
    if result.get("checked_subject_hash") != subject_hash:
        findings.append(ValidationFinding("VLOCK-CHECK-004", result_id, "validation result checked_subject_hash mismatch"))
    if not result.get("command"):
        findings.append(ValidationFinding("VLOCK-CHECK-004", result_id, "validation result command is required"))
    if result.get("exit_code") != 0:
        findings.append(ValidationFinding("VLOCK-CHECK-006", result_id, "validation result exit_code must be 0"))
    if not _is_hash(result.get("result_hash")):
        findings.append(ValidationFinding("VLOCK-CHECK-004", result_id, "validation result_hash must be sha256"))
    status = str(result.get("status", "")).upper()
    if status not in {"PASS", "PASSED"}:
        findings.append(ValidationFinding("VLOCK-CHECK-006", result_id, "validation result is not passing"))
    identity = result.get("validator_identity")
    if not isinstance(identity, Mapping):
        findings.append(ValidationFinding("VLOCK-CHECK-004", result_id, "validator_identity is required"))
    else:
        findings.extend(validate_validator_identity(identity))
    return findings


def runtime_identity() -> str:
    return f"python-{platform.python_version()}"


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.match(value) is not None


def _candidate_output_path(candidate_dir: Path, rel_path: str) -> Path:
    if Path(rel_path).is_absolute():
        raise ValueError("generated output path must be relative to candidate directory")
    candidate_root = candidate_dir.resolve()
    output_path = (candidate_root / rel_path).resolve()
    try:
        output_path.relative_to(candidate_root)
    except ValueError as exc:
        raise ValueError("generated output path escapes candidate directory") from exc
    return output_path
