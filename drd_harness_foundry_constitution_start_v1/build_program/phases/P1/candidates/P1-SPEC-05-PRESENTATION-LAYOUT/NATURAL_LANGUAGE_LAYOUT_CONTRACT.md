# P1-SPEC-05 Natural-Language Layout Contract

## Purpose

The authoritative layout semantic must be written in complete natural language.

It owns:

- `DRD-CHARTER-008`
- `RD-RULE-007`

## Required Layout Coverage

Each layout specification must describe:

- Page or surface purpose.
- Carrier profile: desktop, tablet, mobile, or another declared surface class.
- Platform profile when relevant, including iOS and Material mobile constraints.
- Spatial structure.
- Visual and semantic hierarchy.
- Multi-level parent-child containment.
- Section ordering and how ordering changes within each containment level.
- Component and pattern placement.
- Sizing and relative density.
- Alignment and grouping.
- Scroll areas.
- Sticky or fixed regions.
- Responsive behavior when surface size changes.
- Overlay, modal, drawer, popover, and nested surface behavior.
- State changes and conditional content.
- Empty, loading, error, disabled, permission, success, and recovery states when relevant.
- Content growth behavior.
- Width-bound content completeness and height-unbounded scroll behavior.
- Z-axis or elevation layering for overlays, sticky regions, panels, and Material-like surfaces.
- Surface constraints and Figma reconstruction notes.

## Carrier And Platform Coverage

Each layout must define adaptation behavior for every required carrier:

| Carrier | Required Coverage |
|---|---|
| `DESKTOP` | Wide layout, dense information placement, multi-column behavior, hover availability, keyboard/focus behavior, fixed or sticky regions, and horizontal width constraints. |
| `TABLET` | Intermediate layout, split-view or stacked behavior, touch interaction density, orientation changes, and panel/drawer behavior. |
| `MOBILE` | Narrow layout, single-column or constrained multi-surface behavior, safe areas, system bars, keyboard insets, touch reach, vertical scrolling, and navigation placement. |
| `MOBILE_IOS` | iOS-specific carrier profile including safe-area handling, navigation stack or modal/sheet behavior, platform gesture conflicts, keyboard avoidance, and native control constraints approved by the project. |
| `MOBILE_MATERIAL` | Material-specific carrier profile including app bar, navigation, sheet/dialog, elevation, touch target, keyboard inset, and component behavior constraints approved by the project. |

Carrier profiles must state which carriers are required for the product surface. If a carrier is not supported, the layout must explicitly say so and explain the product or platform reason.

## Multi-Level Containment Coverage

Containment must be multi-level, not a flat list. The layout must describe:

- Page or route container.
- Primary regions.
- Sections inside each region.
- Component groups inside each section.
- Repeated item structure inside lists, tables, cards, or grids.
- Nested child pages, overlays, drawers, panels, and popovers.
- State-specific containers for empty, loading, error, permission, disabled, success, recovery, and validation states.

Each containment level must define its local ordering, direction, grouping, sizing, scroll relationship, and how it changes across carriers.

## Content Growth Coverage

When content length or quantity varies, the layout must explain:

- Wrapping.
- Overflow.
- Scrolling.
- Collapsing.
- Truncation.
- Expansion.
- Pagination or lazy loading when relevant.
- Empty collection behavior.
- Maximum and minimum useful density.

The layout must preserve information completeness. Screen height may change how the user scrolls or expands content, but it must not silently remove required information. Screen width is a constraint that may force wrapping, stacking, truncation with recovery, disclosure, or horizontal alternatives; each such behavior must be explicit.

## Z-Axis And Layering Coverage

Layout prose must describe z-axis or elevation behavior when surfaces overlap or float.

Required coverage:

- Overlay, modal, drawer, popover, menu, tooltip, sticky header, fixed footer, snackbar, toast, and loading layer ordering.
- Which layer blocks interaction with lower layers.
- Which layer preserves background context.
- Focus restoration after the top layer closes.
- Material elevation or z-axis intent when using a Material mobile profile.
- iOS modal, sheet, navigation stack, or overlay layering when using an iOS mobile profile.

## Contract Clauses

### LAYOUT-CONTRACT-001 Natural Language Is Authority

Canonical layout meaning must be expressed in Markdown prose. JSON may index and validate layout obligations, but must not replace the human-readable layout description.

### LAYOUT-CONTRACT-002 Complete Spatial Description

Layout prose must describe carrier profile, hierarchy, multi-level containment, order, size, scroll, state changes, z-axis layering, and surface constraints enough for a reviewer to reconstruct the screen.

### LAYOUT-CONTRACT-003 Content Growth Is Explicit

Variable content must not be left to renderer defaults. Growth, overflow, wrapping, truncation, and scrolling behavior must be specified.

The spec must preserve required information completeness across height changes. Height constraints may require scrolling, progressive disclosure, or section expansion, but not silent information loss.

### LAYOUT-CONTRACT-004 Interaction State Placement

Async, failure, validation, disabled, handoff, exit, empty, permission, and recovery messages from interaction specs must have placement in the layout.

### LAYOUT-CONTRACT-005 Shared Pattern Placement

Layouts must reference shared component and presentation registries when a registered pattern is used.

### LAYOUT-CONTRACT-006 No Renderer Dependence

The layout spec may guide implementation or Figma reconstruction, but cannot rely on a live renderer, Figma API, or generated screenshot as the semantic source.

### LAYOUT-CONTRACT-007 Carrier Adaptation Required

Desktop, tablet, mobile, iOS, and Material profiles must be specified when they are in product scope. Each required carrier must state layout adaptation, navigation placement, input/keyboard handling, safe-area or system-bar constraints, and scroll behavior.

### LAYOUT-CONTRACT-008 Multi-Level Containment Coupling

Containment, ordering, arrangement, sizing, and scrolling must be described together at each hierarchy level. A child section cannot define order or scroll behavior that contradicts its parent container.

### LAYOUT-CONTRACT-009 Z-Axis Layering Required

Overlapping, floating, sticky, fixed, modal, drawer, popover, menu, toast, snackbar, and loading surfaces must declare layer order, occlusion behavior, interaction blocking, and return/focus behavior.

### LAYOUT-CONTRACT-010 Width-Bound Height-Unbounded Completeness

Layout must obey width constraints and adapt by wrapping, stacking, truncating with recovery, or changing arrangement. It must not use screen height as a reason to omit required information; height overflow must be handled by scroll, expansion, pagination, or other declared access path.

## Layout Index Fields

| Field | Requirement |
|---|---|
| `layout_id` | Stable ID. |
| `surface_id` | Page, state, overlay, or child surface ID. |
| `layout_body_ref` | Markdown section containing authoritative prose. |
| `carrier_profiles` | Required desktop, tablet, mobile, iOS, Material, or other carrier adaptation profiles. |
| `section_index` | Ordered multi-level sections and containment relationships. |
| `containment_tree_ref` | Multi-level containment tree with parent-child ordering and scroll coupling. |
| `pattern_refs` | Shared components and presentation patterns used. |
| `state_variants` | State-specific layout differences. |
| `content_growth_refs` | Growth behavior records. |
| `z_axis_refs` | Layering, elevation, occlusion, and focus restoration records. |
| `information_completeness_refs` | Records proving required information remains accessible under height changes and width constraints. |
| `figma_metadata_ref` | Figma reconstruction metadata when required. |
| `trace_refs` | Source, reasoning, interaction, presentation, or Human Gate references. |
