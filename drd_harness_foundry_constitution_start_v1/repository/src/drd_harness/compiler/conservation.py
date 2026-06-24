"""Semantic conservation helpers for final DRD compilation."""

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set


SEMANTIC_UNIT_TYPES: Set[str] = {
    "PAGE",
    "PAGE_STATE",
    "OVERLAY",
    "REGION",
    "COMPONENT_DEFINITION",
    "COMPONENT_INSTANCE",
    "COMPONENT_VARIANT",
    "ELEMENT",
    "CTA",
    "INPUT_FIELD",
    "OPTION",
    "VALIDATION_RULE",
    "DATA_OBJECT",
    "DATA_FIELD",
    "COPY_STRING",
    "GRAPH_NODE",
    "GRAPH_EDGE",
    "REACTION",
    "GUARD_CONDITION",
    "ASYNC_PATH",
    "HANDOFF_PATH",
    "FAILURE_PATH",
    "CANCEL_PATH",
    "RETRY_PATH",
    "RETURN_PATH",
    "EXIT_PATH",
    "PRESENTATION_MODE",
    "SHARED_PATTERN",
    "MESSAGE_PLACEMENT",
    "STATE_PLACEMENT",
    "CONTAINMENT_EDGE",
    "ORDER_RULE",
    "ARRANGEMENT_RULE",
    "SIZING_RULE",
    "WIDTH_BEHAVIOR",
    "HEIGHT_SCROLL_BEHAVIOR",
    "CONTENT_GROWTH_RULE",
    "CARRIER_ADAPTATION_RULE",
    "SAFE_AREA_RULE",
    "Z_AXIS_LAYER",
    "MATERIAL_ELEVATION",
    "TRACE_BINDING",
}

NON_ATOMIC_TYPES = {
    "SCREEN_BUNDLE",
    "FLOW_BUNDLE",
    "LAYOUT_BUNDLE",
    "SECTION",
    "PARAGRAPH",
    "GENERIC",
    "OTHER",
}

REQUIRED_UNIT_FIELDS = {
    "semantic_unit_id",
    "unit_type",
    "unit_class",
    "stage_id",
    "source_path",
    "source_section_id",
    "source_span_ref",
    "source_hash",
    "approval_ref",
    "lock_ref",
    "parent_unit_id",
    "relationship_kind",
    "canonical_value",
    "unit_hash",
    "inventory_version",
}

CHILD_SEMANTIC_HINTS = {
    "button",
    "cta",
    "input",
    "field",
    "copy",
    "message",
    "layout",
    "state",
    "interaction",
    "edge",
    "node",
    "validation",
    "recovery",
    "pagination",
    "permission",
}


@dataclass(frozen=True)
class ConservationFinding:
    code: str
    subject_id: str
    message: str


@dataclass(frozen=True)
class AtomicSemanticUnit:
    semantic_unit_id: str
    unit_type: str
    unit_class: str
    stage_id: str
    source_path: str
    source_section_id: str
    source_span_ref: str
    source_hash: str
    approval_ref: str
    lock_ref: Optional[str]
    parent_unit_id: Optional[str]
    relationship_kind: str
    canonical_value: str
    unit_hash: str
    inventory_version: str

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "AtomicSemanticUnit":
        return cls(**{field: value.get(field) for field in REQUIRED_UNIT_FIELDS})

    def to_dict(self) -> dict:
        return asdict(self)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_unit_hash(unit: Mapping[str, Any]) -> str:
    fields = {
        "semantic_unit_id": unit.get("semantic_unit_id"),
        "unit_type": unit.get("unit_type"),
        "unit_class": unit.get("unit_class"),
        "stage_id": unit.get("stage_id"),
        "source_path": unit.get("source_path"),
        "source_section_id": unit.get("source_section_id"),
        "source_span_ref": unit.get("source_span_ref"),
        "source_hash": unit.get("source_hash"),
        "approval_ref": unit.get("approval_ref"),
        "lock_ref": unit.get("lock_ref"),
        "parent_unit_id": unit.get("parent_unit_id"),
        "relationship_kind": unit.get("relationship_kind"),
        "canonical_value": unit.get("canonical_value"),
        "inventory_version": unit.get("inventory_version"),
    }
    return sha256_text(canonical_json(fields))


