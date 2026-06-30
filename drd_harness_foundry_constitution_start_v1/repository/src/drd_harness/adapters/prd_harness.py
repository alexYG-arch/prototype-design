"""Structured PRD harness bundle adapter for P4 integration entry."""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

from drd_harness.kernel.hashline import sha256_file, sha256_text


ADAPTER_ID = "prd_harness_adapter"
FORBIDDEN_SEMANTIC_KEYS = {
    "product_requirements",
    "page_elements",
    "layout_rules",
    "business_contracts",
    "deduced_product_requirements",
}


def adapt_prd_harness_bundle(bundle_manifest: Path) -> Dict[str, Any]:
    bundle = json.loads(bundle_manifest.read_text(encoding="utf-8"))
    source_files = _source_files(bundle)
    source_hashes = bundle.get("source_hashes", {})
    records = []
    findings = []
    for source_ref in sorted(source_files):
        source_path = _resolve_source(bundle_manifest.parent, source_ref)
        if not source_path.is_file():
            findings.append(_finding("P4ADAPT-SOURCE-MISSING", source_ref, "source file is missing"))
            continue
        actual_hash = sha256_file(source_path)
        expected_hash = source_hashes.get(source_ref) if isinstance(source_hashes, Mapping) else None
        if expected_hash and expected_hash != actual_hash:
            findings.append(_finding("P4ADAPT-SOURCE-HASH", source_ref, "declared source hash does not match file"))
        records.append(
            {
                "source_ref": source_ref,
                "source_path": str(source_path),
                "source_sha256": actual_hash,
                "byte_size": source_path.stat().st_size,
            }
        )

    semantic_keys = sorted(key for key in FORBIDDEN_SEMANTIC_KEYS if key in bundle)
    for key in semantic_keys:
        findings.append(_finding("P4ADAPT-SEMANTIC-BOUNDARY", key, "bundle key requires downstream Human Gate, not adapter output"))

    return {
        "adapter_id": ADAPTER_ID,
        "input_kind": "structured_harness_bundle",
        "status": "HUMAN_REVIEW_REQUIRED" if findings else "PASS",
        "bundle_manifest": str(bundle_manifest),
        "bundle_manifest_sha256": sha256_file(bundle_manifest),
        "source_ref_records": records,
        "normalization_report": {
            "method": "manifest path resolution and hash verification only",
            "source_hashes_preserved": not any(item["code"] == "P4ADAPT-SOURCE-HASH" for item in findings),
            "source_count": len(records),
        },
        "unsupported_content_report": [
            {
                "key": key,
                "reason": "adapter cannot emit product semantics or business contracts",
            }
            for key in semantic_keys
        ],
        "handoff_manifest": {
            "adapter_id": ADAPTER_ID,
            "bundle_manifest": str(bundle_manifest),
            "handoff_id": "prd-harness-" + sha256_text(str(bundle_manifest) + "\0" + sha256_file(bundle_manifest))[:16],
            "source_count": len(records),
        },
        "findings": findings,
    }


def _source_files(bundle: Mapping[str, Any]) -> List[str]:
    value = bundle.get("source_files", [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _resolve_source(base_dir: Path, source_ref: str) -> Path:
    path = Path(source_ref)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _finding(code: str, subject_id: str, message: str) -> Dict[str, str]:
    return {"code": code, "subject_id": subject_id, "message": message}
