from drd_harness.rules.presentation import PatternKind, SharedComponentPattern
from drd_harness.validators.presentation_consistency import validate_shared_component_pattern


def semantic_pattern(**overrides):
    values = {
        "pattern_id": "PATTERN-STATUS-BANNER",
        "pattern_kind": PatternKind.PRESENTATION_PATTERN,
        "semantic_role": "Page-level recoverable status",
        "data_structure": ["status", "reason", "primary_action"],
        "operation_set": ["retry", "return"],
        "state_model": ["blocked", "recoverable"],
        "information_hierarchy": ["reason", "next action"],
        "interaction_model": ["retry reaction", "return reaction"],
        "surface_constraints": ["page header area"],
        "reuse_scope": ["recoverable page-level blocked states"],
        "trace_refs": ["PL-RULE-001"],
        "reuse_reason": "Same semantic role, data, operations, and state model.",
    }
    values.update(overrides)
    return SharedComponentPattern(**values)


def test_semantic_shared_component_passes():
    assert validate_shared_component_pattern(semantic_pattern()) == []


def test_visual_only_shared_component_fails():
    pattern = semantic_pattern(
        semantic_role="Reusable blue card",
        data_structure=[],
        operation_set=[],
        state_model=[],
        information_hierarchy=[],
        interaction_model=[],
        reuse_scope=["same color and icon"],
        reuse_reason="Both cards are blue and have an icon.",
    )

    findings = validate_shared_component_pattern(pattern)

    assert {"PL001", "PL002"} <= {finding.code for finding in findings}


def test_missing_trace_fails_shared_component():
    findings = validate_shared_component_pattern(semantic_pattern(trace_refs=[]))

    assert "PL001" in {finding.code for finding in findings}
