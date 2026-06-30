from drd_harness.release.migration import (
    build_migration_coverage_report,
    compute_migration_report_hash,
    finding_dicts,
    validate_migration_coverage_report,
)


def row(capability_id, status="MIGRATED", **overrides):
    data = {
        "legacy_capability_id": capability_id,
        "legacy_capability_name": f"Legacy {capability_id}",
        "legacy_source_ref": f"v3.1#{capability_id}",
        "target_status": status,
        "target_evidence_ref": f"repository/src/drd_harness/{capability_id}.py",
        "rationale": "covered by locked harness capability",
        "review_required": status == "BLOCKED_REQUIRES_HUMAN_REVIEW",
    }
    data.update(overrides)
    return data


def test_migration_coverage_report_validates_summary_and_hash():
    report = build_migration_coverage_report(
        coverage_id="p4-migration",
        source_version="v3.1",
        target_version="p4-release",
        capability_rows=[
            row("source-intake", "MIGRATED"),
            row("compiler", "REPLACED_BY_LOCKED_CAPABILITY"),
            row("legacy-theme", "DROPPED_WITH_RATIONALE"),
        ],
    )

    assert validate_migration_coverage_report(report) == []
    assert report["coverage_summary"]["total_legacy_capabilities"] == 3
    assert report["coverage_summary"]["release_blocking"] is False
    assert report["report_hash"] == compute_migration_report_hash(report)


def test_migration_coverage_blocks_human_review_rows():
    report = build_migration_coverage_report(
        coverage_id="p4-migration",
        source_version="v3.1",
        target_version="p4-release",
        capability_rows=[row("unknown", "BLOCKED_REQUIRES_HUMAN_REVIEW")],
    )

    assert validate_migration_coverage_report(report) == []
    assert report["blocked_rows"] == ["unknown"]
    assert report["human_review_required"] is True
    assert report["coverage_summary"]["release_blocking"] is True


def test_migration_coverage_rejects_invalid_rows_and_duplicates():
    report = build_migration_coverage_report(
        coverage_id="p4-migration",
        source_version="v3.1",
        target_version="p4-release",
        capability_rows=[
            row("dup", "MIGRATED", target_evidence_ref=""),
            row("dup", "UNKNOWN"),
            row("drop", "DROPPED_WITH_RATIONALE", rationale=""),
        ],
    )

    findings = validate_migration_coverage_report(report)
    codes = {finding.code for finding in findings}

    assert "P4MIG-CHECK-007" in codes
    assert "P4MIG-CHECK-008" in codes
    assert "P4MIG-CHECK-009" in codes
    assert "P4MIG-CHECK-011" in codes


def test_migration_coverage_rejects_stale_summary_hash_and_semantic_payloads():
    report = build_migration_coverage_report(
        coverage_id="p4-migration",
        source_version="v3.1",
        target_version="p4-release",
        capability_rows=[row("compiler", "MIGRATED")],
    )
    report["coverage_summary"]["migrated_count"] = 0
    report["report_hash"] = "bad"
    report["capability_rows"][0]["business_contracts"] = ["forbidden"]

    findings = validate_migration_coverage_report(report)
    rows = finding_dicts(findings)
    codes = {finding["code"] for finding in rows}

    assert "P4MIG-CHECK-003" in codes
    assert "P4MIG-CHECK-006" in codes
    assert "P4MIG-SEMANTIC-BOUNDARY" in codes


def test_migration_coverage_rejects_non_list_blocked_rows_without_crashing():
    report = build_migration_coverage_report(
        coverage_id="p4-migration",
        source_version="v3.1",
        target_version="p4-release",
        capability_rows=[row("blocked", "BLOCKED_REQUIRES_HUMAN_REVIEW")],
    )
    report["blocked_rows"] = 123

    findings = validate_migration_coverage_report(report)

    assert "P4MIG-CHECK-004" in {finding.code for finding in findings}
