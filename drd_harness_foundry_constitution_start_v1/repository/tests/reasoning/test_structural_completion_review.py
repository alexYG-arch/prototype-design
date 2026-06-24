from drd_harness.rules.reasoning import (
    CanonicalEligibility,
    ProductExpansionRisk,
    StructuralCompletionReview,
)
from drd_harness.validators.reasoning import validate_structural_completion_review


def test_structural_completion_review_blocks_before_human_gate():
    review = StructuralCompletionReview(
        review_id="SCR-PROJECT-DASHBOARD-001",
        required_page_or_flow="Project Dashboard",
        missing_surface_summary=["Dashboard sections are not specified."],
        deductive_obligations=["A named page must have executable content."],
        candidate_options=["Summary cards plus activity list"],
        product_expansion_risk=ProductExpansionRisk.NONE,
        canonical_eligibility=CanonicalEligibility.BLOCKED_PENDING_HUMAN,
    )

    assert validate_structural_completion_review(review) == []


def test_structural_completion_cannot_be_eligible_without_human_gate():
    review = StructuralCompletionReview(
        review_id="SCR-PROJECT-DASHBOARD-001",
        required_page_or_flow="Project Dashboard",
        missing_surface_summary=["Dashboard sections are not specified."],
        deductive_obligations=["A named page must have executable content."],
        candidate_options=["Summary cards plus activity list"],
        product_expansion_risk=ProductExpansionRisk.NONE,
        canonical_eligibility=CanonicalEligibility.ELIGIBLE,
    )

    findings = validate_structural_completion_review(review)

    assert [finding.code for finding in findings] == ["REASON015"]


def test_product_expansion_inside_structural_completion_is_reported():
    review = StructuralCompletionReview(
        review_id="SCR-SETTINGS-001",
        required_page_or_flow="Settings",
        missing_surface_summary=["Settings categories are not specified."],
        deductive_obligations=["Settings page must expose executable settings surfaces."],
        candidate_options=["Profile settings", "Automation rule builder"],
        product_expansion_risk=ProductExpansionRisk.PRESENT,
        canonical_eligibility=CanonicalEligibility.BLOCKED_PENDING_HUMAN,
    )

    findings = validate_structural_completion_review(review)

    assert [finding.code for finding in findings] == ["REASON016"]
