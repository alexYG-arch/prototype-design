import pytest

from drd_harness.rules.reasoning import (
    CanonicalEligibility,
    InferenceClass,
    InferenceRecord,
    InputObligation,
)
from drd_harness.validators.reasoning import (
    require_canonical_consumption_allowed,
    validate_inference_record,
    validate_input_obligation,
)


def eligible_deductive_record():
    return InferenceRecord(
        inference_id="INF-ADDR-001",
        inference_class=InferenceClass.DEDUCTIVE_NECESSITY,
        stage_id="DRD-03",
        artifact_id="PAGE_ELEMENT_BLUEPRINT",
        source_refs=["PRD:checkout:shipping_required", "RD-RULE-001"],
        premises=["Checkout cannot complete without shipping address."],
        applied_rules=["RD-RULE-001"],
        necessity_basis="The task cannot complete unless shipping address is obtained.",
        unresolved_product_choices=[],
        conclusion="Checkout requires an address input path.",
        canonical_eligibility=CanonicalEligibility.ELIGIBLE,
        downstream_use=["PAGE_ELEMENT_BLUEPRINT"],
    )


def test_deductive_necessity_record_passes():
    assert validate_inference_record(eligible_deductive_record()) == []
    require_canonical_consumption_allowed(eligible_deductive_record())


def test_deductive_necessity_requires_empty_unresolved_product_choices():
    record = eligible_deductive_record()
    blocked = InferenceRecord(
        **{**record.__dict__, "unresolved_product_choices": ["choose address provider"]}
    )

    findings = validate_inference_record(blocked)

    assert [finding.code for finding in findings] == ["REASON003"]


def test_inductive_candidate_is_blocked_from_canonical_use():
    record = InferenceRecord(
        inference_id="INF-SOCIAL-LOGIN-001",
        inference_class=InferenceClass.INDUCTIVE_CANDIDATE,
        stage_id="DRD-03",
        artifact_id="PAGE_ELEMENT_BLUEPRINT",
        source_refs=["pattern:common_auth_flows"],
        premises=["Many auth flows offer social login."],
        applied_rules=["REASON-CONTRACT-002"],
        necessity_basis=None,
        unresolved_product_choices=[],
        conclusion="Add social login.",
        canonical_eligibility=CanonicalEligibility.ELIGIBLE,
        downstream_use=["PAGE_ELEMENT_BLUEPRINT"],
    )

    findings = validate_inference_record(record)

    assert [finding.code for finding in findings] == ["REASON004"]


def test_rejected_inference_cannot_be_consumed_downstream():
    record = InferenceRecord(
        inference_id="INF-REJECTED-001",
        inference_class=InferenceClass.REJECTED_INFERENCE,
        stage_id="DRD-03",
        artifact_id="PAGE_ELEMENT_BLUEPRINT",
        source_refs=["Review:reject"],
        premises=["Rejected by Human Gate."],
        applied_rules=["REASON-RULE-006"],
        necessity_basis=None,
        unresolved_product_choices=[],
        conclusion="Rejected feature.",
        canonical_eligibility=CanonicalEligibility.REJECTED,
        downstream_use=["PAGE_ELEMENT_BLUEPRINT"],
    )

    findings = validate_inference_record(record)

    assert [finding.code for finding in findings] == ["REASON011"]


def test_input_obligation_requires_path_or_gap():
    findings = validate_input_obligation(
        InputObligation(
            obligation_id="INPUT-QUOTE-001",
            required_input="quote details",
            task_ref="TASK-QUOTE",
            acquisition_path=None,
            gap_ref=None,
        )
    )

    assert [finding.code for finding in findings] == ["REASON008"]


def test_canonical_consumption_rejects_inductive_class():
    record = eligible_deductive_record()
    inductive = InferenceRecord(**{**record.__dict__, "inference_class": InferenceClass.INDUCTIVE_CANDIDATE})

    with pytest.raises(ValueError, match="non-canonical"):
        require_canonical_consumption_allowed(inductive)