def validate_atomic_unit(unit: Mapping[str, Any]) -> List[ConservationFinding]:
    subject_id = str(unit.get("semantic_unit_id") or "semantic_unit")
    findings: List[ConservationFinding] = []

    for field in sorted(REQUIRED_UNIT_FIELDS):
        if field not in unit:
            findings.append(ConservationFinding("COMP-CHECK-018", subject_id, f"{field} is required"))

    for field in sorted(REQUIRED_UNIT_FIELDS - {"parent_unit_id", "lock_ref"}):
        if not unit.get(field):
            findings.append(ConservationFinding("COMP-CHECK-018", subject_id, f"{field} must be non-empty"))

    unit_type = unit.get("unit_type")
    if unit_type in NON_ATOMIC_TYPES or unit_type not in SEMANTIC_UNIT_TYPES:
        findings.append(ConservationFinding("COMP-CHECK-019", subject_id, "unit_type is not an approved atomic type"))

    source_span = str(unit.get("source_span_ref") or "").lower()
    if source_span in {"file", "whole_file", "section"} or source_span.startswith("section:"):
        findings.append(ConservationFinding("COMP-CHECK-017", subject_id, "source_span_ref is too broad for atomic proof"))

    expected_hash = compute_unit_hash(unit)
    if unit.get("unit_hash") != expected_hash:
        findings.append(ConservationFinding("COMP-CHECK-018", subject_id, "unit_hash does not match canonical unit fields"))

    value_text = str(unit.get("canonical_value") or "").lower()
    if unit_type in {"PAGE", "REGION", "COMPONENT_DEFINITION"}:
        child_hints = [hint for hint in CHILD_SEMANTIC_HINTS if hint in value_text]
        if len(child_hints) >= 2:
            findings.append(ConservationFinding("COMP-CHECK-020", subject_id, "parent unit is being used to prove child semantics"))

    return findings


def validate_atomic_inventory(units: Iterable[Mapping[str, Any]]) -> List[ConservationFinding]:
    findings: List[ConservationFinding] = []
    seen = set()
    rows = list(units)
    if not rows:
        return [ConservationFinding("COMP-CHECK-016", "inventory", "atomic semantic inventory is required")]
    row_ids = {str(unit.get("semantic_unit_id")) for unit in rows if unit.get("semantic_unit_id")}
    for unit in rows:
        unit_id = str(unit.get("semantic_unit_id") or "semantic_unit")
        if unit_id in seen:
            findings.append(ConservationFinding("COMP-CHECK-017", unit_id, "semantic_unit_id must be unique"))
        seen.add(unit_id)
        parent_id = unit.get("parent_unit_id")
        relationship = unit.get("relationship_kind")
        if parent_id and parent_id not in row_ids:
            findings.append(ConservationFinding("COMP-CHECK-020", unit_id, "parent_unit_id does not resolve"))
        if parent_id and relationship == "ROOT":
            findings.append(ConservationFinding("COMP-CHECK-020", unit_id, "child unit cannot use ROOT relationship"))
        if not parent_id and relationship not in {"ROOT", "TRACE", "NONE"}:
            findings.append(ConservationFinding("COMP-CHECK-020", unit_id, "non-root relationship requires parent_unit_id"))
        findings.extend(validate_atomic_unit(unit))
    return findings


def compare_semantic_units(
    approved_units: Iterable[Mapping[str, Any]],
    compiled_units: Iterable[Mapping[str, Any]],
) -> dict:
    approved_by_id: Dict[str, Mapping[str, Any]] = {
        str(unit.get("semantic_unit_id")): unit for unit in approved_units
    }
    compiled_by_id: Dict[str, Mapping[str, Any]] = {
        str(unit.get("semantic_unit_id")): unit for unit in compiled_units
    }
    approved_ids = set(approved_by_id)
    compiled_ids = set(compiled_by_id)

    matched = []
    hash_drift = []
    non_atomic = []
    for finding in validate_atomic_inventory(approved_by_id.values()):
        non_atomic.append({"semantic_unit_id": finding.subject_id, "code": finding.code, "message": finding.message})
    for finding in validate_atomic_inventory(compiled_by_id.values()):
        non_atomic.append({"semantic_unit_id": finding.subject_id, "code": finding.code, "message": finding.message})
    for unit_id in sorted(approved_ids & compiled_ids):
        approved = approved_by_id[unit_id]
        compiled = compiled_by_id[unit_id]
        if approved.get("unit_hash") == compiled.get("unit_hash") and approved.get("canonical_value") == compiled.get("canonical_value"):
            matched.append(unit_id)
        else:
            hash_drift.append(unit_id)

    added = sorted(compiled_ids - approved_ids)
    omitted = sorted(approved_ids - compiled_ids)
    status = "PASS"
    if added:
        status = "FAIL_SEMANTIC_ADDITION"
    elif omitted:
        status = "FAIL_SEMANTIC_OMISSION"
    elif hash_drift:
        status = "FAIL_HASH_DRIFT"
    elif non_atomic:
        status = "REQUIRES_HUMAN_REVIEW"

    return {
        "status": status,
        "approved_input_semantic_units": sorted(approved_ids),
        "compiled_output_semantic_units": sorted(compiled_ids),
        "matched_semantic_units": matched,
        "added_semantic_units": added,
        "omitted_semantic_units": omitted,
        "non_atomic_semantic_units": non_atomic,
        "hash_drift": hash_drift,
        "unapproved_inputs": [],
        "ordering_findings": [],
        "nondeterminism_findings": [],
        "read_only_qa_boundary_status": "NOT_RUN",
        "human_review_required": bool(added or omitted or hash_drift or non_atomic),
    }
