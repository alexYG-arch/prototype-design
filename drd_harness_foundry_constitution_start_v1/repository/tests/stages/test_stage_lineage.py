import pytest

from drd_harness.kernel.hashline import HashBinding, binding_root, changed_bindings
from drd_harness.stages.contracts import ArtifactRef, ArtifactStatus, StageId, StageInputBundle


def test_candidate_artifact_cannot_be_downstream_authority():
    bundle = StageInputBundle(
        stage_id=StageId.DRD_04,
        source_prd_snapshot_id="SRC",
        source_prd_snapshot_hash="a" * 64,
        input_artifacts=[
            ArtifactRef(
                artifact_id="DRD-03B-SHARED-PATTERNS",
                stage_id=StageId.DRD_03B,
                status=ArtifactStatus.CANDIDATE,
                sha256="b" * 64,
                path="candidate.md",
            )
        ],
    )

    with pytest.raises(ValueError, match="non-approved"):
        bundle.require_approved_upstream()


def test_semantic_stage_requires_source_snapshot_hash():
    bundle = StageInputBundle(
        stage_id=StageId.DRD_02,
        source_prd_snapshot_id=None,
        source_prd_snapshot_hash=None,
        input_artifacts=[],
    )

    with pytest.raises(ValueError, match="source PRD snapshot"):
        bundle.require_source_for_semantic_stage()


def test_required_upstream_stages_are_checked():
    bundle = StageInputBundle(
        stage_id=StageId.DRD_03,
        source_prd_snapshot_id="SRC",
        source_prd_snapshot_hash="a" * 64,
        input_artifacts=[
            ArtifactRef("DRD-00-SOURCE", StageId.DRD_00, ArtifactStatus.SOURCE_FROZEN, "a" * 64, "source.md"),
            ArtifactRef("DRD-01-BRIEF", StageId.DRD_01, ArtifactStatus.APPROVED, "b" * 64, "brief.md"),
        ],
    )

    with pytest.raises(ValueError, match="DRD-02"):
        bundle.require_required_upstreams()


def test_hashline_detects_changed_upstream_hash():
    previous = [HashBinding("DRD-01", "a" * 64), HashBinding("DRD-02", "b" * 64)]
    current = [HashBinding("DRD-01", "a" * 64), HashBinding("DRD-02", "c" * 64)]

    assert changed_bindings(previous, current) == ["DRD-02"]
    assert binding_root(previous) != binding_root(current)
