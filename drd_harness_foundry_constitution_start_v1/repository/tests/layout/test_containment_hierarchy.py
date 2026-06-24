from drd_harness.rules.layout import ContainmentHierarchy, ContainmentNode, SurfaceKind
from drd_harness.validators.layout_completeness import (
    validate_containment_hierarchy,
    validate_nested_surface_layout,
)


def node(node_id, kind, parent, order, **overrides):
    values = {
        "node_id": node_id,
        "surface_kind": kind,
        "parent_id": parent,
        "order": order,
        "arrangement": "Vertical stack inside parent.",
        "sizing": "Fills available width with minimum readable height.",
        "scroll_behavior": "Participates in parent scroll without contradiction.",
        "width_behavior": "Wraps inside parent width.",
    }
    values.update(overrides)
    return ContainmentNode(**values)


def hierarchy(nodes):
    return ContainmentHierarchy("TREE-PROJECT", "SURFACE-PROJECT", nodes)


def test_multilevel_containment_passes():
    tree = hierarchy(
        [
            node("PAGE", SurfaceKind.PAGE, None, 0),
            node("MAIN", SurfaceKind.SECTION, "PAGE", 0),
            node("FIELDS", SurfaceKind.GROUP, "MAIN", 0),
            node("FIELD-ROW", SurfaceKind.REPEATED_ITEM, "FIELDS", 0),
        ]
    )

    assert validate_containment_hierarchy(tree) == []


def test_flat_containment_fails():
    findings = validate_containment_hierarchy(hierarchy([node("PAGE", SurfaceKind.PAGE, None, 0)]))

    assert "PL008" in {finding.code for finding in findings}


def test_child_contradiction_fails():
    tree = hierarchy(
        [
            node("PAGE", SurfaceKind.PAGE, None, 0),
            node("MAIN", SurfaceKind.SECTION, "PAGE", 0, width_behavior="ignore parent width"),
        ]
    )

    findings = validate_containment_hierarchy(tree)

    assert "PL008" in {finding.code for finding in findings}


def test_nested_surface_requires_entry_and_return_placement():
    tree = hierarchy(
        [
            node("PAGE", SurfaceKind.PAGE, None, 0),
            node("MAIN", SurfaceKind.SECTION, "PAGE", 0),
            node("DETAIL-DRAWER", SurfaceKind.DRAWER, "MAIN", 1),
        ]
    )

    findings = validate_nested_surface_layout(tree)

    assert "PL012" in {finding.code for finding in findings}
