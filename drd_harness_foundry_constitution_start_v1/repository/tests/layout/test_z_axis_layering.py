from drd_harness.rules.layout import LayerKind, ZAxisLayer, ZAxisLayering
from drd_harness.validators.layout_completeness import validate_z_axis_layering


def layering(material=True):
    return ZAxisLayering(
        "Z-PROJECT",
        [
            ZAxisLayer(0, "page content", LayerKind.BASE, False, True, "Base content remains behind overlays."),
            ZAxisLayer(10, "sticky header", LayerKind.STICKY, False, True, "Header stays above content."),
            ZAxisLayer(50, "confirmation modal", LayerKind.MODAL, True, True, "Modal occludes and blocks lower layers."),
        ],
        "Material modal elevation sits above sticky and fixed regions." if material else None,
        "Focus returns to the triggering action after close.",
        ["PL-RULE-013"],
    )


def test_z_axis_layering_passes_with_material_intent():
    assert validate_z_axis_layering(layering(), material_profile_required=True) == []


def test_material_layering_requires_elevation_intent():
    findings = validate_z_axis_layering(layering(material=False), material_profile_required=True)

    assert "PL013" in {finding.code for finding in findings}


def test_modal_layering_requires_blocking_behavior():
    broken = ZAxisLayering(
        "Z-PROJECT",
        [ZAxisLayer(50, "confirmation modal", LayerKind.MODAL, False, True, "Modal appears above content.")],
        "Material elevation declared.",
        "Focus returns after close.",
        ["PL-RULE-013"],
    )

    findings = validate_z_axis_layering(broken, material_profile_required=True)

    assert "PL013" in {finding.code for finding in findings}
