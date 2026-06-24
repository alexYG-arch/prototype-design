from drd_harness.validators.traceability import validate_code_target_map


def test_complete_trace_row_passes(trace_row):
    assert validate_code_target_map([trace_row()]) == []


def test_missing_projection_and_check_ids_are_rejected(trace_row):
    row = trace_row(projection_id="", validator_check_ids=[])

    codes = {finding.code for finding in validate_code_target_map([row])}

    assert "SW-CHECK-003" in codes


def test_multi_obligation_or_generic_row_is_rejected(trace_row):
    row = trace_row(
        implementation_duty="handle_skills_and_workpack",
        validator_check_ids=["SW-CHECK-003", "SW-CHECK-004"],
    )

    assert "SW-CHECK-004" in {finding.code for finding in validate_code_target_map([row])}


def test_code_target_outside_allowed_paths_and_forbidden_path_is_rejected(trace_row):
    row = trace_row(
        code_target="control/locks/P1_SPEC_LOCK.json",
        allowed_write_paths=["repository/src/drd_harness/**"],
        forbidden_write_paths=["control/**"],
    )

    codes = {finding.code for finding in validate_code_target_map([row])}

    assert {"SW-CHECK-005", "SW-CHECK-006"} <= codes
