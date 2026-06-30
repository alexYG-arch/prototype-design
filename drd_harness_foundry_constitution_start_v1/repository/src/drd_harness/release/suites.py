"""P4 release suite report contracts.

The functions in this module build deterministic, in-memory evidence reports.
They do not update golden outputs, publish packages, or create locks.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from drd_harness.kernel.hashline import sha256_text


SUITE_IDS = {"GOLDEN", "INTEGRATION", "RELEASE"}
ALLOWED_STATUS_VALUES = {
    "PASS",
    "FAIL",
    "BLOCKED_HUMAN_REVIEW",
    "BLOCKED_LOCK_BOUNDARY",
    "BLOCKED_UNSAFE_STATE",
}
SHARED_REPORT_REQUIRED_FIELDS = [
    "suite_id",
    "run_id",
    "command",
    "input_hashes",
    "upstream_lock_refs",
    "status",
    "findings",
    "exit_code",
    "started_at",
    "finished_at",
    "report_hash",
]
REQUIRED_INTEGRATION_COVERAGE = {
    "cli",
    "adapters",
    "program_driver",
    "recovery",
    "human_gate",
    "lock_gate",
    "write_scope",
}
REQUIRED_RELEASE_EVIDENCE = {
    "package_dry_run_report",
    "example_project_smoke_report",
    "migration_coverage_report",
    "release_readiness_packet",
}
FORBIDDEN_RELEASE_ACTIONS = {
    "publish_package",
    "create_DRD_HARNESS_RELEASE_LOCK",
    "upload_artifacts_to_external_registry",
}


@dataclass(frozen=True)
class SuiteFinding:
    code: str
    subject_id: str
    message: str


def compute_report_hash(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("report_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)


def validate_suite_report(report: Mapping[str, Any]) -> List[SuiteFinding]:
    findings: List[SuiteFinding] = []
    suite_id = str(report.get("suite_id", "suite_report"))
    for field in SHARED_REPORT_REQUIRED_FIELDS:
        if field not in report:
            findings.append(SuiteFinding("P4REL-SUITE-001", suite_id, f"{field} is required"))
    if report.get("suite_id") not in SUITE_IDS:
        findings.append(SuiteFinding("P4REL-SUITE-002", suite_id, "suite_id is unsupported"))
    if report.get("status") not in ALLOWED_STATUS_VALUES:
        findings.append(SuiteFinding("P4REL-SUITE-003", suite_id, "status is unsupported"))
    if not isinstance(report.get("findings", []), list):
        findings.append(SuiteFinding("P4REL-SUITE-004", suite_id, "findings must be a list"))
    input_hashes = report.get("input_hashes", {})
    if not isinstance(input_hashes, Mapping):
        findings.append(SuiteFinding("P4REL-SUITE-006", suite_id, "input_hashes must be an object"))
    else:
        findings.extend(_hash_findings(input_hashes, "P4REL-SUITE-INPUT-HASH", "input hash must be sha256"))
    expected_hash = report.get("report_hash")
    if not _is_sha256(expected_hash):
        findings.append(SuiteFinding("P4REL-SUITE-005", suite_id, "report_hash must be sha256"))
    elif expected_hash != compute_report_hash(report):
        findings.append(SuiteFinding("P4REL-SUITE-005", suite_id, "report_hash mismatch"))
    return findings


def build_suite_report(
    *,
    suite_id: str,
    command: str,
    input_hashes: Mapping[str, str],
    upstream_lock_refs: Iterable[str],
    status: str,
    findings: Iterable[SuiteFinding | Mapping[str, Any]] = (),
    exit_code: Optional[int] = None,
    started_at: str = "1970-01-01T00:00:00Z",
    finished_at: str = "1970-01-01T00:00:00Z",
    **extra: Any,
) -> dict:
    input_rows = [f"{key}\0{value}" for key, value in sorted(input_hashes.items())]
    report = {
        "suite_id": suite_id,
        "run_id": _stable_id("suite-run", [suite_id, command] + input_rows + sorted(upstream_lock_refs)),
        "command": command,
        "input_hashes": _sorted_mapping(input_hashes),
        "upstream_lock_refs": sorted(str(ref) for ref in upstream_lock_refs),
        "status": status,
        "findings": _finding_dicts(findings),
        "exit_code": 0 if exit_code is None and status == "PASS" else 1 if exit_code is None else exit_code,
        "started_at": started_at,
        "finished_at": finished_at,
    }
    report.update(extra)
    report["report_hash"] = compute_report_hash(report)
    return report


def run_golden_suite(
    *,
    command: str,
    input_hashes: Mapping[str, str],
    upstream_lock_refs: Iterable[str],
    expected_output_hashes: Mapping[str, str],
    actual_output_hashes: Mapping[str, str],
    fixture_hash_report: Optional[Mapping[str, str]] = None,
    update_expected: bool = False,
) -> dict:
    findings: List[SuiteFinding] = []
    findings.extend(_hash_findings(input_hashes, "P4REL-SUITE-INPUT-HASH", "input hash must be sha256"))
    findings.extend(_hash_findings(expected_output_hashes, "P4REL-GOLDEN-EXPECTED-HASH", "expected output hash must be sha256"))
    findings.extend(_hash_findings(actual_output_hashes, "P4REL-GOLDEN-ACTUAL-HASH", "actual output hash must be sha256"))
    comparisons = []
    for output_id, expected_hash in sorted(expected_output_hashes.items()):
        actual_hash = actual_output_hashes.get(output_id)
        if actual_hash is None:
            findings.append(SuiteFinding("P4REL-GOLDEN-MISSING", output_id, "expected output is missing"))
        elif actual_hash != expected_hash:
            findings.append(SuiteFinding("P4REL-GOLDEN-CHANGED", output_id, "expected output hash changed"))
        comparisons.append({"output_id": output_id, "expected_sha256": expected_hash, "actual_sha256": actual_hash})
    for output_id in sorted(set(actual_output_hashes) - set(expected_output_hashes)):
        findings.append(SuiteFinding("P4REL-GOLDEN-UNEXPECTED", output_id, "unexpected output was produced"))
    if update_expected:
        findings.append(
            SuiteFinding(
                "P4REL-GOLDEN-UPDATE-REQUESTED",
                "golden_update_policy",
                "golden expected outputs cannot be rewritten during release checks",
            )
        )
    status = _golden_status(findings, update_expected)
    return build_suite_report(
        suite_id="GOLDEN",
        command=command,
        input_hashes=input_hashes,
        upstream_lock_refs=upstream_lock_refs,
        status=status,
        findings=findings,
        fixture_hash_report=_sorted_mapping(fixture_hash_report or {}),
        output_hash_comparison=comparisons,
        unexpected_diff_report=_finding_dicts(findings),
        golden_update_policy={"requested": update_expected, "allowed": False},
        rewritten_expected_outputs=False,
    )


def run_integration_suite(
    *,
    command: str,
    input_hashes: Mapping[str, str],
    upstream_lock_refs: Iterable[str],
    coverage_evidence: Mapping[str, bool],
    command_status_payloads: Iterable[Mapping[str, Any]],
    gate_stop_report: Mapping[str, Any],
    write_scope_report: Mapping[str, Any],
) -> dict:
    findings: List[SuiteFinding] = []
    findings.extend(_hash_findings(input_hashes, "P4REL-SUITE-INPUT-HASH", "input hash must be sha256"))
    missing_coverage = sorted(area for area in REQUIRED_INTEGRATION_COVERAGE if not coverage_evidence.get(area))
    for area in missing_coverage:
        findings.append(SuiteFinding("P4REL-INTEGRATION-COVERAGE-MISSING", area, "required integration coverage is missing"))
    payloads = [dict(payload) for payload in command_status_payloads]
    for index, payload in enumerate(payloads):
        missing = sorted({"command", "status", "run_id", "written_paths", "findings", "exit_code"} - set(payload))
        if missing:
            findings.append(SuiteFinding("P4REL-INTEGRATION-PAYLOAD-SHAPE", str(index), "payload missing fields: " + ", ".join(missing)))
        if "written_paths" in payload and not isinstance(payload["written_paths"], list):
            findings.append(SuiteFinding("P4REL-INTEGRATION-PAYLOAD-SHAPE", str(index), "written_paths must be a list"))
        if "findings" in payload and not isinstance(payload["findings"], list):
            findings.append(SuiteFinding("P4REL-INTEGRATION-PAYLOAD-SHAPE", str(index), "findings must be a list"))
        if "exit_code" in payload and not isinstance(payload["exit_code"], int):
            findings.append(SuiteFinding("P4REL-INTEGRATION-PAYLOAD-SHAPE", str(index), "exit_code must be an integer"))
    if gate_stop_report.get("human_gate_bypassed") is True:
        findings.append(SuiteFinding("P4REL-INTEGRATION-HUMAN-GATE-BYPASS", "human_gate", "Human Gate was bypassed"))
    if gate_stop_report.get("lock_gate_bypassed") is True:
        findings.append(SuiteFinding("P4REL-INTEGRATION-LOCK-GATE-BYPASS", "lock_gate", "lock gate was bypassed"))
    violations = list(write_scope_report.get("violations", []))
    if write_scope_report.get("status") == "FAIL" or violations:
        findings.append(SuiteFinding("P4REL-INTEGRATION-WRITE-SCOPE", "write_scope", "write scope violations are present"))
    status = _integration_status(findings)
    return build_suite_report(
        suite_id="INTEGRATION",
        command=command,
        input_hashes=input_hashes,
        upstream_lock_refs=upstream_lock_refs,
        status=status,
        findings=findings,
        command_status_payloads=sorted(payloads, key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))),
        gate_stop_report=dict(gate_stop_report),
        write_scope_report=dict(write_scope_report),
        coverage_report={key: bool(coverage_evidence.get(key)) for key in sorted(REQUIRED_INTEGRATION_COVERAGE)},
    )


def run_release_suite(
    *,
    command: str,
    input_hashes: Mapping[str, str],
    upstream_lock_refs: Iterable[str],
    evidence_hashes: Mapping[str, str],
    requested_actions: Iterable[str] = (),
) -> dict:
    findings: List[SuiteFinding] = []
    findings.extend(_hash_findings(input_hashes, "P4REL-SUITE-INPUT-HASH", "input hash must be sha256"))
    missing_evidence = sorted(key for key in REQUIRED_RELEASE_EVIDENCE if key not in evidence_hashes)
    for key in missing_evidence:
        findings.append(SuiteFinding("P4REL-RELEASE-EVIDENCE-MISSING", key, "required release suite evidence is missing"))
    forbidden = sorted(set(requested_actions) & FORBIDDEN_RELEASE_ACTIONS)
    for action in forbidden:
        findings.append(SuiteFinding("P4REL-RELEASE-FORBIDDEN-ACTION", action, "release suite cannot perform this action"))
    findings.extend(_hash_findings(evidence_hashes, "P4REL-RELEASE-EVIDENCE-HASH", "evidence hash must be sha256"))
    status = _release_status(findings, forbidden)
    return build_suite_report(
        suite_id="RELEASE",
        command=command,
        input_hashes=input_hashes,
        upstream_lock_refs=upstream_lock_refs,
        status=status,
        findings=findings,
        package_dry_run_report=evidence_hashes.get("package_dry_run_report"),
        example_project_smoke_report=evidence_hashes.get("example_project_smoke_report"),
        migration_coverage_report=evidence_hashes.get("migration_coverage_report"),
        release_readiness_verification=evidence_hashes.get("release_readiness_packet"),
        forbidden_actions_requested=forbidden,
        would_publish_package=False,
        would_create_release_lock=False,
    )


def _golden_status(findings: Iterable[SuiteFinding], update_expected: bool) -> str:
    codes = {finding.code for finding in findings}
    if {"P4REL-SUITE-INPUT-HASH", "P4REL-GOLDEN-EXPECTED-HASH", "P4REL-GOLDEN-ACTUAL-HASH"} & codes:
        return "BLOCKED_UNSAFE_STATE"
    if update_expected:
        return "BLOCKED_HUMAN_REVIEW"
    if findings:
        return "FAIL"
    return "PASS"


def _integration_status(findings: Iterable[SuiteFinding]) -> str:
    codes = {finding.code for finding in findings}
    if "P4REL-INTEGRATION-HUMAN-GATE-BYPASS" in codes:
        return "BLOCKED_HUMAN_REVIEW"
    if "P4REL-INTEGRATION-LOCK-GATE-BYPASS" in codes:
        return "BLOCKED_LOCK_BOUNDARY"
    if {"P4REL-SUITE-INPUT-HASH", "P4REL-INTEGRATION-PAYLOAD-SHAPE"} & codes:
        return "BLOCKED_UNSAFE_STATE"
    if findings:
        return "FAIL"
    return "PASS"


def _release_status(findings: Iterable[SuiteFinding], forbidden: Iterable[str]) -> str:
    if list(forbidden):
        return "BLOCKED_LOCK_BOUNDARY"
    if {finding.code for finding in findings} & {"P4REL-SUITE-INPUT-HASH", "P4REL-RELEASE-EVIDENCE-HASH"}:
        return "BLOCKED_UNSAFE_STATE"
    if findings:
        return "FAIL"
    return "PASS"


def _finding_dicts(findings: Iterable[SuiteFinding | Mapping[str, Any]]) -> List[dict]:
    rows = [asdict(finding) if isinstance(finding, SuiteFinding) else dict(finding) for finding in findings]
    return sorted(rows, key=lambda row: (row.get("code", ""), row.get("subject_id", ""), row.get("message", "")))


def _sorted_mapping(value: Mapping[str, str]) -> dict:
    return {key: value[key] for key in sorted(value)}


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _hash_findings(values: Mapping[str, str], code: str, message: str) -> List[SuiteFinding]:
    return [SuiteFinding(code, key, message) for key, value in sorted(values.items()) if not _is_sha256(value)]


def _stable_id(prefix: str, parts: Iterable[str]) -> str:
    normalized = json.dumps([str(part) for part in parts], sort_keys=True, separators=(",", ":"))
    return f"{prefix}-{sha256_text(normalized)[:16]}"
