from drd_harness.validators.postflight import build_scope_report, validate_scope


def test_scope_postflight_accepts_allowed_paths():
    findings = validate_scope(
        ["repository/src/drd_harness/validators/spec_validator.py"],
        ["repository/src/drd_harness/validators/**"],
        ["control/**", "constitution/**"],
    )

    assert findings == []


def test_scope_postflight_rejects_forbidden_path_before_allowed_path():
    findings = validate_scope(
        ["control/locks/P1_BUILD_LOCK.json"],
        ["control/**", "repository/src/drd_harness/validators/**"],
        ["control/**"],
    )

    assert findings[0].code == "VLOCK-CHECK-003"
    assert "forbidden" in findings[0].message


def test_scope_postflight_rejects_outside_allowed_paths():
    findings = validate_scope(
        ["repository/src/drd_harness/compiler/future.py"],
        ["repository/src/drd_harness/validators/**"],
        ["control/**"],
    )

    assert findings[0].message == "changed path is outside allowed scope"


def test_scope_report_marks_failure_when_findings_exist():
    report = build_scope_report(
        ["references/source.md"],
        ["repository/src/drd_harness/validators/**"],
        ["references/**"],
    )

    assert report["status"] == "FAIL"
    assert report["findings"][0]["code"] == "VLOCK-CHECK-003"
