import json
from pathlib import Path

from drd_harness.release.packaging import run_example_project_smoke, validate_example_project_manifest


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
FIXTURE = Path("repository/examples/p4_release_smoke/example_manifest.json")


def example_manifest(**overrides):
    manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
    manifest.update(overrides)
    return manifest


def test_example_project_fixture_manifest_validates():
    manifest = example_manifest()

    assert validate_example_project_manifest(manifest) == []


def test_example_project_smoke_passes_when_expected_outputs_match():
    manifest = example_manifest()
    expected_path = manifest["expected_outputs"][0]["path"]

    report = run_example_project_smoke(manifest, {expected_path: manifest["expected_outputs"][0]["sha256"]})

    assert report["status"] == "PASS"
    assert report["would_publish_package"] is False
    assert report["would_create_lock"] is False
    assert report["would_create_product_semantics"] is False


def test_example_project_smoke_fails_on_missing_or_mismatched_output():
    manifest = example_manifest()
    expected_path = manifest["expected_outputs"][0]["path"]

    missing = run_example_project_smoke(manifest, {})
    mismatch = run_example_project_smoke(manifest, {expected_path: HASH_A})

    assert "P4EXAMPLE-CHECK-005" in {finding["code"] for finding in missing["findings"]}
    assert "P4EXAMPLE-CHECK-006" in {finding["code"] for finding in mismatch["findings"]}


def test_example_project_manifest_rejects_escape_status_hash_and_semantics():
    manifest = example_manifest(
        example_path="../outside",
        smoke_status="PUBLISHED",
        smoke_report_hash="bad",
        source_input_refs=[{"path": "source.md", "sha256": "bad"}],
        expected_outputs=[{"path": "/tmp/out.json", "sha256": "bad"}],
        page_elements=["forbidden"],
    )

    findings = validate_example_project_manifest(manifest)
    codes = {finding.code for finding in findings}

    assert "P4PKG-CHECK-PATH" in codes
    assert "P4EXAMPLE-CHECK-003" in codes
    assert "P4EXAMPLE-CHECK-004" in codes
    assert "P4EXAMPLE-CHECK-007" in codes
    assert "P4EXAMPLE-CHECK-008" in codes
    assert "P4REL-SEMANTIC-BOUNDARY" in codes


def test_example_project_manifest_rejects_prefix_only_path_escape():
    manifest = example_manifest(example_path="repository/examples/p4_release_smoke_evil")

    findings = validate_example_project_manifest(manifest)

    assert "P4EXAMPLE-CHECK-002" in {finding.code for finding in findings}
