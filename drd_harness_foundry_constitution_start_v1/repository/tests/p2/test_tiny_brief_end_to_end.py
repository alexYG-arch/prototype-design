import hashlib
import json
from pathlib import Path

from drd_harness.compiler.final_drd import compile_final_drd, deterministic_hash
from drd_harness.validators.compiler_conservation import validate_final_manifest
from drd_harness.validators.phase_gate import validate_build_lock_readiness, validate_promotion_readiness
from drd_harness.validators.spec_validator import validate_validation_result


FIXTURE_ROOT = Path("repository/fixtures/p2/tiny_brief_intake")
REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id",
    "stage_id",
    "fixture_id",
    "path",
    "schema_ref",
    "schema_payload_key",
    "source_refs",
    "upstream_artifact_refs",
    "upstream_hashes",
    "validator_ref",
    "review_gate",
    "promotion_state",
    "invalidation_inputs",
}
FINAL_REVIEW_ARTIFACTS = {
    "final_drd_manifest.json": (
        "p2.tiny_brief.final_drd_manifest",
        "manifest",
        "repository/schemas/compiler/final_drd_manifest.schema.json",
    ),
    "final_drd_hash_index.json": (
        "p2.tiny_brief.final_drd_hash_index",
        "hash_index",
        "repository/schemas/compiler/final_drd_hash_index.schema.json",
    ),
    "final_drd_reference_index.json": (
        "p2.tiny_brief.final_drd_reference_index",
        "reference_index",
        "repository/schemas/compiler/final_drd_reference_index.schema.json",
    ),
    "final_review_target.json": (
        "p2.tiny_brief.final_review_target",
        "review_target",
        None,
    ),
    "final_review_decision.json": (
        "p2.tiny_brief.final_review_decision",
        "review_decision",
        "repository/templates/review_decision.template.json",
    ),
}
UPSTREAM_ARTIFACT_FILES = {
    "p2.tiny_brief.source_prd": FIXTURE_ROOT / "source/source_prd.md",
    "p2.tiny_brief.source_snapshot_manifest": FIXTURE_ROOT / "source_snapshot_manifest.json",
    "p2.tiny_brief.prd_element_inventory": FIXTURE_ROOT / "prd_element_inventory.json",
    "p2.tiny_brief.derived_element_decisions": FIXTURE_ROOT / "derived_element_decisions.json",
    "p2.tiny_brief.product_expansion_gaps": FIXTURE_ROOT / "product_expansion_gaps.json",
    "p2.tiny_brief.inference_records": FIXTURE_ROOT / "inference_records.json",
    "p2.tiny_brief.structural_completion_review": FIXTURE_ROOT / "structural_completion_review.json",
    "p2.tiny_brief.interaction_graph": FIXTURE_ROOT / "interaction_graph.json",
    "p2.tiny_brief.clickable_inventory": FIXTURE_ROOT / "clickable_inventory.json",
    "p2.tiny_brief.async_behavior": FIXTURE_ROOT / "async_behavior.json",
    "p2.tiny_brief.failure_recovery": FIXTURE_ROOT / "failure_recovery.json",
    "p2.tiny_brief.interaction_messages": FIXTURE_ROOT / "interaction_messages.json",
    "p2.tiny_brief.information_presentation_registry": FIXTURE_ROOT / "information_presentation_registry.json",
    "p2.tiny_brief.shared_component_registry": FIXTURE_ROOT / "shared_component_registry.json",
    "p2.tiny_brief.natural_language_layout": FIXTURE_ROOT / "natural_language_layout.json",
    "p2.tiny_brief.carrier_adaptation_profile": FIXTURE_ROOT / "carrier_adaptation_profile.json",
    "p2.tiny_brief.containment_hierarchy": FIXTURE_ROOT / "containment_hierarchy.json",
    "p2.tiny_brief.z_axis_layering": FIXTURE_ROOT / "z_axis_layering.json",
    "p2.tiny_brief.compiler_input_bundle": FIXTURE_ROOT / "compiler_input_bundle.json",
    "p2.tiny_brief.compiler_semantic_unit_inventory": FIXTURE_ROOT / "compiler_semantic_unit_inventory.json",
    "p2.tiny_brief.compiler_conservation_report": FIXTURE_ROOT / "compiler_conservation_report.json",
    "p2.tiny_brief.final_drd": FIXTURE_ROOT / "FINAL_DRD.md",
}
P2_CODE_TARGET_FILES = {
    "repository/src/drd_harness/stages/source_snapshot.py",
    "repository/src/drd_harness/validators/prd_adoption.py",
    "repository/src/drd_harness/validators/reasoning.py",
    "repository/src/drd_harness/validators/interaction_closure.py",
    "repository/src/drd_harness/validators/presentation_consistency.py",
    "repository/src/drd_harness/validators/layout_completeness.py",
    "repository/src/drd_harness/validators/compiler_conservation.py",
    "repository/src/drd_harness/compiler/final_drd.py",
}
REVIEW_DECISION_REQUIRED_FIELDS = {
    "decision_id",
    "subject_hash",
    "decision",
    "reviewer",
    "open_blockers",
    "approved_sections",
}


