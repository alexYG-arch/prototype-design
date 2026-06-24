# P1-SPEC-05 Presentation Layout Examples

## Positive Example: Shared Component Based On Semantics

```json
{
  "pattern_id": "PATTERN-STATUS-BANNER",
  "pattern_kind": "presentation pattern",
  "semantic_role": "Page-level blocking status",
  "data_structure": ["status", "reason", "primary_action"],
  "operation_set": ["retry", "return"],
  "state_model": ["blocked", "recoverable"],
  "information_hierarchy": ["reason", "next action"],
  "interaction_model": ["retry reaction", "return reaction"],
  "surface_constraints": ["page header area"],
  "reuse_scope": ["recoverable page-level blocked states"]
}
```

Why this passes:

- Sharing is justified by semantic role, data, actions, and state model.

## Negative Example: Visual-Only Merge

```json
{
  "pattern_id": "PATTERN-BLUE-CARD",
  "semantic_role": "Reusable card",
  "reuse_reason": "Both cards are blue and have an icon."
}
```

Expected result: fail.

Reason:

- Visual similarity is not enough to share a component.

## Negative Example: Transient-Only Decision Information

```json
{
  "presentation_id": "PRESENTATION-EXPORT-LIMIT",
  "semantic_intent": "Explain export limit before user chooses export strategy.",
  "scope": "flow",
  "information_lifecycle": "until resolved",
  "presentation_mode": "TOAST"
}
```

Expected result: fail.

Reason:

- A user decision depends on the information, so it cannot be only a short-lived toast.

## Positive Example: Natural-Language Layout

```markdown
The Project Detail page uses a two-column desktop structure. The page container contains a header, then a main content region. The main content region contains a left project-summary column and a right activity column. The left column contains the project identity group, status banner group, and key fields group in that order. The right column contains the activity list group above the recovery actions group. On tablet, the two columns remain side by side only when both columns can keep their minimum readable widths; otherwise the right column stacks below the left column. On mobile, the page becomes a single vertical stack. The iOS profile keeps content inside safe areas and uses navigation-stack placement for back behavior. The Material profile uses app-bar placement and declares elevation for the status banner, bottom action region, and modal overlays. The activity list scrolls within its section after ten items on desktop, but becomes part of the page scroll on mobile. Long project names wrap to two lines before truncating and provide a full-title recovery path. Failed sync state replaces the status banner with a recoverable error banner and keeps the retry action in the same section. Required project fields remain accessible by vertical scroll when screen height is short.
```

Why this passes:

- It describes carrier profiles, multi-level containment, order, responsive behavior, scroll, width-constrained wrapping, height-unbounded completeness, Material z-axis intent, and state placement.

## Positive Example: Carrier Adaptation Profile

```json
{
  "carrier_profile_id": "CARRIER-PROJECT-DETAIL",
  "required_carriers": ["DESKTOP", "TABLET", "MOBILE_IOS", "MOBILE_MATERIAL"],
  "desktop": {
    "arrangement": "Two-column main content with fixed header and internal activity scroll.",
    "width_constraint": "Columns keep minimum readable width before stacking."
  },
  "tablet": {
    "arrangement": "Two-column when width permits; stacked when minimum readable widths would be violated.",
    "orientation_change": "Landscape may use two columns; portrait stacks."
  },
  "mobile_ios": {
    "arrangement": "Single-column page scroll.",
    "platform_constraints": ["safe-area aware content", "navigation-stack back behavior", "keyboard avoidance for edit surfaces"]
  },
  "mobile_material": {
    "arrangement": "Single-column page scroll with Material app bar.",
    "platform_constraints": ["Material navigation behavior", "Material elevation for layered surfaces", "keyboard inset handling"]
  }
}
```

Why this passes:

- Carrier differences are explicit instead of being left to responsive defaults.

## Negative Example: Height-Limited Information Loss

```markdown
On mobile, show the first three project fields and hide the rest when the screen is short.
```

Expected result: fail.

Reason:

- Required information is removed because height is limited. The layout must provide scroll, expansion, pagination, or another access path.

## Negative Example: Flat Containment

```json
{
  "sections": ["Header", "Project fields", "Activity", "Actions", "Errors"]
}
```

Expected result: fail when nested regions exist.

Reason:

- The record does not show page container, region, group, repeated item, state container, or parent-child ordering and scroll coupling.

## Positive Example: Z-Axis Layering

```json
{
  "z_axis_layer_id": "Z-PROJECT-DETAIL",
  "layers": [
    {"layer": 0, "surface": "page content", "blocks_lower_layers": false},
    {"layer": 10, "surface": "sticky header", "blocks_lower_layers": false},
    {"layer": 20, "surface": "bottom action region", "blocks_lower_layers": false},
    {"layer": 50, "surface": "confirmation modal", "blocks_lower_layers": true}
  ],
  "material_elevation_intent": "Modal overlays sit above sticky and fixed regions and block lower-layer interaction.",
  "focus_restoration": "Return focus to the triggering action after modal close."
}
```

Why this passes:

- Layer order, Material elevation intent, blocking behavior, and focus restoration are explicit.

## Negative Example: Layout Too Thin

```markdown
Show the project page with details and actions.
```

Expected result: fail.

Reason:

- It does not define spatial structure, hierarchy, containment, ordering, sizing, scroll, states, or growth behavior.

## Positive Example: Figma Metadata

```json
{
  "figma_metadata_id": "FIGMA-PROJECT-DETAIL",
  "layout_id": "LAYOUT-PROJECT-DETAIL",
  "frame_hierarchy": ["Page frame", "Header", "Main content", "Left stack", "Right stack"],
  "selection_box_hierarchy": ["Status banner group", "Project fields group", "Activity list group"],
  "auto_layout_guidance": "Main content is horizontal on desktop and vertical on narrow surfaces.",
  "component_instances": ["PATTERN-STATUS-BANNER"],
  "state_variants": ["default", "loading", "sync failed"],
  "carrier_variants": ["desktop", "tablet", "mobile_iOS", "mobile_Material"],
  "z_axis_layers": ["sticky header", "bottom action region", "modal overlay"],
  "scroll_frames": ["Activity list"],
  "constraints": ["Header fixed width fill", "Activity list vertical scroll"],
  "non_goals": ["No Figma API call", "No renderer implementation"]
}
```

Why this passes:

- It supports reconstruction without writing to Figma or adding new semantics.
