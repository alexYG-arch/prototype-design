"""P4 package manifest and example project validation."""

import fnmatch
import json
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable, List, Mapping, Optional, Sequence

from drd_harness.kernel.hashline import sha256_text


REQUIRED_PACKAGE_FIELDS = [
    "package_name",
    "package_version",
    "source_git_commit",
    "source_dirty_state",
    "included_files",
    "excluded_files",
    "entrypoints",
    "dependency_lock_hash",
    "build_command",
    "package_artifact_hash",
    "dry_run_report_hash",
]
FORBIDDEN_INCLUDED_PATTERNS = [
    ".env",
    "*.pem",
    "*.key",
    ".git/**",
    "build_program/phases/**/REVIEW_DECISION.json",
    "control/locks/DRD_HARNESS_RELEASE_LOCK.json",
]
REQUIRED_EXAMPLE_FIELDS = [
    "example_id",
    "example_path",
    "source_input_refs",
    "expected_commands",
    "expected_outputs",
    "smoke_command",
    "smoke_status",
    "smoke_report_hash",
    "cleanup_policy",
]
ALLOWED_SMOKE_STATUS = {"PASS", "FAIL", "BLOCKED_HUMAN_REVIEW"}
ALLOWED_SOURCE_DIRTY_STATE = {"CLEAN", "DOCUMENTED_DIRTY", "BLOCKED_DIRTY"}
FORBIDDEN_SEMANTIC_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


@dataclass(frozen=True)
class PackageFinding:
    code: str
    subject_id: str
    message: str


def validate_package_manifest(
    manifest: Mapping[str, Any],
    *,
    tracked_release_inputs: Optional[Iterable[str]] = None,
) -> List[PackageFinding]:
    findings: List[PackageFinding] = []
    subject = str(manifest.get("package_name", "package_manifest"))
    findings.extend(_required_field_findings(manifest, REQUIRED_PACKAGE_FIELDS, subject, "P4PKG-CHECK-001"))
    findings.extend(_semantic_key_findings(manifest, subject))
    findings.extend(_hash_field_findings(manifest, subject, ["dependency_lock_hash", "package_artifact_hash", "dry_run_report_hash"]))

    tracked = set(tracked_release_inputs or [])
    included = manifest.get("included_files", [])
    if not isinstance(included, list):
        findings.append(PackageFinding("P4PKG-CHECK-002", subject, "included_files must be a list"))
        included = []
    for index, row in enumerate(included):
        file_id = _included_file_id(row, index)
        path = _included_file_path(row)
        if path is None:
            findings.append(PackageFinding("P4PKG-CHECK-002", file_id, "included file requires path"))
            continue
        findings.extend(_path_safety_findings(path, file_id))
        if _matches_forbidden(path):
            findings.append(PackageFinding("P4PKG-CHECK-003", path, "included file path is forbidden"))
        if tracked and path not in tracked:
            findings.append(PackageFinding("P4PKG-CHECK-004", path, "included release input is not tracked"))
        if not isinstance(row, Mapping) or not _is_sha256(row.get("sha256")):
            findings.append(PackageFinding("P4PKG-CHECK-005", path, "included file sha256 is required"))

    excluded = manifest.get("excluded_files", [])
    if not isinstance(excluded, list):
        findings.append(PackageFinding("P4PKG-CHECK-006", subject, "excluded_files must be a list"))
    if manifest.get("source_dirty_state") not in ALLOWED_SOURCE_DIRTY_STATE:
        findings.append(PackageFinding("P4PKG-CHECK-007", subject, "source_dirty_state is unsupported"))
    if manifest.get("source_dirty_state") == "BLOCKED_DIRTY":
        findings.append(PackageFinding("P4PKG-CHECK-007", subject, "blocked dirty state cannot pass package manifest validation"))
    return sorted(findings, key=lambda item: (item.code, item.subject_id, item.message))


def build_package_dry_run_report(manifest: Mapping[str, Any], findings: Iterable[PackageFinding | Mapping[str, Any]] = ()) -> dict:
    finding_rows = _finding_dicts(findings)
    report = {
        "report_id": _stable_id("package-dry-run", [str(manifest.get("package_name", "")), str(manifest.get("package_version", ""))]),
        "package_name": manifest.get("package_name"),
        "package_version": manifest.get("package_version"),
        "status": "PASS" if not finding_rows else "FAIL",
        "findings": finding_rows,
        "would_publish_package": False,
        "would_upload_artifacts": False,
        "would_create_lock": False,
        "included_file_count": len(manifest.get("included_files", [])) if isinstance(manifest.get("included_files"), list) else 0,
    }
    report["dry_run_report_hash"] = _self_hash(report, "dry_run_report_hash")
    return report


def validate_example_project_manifest(manifest: Mapping[str, Any]) -> List[PackageFinding]:
    findings: List[PackageFinding] = []
    subject = str(manifest.get("example_id", "example_project_manifest"))
    findings.extend(_required_field_findings(manifest, REQUIRED_EXAMPLE_FIELDS, subject, "P4EXAMPLE-CHECK-001"))
    findings.extend(_semantic_key_findings(manifest, subject))
    example_path = manifest.get("example_path")
    if isinstance(example_path, str):
        findings.extend(_path_safety_findings(example_path, subject))
        if not _is_within_example_root(example_path):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-002", subject, "example_path must stay in repository/examples/p4_release_smoke"))
    if manifest.get("smoke_status") not in ALLOWED_SMOKE_STATUS:
        findings.append(PackageFinding("P4EXAMPLE-CHECK-003", subject, "smoke_status is unsupported"))
    if not _is_sha256(manifest.get("smoke_report_hash")):
        findings.append(PackageFinding("P4EXAMPLE-CHECK-004", subject, "smoke_report_hash must be sha256"))
    findings.extend(_source_ref_findings(manifest.get("source_input_refs", []), subject))
    findings.extend(_expected_output_findings(manifest.get("expected_outputs", []), subject))
    return sorted(findings, key=lambda item: (item.code, item.subject_id, item.message))


