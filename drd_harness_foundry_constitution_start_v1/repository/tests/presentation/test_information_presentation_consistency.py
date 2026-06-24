from drd_harness.rules.presentation import (
    InformationPresentationDecision,
    PresentationConsistencyException,
    PresentationMode,
)
from drd_harness.validators.presentation_consistency import (
    validate_interaction_message_presentation_mapping,
    validate_presentation_consistency,
)


def decision(presentation_id, mode=PresentationMode.BANNER, **overrides):
    values = {
        "presentation_id": presentation_id,
        "semantic_intent": "Explain export limit before user chooses export strategy.",
        "trigger_condition": "Export requested.",
        "scope": "flow",
        "information_lifecycle": "until resolved",
        "presentation_mode": mode,
        "recoverability": "Recoverable from the export panel.",
        "trace_refs": ["INFO-CONTRACT-001"],
        "user_decision_need": True,
        "sustained_processing_required": True,
        "message_ref": "MSG-EXPORT-LIMIT",
    }
    values.update(overrides)
    return InformationPresentationDecision(**values)


def test_consistent_information_presentation_passes():
    findings = validate_presentation_consistency([decision("PRESENTATION-EXPORT-LIMIT")])

    assert findings == []


def test_transient_only_sustained_information_fails():
    findings = validate_presentation_consistency(
        [
            decision(
                "PRESENTATION-EXPORT-LIMIT",
                PresentationMode.TOAST,
                recoverability="Unrecoverable after timeout.",
            )
        ]
    )

    assert "PL004" in {finding.code for finding in findings}


def test_equivalent_semantics_with_different_modes_require_exception():
    findings = validate_presentation_consistency(
        [
            decision("PRESENTATION-A", PresentationMode.BANNER),
            decision("PRESENTATION-B", PresentationMode.MODAL_DIALOG),
        ]
    )

    assert "PL003" in {finding.code for finding in findings}


def test_equivalent_semantics_with_exception_passes_consistency_check():
    exception = PresentationConsistencyException(
        "EXCEPTION-EXPORT-LIMIT",
        "Explain export limit before user chooses export strategy.",
        "Export requested.",
        "flow",
        "until resolved",
        [PresentationMode.BANNER, PresentationMode.MODAL_DIALOG],
        "Modal is used only when the export request would discard unsaved work.",
        ["HUMAN-GATE"],
    )

    findings = validate_presentation_consistency(
        [
            decision("PRESENTATION-A", PresentationMode.BANNER),
            decision("PRESENTATION-B", PresentationMode.MODAL_DIALOG),
        ],
        [exception],
    )

    assert findings == []


def test_interaction_message_mapping_required():
    findings = validate_interaction_message_presentation_mapping(
        ["MSG-EXPORT-LIMIT", "MSG-FAILURE"],
        [decision("PRESENTATION-EXPORT-LIMIT")],
    )

    assert "PL005" in {finding.code for finding in findings}
