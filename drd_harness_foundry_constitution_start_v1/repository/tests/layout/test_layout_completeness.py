from drd_harness.rules.layout import NaturalLanguageLayout
from drd_harness.validators.layout_completeness import validate_natural_language_layout


COMPLETE_LAYOUT_TEXT = (
    "The desktop carrier uses a two-column main container with a header region and main section. "
    "The hierarchy has primary and secondary groups inside parent and child containment. "
    "Project fields appear before activity, and actions are below details in local order. "
    "Each region states width, height, minimum sizing, density, wrapping, scroll, sticky header, and fixed footer behavior. "
    "Tablet and mobile carriers stack sections responsively; iOS uses safe area and navigation stack constraints, "
    "while Material uses app bar, keyboard inset, system bar constraints, and elevation. "
    "Empty, loading, error, disabled, permission, success, recovery, and validation state placement is described. "
    "Long content growth can wrap, overflow into scroll, truncate with recovery, expand, or use pagination. "
    "Overlay, modal, drawer, popover, toast, and loading layer z-axis behavior preserves focus restoration."
)


def layout(text=COMPLETE_LAYOUT_TEXT, **overrides):
    values = {
        "layout_id": "LAYOUT-PROJECT",
        "surface_id": "SURFACE-PROJECT",
        "layout_body_ref": "LAYOUT.md#project",
        "layout_text": text,
        "semantic_authority": "Natural language layout prose is the canonical semantic authority.",
        "inventory_role": "Inventory records are index and validation skeleton only.",
        "carrier_profile_refs": ["CARRIER-PROJECT"],
        "section_index": ["Header", "Main", "Activity"],
        "containment_tree_ref": "TREE-PROJECT",
        "pattern_refs": ["PATTERN-STATUS-BANNER"],
        "state_variants": ["failed"],
        "content_growth_refs": ["GROWTH-PROJECT"],
        "z_axis_refs": ["Z-PROJECT"],
        "information_completeness_refs": ["INFO-PROJECT"],
        "figma_metadata_ref": "FIGMA-PROJECT",
        "trace_refs": ["LAYOUT-CONTRACT-002"],
    }
    values.update(overrides)
    return NaturalLanguageLayout(**values)


def test_complete_natural_language_layout_passes():
    assert validate_natural_language_layout(layout()) == []


def test_thin_layout_fails():
    findings = validate_natural_language_layout(layout("Show the project page with details and actions."))

    assert "PL006" in {finding.code for finding in findings}


def test_layout_requires_growth_and_information_completeness_refs():
    findings = validate_natural_language_layout(layout(content_growth_refs=[], information_completeness_refs=[]))

    assert "PL006" in {finding.code for finding in findings}


def test_layout_requires_natural_language_as_canonical_semantic_authority():
    findings = validate_natural_language_layout(
        layout(semantic_authority="Inventory is the canonical source of truth.")
    )

    assert "PL006" in {finding.code for finding in findings}


def test_layout_inventory_role_must_be_index_and_validation_skeleton_only():
    findings = validate_natural_language_layout(
        layout(inventory_role="Inventory is semantic authority for layout meaning.")
    )

    assert "PL006" in {finding.code for finding in findings}