def run_example_project_smoke(manifest: Mapping[str, Any], observed_output_hashes: Mapping[str, str]) -> dict:
    findings = validate_example_project_manifest(manifest)
    expected_outputs = manifest.get("expected_outputs", [])
    if isinstance(expected_outputs, list):
        for row in expected_outputs:
            if not isinstance(row, Mapping):
                continue
            path = str(row.get("path", ""))
            expected_hash = row.get("sha256")
            observed_hash = observed_output_hashes.get(path)
            if observed_hash is None:
                findings.append(PackageFinding("P4EXAMPLE-CHECK-005", path, "expected output was not observed"))
            elif observed_hash != expected_hash:
                findings.append(PackageFinding("P4EXAMPLE-CHECK-006", path, "expected output hash mismatch"))
    report = {
        "example_id": manifest.get("example_id"),
        "smoke_command": manifest.get("smoke_command"),
        "status": "PASS" if not findings else "FAIL",
        "findings": _finding_dicts(findings),
        "observed_output_hashes": {key: observed_output_hashes[key] for key in sorted(observed_output_hashes)},
        "would_create_product_semantics": False,
        "would_publish_package": False,
        "would_create_lock": False,
    }
    report["smoke_report_hash"] = _self_hash(report, "smoke_report_hash")
    return report


def _required_field_findings(manifest: Mapping[str, Any], fields: Sequence[str], subject: str, code: str) -> List[PackageFinding]:
    return [PackageFinding(code, subject, f"{field} is required") for field in fields if field not in manifest]


def _hash_field_findings(manifest: Mapping[str, Any], subject: str, fields: Sequence[str]) -> List[PackageFinding]:
    return [PackageFinding("P4PKG-CHECK-005", subject, f"{field} must be sha256") for field in fields if field in manifest and not _is_sha256(manifest.get(field))]


def _included_file_id(row: object, index: int) -> str:
    if isinstance(row, Mapping):
        return str(row.get("path", f"included_files[{index}]"))
    return str(row)


def _included_file_path(row: object) -> Optional[str]:
    if isinstance(row, Mapping):
        path = row.get("path")
        return str(path) if isinstance(path, str) else None
    if isinstance(row, str):
        return row
    return None


def _path_safety_findings(path: str, subject: str) -> List[PackageFinding]:
    findings: List[PackageFinding] = []
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "\\" in path:
        findings.append(PackageFinding("P4PKG-CHECK-PATH", subject, "path must be relative and cannot escape the package root"))
    return findings


def _is_within_example_root(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return len(parts) >= 3 and parts[:3] == ("repository", "examples", "p4_release_smoke")


def _matches_forbidden(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in FORBIDDEN_INCLUDED_PATTERNS)


def _source_ref_findings(rows: object, subject: str) -> List[PackageFinding]:
    if not isinstance(rows, list):
        return [PackageFinding("P4EXAMPLE-CHECK-007", subject, "source_input_refs must be a list")]
    findings: List[PackageFinding] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-007", f"source_input_refs[{index}]", "source input ref must be an object"))
            continue
        if "path" not in row or "sha256" not in row:
            findings.append(PackageFinding("P4EXAMPLE-CHECK-007", str(row.get("path", index)), "source input ref requires path and sha256"))
        elif not _is_sha256(row.get("sha256")):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-007", str(row.get("path", index)), "source input sha256 must be sha256"))
    return findings


def _expected_output_findings(rows: object, subject: str) -> List[PackageFinding]:
    if not isinstance(rows, list):
        return [PackageFinding("P4EXAMPLE-CHECK-008", subject, "expected_outputs must be a list")]
    findings: List[PackageFinding] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-008", f"expected_outputs[{index}]", "expected output must be an object"))
            continue
        path = row.get("path")
        if not isinstance(path, str):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-008", str(index), "expected output requires path"))
            continue
        findings.extend(_path_safety_findings(path, path))
        if not _is_sha256(row.get("sha256")):
            findings.append(PackageFinding("P4EXAMPLE-CHECK-008", path, "expected output sha256 must be sha256"))
    return findings


def _semantic_key_findings(manifest: Mapping[str, Any], subject: str) -> List[PackageFinding]:
    return [
        PackageFinding("P4REL-SEMANTIC-BOUNDARY", subject, f"{key} is outside release packaging authority")
        for key in sorted(FORBIDDEN_SEMANTIC_KEYS & set(manifest))
    ]


def _finding_dicts(findings: Iterable[PackageFinding | Mapping[str, Any]]) -> List[dict]:
    rows = [asdict(finding) if isinstance(finding, PackageFinding) else dict(finding) for finding in findings]
    return sorted(rows, key=lambda row: (row.get("code", ""), row.get("subject_id", ""), row.get("message", "")))


def _self_hash(payload: Mapping[str, Any], excluded_field: str) -> str:
    row = dict(payload)
    row.pop(excluded_field, None)
    return sha256_text(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _stable_id(prefix: str, parts: Iterable[str]) -> str:
    normalized = json.dumps([str(part) for part in parts], sort_keys=True, separators=(",", ":"))
    return f"{prefix}-{sha256_text(normalized)[:16]}"
