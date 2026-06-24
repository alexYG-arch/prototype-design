import copy
import sys
from pathlib import Path

import pytest


HASH_A = "a" * 64
HASH_B = "b" * 64

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPOSITORY_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def trace_row():
    def _trace_row(**overrides):
        row = {
            "trace_row_id": "TRACE-P1-08-001",
            "implementation_duty": "emit_workpack_envelope",
            "contract_clause_id": "P1-SPEC-08-WORKPACK-GENERATION-001",
            "source_spec_part": "P1-SPEC-08",
            "spec_lock_ref": {"lock_id": "P1_SPEC_LOCK", "lock_hash": HASH_A},
            "contract_section_id": "workpack-generation",
            "rule_id": "SBC-RULE-001",
            "projection_id": "IMPLEMENTATION_WORKPACK_INDEX",
            "implementation_workpack_id": "P1-IMPLEMENT-08",
            "code_target": "repository/src/drd_harness/orchestrator/workpacks.py",
            "class_or_function": "emit_candidate_workpack_envelope",
            "validator": "repository/src/drd_harness/validators/workpack_scope.py",
            "test": "repository/tests/workpacks/test_workpack_generation.py",
            "acceptance_command": "python3 -m pytest repository/tests/workpacks",
            "validator_check_ids": ["SW-CHECK-010"],
            "allowed_write_paths": [
                "repository/src/drd_harness/orchestrator/**",
                "repository/src/drd_harness/validators/**",
                "repository/schemas/workpacks/**",
                "repository/tests/workpacks/**",
            ],
            "forbidden_write_paths": [
                "constitution/**",
                "control/**",
                ".agents/skills/**",
                "references/**",
                "tooling/**",
            ],
            "dependency_edges": [{"edge_type": "SPEC_LOCK_DEPENDENCY", "subject": "P1_SPEC_LOCK"}],
            "invalidation_policy": "invalidate_workpack_on_spec_lock_drift",
        }
        row.update(overrides)
        return row

    return _trace_row


@pytest.fixture
def workpack():
    def _workpack(**overrides):
        base = {
            "workpack_id": "P1-IMPLEMENT-08",
            "phase": "P1",
            "lane": "implementation",
            "objective": "Implement skills and workpack traceability harness.",
            "required_specs": ["P1-SPEC-08"],
            "required_spec_locks": [{"spec_part": "P1-SPEC-08", "lock_hash": HASH_A}],
            "required_output_families": ["WORKPACK_TRACEABILITY"],
            "required_output_family_locks": [{"output_family": "WORKPACK_TRACEABILITY", "lock_hash": HASH_A}],
            "traceability_rows": ["TRACE-P1-08-001"],
            "allowed_write_paths": [
                "repository/src/drd_harness/orchestrator/**",
                "repository/src/drd_harness/validators/**",
                "repository/schemas/workpacks/**",
                "repository/tests/workpacks/**",
            ],
            "forbidden_write_paths": [
                "constitution/**",
                "control/**",
                ".agents/skills/**",
                "references/**",
                "tooling/**",
            ],
            "code_targets": [
                "repository/src/drd_harness/orchestrator/workpacks.py",
                "repository/src/drd_harness/validators/traceability.py",
            ],
            "changed_paths": [
                "repository/src/drd_harness/orchestrator/workpacks.py",
                "repository/tests/workpacks/test_workpack_generation.py",
            ],
            "validators": ["drd_harness.validators.workpack_scope.validate_workpack_readiness"],
            "tests": ["repository/tests/workpacks/test_workpack_generation.py"],
            "acceptance_commands": ["python3 -m pytest repository/tests/workpacks"],
            "skill_bindings": ["skills/P1-IMPLEMENT-08/SKILL_BINDING.json"],
            "dependency_edges": ["SPEC_LOCK_DEPENDENCY"],
            "status": "READY",
            "review_policy": "human_review_required_before_promotion",
            "promotion_policy": "promotion_requires_approved_review_decision",
            "invalidation_policy": "invalidate_on_spec_or_skill_drift",
        }
        base.update(overrides)
        return base

    return _workpack


@pytest.fixture
def test_matrix_row():
    def _test_matrix_row(**overrides):
        row = {
            "trace_row_id": "TRACE-P1-08-001",
            "implementation_duty": "emit_workpack_envelope",
            "validator_check_ids": ["SW-CHECK-010"],
            "test": "repository/tests/workpacks/test_workpack_generation.py",
            "positive_case": "ready workpack emits a candidate envelope",
            "negative_case": "candidate envelope cannot self approve",
            "acceptance_command": "python3 -m pytest repository/tests/workpacks",
        }
        row.update(overrides)
        return row

    return _test_matrix_row


@pytest.fixture
def skill_manifest():
    def _skill_manifest(**overrides):
        manifest = {
            "skill_id": "P1-IMPLEMENT-08-SKILL",
            "skill_version": "1.0.0",
            "skill_source_path": ".agents/skills/P1-IMPLEMENT-08/SKILL.md",
            "skill_source_hash": HASH_A,
            "bound_spec_locks": [{"lock_id": "P1_SPEC_LOCK", "lock_hash": HASH_A}],
            "allowed_workpack_types": ["implementation"],
            "allowed_write_paths": ["repository/src/drd_harness/**", "repository/tests/workpacks/**"],
            "forbidden_write_paths": ["constitution/**", "control/**", ".agents/skills/**"],
            "allowed_commands": ["python3 -m pytest repository/tests/workpacks"],
            "traceability_rows": ["TRACE-P1-08-001"],
            "validator_refs": ["drd_harness.validators.traceability.validate_code_target_map"],
            "test_refs": ["repository/tests/workpacks/test_skill_version_binding.py"],
            "human_gate_required": True,
            "invalidation_dependencies": ["SPEC_LOCK_DEPENDENCY", "SKILL_DEPENDENCY"],
        }
        manifest.update(overrides)
        return copy.deepcopy(manifest)

    return _skill_manifest
