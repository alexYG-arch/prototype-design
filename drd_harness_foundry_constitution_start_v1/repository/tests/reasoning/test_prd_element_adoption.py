from drd_harness.rules.prd_adoption import (
    AdoptionOutcome,
    ElementType,
    PrdElementDecision,
    PrdElementInventoryItem,
)
from drd_harness.validators.prd_adoption import (
    validate_adoption_decision,
    validate_inventory_coverage,
)


def inventory_item(element_id="EL-LOGIN-CTA"):
    return PrdElementInventoryItem(
        element_id=element_id,
        element_type=ElementType.CTA,
        source_refs=["PRD:auth:login_button"],
        source_text_hash="a" * 64,
        stage_id="DRD-03",
        artifact_id="PRD_EXPLICIT_ELEMENT_INVENTORY",
    )


def adoption_decision(element_id="EL-LOGIN-CTA", outcome=AdoptionOutcome.ADOPT_AS_IS):
    return PrdElementDecision(
        element_id=element_id,
        source_refs=["PRD:auth:login_button"],
        element_type=ElementType.CTA,
        outcome=outcome,
        normalized_label=None,
        blocking_reason=None,
        input_obligations=[],
        inference_refs=["INF-LOGIN-CTA-001"],
    )


def test_inventory_element_has_exactly_one_decision():
    assert validate_inventory_coverage([inventory_item()], [adoption_decision()]) == []


def test_missing_adoption_decision_is_reported():
    findings = validate_inventory_coverage([inventory_item()], [])

    assert [finding.code for finding in findings] == ["REASON013"]


def test_decision_for_non_inventory_element_is_reported():
    findings = validate_inventory_coverage([inventory_item()], [adoption_decision("EL-OTHER")])

    assert [finding.code for finding in findings] == ["REASON013"]


def test_normalized_adoption_requires_normalized_label():
    findings = validate_adoption_decision(adoption_decision(outcome=AdoptionOutcome.ADOPT_NORMALIZED))

    assert [finding.code for finding in findings] == ["REASON006"]


def test_product_gap_outcome_requires_blocking_reason():
    findings = validate_adoption_decision(adoption_decision(outcome=AdoptionOutcome.ROUTE_PRODUCT_GAP))

    assert [finding.code for finding in findings] == ["REASON006"]