def test_final_review_artifacts_have_wrapper_contract():
    required_upstream_refs = {
        "p2.tiny_brief.compiler_input_bundle",
        "p2.tiny_brief.compiler_semantic_unit_inventory",
        "p2.tiny_brief.compiler_conservation_report",
        "p2.tiny_brief.final_drd",
    }

    for filename, (artifact_id, payload_key, schema_ref) in FINAL_REVIEW_ARTIFACTS.items():
        artifact = _load_json(filename)

        assert REQUIRED_ARTIFACT_FIELDS <= set(artifact)
        assert artifact["artifact_id"] == artifact_id
        assert artifact["stage_id"] == "DRD-06-FINAL-REVIEW"
        assert artifact["fixture_id"] == "tiny_brief_intake"
        assert artifact["path"] == f"repository/fixtures/p2/tiny_brief_intake/{filename}"
        assert artifact["schema_ref"] == schema_ref
        assert artifact["schema_payload_key"] == payload_key
        assert artifact["review_gate"] == "FINAL_HUMAN_GATE"
        assert artifact["promotion_state"] == "CANDIDATE"
        assert payload_key in artifact
        assert required_upstream_refs <= set(artifact["upstream_artifact_refs"])
        assert required_upstream_refs <= set(artifact["upstream_hashes"])


def test_final_review_artifact_upstream_hashes_match_current_files():
    for filename in FINAL_REVIEW_ARTIFACTS:
        artifact = _load_json(filename)

        for artifact_id in artifact["upstream_artifact_refs"]:
            assert artifact_id in UPSTREAM_ARTIFACT_FILES
            assert artifact["upstream_hashes"][artifact_id] == _sha256_file(UPSTREAM_ARTIFACT_FILES[artifact_id])


def test_final_manifest_hash_index_and_reference_index_match_compiler_output():
    bundle = _load_json("compiler_input_bundle.json")["bundle"]
    compiled = compile_final_drd(bundle)
    final_text = (FIXTURE_ROOT / "FINAL_DRD.md").read_text(encoding="utf-8")
    manifest = _load_json("final_drd_manifest.json")["manifest"]
    hash_index = _load_json("final_drd_hash_index.json")["hash_index"]
    reference_index = _load_json("final_drd_reference_index.json")["reference_index"]

    assert manifest == compiled["final_drd_manifest.json"]
    assert hash_index == compiled["final_drd_hash_index.json"]
    assert reference_index == compiled["final_drd_reference_index.json"]
    assert validate_final_manifest(manifest) == []
    assert hashlib.sha256(final_text.encode("utf-8")).hexdigest() == manifest["final_drd_hash"]
    assert hash_index["full_output_hash"] == manifest["final_drd_hash"]
    assert deterministic_hash(hash_index) == manifest["hash_index_hash"]
    assert deterministic_hash(reference_index) == manifest["reference_index_hash"]
    assert manifest["conservation_status"] == "PASS"


