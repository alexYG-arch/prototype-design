import json
from pathlib import Path

from drd_harness.adapters.markdown_prd import adapt_markdown_prd
from drd_harness.adapters.prd_harness import adapt_prd_harness_bundle
from drd_harness.kernel.hashline import sha256_file
from drd_harness.orchestrator.program_driver import validate_adapter_semantic_boundary


FORBIDDEN_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


def test_markdown_adapter_preserves_source_hash_and_splits_headings(tmp_path: Path):
    source = tmp_path / "prd.md"
    source.write_text("# Intro\nOne\n## Details\nTwo\n", encoding="utf-8")

    result = adapt_markdown_prd(source)

    assert result["adapter_id"] == "markdown_prd_adapter"
    assert result["source_sha256"] == sha256_file(source)
    assert result["normalization_report"]["source_hash_preserved"] is True
    assert [section["heading"] for section in result["source_section_records"]] == ["Intro", "Details"]
    assert FORBIDDEN_KEYS.isdisjoint(result)


def test_markdown_adapter_routes_active_html_to_human_gate(tmp_path: Path):
    source = tmp_path / "prd.md"
    source.write_text("# Intro\n<script>alert(1)</script>\n", encoding="utf-8")

    result = adapt_markdown_prd(source)

    assert result["status"] == "HUMAN_REVIEW_REQUIRED"
    assert result["unsupported_content_report"]


def test_prd_harness_adapter_preserves_declared_hashes(tmp_path: Path):
    source = tmp_path / "source.md"
    source.write_text("# Source\n", encoding="utf-8")
    manifest = tmp_path / "bundle.json"
    manifest.write_text(
        json.dumps({"source_files": ["source.md"], "source_hashes": {"source.md": sha256_file(source)}}),
        encoding="utf-8",
    )

    result = adapt_prd_harness_bundle(manifest)

    assert result["adapter_id"] == "prd_harness_adapter"
    assert result["status"] == "PASS"
    assert result["source_ref_records"][0]["source_sha256"] == sha256_file(source)
    assert result["normalization_report"]["source_hashes_preserved"] is True
    assert FORBIDDEN_KEYS.isdisjoint(result)


def test_adapter_semantic_boundary_rejects_forbidden_output_keys():
    findings = validate_adapter_semantic_boundary(
        {
            "adapter_id": "bad_adapter",
            "source_ref_records": [],
            "product_requirements": [],
        }
    )

    assert findings[0].code == "RUN-CHECK-SEMANTIC-BOUNDARY"
