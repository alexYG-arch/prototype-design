from drd_harness.validators.traceability import (
    validate_orphan_code_targets,
    validate_trace_row_to_test_matrix,
)


def test_test_obligation_matrix_binds_validator_test_and_acceptance(trace_row, test_matrix_row):
    assert validate_trace_row_to_test_matrix([trace_row()], [test_matrix_row()]) == []


def test_positive_and_negative_test_obligations_are_required(trace_row, test_matrix_row):
    findings = validate_trace_row_to_test_matrix([trace_row()], [test_matrix_row(negative_case="")])

    assert findings[0].code == "SW-CHECK-008"


def test_trace_row_and_matrix_must_match(trace_row, test_matrix_row):
    findings = validate_trace_row_to_test_matrix(
        [trace_row()],
        [test_matrix_row(validator_check_ids=["SW-CHECK-011"])],
    )

    assert "SW-CHECK-019" in {finding.code for finding in findings}


def test_extra_test_matrix_row_without_trace_row_is_rejected(trace_row, test_matrix_row):
    findings = validate_trace_row_to_test_matrix(
        [trace_row()],
        [
            test_matrix_row(),
            test_matrix_row(trace_row_id="TRACE-P1-08-EXTRA"),
        ],
    )

    assert "SW-CHECK-019" in {finding.code for finding in findings}
    assert "lacks matching trace row" in " ".join(finding.message for finding in findings)


def test_duplicate_test_matrix_row_is_rejected(trace_row, test_matrix_row):
    findings = validate_trace_row_to_test_matrix(
        [trace_row()],
        [
            test_matrix_row(),
            test_matrix_row(),
        ],
    )

    assert "duplicate test obligation row" in " ".join(finding.message for finding in findings)


def test_orphan_code_target_is_rejected(trace_row):
    findings = validate_orphan_code_targets(
        [
            "repository/src/drd_harness/orchestrator/workpacks.py",
            "repository/src/drd_harness/orchestrator/extra.py",
        ],
        [trace_row()],
    )

    assert findings[0].code == "SW-CHECK-015"
