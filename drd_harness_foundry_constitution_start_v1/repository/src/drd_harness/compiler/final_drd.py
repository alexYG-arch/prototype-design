"""Deterministic final DRD assembly from closed approved input bundles."""

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

from drd_harness.compiler.conservation import canonical_json, compare_semantic_units, sha256_text


STAGE_ORDER = ["DRD-01", "DRD-02", "DRD-03", "DRD-03B", "DRD-04"]
ALLOWED_MECHANICAL_TEMPLATES = {
    "title": "# Final DRD",
    "toc_heading": "## Table of Contents",
    "separator": "---",
    "references_heading": "## Reference Index",
    "hashes_heading": "## Hash Index",
}


class CompilerFailure(ValueError):
    def __init__(self, findings: List[object]):
        self.findings = findings
        super().__init__("compiler conservation checks failed")


@dataclass(frozen=True)
class ApprovedSection:
    section_id: str
    stage_id: str
    stage_order_index: int
    section_order_index: int
    heading_text: str
    source_path: str
    source_hash: str
    approved_hash_ref: str
    body: str
    semantic_unit_ids: List[str]
    approved_semantic_artifact_ref: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def deterministic_hash(value: Any) -> str:
    return sha256_text(canonical_json(value))


def compile_final_drd(bundle: Mapping[str, Any]) -> dict:
    _require_compilable_bundle(bundle)
    sections = [_section_from_dict(section) for section in bundle.get("sections", [])]
    ordered_sections = sort_sections(sections)
    final_drd = render_final_drd(ordered_sections)
    if bundle.get("requires_approved_stage_semantic_artifacts"):
        _require_reader_facing_final_drd(final_drd)
    toc = build_toc(ordered_sections)
    reference_index = build_reference_index(bundle, ordered_sections)
    approved_units = list(bundle.get("semantic_units", []))
    compiled_units = _compiled_units_from_sections(approved_units, ordered_sections, bundle.get("compiled_semantic_units"))
    conservation_report = compare_semantic_units(approved_units, compiled_units)
    _append_uninventoried_semantics(conservation_report, ordered_sections, compiled_units)
    input_bundle_hash = deterministic_hash(bundle)
    semantic_hash = sha256_text("\n".join(section.body for section in ordered_sections))
    mechanical_hash = deterministic_hash(
        {
            "templates": ALLOWED_MECHANICAL_TEMPLATES,
            "toc": toc,
            "references": reference_index,
        }
    )
    final_drd_hash = sha256_text(final_drd)
    hash_index = {
        "input_bundle_hash": input_bundle_hash,
        "semantic_hash": semantic_hash,
        "mechanical_hash": mechanical_hash,
        "full_output_hash": final_drd_hash,
        "toc_hash": deterministic_hash(toc),
        "reference_index_hash": deterministic_hash(reference_index),
        "conservation_report_hash": deterministic_hash(conservation_report),
        "schema_hashes": dict(sorted(bundle.get("schema_hashes", {}).items())),
        "compiler_code_hash": str(bundle.get("compiler_code_hash", "")),
    }
    manifest = {
        "final_drd_path": "FINAL_DRD.md",
        "final_drd_hash": final_drd_hash,
        "semantic_hash": semantic_hash,
        "mechanical_hash": mechanical_hash,
        "input_bundle_hash": input_bundle_hash,
        "toc_hash": hash_index["toc_hash"],
        "reference_index_hash": hash_index["reference_index_hash"],
        "hash_index_hash": deterministic_hash(hash_index),
        "conservation_report_hash": hash_index["conservation_report_hash"],
        "approved_input_count": len(bundle.get("approved_semantic_artifacts", [])),
        "compiled_section_count": len(ordered_sections),
        "compiled_semantic_unit_count": len(compiled_units),
        "omitted_semantic_unit_count": len(conservation_report["omitted_semantic_units"]),
        "added_semantic_unit_count": len(conservation_report["added_semantic_units"]),
        "hash_drift_count": len(conservation_report["hash_drift"]),
        "unapproved_input_count": len(conservation_report["unapproved_inputs"]),
        "conservation_status": conservation_report["status"],
        "assembly_plan": {
            "compiler_id": bundle.get("compiler_id", "drd_harness.compiler.final_drd"),
            "compiler_version": bundle.get("compiler_version", "1.0.0"),
            "compiler_code_hash": bundle.get("compiler_code_hash", ""),
            "schema_hashes": dict(sorted(bundle.get("schema_hashes", {}).items())),
            "stage_order": bundle.get("stage_order", []),
            "section_order": bundle.get("section_order", []),
            "input_bundle_ref": bundle.get("bundle_id", ""),
            "output_files": [
                "FINAL_DRD.md",
                "final_drd_manifest.json",
                "final_drd_toc.json",
                "final_drd_reference_index.json",
                "final_drd_hash_index.json",
                "compiler_conservation_report.json",
            ],
            "conservation_report_ref": "compiler_conservation_report.json",
            "semantic_hash": semantic_hash,
            "mechanical_hash": mechanical_hash,
            "full_output_hash": final_drd_hash,
        },
    }
    return {
        "FINAL_DRD.md": final_drd,
        "final_drd_manifest.json": manifest,
        "final_drd_toc.json": toc,
        "final_drd_reference_index.json": reference_index,
        "final_drd_hash_index.json": hash_index,
        "compiler_conservation_report.json": conservation_report,
        "compiler_semantic_unit_inventory.json": compiled_units,
    }


def sort_sections(sections: Iterable[ApprovedSection]) -> List[ApprovedSection]:
    return sorted(sections, key=lambda section: (section.stage_order_index, section.section_order_index, section.section_id))


