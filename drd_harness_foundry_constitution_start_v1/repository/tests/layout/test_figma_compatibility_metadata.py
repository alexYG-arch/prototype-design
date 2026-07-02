from drd_harness.rules.layout import FigmaReconstructionMetadata, NaturalLanguageLayout
from drd_harness.validators.layout_completeness import validate_figma_metadata


def metadata(**overrides):
    values = {
        "figma_metadata_id": "FIGMA-PROJECT",
        "layout_id": "LAYOUT-PROJECT",
        "frame_hierarchy": ["Page frame", "Header", "Main content"],
        "selection_box_hierarchy": ["Status banner group", "Project fields group"],
        "auto_layout_guidance": "Main content is horizontal on desktop and vertical on narrow carriers.",
        "component_instances": ["PATTERN-STATUS-BANNER"],
        "state_variants": ["failed"],
        "carrier_variants": ["CARRIER-PROJECT"],
        "z_axis_layers": ["Z-PROJECT"],
        "scroll_frames": ["Activity list"],
        "constraints": ["Header fills width", "Activity list vertical scroll"],
        "non_goals": ["No Figma API call", "No renderer implementation", "No file write"],
        "trace_refs": ["FIGMA-CONTRACT-001"],
        "page_arrangement_order": [
            {
                "module_id": "module-project",
                "function_group_id": "function-project",
                "variant_page_id": "Page frame",
                "frame_id": "Page frame",
                "page_order_index": 0,
                "variant_order_index": 0,
                "figma_frame_order_index": 0,
                "derivation_origin": "PRD_EXPLICIT",
            }
        ],
    }
    values.update(overrides)
    return FigmaReconstructionMetadata(**values)


def layout():
    return NaturalLanguageLayout(
        "LAYOUT-PROJECT",
        "SURFACE-PROJECT",
        "LAYOUT.md#project",
        "Desktop, tablet, mobile, iOS, and Material layout authority.",
        "Natural language layout prose is the canonical semantic authority.",
        "Inventory records are index and validation skeleton only.",
        ["CARRIER-PROJECT"],
        ["Header", "Main"],
        "TREE-PROJECT",
        ["PATTERN-STATUS-BANNER"],
        ["failed"],
        ["GROWTH-PROJECT"],
        ["Z-PROJECT"],
        ["INFO-PROJECT"],
        "FIGMA-PROJECT",
        ["FIGMA-CONTRACT-002"],
    )


def test_figma_metadata_passes_when_derived_from_layout():
    assert validate_figma_metadata(metadata(), layout()) == []


def test_figma_metadata_rejects_write_authority():
    findings = validate_figma_metadata(
        metadata(non_goals=["Renderer implementation may write to Figma API"]),
        layout(),
    )

    assert "PL015" in {finding.code for finding in findings}


def test_figma_metadata_rejects_semantic_drift():
    findings = validate_figma_metadata(
        metadata(component_instances=["PATTERN-NEW-PRODUCT-CARD"]),
        layout(),
    )

    assert "PL016" in {finding.code for finding in findings}


def test_figma_metadata_requires_module_function_page_arrangement():
    findings = validate_figma_metadata(
        metadata(page_arrangement_order=[]),
        layout(),
    )

    assert "PL014" in {finding.code for finding in findings}


def test_figma_metadata_rejects_arrangement_frame_order_drift():
    findings = validate_figma_metadata(
        metadata(
            page_arrangement_order=[
                {
                    "module_id": "module-project",
                    "function_group_id": "function-project",
                    "variant_page_id": "Header",
                    "frame_id": "Header",
                    "page_order_index": 0,
                    "variant_order_index": 0,
                    "figma_frame_order_index": 0,
                    "derivation_origin": "PRD_EXPLICIT",
                }
            ]
        ),
        layout(),
    )

    assert "PL017" in {finding.code for finding in findings}
