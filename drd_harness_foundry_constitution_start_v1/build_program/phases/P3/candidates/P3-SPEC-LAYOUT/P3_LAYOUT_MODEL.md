# P3 Layout Model

## P3 Required Bindings

Some generic schema fields are optional because not every layout package has patterns, state variants, z-axis layers, or Figma handoff metadata. In P3 they are mandatory: `pattern_refs`, `state_variants`, `z_axis_refs`, and `figma_metadata_ref` must be present and non-empty where their type allows it. The composition index must also include `z_axis_refs`.

## Layout Package

A complete layout package contains nine schema-bound artifacts:

1. `natural_language_layout`: canonical layout prose and top-level references.
2. `carrier_adaptation_profile`: desktop, tablet, mobile, iOS, and Material carrier constraints.
3. `containment_hierarchy`: multi-level surface tree with ordering and parent-child constraints.
4. `content_growth_rules`: growth, wrapping, overflow, scroll, truncation recovery, expansion, pagination, and empty behavior.
5. `information_completeness_rules`: required information access under height and width constraints.
6. `state_placement_index`: layout placement for approved messages and state variants.
7. `z_axis_layering`: ordered layers, Material elevation, blocking behavior, and focus restoration.
8. `layout_composition_index`: reference index tying the package together.
9. `figma_reconstruction_metadata`: non-authoritative reconstruction guidance and non-goals.

## Natural Language Coverage

The layout prose must explicitly cover carrier, spatial structure, hierarchy, containment, ordering, sizing, scrolling, states, growth, layering, and platform constraints. It must say that natural language is canonical semantic authority and structured records are index and validation skeleton only.

## Carrier Adaptation

`DESKTOP` may use wider composition and denser scan paths. `TABLET` may reflow into fewer columns. `MOBILE` establishes the generic mobile stack. `MOBILE_IOS` adds iOS safe area, navigation stack, home indicator, status bar, and keyboard behavior. `MOBILE_MATERIAL` adds Material system bars, app bar, keyboard inset, elevation, dialog, snackbar, and bottom action conventions.

Carrier changes must preserve semantic sequence and information access. They may change arrangement but cannot remove required fields, actions, messages, recovery paths, or state explanations.

## Containment And Ordering

Containment is multi-level. A page contains sections, sections contain groups, groups contain repeated items or state containers, and overlays or drawers have entry and return placement. Each node declares order, arrangement, sizing, scroll behavior, and width behavior. Order and arrangement are coupled because reflow must preserve meaning even when desktop rows become mobile stacks.

## Information Completeness

Height is never a reason to drop content. Short height must use vertical scroll, sticky access, expansion, disclosure, detail, or pagination. Width must be handled by wrap, stack, density changes, or a declared horizontal scroll exception. Horizontal scroll is an exception, not the default, and only applies to wide structures that cannot be meaningfully wrapped without losing comparison or sequence.

## State And Layer Placement

Every approved interaction message that needs layout must appear in `state_placement_index`. Each placement names message id, state type, presentation mode, surface id, and trace refs. Layering uses ordered z-axis records. Material elevation intent is required when Material mobile is a supported carrier.

## Figma Metadata Boundary

Figma reconstruction metadata is a handoff aid. It can describe frame hierarchy, selection hierarchy, auto-layout guidance, carrier variants, scroll frames, constraints, and non-goals. It cannot call Figma APIs, write files, render final design, or become canonical semantic authority.