def render_final_drd(sections: Iterable[ApprovedSection]) -> str:
    ordered_sections = list(sections)
    lines = [ALLOWED_MECHANICAL_TEMPLATES["title"], "", ALLOWED_MECHANICAL_TEMPLATES["toc_heading"]]
    for section in ordered_sections:
        lines.append(f"- {section.stage_order_index}.{section.section_order_index} {section.heading_text}")
    for section in ordered_sections:
        lines.extend(
            [
                "",
                ALLOWED_MECHANICAL_TEMPLATES["separator"],
                "",
                f"## {section.heading_text}",
                section.body.rstrip(),
            ]
        )
    lines.append("")
    return "\n".join(lines)


def build_toc(sections: Iterable[ApprovedSection]) -> List[dict]:
    return [
        {
            "toc_entry_id": f"TOC-{section.stage_id}-{section.section_id}",
            "stage_id": section.stage_id,
            "section_id": section.section_id,
            "stage_order_index": section.stage_order_index,
            "section_order_index": section.section_order_index,
            "heading_text": section.heading_text,
            "source_path": section.source_path,
            "source_hash": section.source_hash,
        }
        for section in sections
    ]


def build_reference_index(bundle: Mapping[str, Any], sections: Iterable[ApprovedSection]) -> List[dict]:
    source_snapshot = bundle.get("source_snapshot_identity", {})
    return [
        {
            "reference_id": f"REF-{section.stage_id}-{section.section_id}",
            "compiled_section_id": section.section_id,
            "source_stage_id": section.stage_id,
            "source_path": section.source_path,
            "source_hash": section.source_hash,
            "approval_ref": section.approved_hash_ref,
            "approved_semantic_artifact_ref": section.approved_semantic_artifact_ref,
            "lock_ref": bundle.get("default_lock_ref"),
            "validator_result_refs": list(bundle.get("validator_result_refs", [])),
            "source_snapshot_identity": source_snapshot,
        }
        for section in sections
    ]


def _require_compilable_bundle(bundle: Mapping[str, Any]) -> None:
    from drd_harness.validators.compiler_conservation import (
        input_records,
        validate_atomic_inventory_for_compiler,
        validate_hash_drift,
        validate_input_bundle,
        validate_section_order,
        validate_section_semantic_unit_refs,
    )

    findings = []
    findings.extend(validate_input_bundle(bundle))
    findings.extend(validate_section_order(bundle.get("sections", [])))
    findings.extend(validate_section_semantic_unit_refs(bundle))
    findings.extend(validate_atomic_inventory_for_compiler(bundle.get("semantic_units", [])))
    current_hashes = bundle.get("current_hashes", {})
    if current_hashes:
        findings.extend(validate_hash_drift(input_records(bundle), current_hashes))
    if findings:
        raise CompilerFailure(findings)


def _require_reader_facing_final_drd(final_drd: str) -> None:
    from drd_harness.validators.compiler_conservation import validate_final_drd_reader_structure

    findings = validate_final_drd_reader_structure(final_drd)
    if findings:
        raise CompilerFailure(findings)


def _compiled_units_from_sections(
    approved_units: List[Mapping[str, Any]],
    sections: Iterable[ApprovedSection],
    explicit_compiled_units: Optional[Iterable[Mapping[str, Any]]] = None,
) -> List[Mapping[str, Any]]:
    if explicit_compiled_units is not None:
        return list(explicit_compiled_units)
    approved_by_id = {unit.get("semantic_unit_id"): unit for unit in approved_units}
    referenced_ids = []
    for section in sections:
        referenced_ids.extend(section.semantic_unit_ids)
    return [approved_by_id[unit_id] for unit_id in referenced_ids if unit_id in approved_by_id]


def _append_uninventoried_semantics(
    report: Dict[str, Any],
    sections: Iterable[ApprovedSection],
    compiled_units: Iterable[Mapping[str, Any]],
) -> None:
    units_by_id = {unit.get("semantic_unit_id"): unit for unit in compiled_units}
    for section in sections:
        unit_types = {units_by_id[unit_id].get("unit_type") for unit_id in section.semantic_unit_ids if unit_id in units_by_id}
        body = section.body.lower()
        if "button" in body and "CTA" not in unit_types:
            report["added_semantic_units"].append(f"UNINVENTORIED:{section.section_id}:CTA")
        if "error" in body and "COPY_STRING" not in unit_types:
            report["added_semantic_units"].append(f"UNINVENTORIED:{section.section_id}:COPY_STRING")
        if "layout" in body and not (unit_types & {"ARRANGEMENT_RULE", "CONTAINMENT_EDGE", "WIDTH_BEHAVIOR", "HEIGHT_SCROLL_BEHAVIOR"}):
            report["added_semantic_units"].append(f"UNINVENTORIED:{section.section_id}:LAYOUT")
    if report["added_semantic_units"]:
        report["status"] = "FAIL_SEMANTIC_ADDITION"
        report["human_review_required"] = True


def _section_from_dict(value: Mapping[str, Any]) -> ApprovedSection:
    return ApprovedSection(
        section_id=str(value.get("section_id")),
        stage_id=str(value.get("stage_id")),
        stage_order_index=int(value.get("stage_order_index")),
        section_order_index=int(value.get("section_order_index")),
        heading_text=str(value.get("heading_text")),
        source_path=str(value.get("source_path")),
        source_hash=str(value.get("source_hash")),
        approved_hash_ref=str(value.get("approved_hash_ref")),
        body=str(value.get("body")),
        semantic_unit_ids=list(value.get("semantic_unit_ids", [])),
        approved_semantic_artifact_ref=value.get("approved_semantic_artifact_ref"),
    )
