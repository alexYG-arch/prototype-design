"""Stage contract and lineage models."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Union

from drd_harness.kernel.runtime import PrimaryRuntime


class StageId(str, Enum):
    DRD_00 = "DRD-00"
    DRD_01 = "DRD-01"
    DRD_02 = "DRD-02"
    DRD_03 = "DRD-03"
    DRD_03B = "DRD-03B"
    DRD_04 = "DRD-04"
    DRD_05 = "DRD-05"
    DRD_06 = "DRD-06"


class ArtifactStatus(str, Enum):
    SOURCE_FROZEN = "SOURCE_FROZEN"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    INVALIDATED = "INVALIDATED"


SEMANTIC_SOURCE_STAGES = {
    StageId.DRD_01,
    StageId.DRD_02,
    StageId.DRD_03,
    StageId.DRD_03B,
    StageId.DRD_04,
}

APPROVED_AUTHORITY_STATUSES = {
    ArtifactStatus.APPROVED,
    ArtifactStatus.PROMOTED,
    ArtifactStatus.SOURCE_FROZEN,
}

CANONICAL_STAGE_ORDER = {
    StageId.DRD_00: 0,
    StageId.DRD_01: 10,
    StageId.DRD_02: 20,
    StageId.DRD_03: 30,
    StageId.DRD_03B: 35,
    StageId.DRD_04: 40,
    StageId.DRD_05: 50,
    StageId.DRD_06: 60,
}

REQUIRED_UPSTREAM = {
    StageId.DRD_00: [],
    StageId.DRD_01: [StageId.DRD_00],
    StageId.DRD_02: [StageId.DRD_00, StageId.DRD_01],
    StageId.DRD_03: [StageId.DRD_00, StageId.DRD_01, StageId.DRD_02],
    StageId.DRD_03B: [StageId.DRD_00, StageId.DRD_02, StageId.DRD_03],
    StageId.DRD_04: [StageId.DRD_00, StageId.DRD_02, StageId.DRD_03, StageId.DRD_03B],
    StageId.DRD_05: [StageId.DRD_01, StageId.DRD_02, StageId.DRD_03, StageId.DRD_03B, StageId.DRD_04],
    StageId.DRD_06: [StageId.DRD_00, StageId.DRD_01, StageId.DRD_02, StageId.DRD_03, StageId.DRD_03B, StageId.DRD_04, StageId.DRD_05],
}

CANONICAL_CANDIDATE_OUTPUTS = {
    StageId.DRD_01: ["DRD-01/PRD_EXPERIENCE_BRIEF.md", "DRD-01/experience_fact_index.json"],
    StageId.DRD_02: [
        "DRD-02/USER_TASK_FLOW.md",
        "DRD-02/INTERACTION_CLOSURE_REPORT.md",
        "DRD-02/interaction_graph.json",
    ],
    StageId.DRD_03: ["DRD-03/PAGE_ELEMENT_BLUEPRINT.md", "DRD-03/prd_element_decision_index.json"],
    StageId.DRD_03B: [
        "DRD-03B/SHARED_COMPONENT_REGISTRY.md",
        "DRD-03B/INFORMATION_PRESENTATION_REGISTRY.md",
        "DRD-03B/shared_pattern_index.json",
    ],
    StageId.DRD_04: [
        "DRD-04/LAYOUT_COMPOSITION_SPEC.md",
        "DRD-04/FIGMA_RECONSTRUCTION_GUIDANCE.md",
        "DRD-04/layout_anchor_index.json",
    ],
}

CANONICAL_PROMOTION_OUTPUTS = {
    stage_id: [
        f"{stage_id.value}/APPROVED_SEMANTIC_ARTIFACT.md",
        f"{stage_id.value}/approved_semantic_artifact.json",
    ]
    for stage_id in SEMANTIC_SOURCE_STAGES
}

CANONICAL_NON_CANDIDATE_OUTPUTS = {
    StageId.DRD_00: ["DRD-00/source_prd_snapshot.md", "DRD-00/source_snapshot_manifest.json"],
    StageId.DRD_05: [
        "DRD-05/FINAL_DRD.md",
        "DRD-05/final_drd_manifest.json",
        "DRD-05/final_drd_toc.json",
        "DRD-05/final_drd_reference_index.json",
        "DRD-05/final_drd_hash_index.json",
        "DRD-05/compiler_conservation_report.json",
        "DRD-05/compiler_semantic_unit_inventory.json",
        "DRD-05/compiler_input_bundle.json",
    ],
    StageId.DRD_06: ["DRD-06/READ_ONLY_QA_REPORT.md", "DRD-06/qa_finding_index.json"],
}


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    stage_id: StageId
    status: ArtifactStatus
    sha256: str
    path: str


@dataclass(frozen=True)
class StageContract:
    stage_id: StageId
    purpose: str
    primary_runtime: PrimaryRuntime
    source_prd_snapshot_id: Optional[str]
    required_upstream_artifacts: List[str]
    required_upstream_hashes: List[str]
    authority_inputs: List[str]
    candidate_outputs: List[str]
    promotion_outputs: List[str]
    validator: str
    human_gate: str
    promotion_target: str
    invalidation_inputs: List[str]

    @property
    def stage_order_index(self) -> int:
        return CANONICAL_STAGE_ORDER[self.stage_id]

    def require_source_snapshot(self) -> None:
        if self.stage_id in SEMANTIC_SOURCE_STAGES and not self.source_prd_snapshot_id:
            raise ValueError(f"{self.stage_id.value} must bind source_prd_snapshot_id")


@dataclass(frozen=True)
class StageInputBundle:
    stage_id: StageId
    source_prd_snapshot_id: Optional[str]
    source_prd_snapshot_hash: Optional[str]
    input_artifacts: List[ArtifactRef]

    def require_source_for_semantic_stage(self) -> None:
        if self.stage_id in SEMANTIC_SOURCE_STAGES:
            if not self.source_prd_snapshot_id or not self.source_prd_snapshot_hash:
                raise ValueError(f"{self.stage_id.value} must include source PRD snapshot identity and hash")

    def require_approved_upstream(self) -> None:
        invalid = [
            artifact.artifact_id
            for artifact in self.input_artifacts
            if artifact.status not in APPROVED_AUTHORITY_STATUSES
        ]
        if invalid:
            raise ValueError("stage input uses non-approved upstream artifacts: " + ", ".join(sorted(invalid)))

    def require_required_upstreams(self) -> None:
        required = set(REQUIRED_UPSTREAM[self.stage_id])
        present = {artifact.stage_id for artifact in self.input_artifacts}
        missing = sorted(stage.value for stage in required - present)
        if missing:
            raise ValueError("stage input missing required upstream stages: " + ", ".join(missing))


def canonical_stage_order() -> List[Dict[str, int]]:
    return [
        {"stage_id": stage.value, "stage_order_index": CANONICAL_STAGE_ORDER[stage]}
        for stage in sorted(CANONICAL_STAGE_ORDER, key=lambda item: CANONICAL_STAGE_ORDER[item])
    ]


def candidate_outputs_for_stage(stage_id: Union[StageId, str]) -> List[str]:
    stage = _coerce_stage_id(stage_id)
    return list(CANONICAL_CANDIDATE_OUTPUTS.get(stage, []))


def promotion_outputs_for_stage(stage_id: Union[StageId, str]) -> List[str]:
    stage = _coerce_stage_id(stage_id)
    return list(CANONICAL_PROMOTION_OUTPUTS.get(stage, []))


def canonical_outputs_for_stage(stage_id: Union[StageId, str]) -> List[str]:
    stage = _coerce_stage_id(stage_id)
    if stage in CANONICAL_CANDIDATE_OUTPUTS:
        return candidate_outputs_for_stage(stage) + promotion_outputs_for_stage(stage)
    return list(CANONICAL_NON_CANDIDATE_OUTPUTS[stage])


def sort_stage_ids_by_contract(stage_ids: Iterable[StageId]) -> List[StageId]:
    return sorted(stage_ids, key=lambda stage_id: CANONICAL_STAGE_ORDER[stage_id])


def _coerce_stage_id(stage_id: Union[StageId, str]) -> StageId:
    return stage_id if isinstance(stage_id, StageId) else StageId(stage_id)
