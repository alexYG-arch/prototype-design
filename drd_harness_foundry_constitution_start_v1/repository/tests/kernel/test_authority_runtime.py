import pytest

from drd_harness.kernel.authority import AuthorityLevel, can_override, require_no_silent_override
from drd_harness.kernel.runtime import PrimaryRuntime, RuntimeDeclaration


def test_authority_order_allows_higher_authority_to_override_lower():
    assert can_override(AuthorityLevel.HUMAN_DECISION, AuthorityLevel.CANDIDATE_OUTPUT)
    assert not can_override(AuthorityLevel.CANDIDATE_OUTPUT, AuthorityLevel.HUMAN_DECISION)


def test_no_silent_override_rejects_lower_authority_override():
    with pytest.raises(ValueError, match="cannot override"):
        require_no_silent_override(AuthorityLevel.SKILL_AND_WORKPACK, AuthorityLevel.LOCKED_CONSTITUTION_AND_CONTRACT)


def test_runtime_declaration_round_trips_required_fields():
    declaration = RuntimeDeclaration.from_dict(
        {
            "unit_id": "DRD-02",
            "primary_runtime": "CODEX_PYTHON_LOOP",
            "python_duties": ["Validate graph closure"],
            "codex_duties": ["Derive candidate interaction states"],
            "validator": "interaction_closure_validator",
            "human_gate": "Review A",
            "authority_inputs": ["locked interaction contract"],
            "write_scope": ["candidate interaction artifacts"],
            "forbidden_scope": ["locked contracts"],
        }
    )

    assert declaration.primary_runtime is PrimaryRuntime.CODEX_PYTHON_LOOP
    assert declaration.to_dict()["unit_id"] == "DRD-02"
    declaration.validate_responsibilities()


def test_runtime_declaration_requires_explicit_fields():
    with pytest.raises(ValueError, match="missing fields"):
        RuntimeDeclaration.from_dict({"unit_id": "DRD-00"})


def test_codex_runtime_does_not_own_promotion_or_locking():
    declaration = RuntimeDeclaration.from_dict(
        {
            "unit_id": "PROMOTE-DRD-02",
            "primary_runtime": "CODEX",
            "python_duties": [],
            "codex_duties": ["Approve and promote its own candidate"],
            "validator": "foundation_validator",
            "human_gate": "Review A",
            "authority_inputs": ["candidate"],
            "write_scope": ["candidate output"],
            "forbidden_scope": ["canonical output"],
        }
    )

    with pytest.raises(ValueError, match="authority-changing"):
        declaration.validate_responsibilities()
