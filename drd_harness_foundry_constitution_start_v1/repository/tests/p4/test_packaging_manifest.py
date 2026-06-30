from drd_harness.release.packaging import build_package_dry_run_report, validate_package_manifest


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def package_manifest(**overrides):
    manifest = {
        "package_name": "drd-harness",
        "package_version": "0.0.0",
        "source_git_commit": HASH_A,
        "source_dirty_state": "CLEAN",
        "included_files": [
            {"path": "repository/src/drd_harness/release/suites.py", "sha256": HASH_B},
            {"path": "repository/src/drd_harness/release/packaging.py", "sha256": HASH_C},
        ],
        "excluded_files": [".git/**", "build_program/phases/**/REVIEW_DECISION.json"],
        "entrypoints": {"drd-harness": "drd_harness.cli.main:main"},
        "dependency_lock_hash": HASH_A,
        "build_command": "python -m build --wheel --no-isolation",
        "package_artifact_hash": HASH_B,
        "dry_run_report_hash": HASH_C,
    }
    manifest.update(overrides)
    return manifest


def test_package_manifest_accepts_hash_bound_tracked_relative_paths():
    manifest = package_manifest()

    findings = validate_package_manifest(
        manifest,
        tracked_release_inputs={row["path"] for row in manifest["included_files"]},
    )
    report = build_package_dry_run_report(manifest, findings)

    assert findings == []
    assert report["status"] == "PASS"
    assert report["would_publish_package"] is False
    assert report["would_create_lock"] is False


def test_package_manifest_rejects_forbidden_included_paths():
    manifest = package_manifest(
        included_files=[
            {"path": ".env", "sha256": HASH_A},
            {"path": ".git/config", "sha256": HASH_A},
            {"path": "build_program/phases/P4/candidates/P4-IMPL-03/REVIEW_DECISION.json", "sha256": HASH_A},
            {"path": "control/locks/DRD_HARNESS_RELEASE_LOCK.json", "sha256": HASH_A},
        ]
    )

    findings = validate_package_manifest(manifest, tracked_release_inputs={row["path"] for row in manifest["included_files"]})

    assert [finding.code for finding in findings].count("P4PKG-CHECK-003") == 4


def test_package_manifest_rejects_path_escape_and_untracked_inputs():
    manifest = package_manifest(
        included_files=[
            {"path": "../outside.py", "sha256": HASH_A},
            {"path": "/tmp/absolute.py", "sha256": HASH_A},
            {"path": "repository/src/drd_harness/release/packaging.py", "sha256": HASH_A},
        ],
    )

    findings = validate_package_manifest(manifest, tracked_release_inputs={"repository/src/drd_harness/release/suites.py"})
    codes = {finding.code for finding in findings}

    assert "P4PKG-CHECK-PATH" in codes
    assert "P4PKG-CHECK-004" in codes


def test_package_manifest_rejects_invalid_hashes_and_semantic_payloads():
    manifest = package_manifest(
        dependency_lock_hash="not-a-hash",
        included_files=[{"path": "repository/src/drd_harness/release/packaging.py", "sha256": "bad"}],
        product_requirements=["forbidden"],
    )

    findings = validate_package_manifest(manifest)
    codes = {finding.code for finding in findings}

    assert "P4PKG-CHECK-005" in codes
    assert "P4REL-SEMANTIC-BOUNDARY" in codes


def test_package_manifest_rejects_unsupported_dirty_state_and_unhashed_string_entries():
    manifest = package_manifest(
        source_dirty_state="MAYBE_DIRTY",
        included_files=["repository/src/drd_harness/release/packaging.py"],
    )

    findings = validate_package_manifest(manifest)
    codes = {finding.code for finding in findings}

    assert "P4PKG-CHECK-005" in codes
    assert "P4PKG-CHECK-007" in codes
