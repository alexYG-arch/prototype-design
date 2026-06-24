# P1-SPEC-05 Figma Compatibility Contract

## Purpose

The Harness must produce layout descriptions that a designer or Agent can reconstruct in Figma, but the Harness must not implement Figma API, renderer, or writer behavior.

It owns `DRD-CHARTER-009`.

## Compatibility Metadata

Figma reconstruction metadata must include:

- Frame or surface purpose.
- Layer hierarchy.
- Selection box boundaries.
- Auto Layout direction, grouping, and spacing intent.
- Component instance references.
- Variant dimensions and state variants.
- Text hierarchy.
- Responsive constraints.
- Carrier-specific frame variants for desktop, tablet, mobile, iOS, and Material when in scope.
- Z-axis or elevation layering records for overlapping surfaces.
- Overlay positioning.
- Scroll frame behavior.
- Interaction-state surfaces that must be represented.

## Contract Clauses

### FIGMA-CONTRACT-001 Compatibility Only

The Harness defines reconstruction guidance and metadata only. It must not write to Figma, call Figma APIs, generate renderer code, or treat Figma output as canonical authority.

### FIGMA-CONTRACT-002 Layout Prose Comes First

Figma metadata must derive from natural-language layout authority and must not introduce new layout meaning.

### FIGMA-CONTRACT-003 Auto Layout Guidance

When a surface has repeated items, grouped controls, rows, columns, cards, or responsive sections, the metadata must describe Auto Layout grouping and resize intent.

### FIGMA-CONTRACT-004 Variant Guidance

State variants, component variants, and responsive variants must be named and linked to the layout states they represent.

### FIGMA-CONTRACT-005 Reconstruction Completeness

A designer or Agent must be able to identify frame hierarchy, containment, ordering, component instances, and state variants without guessing product semantics.

### FIGMA-CONTRACT-006 Carrier Variants

Figma metadata must identify required carrier variants and their frame, constraint, Auto Layout, scroll, safe-area, and platform-specific differences.

### FIGMA-CONTRACT-007 Layer Reconstruction

Figma metadata must preserve z-axis or elevation intent for overlays, drawers, modals, popovers, menus, sticky regions, fixed regions, toasts, snackbars, and loading layers.

## Figma Metadata Fields

| Field | Requirement |
|---|---|
| `figma_metadata_id` | Stable ID. |
| `layout_id` | Source layout ID. |
| `frame_hierarchy` | Frame and nested frame plan. |
| `selection_box_hierarchy` | Selectable grouping plan. |
| `auto_layout_guidance` | Direction, spacing, alignment, wrapping, and resize intent. |
| `component_instances` | Shared component references and variants. |
| `state_variants` | Empty, loading, error, success, disabled, permission, overlay, and responsive variants when applicable. |
| `carrier_variants` | Desktop, tablet, mobile, iOS, Material, and other required carrier frames. |
| `z_axis_layers` | Layer and elevation plan for overlapping or floating surfaces. |
| `scroll_frames` | Scroll containers and sticky/fixed regions. |
| `constraints` | Resize, pinning, fill, hug, fixed, min, max, or equivalent constraints. |
| `non_goals` | Renderer, API, and implementation actions excluded from Harness authority. |
