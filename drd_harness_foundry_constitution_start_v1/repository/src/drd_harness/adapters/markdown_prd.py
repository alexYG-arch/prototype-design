"""Markdown PRD adapter for P4 integration entry."""

from pathlib import Path
from typing import Any, Dict, List

from drd_harness.kernel.hashline import sha256_bytes, sha256_file, sha256_text


ADAPTER_ID = "markdown_prd_adapter"


def adapt_markdown_prd(markdown_path: Path) -> Dict[str, Any]:
    data = markdown_path.read_bytes()
    source_hash = sha256_bytes(data)
    text = data.decode("utf-8")
    lines = text.splitlines()
    sections = _split_sections(lines, source_hash, markdown_path)
    unsupported = _unsupported_markdown(lines)
    return {
        "adapter_id": ADAPTER_ID,
        "input_kind": "markdown_prd",
        "status": "HUMAN_REVIEW_REQUIRED" if unsupported else "PASS",
        "source_path": str(markdown_path),
        "source_sha256": source_hash,
        "source_section_records": sections,
        "source_ref_records": [
            {
                "source_ref": section["section_id"],
                "source_path": section["source_path"],
                "source_sha256": source_hash,
            }
            for section in sections
        ],
        "heading_index": [
            {
                "section_id": section["section_id"],
                "heading": section["heading"],
                "line_start": section["line_start"],
            }
            for section in sections
        ],
        "normalization_report": {
            "method": "utf-8 decode without semantic inference",
            "source_hash_preserved": sha256_file(markdown_path) == source_hash,
            "section_count": len(sections),
        },
        "unsupported_content_report": unsupported,
        "handoff_manifest": {
            "adapter_id": ADAPTER_ID,
            "source_path": str(markdown_path),
            "source_sha256": source_hash,
            "section_count": len(sections),
        },
        "findings": [
            {
                "code": "P4ADAPT-HUMAN-GATE",
                "subject_id": item["line"],
                "message": item["reason"],
            }
            for item in unsupported
        ],
    }


def _split_sections(lines: List[str], source_hash: str, markdown_path: Path) -> List[Dict[str, Any]]:
    starts = [index for index, line in enumerate(lines, 1) if line.startswith("#")]
    if not starts:
        starts = [1]

    sections = []
    for position, start in enumerate(starts):
        end = starts[position + 1] - 1 if position + 1 < len(starts) else len(lines)
        heading = lines[start - 1].lstrip("#").strip() if lines[start - 1].startswith("#") else "preamble"
        body = "\n".join(lines[start - 1 : end])
        section_id = "md-section-" + sha256_text(f"{source_hash}\0{position}\0{heading}\0{start}")[:16]
        sections.append(
            {
                "section_id": section_id,
                "source_path": str(markdown_path),
                "source_sha256": source_hash,
                "heading": heading,
                "line_start": start,
                "line_end": end,
                "content_sha256": sha256_text(body),
            }
        )
    return sections


def _unsupported_markdown(lines: List[str]) -> List[Dict[str, str]]:
    unsupported = []
    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        if "\x00" in line:
            unsupported.append({"line": str(index), "reason": "NUL byte marker requires Human Gate review"})
        if stripped.startswith("<script") or stripped.startswith("<iframe"):
            unsupported.append({"line": str(index), "reason": "active embedded HTML requires Human Gate review"})
    return unsupported
