"""P4 release lock input bundle construction.

The functions here prepare candidate input evidence for a later explicit lock
creation step. They never write DRD_HARNESS_RELEASE_LOCK or publish a package.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, List, Mapping, Sequence

from drd_harness.kernel.hashline import sha256_text


REQUIRED_BUNDLE_FIELDS = [
    "bundle_id",
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
    "bundle_hash",
]
REQUIRED_SUITE_REPORTS = {"GOLDEN", "INTEGRATION", "RELEASE"}
REQUIRED_SPEC_DECISION_PATHS = {
    "build_program/phases/P4/candidates/P4-SPEC-01/REVIEW_DECISION.json",
    "build_program/phases/P4/candidates/P4-SPEC-02/REVIEW_DECISION.json",
    "build_program/phases/P4/candidates/P4-SPEC-03/REVIEW_DECISION.json",
}
HASH_FIELDS = [
    "package_manifest_hash",
    "example_project_manifest_hash",
    "migration_coverage_hash",
    "release_readiness_packet_hash",
    "source_git_commit",
]
FORBIDDEN_ACTIONS = {"create_release_lock", "rewrite_release_lock", "publish_package"}
FORBIDDEN_LOCK_OUTPUT_FIELDS = {"created_lock_path", "release_lock_path", "output_lock_path", "lock_file_written"}
FORBIDDEN_SEMANTIC_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


@dataclass(frozen=True)
class LockInputFinding:
    code: str
    subject_id: str
    message: str


def compute_release_lock_input_bundle_hash(bundle: Mapping[str, Any]) -> str:
    payload = dict(bundle)
    payload.pop("bundle_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)


def build_release_lock_input_bundle(
    *,
    bundle_id: str,
    p4_spec_lock_ref: Mapping[str, Any],
    p4_build_lock_ref: Mapping[str, Any],
    approved_spec_decisions: Iterable[Mapping[str, Any]],
    approved_build_decision: Mapping[str, Any],
    suite_report_hashes: Mapping[str, str],
    package_manifest_hash: str,
    example_project_manifest_hash: str,
    migration_coverage_hash: str,
    release_readiness_packet_hash: str,
    source_git_commit: str,
    required_human_authorization: Mapping[str, Any] | None = None,
) -> dict:
    bundle = {
        "bundle_id": bundle_id,
        "p4_spec_lock_ref": dict(p4_spec_lock_ref),
        "p4_build_lock_ref": dict(p4_build_lock_ref),
        "approved_spec_decisions": sorted(
            (dict(row) for row in approved_spec_decisions),
            key=lambda row: str(row.get("path", "")),
        ),
        "approved_build_decision": dict(approved_build_decision),
        "suite_report_hashes": _sorted_mapping(suite_report_hashes),
        "package_manifest_hash": package_manifest_hash,
        "example_project_manifest_hash": example_project_manifest_hash,
        "migration_coverage_hash": migration_coverage_hash,
        "release_readiness_packet_hash": release_readiness_packet_hash,
        "source_git_commit": source_git_commit,
        "required_human_authorization": dict(
            required_human_authorization
            if required_human_authorization is not None
            else {"required": True, "authorization_ref": None}
        ),
        "release_lock_eligibility_state": "PENDING_HUMAN_AUTHORIZATION",
        "will_create_release_lock": False,
        "will_publish_package": False,
        "forbidden_actions_performed": [],
    }
    bundle["bundle_hash"] = compute_release_lock_input_bundle_hash(bundle)
    return bundle


def validate_release_lock_input_bundle(bundle: Mapping[str, Any]) -> List[LockInputFinding]:
    findings: List[LockInputFinding] = []
    subject = str(bundle.get("bundle_id", "release_lock_input_bundle"))
    findings.extend(_required_field_findings(bundle, REQUIRED_BUNDLE_FIELDS, subject, "P4LOCKIN-CHECK-001"))
    findings.extend(_semantic_key_findings(bundle, subject))
    findings.extend(_lock_ref_findings(bundle.get("p4_spec_lock_ref"), "p4_spec_lock_ref"))
    findings.extend(_lock_ref_findings(bundle.get("p4_build_lock_ref"), "p4_build_lock_ref"))
    findings.extend(_review_ref_list_findings(bundle.get("approved_spec_decisions", []), "approved_spec_decisions"))
    findings.extend(_review_ref_findings(bundle.get("approved_build_decision"), "approved_build_decision"))
    findings.extend(_suite_hash_findings(bundle.get("suite_report_hashes", {})))
    findings.extend(_hash_field_findings(bundle, subject, HASH_FIELDS))
    findings.extend(_human_authorization_findings(bundle.get("required_human_authorization"), subject))
    findings.extend(_forbidden_action_findings(bundle, subject))
    if "release_readiness_packet" in bundle:
        findings.append(
            LockInputFinding(
                "P4LOCKIN-CHECK-007",
                subject,
                "release lock input bundle must reference readiness hash, not embed readiness packet",
            )
        )
    expected_hash = bundle.get("bundle_hash")
    if not _is_sha256(expected_hash):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-008", subject, "bundle_hash must be sha256"))
    elif expected_hash != compute_release_lock_input_bundle_hash(bundle):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-008", subject, "bundle_hash mismatch"))
    return sorted(findings, key=lambda item: (item.code, item.subject_id, item.message))


def _required_field_findings(
    value: Mapping[str, Any],
    fields: Sequence[str],
    subject: str,
    code: str,
) -> List[LockInputFinding]:
    return [LockInputFinding(code, subject, f"{field} is required") for field in fields if field not in value]


def _lock_ref_findings(value: object, subject: str) -> List[LockInputFinding]:
    if not isinstance(value, Mapping):
        return [LockInputFinding("P4LOCKIN-CHECK-002", subject, "lock ref must be an object")]
    findings: List[LockInputFinding] = []
    if not value.get("path"):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-002", subject, "lock ref path is required"))
    if not _is_sha256(value.get("sha256")):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-002", subject, "lock ref sha256 must be sha256"))
    return findings


def _review_ref_list_findings(value: object, subject: str) -> List[LockInputFinding]:
    if not isinstance(value, list) or not value:
        return [LockInputFinding("P4LOCKIN-CHECK-003", subject, "approved spec decisions must be a non-empty list")]
    findings: List[LockInputFinding] = []
    for index, row in enumerate(value):
        findings.extend(_review_ref_findings(row, f"{subject}[{index}]"))
    decision_paths = {str(row.get("path")) for row in value if isinstance(row, Mapping)}
    missing = sorted(REQUIRED_SPEC_DECISION_PATHS - decision_paths)
    for path in missing:
        findings.append(LockInputFinding("P4LOCKIN-CHECK-003", path, "required P4 spec review decision is missing"))
    return findings


def _review_ref_findings(value: object, subject: str) -> List[LockInputFinding]:
    if not isinstance(value, Mapping):
        return [LockInputFinding("P4LOCKIN-CHECK-003", subject, "review decision ref must be an object")]
    findings: List[LockInputFinding] = []
    if not value.get("path"):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-003", subject, "review decision path is required"))
    for field in ("sha256", "subject_hash"):
        if not _is_sha256(value.get(field)):
            findings.append(LockInputFinding("P4LOCKIN-CHECK-003", subject, f"{field} must be sha256"))
    return findings


def _suite_hash_findings(value: object) -> List[LockInputFinding]:
    if not isinstance(value, Mapping):
        return [LockInputFinding("P4LOCKIN-CHECK-004", "suite_report_hashes", "suite_report_hashes must be an object")]
    findings: List[LockInputFinding] = []
    missing = sorted(REQUIRED_SUITE_REPORTS - set(value))
    for suite_id in missing:
        findings.append(LockInputFinding("P4LOCKIN-CHECK-004", suite_id, "required suite report hash is missing"))
    for suite_id, report_hash in sorted(value.items()):
        if not _is_sha256(report_hash):
            findings.append(LockInputFinding("P4LOCKIN-CHECK-004", str(suite_id), "suite report hash must be sha256"))
    return findings


def _hash_field_findings(bundle: Mapping[str, Any], subject: str, fields: Sequence[str]) -> List[LockInputFinding]:
    return [
        LockInputFinding("P4LOCKIN-CHECK-005", subject, f"{field} must be sha256")
        for field in fields
        if field in bundle and not _is_sha256(bundle.get(field))
    ]


def _human_authorization_findings(value: object, subject: str) -> List[LockInputFinding]:
    if not isinstance(value, Mapping):
        return [
            LockInputFinding(
                "P4LOCKIN-CHECK-006",
                subject,
                "required_human_authorization must be an object",
            )
        ]
    if value.get("required") is not True:
        return [
            LockInputFinding(
                "P4LOCKIN-CHECK-006",
                subject,
                "release lock input bundle must require explicit human authorization",
            )
        ]
    return []


def _forbidden_action_findings(bundle: Mapping[str, Any], subject: str) -> List[LockInputFinding]:
    findings: List[LockInputFinding] = []
    for field in sorted(FORBIDDEN_LOCK_OUTPUT_FIELDS & set(bundle)):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-007", field, "bundle cannot declare a written release lock path"))
    if bundle.get("will_create_release_lock") is True or bundle.get("would_create_release_lock") is True:
        findings.append(LockInputFinding("P4LOCKIN-CHECK-007", subject, "bundle cannot create a release lock"))
    if bundle.get("will_publish_package") is True or bundle.get("would_publish_package") is True:
        findings.append(LockInputFinding("P4LOCKIN-CHECK-007", subject, "bundle cannot publish a package"))
    actions = bundle.get("forbidden_actions_performed", [])
    if not isinstance(actions, list):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-007", subject, "forbidden_actions_performed must be a list"))
        return findings
    for action in sorted(set(actions) & FORBIDDEN_ACTIONS):
        findings.append(LockInputFinding("P4LOCKIN-CHECK-007", action, "forbidden release action was performed"))
    return findings


def _semantic_key_findings(value: Mapping[str, Any], subject: str) -> List[LockInputFinding]:
    return [
        LockInputFinding("P4REL-SEMANTIC-BOUNDARY", subject, f"{key} is outside release lock input authority")
        for key in sorted(FORBIDDEN_SEMANTIC_KEYS & set(value))
    ]


def _sorted_mapping(value: Mapping[str, str]) -> dict:
    return {key: value[key] for key in sorted(value)}


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def finding_dicts(findings: Iterable[LockInputFinding | Mapping[str, Any]]) -> List[dict]:
    rows = [asdict(finding) if isinstance(finding, LockInputFinding) else dict(finding) for finding in findings]
    return sorted(rows, key=lambda row: (row.get("code", ""), row.get("subject_id", ""), row.get("message", "")))
