"""Stage contract and lineage models."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional

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


def sort_stage_ids_by_contract(stage_ids: Iterable[StageId]) -> List[StageId]:
    return sorted(stage_ids, key=lambda stage_id: CANONICAL_STAGE_ORDER[stage_id])
