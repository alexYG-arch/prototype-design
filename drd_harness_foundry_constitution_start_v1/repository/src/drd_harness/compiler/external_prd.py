"""Source-preserving external PRD to final DRD generation."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from drd_harness.compiler.conservation import compute_unit_hash, sha256_text
from drd_harness.compiler.final_drd import CompilerFailure, compile_final_drd, deterministic_hash
from drd_harness.kernel.hashline import sha256_bytes, sha256_file
from drd_harness.orchestrator.program_driver import (
    DriverFinding,
    build_status_payload,
    validate_external_prd_output_scope,
)
from drd_harness.validators.compiler_conservation import (
    compute_closed_input_hash,
    compute_semantic_content_hash,
)


STAGE_ORDER_ROWS = [
    {"stage_id": "DRD-01", "stage_order_index": 10},
    {"stage_id": "DRD-02", "stage_order_index": 20},
    {"stage_id": "DRD-03", "stage_order_index": 30},
    {"stage_id": "DRD-03B", "stage_order_index": 40},
    {"stage_id": "DRD-04", "stage_order_index": 50},
]
DOCUMENT_GENERATION_STAGE_ROWS = [
    {"stage_id": "DRD-00", "stage_order_index": 0, "status": "SOURCE_SNAPSHOT_BOUND"},
    {"stage_id": "DRD-01", "stage_order_index": 10, "status": "SOURCE_PRESERVING_INVENTORY_BOUND"},
    {"stage_id": "DRD-02", "stage_order_index": 20, "status": "REQUIRES_HUMAN_REVIEW_FOR_INFERENCE"},
    {"stage_id": "DRD-03", "stage_order_index": 30, "status": "REQUIRES_HUMAN_REVIEW_FOR_INTERACTION_CLOSURE"},
    {"stage_id": "DRD-03B", "stage_order_index": 35, "status": "REQUIRES_HUMAN_REVIEW_FOR_PRESENTATION"},
    {"stage_id": "DRD-04", "stage_order_index": 40, "status": "REQUIRES_HUMAN_REVIEW_FOR_LAYOUT"},
    {"stage_id": "DRD-05", "stage_order_index": 50, "status": "FINAL_DRD_COMPILED"},
    {"stage_id": "DRD-06", "stage_order_index": 60, "status": "READ_ONLY_QA_RECORDED"},
]
GENERATED_FILENAMES = [
    "external_prd_section_index.json",
    "external_prd_review_decision.json",
    "external_prd_source_snapshot_binding.json",
    "external_prd_validation_report.json",
    "drd_generation_stage_plan.json",
    "compiler_input_bundle.json",
    "FINAL_DRD.md",
    "final_drd_manifest.json",
    "final_drd_toc.json",
    "final_drd_reference_index.json",
    "final_drd_hash_index.json",
    "compiler_conservation_report.json",
    "compiler_semantic_unit_inventory.json",
]


def generate_external_prd_drd(
    *,
    work_dir: Path,
    source_ref: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict:
    """Compile a Markdown PRD into a source-preserving DRD package."""
    planned_paths = [(output_dir / filename).as_posix() for filename in GENERATED_FILENAMES]
    findings: List[Any] = []
    findings.extend(validate_external_prd_output_scope(work_dir, output_dir))
    if not source_ref.is_file():
        findings.append(DriverFinding("DRDGEN-INPUT-001", str(source_ref), "source_ref must be a readable file"))

    source_hash = ""
    sections: List[dict] = []
    if not findings:
        try:
            source_hash, sections = parse_markdown_sections(source_ref)
            if not any(section["body"].strip() or section["heading"].strip() for section in sections):
                findings.append(DriverFinding("DRDGEN-INPUT-002", str(source_ref), "source_ref must contain non-empty Markdown content"))
            findings.extend(_unsupported_markdown_findings(sections))
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(DriverFinding("DRDGEN-INPUT-001", str(source_ref), str(exc)))

    if findings:
        payload = build_status_payload(
            command="generate-drd",
            status="STOPPED",
            run_id=_stable_id("drdgen", [str(source_ref), str(output_dir), source_hash]),
            written_paths=[],
            findings=findings,
            exit_code=1,
            planned_written_paths=planned_paths,
            dry_run=dry_run,
            release_lock_eligibility_state="NOT_APPLICABLE",
            will_create_release_lock=False,
            will_publish_package=False,
            source_preserving_compile_only=True,
            staged_execution_complete=False,
            staged_execution_command="staged-run",
        )
        return payload

    if dry_run:
        return build_status_payload(
            command="generate-drd",
            status="DRY_RUN",
            run_id=_stable_id("drdgen", [str(source_ref), str(output_dir), source_hash]),
            written_paths=[],
            findings=[],
            exit_code=0,
            planned_written_paths=planned_paths,
            source_sha256=source_hash,
            source_section_count=len(sections),
            document_generation_stage_order=[row["stage_id"] for row in DOCUMENT_GENERATION_STAGE_ROWS],
            dry_run=True,
            release_lock_eligibility_state="NOT_APPLICABLE",
            will_create_release_lock=False,
            will_publish_package=False,
            source_preserving_compile_only=True,
            staged_execution_complete=False,
            staged_execution_command="staged-run",
        )

    try:
        artifacts, bundle = build_external_prd_drd_artifacts(source_ref, source_hash, sections, output_dir)
        _write_artifacts(artifacts)
    except (CompilerFailure, OSError, ValueError) as exc:
        compiler_findings = getattr(exc, "findings", None)
        findings = _finding_dicts(compiler_findings) if compiler_findings else [
            {"code": "DRDGEN-COMPILE-001", "subject_id": str(source_ref), "message": str(exc)}
        ]
        return build_status_payload(
            command="generate-drd",
            status="FAIL",
            run_id=_stable_id("drdgen", [str(source_ref), str(output_dir), source_hash]),
            written_paths=[],
            findings=findings,
            exit_code=1,
            planned_written_paths=planned_paths,
            source_sha256=source_hash,
            source_section_count=len(sections),
            dry_run=False,
            release_lock_eligibility_state="NOT_APPLICABLE",
            will_create_release_lock=False,
            will_publish_package=False,
            source_preserving_compile_only=True,
            staged_execution_complete=False,
            staged_execution_command="staged-run",
        )

    written_paths = sorted(path.as_posix() for path in artifacts)
    return build_status_payload(
        command="generate-drd",
        status="PASS",
        run_id=_stable_id("drdgen", [str(source_ref), str(output_dir), source_hash]),
        written_paths=written_paths,
        findings=[],
        exit_code=0,
        planned_written_paths=planned_paths,
        output_hashes={path: sha256_file(Path(path)) for path in written_paths},
        source_sha256=source_hash,
        source_section_count=len(sections),
        final_drd_path=(output_dir / "FINAL_DRD.md").as_posix(),
        final_drd_hash=sha256_file(output_dir / "FINAL_DRD.md"),
        compiler_input_bundle_hash=deterministic_hash(bundle),
        conservation_status=artifacts[output_dir / "compiler_conservation_report.json"]["status"],
        document_generation_stage_order=[row["stage_id"] for row in DOCUMENT_GENERATION_STAGE_ROWS],
        dry_run=False,
        release_lock_eligibility_state="NOT_APPLICABLE",
        will_create_release_lock=False,
        will_publish_package=False,
        source_preserving_compile_only=True,
        staged_execution_complete=False,
        staged_execution_command="staged-run",
    )


def parse_markdown_sections(source_ref: Path) -> tuple[str, List[dict]]:
    data = source_ref.read_bytes()
    source_hash = sha256_bytes(data)
    text = data.decode("utf-8")
    lines = text.splitlines()
    if not lines:
        return source_hash, []

    starts = [index for index, line in enumerate(lines, 1) if line.startswith("#")]
    if not starts:
        starts = [1]

    sections = []
    for position, start in enumerate(starts):
        end = starts[position + 1] - 1 if position + 1 < len(starts) else len(lines)
        first_line = lines[start - 1]
        is_heading = first_line.startswith("#")
        heading = first_line.lstrip("#").strip() if is_heading else "preamble"
        section_lines = lines[start - 1 : end]
        body_start = start + 1 if is_heading else start
        body_lines = lines[body_start - 1 : end] if body_start <= end else []
        section_id = "md-section-" + sha256_text(f"{source_hash}\0{position}\0{heading}\0{start}")[:16]
        sections.append(
            {
                "section_id": section_id,
                "source_path": str(source_ref),
                "source_sha256": source_hash,
                "heading": heading,
                "line_start": start,
                "line_end": end,
                "body_line_start": body_start,
                "content_sha256": sha256_text("\n".join(section_lines)),
                "body": "\n".join(body_lines).rstrip(),
                "source_lines": [
                    {"line_number": line_number, "text": line}
                    for line_number, line in enumerate(section_lines, start)
                ],
                "body_lines": [
                    {"line_number": line_number, "text": line}
                    for line_number, line in enumerate(body_lines, body_start)
                ],
            }
        )
    return source_hash, sections


def build_external_prd_drd_artifacts(
    source_ref: Path,
    source_hash: str,
    sections: Sequence[Mapping[str, Any]],
    output_dir: Path,
) -> tuple[Dict[Path, Any], dict]:
    section_index = _section_index(source_ref, source_hash, sections)
    review_decision = _review_decision(source_ref, source_hash, sections)
    stage_plan = {
        "artifact": "drd_generation_stage_plan",
        "stage_order": DOCUMENT_GENERATION_STAGE_ROWS,
        "section_stage_policy": "All source-preserved external PRD lines enter DRD-01; DRD-02 through DRD-04 enrichment requires separate human-reviewed inputs.",
        "lock_or_release_stage_included": False,
    }
    source_binding = {
        "artifact": "external_prd_source_snapshot_binding",
        "binding_kind": "source_snapshot_evidence_ref",
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "section_index_ref": (output_dir / "external_prd_section_index.json").as_posix(),
        "section_index_sha256": _json_sha256(section_index),
        "control_scope": "current_capsule_outputs_only",
        "creates_control_lock": False,
        "creates_release_lock": False,
    }
    validation_report = {
        "artifact": "external_prd_validation_report",
        "status": "PASS",
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "source_section_count": len(sections),
        "validation_scope": "source_preserving_prd_to_drd_generation",
        "product_capability_additions_allowed": False,
        "findings": [],
    }

    paths = {
        "section_index": output_dir / "external_prd_section_index.json",
        "review_decision": output_dir / "external_prd_review_decision.json",
        "source_binding": output_dir / "external_prd_source_snapshot_binding.json",
        "validation_report": output_dir / "external_prd_validation_report.json",
        "stage_order": output_dir / "drd_generation_stage_plan.json",
        "schema": Path("repository/schemas/compiler/final_drd_manifest.schema.json"),
    }
    generated_hashes = {
        paths["section_index"].as_posix(): _json_sha256(section_index),
        paths["review_decision"].as_posix(): _json_sha256(review_decision),
        paths["source_binding"].as_posix(): _json_sha256(source_binding),
        paths["validation_report"].as_posix(): _json_sha256(validation_report),
        paths["stage_order"].as_posix(): _json_sha256(stage_plan),
    }
    schema_hash = sha256_file(paths["schema"])
    bundle = _compiler_bundle(
        source_ref=source_ref,
        source_hash=source_hash,
        sections=sections,
        output_dir=output_dir,
        record_paths=paths,
        generated_hashes=generated_hashes,
        schema_hash=schema_hash,
    )
    compiled = compile_final_drd(bundle)
    artifacts: Dict[Path, Any] = {
        paths["section_index"]: section_index,
        paths["review_decision"]: review_decision,
        paths["source_binding"]: source_binding,
        paths["validation_report"]: validation_report,
        paths["stage_order"]: stage_plan,
        output_dir / "compiler_input_bundle.json": {"bundle": bundle},
    }
    artifacts.update({output_dir / filename: value for filename, value in compiled.items()})
    return artifacts, bundle


def _compiler_bundle(
    *,
    source_ref: Path,
    source_hash: str,
    sections: Sequence[Mapping[str, Any]],
    output_dir: Path,
    record_paths: Mapping[str, Path],
    generated_hashes: Mapping[str, str],
    schema_hash: str,
) -> dict:
    review_path = record_paths["review_decision"].as_posix()
    binding_path = record_paths["source_binding"].as_posix()
    section_index_path = record_paths["section_index"].as_posix()
    validation_path = record_paths["validation_report"].as_posix()
    stage_order_path = record_paths["stage_order"].as_posix()
    schema_path = record_paths["schema"].as_posix()
    compiled_sections = []
    semantic_units = []
    section_order = []

    for section_index, section in enumerate(sections, 1):
        section_id = str(section["section_id"])
        units = _semantic_units_for_section(section, review_path, binding_path)
        semantic_units.extend(units)
        section_order.append(
            {
                "stage_id": "DRD-01",
                "section_id": section_id,
                "section_order_index": section_index,
            }
        )
        compiled_sections.append(
            {
                "section_id": section_id,
                "stage_id": "DRD-01",
                "stage_order_index": 10,
                "section_order_index": section_index,
                "heading_text": str(section["heading"]),
                "source_path": str(source_ref),
                "source_hash": source_hash,
                "approved_hash_ref": review_path,
                "body": str(section["body"]),
                "semantic_unit_ids": [unit["semantic_unit_id"] for unit in units],
            }
        )

    current_hashes = {
        str(source_ref): source_hash,
        section_index_path: generated_hashes[section_index_path],
        review_path: generated_hashes[review_path],
        binding_path: generated_hashes[binding_path],
        validation_path: generated_hashes[validation_path],
        stage_order_path: generated_hashes[stage_order_path],
        schema_path: schema_hash,
    }
    bundle = {
        "bundle_id": "external-prd-drd-bundle-" + sha256_text(str(source_ref) + "\0" + source_hash)[:16],
        "bundle_version": "1.0",
        "compiler_id": "drd_harness.compiler.final_drd",
        "compiler_version": "1.0.0",
        "compiler_code_hash": sha256_file(Path(__file__).with_name("final_drd.py")),
        "compiler_stage_id": "DRD-05",
        "requires_approved_stage_semantic_artifacts": False,
        "source_snapshot_identity": {
            "snapshot_id": "external-prd-source-snapshot-" + source_hash[:16],
            "source_path": str(source_ref),
            "sha256": source_hash,
            "section_count": len(sections),
        },
        "approved_semantic_artifacts": [
            {
                "input_id": "EXTERNAL-PRD-SOURCE",
                "input_type": "APPROVED_SEMANTIC_ARTIFACT",
                "stage_id": "DRD-01",
                "path": str(source_ref),
                "sha256": source_hash,
                "approval_ref": review_path,
                "section_index_ref": section_index_path,
                "semantic_role": "source_prd",
            }
        ],
        "approved_operational_indexes": [
            {
                "input_id": "EXTERNAL-PRD-SECTION-INDEX",
                "input_type": "APPROVED_OPERATIONAL_INDEX",
                "stage_id": "DRD-01",
                "path": section_index_path,
                "sha256": generated_hashes[section_index_path],
                "approval_ref": review_path,
                "semantic_role": "source_section_index",
            }
        ],
        "review_decisions": [
            {
                "input_id": "EXTERNAL-PRD-SOURCE-REVIEW",
                "input_type": "REVIEW_DECISION",
                "path": review_path,
                "sha256": generated_hashes[review_path],
            }
        ],
        "lock_refs": [
            {
                "input_id": "EXTERNAL-PRD-SOURCE-BINDING",
                "input_type": "SPEC_LOCK_REF",
                "path": binding_path,
                "sha256": generated_hashes[binding_path],
            }
        ],
        "validator_results": [
            {
                "input_id": "EXTERNAL-PRD-VALIDATION",
                "input_type": "VALIDATOR_RESULT",
                "path": validation_path,
                "sha256": generated_hashes[validation_path],
            }
        ],
        "control_indexes": [
            {
                "input_id": "EXTERNAL-PRD-STAGE-ORDER",
                "input_type": "CONTROL_INDEX",
                "path": stage_order_path,
                "sha256": generated_hashes[stage_order_path],
            }
        ],
        "schemas": [
            {
                "input_id": "FINAL-DRD-MANIFEST-SCHEMA",
                "input_type": "SCHEMA",
                "path": schema_path,
                "sha256": schema_hash,
            }
        ],
        "stage_order": STAGE_ORDER_ROWS,
        "section_order": section_order,
        "sections": compiled_sections,
        "semantic_units": semantic_units,
        "compiled_semantic_units": semantic_units,
        "schema_hashes": {"final_drd_manifest.schema.json": schema_hash},
        "validator_result_refs": [validation_path],
        "default_lock_ref": binding_path,
        "semantic_content_hash": "",
        "current_hashes": current_hashes,
        "closed_input_hash": "",
    }
    bundle["semantic_content_hash"] = compute_semantic_content_hash(bundle)
    bundle["closed_input_hash"] = compute_closed_input_hash(bundle)
    return bundle


def _section_index(source_ref: Path, source_hash: str, sections: Sequence[Mapping[str, Any]]) -> dict:
    return {
        "artifact": "external_prd_section_index",
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "section_count": len(sections),
        "sections": [
            {
                "section_id": section["section_id"],
                "heading": section["heading"],
                "line_start": section["line_start"],
                "line_end": section["line_end"],
                "content_sha256": section["content_sha256"],
            }
            for section in sections
        ],
    }


def _review_decision(source_ref: Path, source_hash: str, sections: Sequence[Mapping[str, Any]]) -> dict:
    return {
        "artifact": "external_prd_review_decision",
        "decision": "ALLOW_SOURCE_PRESERVING_COMPILATION",
        "decision_scope": "mechanical PRD-to-DRD assembly only",
        "human_approval": False,
        "requires_human_review_before_product_inference": True,
        "source_path": str(source_ref),
        "source_sha256": source_hash,
        "section_ids": [section["section_id"] for section in sections],
        "product_capability_additions_allowed": False,
    }


def _semantic_units_for_section(section: Mapping[str, Any], approval_ref: str, lock_ref: str) -> List[dict]:
    units = []
    for row in section.get("source_lines", []):
        line = str(row["text"]).rstrip()
        if not line.strip():
            continue
        units.append(_semantic_unit(section, row, "COPY_STRING", "Explicit source copy", approval_ref, lock_ref))
        units.extend(
            _semantic_unit(section, row, unit_type, unit_class, approval_ref, lock_ref)
            for unit_type, unit_class in _extra_unit_types(line)
        )
    return units


def _semantic_unit(
    section: Mapping[str, Any],
    row: Mapping[str, Any],
    unit_type: str,
    unit_class: str,
    approval_ref: str,
    lock_ref: str,
) -> dict:
    line = str(row["text"]).rstrip()
    line_no = int(row["line_number"])
    unit_id = (
        "UNIT-"
        + str(section["section_id"]).replace("md-section-", "MD-").upper()
        + "-"
        + unit_type
        + "-"
        + sha256_text(f"{line_no}\0{unit_type}\0{line}")[:12].upper()
    )
    unit = {
        "semantic_unit_id": unit_id,
        "unit_type": unit_type,
        "unit_class": unit_class,
        "stage_id": "DRD-01",
        "source_path": str(section["source_path"]),
        "source_section_id": str(section["section_id"]),
        "source_span_ref": f"line:{line_no}:{unit_type.lower()}",
        "source_hash": sha256_text(line),
        "approval_ref": approval_ref,
        "lock_ref": lock_ref,
        "parent_unit_id": None,
        "relationship_kind": "ROOT",
        "canonical_value": line,
        "unit_hash": "",
        "inventory_version": "external-prd-source-preserving-v1",
    }
    unit["unit_hash"] = compute_unit_hash(unit)
    return unit


def _extra_unit_types(line: str) -> List[tuple[str, str]]:
    text = line.lower()
    units = []
    if any(token in text for token in ("button", "cta", "按钮")):
        units.append(("CTA", "Explicit source control"))
    if any(token in text for token in ("input", "field", "输入", "表单", "字段")):
        units.append(("INPUT_FIELD", "Explicit source input"))
    if any(token in text for token in ("validation", "validate", "校验", "验证")):
        units.append(("VALIDATION_RULE", "Explicit source validation"))
    if any(token in text for token in ("async", "asynchronous", "异步")):
        units.append(("ASYNC_PATH", "Explicit source async path"))
    if any(token in text for token in ("failure", "failed", "error", "失败", "错误", "异常")):
        units.append(("FAILURE_PATH", "Explicit source failure path"))
    if any(token in text for token in ("layout", "布局", "排列", "排布")):
        units.append(("ARRANGEMENT_RULE", "Explicit source layout rule"))
    return units


def _unsupported_markdown_findings(sections: Iterable[Mapping[str, Any]]) -> List[DriverFinding]:
    findings = []
    for section in sections:
        for row in section.get("source_lines", []):
            line = str(row["text"])
            line_no = str(row["line_number"])
            stripped = line.strip().lower()
            if "\x00" in line:
                findings.append(DriverFinding("DRDGEN-INPUT-003", line_no, "NUL byte marker requires human review"))
            if stripped.startswith("<script") or stripped.startswith("<iframe"):
                findings.append(DriverFinding("DRDGEN-INPUT-003", line_no, "active embedded HTML requires human review"))
    return findings


def _write_artifacts(artifacts: Mapping[Path, Any]) -> None:
    for path, value in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(_json_text(value), encoding="utf-8")


def _json_sha256(value: Any) -> str:
    return sha256_text(_json_text(value))


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _stable_id(prefix: str, parts: Sequence[str]) -> str:
    return prefix + "-" + sha256_text("\0".join(parts))[:16]


def _finding_dicts(findings: Iterable[Any]) -> List[dict]:
    values = []
    for finding in findings:
        if isinstance(finding, Mapping):
            values.append(dict(finding))
        else:
            values.append(
                {
                    "code": getattr(finding, "code", "DRDGEN-COMPILE-001"),
                    "subject_id": getattr(finding, "subject_id", "compiler"),
                    "message": getattr(finding, "message", str(finding)),
                }
            )
    return values
