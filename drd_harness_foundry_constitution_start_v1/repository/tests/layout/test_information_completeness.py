from drd_harness.rules.layout import ContentGrowthRule, InformationCompletenessRule
from drd_harness.validators.layout_completeness import (
    validate_content_growth_rule,
    validate_information_completeness_rule,
)


def test_content_growth_with_recovery_passes():
    rule = ContentGrowthRule(
        "GROWTH-PROJECT",
        "FIELDS",
        ["project name", "activity list"],
        "Long labels wrap before truncation.",
        "Overflow is contained inside the section.",
        "Activity list scrolls when item count grows.",
        None,
        "Project name truncates after two lines.",
        "Full title is available in detail expansion.",
        "Sections can expand.",
        "Pagination applies after many activity rows.",
        "Empty collection shows an empty state.",
        ["PL-RULE-010"],
    )

    assert validate_content_growth_rule(rule) == []


def test_truncation_without_recovery_fails():
    rule = ContentGrowthRule(
        "GROWTH-PROJECT",
        "FIELDS",
        ["project name"],
        "Long labels wrap.",
        "Overflow is contained.",
        "Page scrolls.",
        None,
        "Project name truncates.",
        None,
        None,
        None,
        "Empty state appears.",
        ["PL-RULE-010"],
    )

    findings = validate_content_growth_rule(rule)

    assert "PL009" in {finding.code for finding in findings}


def test_information_completeness_under_height_and_width_passes():
    rule = InformationCompletenessRule(
        "INFO-PROJECT",
        ["required fields", "activity"],
        "Short height uses vertical scroll.",
        "Narrow width stacks and wraps content.",
        "All required information remains available by scroll and expansion.",
        ["LAYOUT-CONTRACT-010"],
    )

    assert validate_information_completeness_rule(rule) == []


def test_height_limited_information_loss_fails():
    rule = InformationCompletenessRule(
        "INFO-PROJECT",
        ["required fields"],
        "Hide the rest when the screen is short.",
        "Narrow width stacks content.",
        "No recovery path.",
        ["LAYOUT-CONTRACT-010"],
    )

    findings = validate_information_completeness_rule(rule)

    assert "PL010" in {finding.code for finding in findings}


def test_width_constraint_ignored_fails():
    rule = InformationCompletenessRule(
        "INFO-PROJECT",
        ["required fields"],
        "Short height uses scroll.",
        "Ignore width and allow overflow offscreen.",
        "All information can be recovered by scroll.",
        ["LAYOUT-CONTRACT-010"],
    )

    findings = validate_information_completeness_rule(rule)

    assert "PL010" in {finding.code for finding in findings}


def test_declared_horizontal_scroll_exception_passes_width_overflow_case():
    rule = InformationCompletenessRule(
        "INFO-WIDE-TABLE",
        ["wide comparison table"],
        "Short height uses vertical scroll.",
        "Narrow width may overflow offscreen only in the table state with horizontal scroll.",
        "Required columns remain available by horizontal scroll and detail expansion.",
        ["LAYOUT-CONTRACT-010"],
        horizontal_scroll_exception="Wide tables declare a horizontal scroll exception with visible affordance.",
    )

    assert validate_information_completeness_rule(rule) == []


def test_width_overflow_without_horizontal_scroll_exception_fails():
    rule = InformationCompletenessRule(
        "INFO-WIDE-TABLE",
        ["wide comparison table"],
        "Short height uses vertical scroll.",
        "Narrow width may overflow offscreen.",
        "Required columns remain available by scroll.",
        ["LAYOUT-CONTRACT-010"],
    )

    findings = validate_information_completeness_rule(rule)

    assert "PL010" in {finding.code for finding in findings}
