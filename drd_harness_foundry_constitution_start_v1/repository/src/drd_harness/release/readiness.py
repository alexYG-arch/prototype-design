"""P4 release readiness packet validation.

This module builds deterministic, in-memory readiness evidence. It reports
release-lock input eligibility, but never creates locks or publishes packages.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_text


REQUIRED_PACKET_FIELDS = [
    "release_candidate_id",
    "p4_spec_lock_ref",
    "p4_build_lock_ref",
    "test_suite_reports",
    "migration_coverage_report",
    "package_manifest",
    "example_project_manifest",
    "missing_gate_list",
    "dirty_state_policy",
    "dirty_state_records",
    "release_lock_input_bundle_preview",
    "human_authorization_required",
    "readiness_packet_hash",
]
REQUIRED_SUITE_REPORTS = {"GOLDEN", "INTEGRATION", "RELEASE"}
ALLOWED_DIRTY_STATE_POLICY = {"CLEAN", "DOCUMENTED_DIRTY", "BLOCKED_DIRTY"}
REQUIRED_DIRTY_STATE_FIELDS = [
    "path",
    "git_status",
    "is_release_input",
    "classification",
    "reason",
    "required_action",
]
ALLOWED_DIRTY_CLASSIFICATION = {
    "EXCLUDED_FROM_RELEASE_INPUTS",
    "AFFECTS_RELEASE_INPUTS",
    "UNCLASSIFIED",
}
REQUIRED_PREVIEW_FIELDS = [
    "expected_bundle_id",
    "required_input_kinds",
    "missing_input_kinds",
    "blocked_until_human_authorization",
]
FORBIDDEN_PREVIEW_FIELDS = {"release_readiness_packet_hash", "bundle_hash"}
REQUIRED_LOCK_INPUT_KINDS = [
    "p4_spec_lock_ref",
    "p4_build_lock_ref",
    "approved_spec_decisions",
    "approved_build_decision",
    "suite_report_hashes",
    "package_manifest_hash",
    "example_project_manifest_hash",
    "migration_coverage_hash",
    "release_readiness_packet_hash",
    "source_git_commit",
    "required_human_authorization",
]
HASH_FIELDS = [
    "migration_coverage_report",
    "package_manifest",
    "example_project_manifest",
]
FORBIDDEN_SEMANTIC_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


@dataclass(frozen=True)
class ReadinessFinding:
    code: str
    subject_id: str
    message: str


def compute_readiness_packet_hash(packet: Mapping[str, Any]) -> str:
    payload = dict(packet)
    payload.pop("readiness_packet_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)


def build_release_readiness_packet(
    *,
    release_candidate_id: str,
    p4_spec_lock_ref: Mapping[str, Any],
    p4_build_lock_ref: Mapping[str, Any],
    test_suite_reports: Mapping[str, str],
    migration_coverage_report: str,
    package_manifest: str,
    example_project_manifest: str,
    source_git_commit: str,
    dirty_state_policy: str,
    dirty_state_records: Iterable[Mapping[str, Any]],
    missing_gate_list: Iterable[str] = (),
    human_authorization_required: bool = True,
    release_lock_input_bundle_preview: Mapping[str, Any] | None = None,
) -> dict:
    missing_gates = sorted(str(item) for item in missing_gate_list)
    if release_lock_input_bundle_preview is None:
        release_lock_input_bundle_preview = {
            "expected_bundle_id": f"release-lock-inputs-{_stable_id([release_candidate_id, source_git_commit])}",
            "required_input_kinds": list(REQUIRED_LOCK_INPUT_KINDS),
            "missing_input_kinds": missing_gates,
            "blocked_until_human_authorization": human_authorization_required,
        }
    packet = {
        "release_candidate_id": release_candidate_id,
        "p4_spec_lock_ref": dict(p4_spec_lock_ref),
        "p4_build_lock_ref": dict(p4_build_lock_ref),
        "test_suite_reports": _sorted_mapping(test_suite_reports),
        "migration_coverage_report": migration_coverage_report,
        "package_manifest": package_manifest,
        "example_project_manifest": example_project_manifest,
        "source_git_commit": source_git_commit,
        "missing_gate_list": missing_gates,
        "dirty_state_policy": dirty_state_policy,
        "dirty_state_records": sorted((dict(row) for row in dirty_state_records), key=lambda row: str(row.get("path", ""))),
        "release_lock_input_bundle_preview": dict(release_lock_input_bundle_preview),
        "human_authorization_required": human_authorization_required,
        "will_create_release_lock": False,
        "will_publish_package": False,
    }
    findings = _validate_release_readiness_packet(packet, check_hash=False)
    packet["status"] = "PASS" if not findings else _status_from_findings(findings)
    packet["release_lock_eligibility_state"] = (
        "ELIGIBLE_FOR_INPUT_BUNDLE" if not findings else "NOT_ELIGIBLE"
    )
    packet["readiness_packet_hash"] = compute_readiness_packet_hash(packet)
    return packet


def validate_release_readiness_packet(packet: Mapping[str, Any]) -> List[ReadinessFinding]:
    return _validate_release_readiness_packet(packet, check_hash=True)


def _validate_release_readiness_packet(packet: Mapping[str, Any], *, check_hash: bool) -> List[ReadinessFinding]:
    findings: List[ReadinessFinding] = []
    subject = str(packet.get("release_candidate_id", "release_readiness_packet"))
    required_fields = REQUIRED_PACKET_FIELDS if check_hash else [field for field in REQUIRED_PACKET_FIELDS if field != "readiness_packet_hash"]
    findings.extend(_required_field_findings(packet, required_fields, subject, "P4READY-CHECK-001"))
    findings.extend(_semantic_key_findings(packet, subject))
    findings.extend(_lock_ref_findings(packet.get("p4_spec_lock_ref"), "p4_spec_lock_ref"))
    findings.extend(_lock_ref_findings(packet.get("p4_build_lock_ref"), "p4_build_lock_ref"))
    findings.extend(_suite_report_findings(packet.get("test_suite_reports", {})))
    findings.extend(_hash_field_findings(packet, subject, HASH_FIELDS + ["source_git_commit"]))
    findings.extend(_missing_gate_findings(packet.get("missing_gate_list", []), subject))
    findings.extend(
        _dirty_state_findings(
            packet.get("dirty_state_policy"),
            packet.get("dirty_state_records", []),
            subject,
        )
    )
    findings.extend(
        _preview_findings(
            packet.get("release_lock_input_bundle_preview"),
            subject,
            packet.get("missing_gate_list", []),
        )
    )
    if packet.get("human_authorization_required") is not True:
        findings.append(
            ReadinessFinding(
                "P4READY-CHECK-009",
                subject,
                "release lock creation must remain blocked until explicit human authorization",
            )
        )
    if packet.get("will_create_release_lock") is True or packet.get("would_create_release_lock") is True:
        findings.append(ReadinessFinding("P4READY-CHECK-010", subject, "readiness packet cannot create a release lock"))
    if packet.get("will_publish_package") is True or packet.get("would_publish_package") is True:
        findings.append(ReadinessFinding("P4READY-CHECK-010", subject, "readiness packet cannot publish a package"))
    if "release_lock_input_bundle" in packet:
        findings.append(
            ReadinessFinding(
                "P4READY-CHECK-007",
                subject,
                "readiness packet may include only release_lock_input_bundle_preview",
            )
        )
    if check_hash:
        expected_hash = packet.get("readiness_packet_hash")
        if not _is_sha256(expected_hash):
            findings.append(ReadinessFinding("P4READY-CHECK-008", subject, "readiness_packet_hash must be sha256"))
        elif expected_hash != compute_readiness_packet_hash(packet):
            findings.append(ReadinessFinding("P4READY-CHECK-008", subject, "readiness_packet_hash mismatch"))
    return sorted(findings, key=lambda item: (item.code, item.subject_id, item.message))


def _required_field_findings(
    value: Mapping[str, Any],
    fields: Sequence[str],
    subject: str,
    code: str,
) -> List[ReadinessFinding]:
    return [ReadinessFinding(code, subject, f"{field} is required") for field in fields if field not in value]


def _lock_ref_findings(value: object, subject: str) -> List[ReadinessFinding]:
    if not isinstance(value, Mapping):
        return [ReadinessFinding("P4READY-CHECK-002", subject, "lock ref must be an object")]
    findings: List[ReadinessFinding] = []
    if not value.get("path"):
        findings.append(ReadinessFinding("P4READY-CHECK-002", subject, "lock ref path is required"))
    if not _is_sha256(value.get("sha256")):
        findings.append(ReadinessFinding("P4READY-CHECK-002", subject, "lock ref sha256 must be sha256"))
    return findings


def _suite_report_findings(value: object) -> List[ReadinessFinding]:
    if not isinstance(value, Mapping):
        return [ReadinessFinding("P4READY-CHECK-003", "test_suite_reports", "test_suite_reports must be an object")]
    findings: List[ReadinessFinding] = []
    missing = sorted(REQUIRED_SUITE_REPORTS - set(value))
    for suite_id in missing:
        findings.append(ReadinessFinding("P4READY-CHECK-003", suite_id, "required suite report hash is missing"))
    for suite_id, report_hash in sorted(value.items()):
        if not _is_sha256(report_hash):
            findings.append(ReadinessFinding("P4READY-CHECK-003", str(suite_id), "suite report hash must be sha256"))
    return findings


def _hash_field_findings(packet: Mapping[str, Any], subject: str, fields: Sequence[str]) -> List[ReadinessFinding]:
    return [
        ReadinessFinding("P4READY-CHECK-003", subject, f"{field} must be sha256")
        for field in fields
        if field in packet and not _is_sha256(packet.get(field))
    ]


def _missing_gate_findings(value: object, subject: str) -> List[ReadinessFinding]:
    if not isinstance(value, list):
        return [ReadinessFinding("P4READY-CHECK-004", subject, "missing_gate_list must be a list")]
    return [
        ReadinessFinding("P4READY-CHECK-004", str(gate), "missing release gate blocks release readiness")
        for gate in sorted(str(item) for item in value)
    ]


def _dirty_state_findings(policy: object, records: object, subject: str) -> List[ReadinessFinding]:
    findings: List[ReadinessFinding] = []
    if policy not in ALLOWED_DIRTY_STATE_POLICY:
        findings.append(ReadinessFinding("P4READY-CHECK-005", subject, "dirty_state_policy is unsupported"))
    if not isinstance(records, list):
        return findings + [ReadinessFinding("P4READY-CHECK-006", subject, "dirty_state_records must be a list")]

    if policy == "CLEAN" and records:
        findings.append(ReadinessFinding("P4READY-CHECK-006", subject, "CLEAN policy cannot include dirty records"))
    if policy == "BLOCKED_DIRTY":
        findings.append(ReadinessFinding("P4READY-CHECK-006", subject, "BLOCKED_DIRTY blocks release readiness"))

    for index, record in enumerate(records):
        record_subject = str(record.get("path", index)) if isinstance(record, Mapping) else str(index)
        if not isinstance(record, Mapping):
            findings.append(ReadinessFinding("P4READY-CHECK-006", record_subject, "dirty state record must be an object"))
            continue
        findings.extend(_required_field_findings(record, REQUIRED_DIRTY_STATE_FIELDS, record_subject, "P4READY-CHECK-006"))
        classification = record.get("classification")
        if classification not in ALLOWED_DIRTY_CLASSIFICATION:
            findings.append(ReadinessFinding("P4READY-CHECK-006", record_subject, "dirty state classification is unsupported"))
        if record.get("is_release_input") is not False and classification == "EXCLUDED_FROM_RELEASE_INPUTS":
            findings.append(ReadinessFinding("P4READY-CHECK-006", record_subject, "release inputs cannot be documented as excluded"))
        if classification in {"AFFECTS_RELEASE_INPUTS", "UNCLASSIFIED"} or record.get("is_release_input") is True:
            findings.append(ReadinessFinding("P4READY-CHECK-006", record_subject, "dirty state affects release readiness"))
        if policy == "DOCUMENTED_DIRTY" and classification != "EXCLUDED_FROM_RELEASE_INPUTS":
            findings.append(
                ReadinessFinding(
                    "P4READY-CHECK-006",
                    record_subject,
                    "DOCUMENTED_DIRTY allows only excluded non-release-input records",
                )
            )
    return findings


def _preview_findings(value: object, subject: str, missing_gate_list: object) -> List[ReadinessFinding]:
    if not isinstance(value, Mapping):
        return [
            ReadinessFinding(
                "P4READY-CHECK-007",
                subject,
                "release_lock_input_bundle_preview must be an object",
            )
        ]
    findings = _required_field_findings(value, REQUIRED_PREVIEW_FIELDS, subject, "P4READY-CHECK-007")
    forbidden = sorted(FORBIDDEN_PREVIEW_FIELDS & set(value))
    for field in forbidden:
        findings.append(ReadinessFinding("P4READY-CHECK-007", subject, f"{field} cannot appear in preview"))
    if not isinstance(value.get("required_input_kinds", []), list):
        findings.append(ReadinessFinding("P4READY-CHECK-007", subject, "required_input_kinds must be a list"))
    elif sorted(str(item) for item in value.get("required_input_kinds", [])) != sorted(REQUIRED_LOCK_INPUT_KINDS):
        findings.append(
            ReadinessFinding(
                "P4READY-CHECK-007",
                subject,
                "required_input_kinds must match release lock input contract",
            )
        )
    if not isinstance(value.get("missing_input_kinds", []), list):
        findings.append(ReadinessFinding("P4READY-CHECK-007", subject, "missing_input_kinds must be a list"))
    elif isinstance(missing_gate_list, list) and sorted(str(item) for item in value.get("missing_input_kinds", [])) != sorted(str(item) for item in missing_gate_list):
        findings.append(
            ReadinessFinding(
                "P4READY-CHECK-007",
                subject,
                "preview missing_input_kinds must match missing_gate_list",
            )
        )
    if value.get("blocked_until_human_authorization") is not True:
        findings.append(
            ReadinessFinding(
                "P4READY-CHECK-007",
                subject,
                "preview must remain blocked until human authorization",
            )
        )
    return findings


def _semantic_key_findings(value: Mapping[str, Any], subject: str) -> List[ReadinessFinding]:
    return [
        ReadinessFinding("P4REL-SEMANTIC-BOUNDARY", subject, f"{key} is outside release readiness authority")
        for key in sorted(FORBIDDEN_SEMANTIC_KEYS & set(value))
    ]


def _status_from_findings(findings: Iterable[ReadinessFinding]) -> str:
    codes = {finding.code for finding in findings}
    if {"P4READY-CHECK-002", "P4READY-CHECK-003", "P4READY-CHECK-007", "P4READY-CHECK-008"} & codes:
        return "BLOCKED_UNSAFE_STATE"
    if "P4READY-CHECK-006" in codes:
        return "BLOCKED_DIRTY"
    return "FAIL"


def _sorted_mapping(value: Mapping[str, str]) -> dict:
    return {key: value[key] for key in sorted(value)}


def _stable_id(parts: Iterable[str]) -> str:
    normalized = json.dumps([str(part) for part in parts], sort_keys=True, separators=(",", ":"))
    return sha256_text(normalized)[:16]


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def finding_dicts(findings: Iterable[ReadinessFinding | Mapping[str, Any]]) -> List[dict]:
    rows = [asdict(finding) if isinstance(finding, ReadinessFinding) else dict(finding) for finding in findings]
    return sorted(rows, key=lambda row: (row.get("code", ""), row.get("subject_id", ""), row.get("message", "")))