def test_reference_index_binds_every_final_section_to_lock_and_reviews():
    reference_index = _load_json("final_drd_reference_index.json")["reference_index"]

    assert len(reference_index) == 5
    assert len({entry["reference_id"] for entry in reference_index}) == 5
    assert {entry["lock_ref"] for entry in reference_index} == {"control/locks/P2_SPEC_LOCK.json"}
    assert all(entry["approval_ref"].endswith("REVIEW_DECISION.json") for entry in reference_index)
    assert all(entry["validator_result_refs"] for entry in reference_index)
    assert {entry["source_stage_id"] for entry in reference_index} == {
        "DRD-01",
        "DRD-02",
        "DRD-03",
        "DRD-03B",
        "DRD-04",
    }


def test_final_review_target_subject_hash_is_recomputed_from_final_subject_paths():
    target = _load_json("final_review_target.json")["review_target"]
    subject_paths = target["review_subject_paths"]

    assert "repository/fixtures/p2/tiny_brief_intake/final_review_target.json" not in subject_paths
    assert "repository/fixtures/p2/tiny_brief_intake/final_review_decision.json" not in subject_paths
    assert target["review_subject_hash"] == _review_subject_hash(subject_paths)
    assert set(target["checked_artifact_ids"]) == {
        "p2.tiny_brief.final_drd_manifest",
        "p2.tiny_brief.final_drd_hash_index",
        "p2.tiny_brief.final_drd_reference_index",
        "p2.tiny_brief.final_review_target",
        "p2.tiny_brief.final_review_decision",
    }
    assert validate_validation_result(target["validation_result"], target["review_subject_hash"]) == []


def test_final_review_decision_binds_target_hash_and_has_no_blockers():
    target = _load_json("final_review_target.json")["review_target"]
    decision = _load_json("final_review_decision.json")["review_decision"]

    assert REVIEW_DECISION_REQUIRED_FIELDS <= set(decision)
    assert decision["subject_hash"] == target["review_subject_hash"]
    assert decision["decision"] == "APPROVED"
    assert decision["open_blockers"] == []
    assert set(decision["approved_sections"]) == set(target["review_subject_paths"])
    assert validate_promotion_readiness(
        [target["validation_result"]],
        decision,
        target["review_subject_hash"],
        upstream_bindings_present=True,
        forbidden_write_paths=[],
        invalidation_state="CLEAR",
    ) == []


def test_build_lock_readiness_matrix_covers_p2_code_targets():
    matrix = json.loads(
        Path("build_program/phases/P2/candidates/P2-BUILD-READINESS/BUILD_LOCK_INPUT_MATRIX.json").read_text(
            encoding="utf-8"
        )
    )
    candidates = {entry["path"]: entry["sha256"] for entry in matrix["lock_file_candidates"]}

    assert P2_CODE_TARGET_FILES <= set(candidates)
    for path, file_hash in candidates.items():
        assert file_hash == _sha256_file(Path(path))


def test_p2_build_lock_state_is_explicit():
    matrix = json.loads(
        Path("build_program/phases/P2/candidates/P2-BUILD-READINESS/BUILD_LOCK_INPUT_MATRIX.json").read_text(
            encoding="utf-8"
        )
    )
    lock_path = Path("control/locks/P2_BUILD_LOCK.json")
    if not lock_path.exists():
        assert matrix["build_lock_created"] is False
        assert matrix["not_a_build_lock"] is True
        return

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["phase"] == "P2"
    assert lock["spec_lock_hash"] == matrix["spec_lock"]["sha256"]
    assert lock["files"] == matrix["lock_file_candidates"]
    assert lock["test_results"] == [
        {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "result_hash": result["result_hash"],
        }
        for result in matrix["test_results"]
    ]
    assert validate_build_lock_readiness(lock) == []


def _load_json(filename: str):
    return json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _review_subject_hash(paths):
    rows = [f"{path}\0{hashlib.sha256(Path(path).read_bytes()).hexdigest()}" for path in paths]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
