# P3-SPEC-LAYOUT Contract

## Workpack

- Workpack: `P3-SPEC-LAYOUT`
- Phase: `P3`
- Lane: `SPEC`
- Module: `natural_language_layout`
- Upstream approved candidate: `P3-SPEC-PATTERNS`

## Intent

`P3-SPEC-LAYOUT` defines the natural-language layout authority and its validation skeleton for the approved element and pattern universe. It specifies carrier adaptation, containment hierarchy, state placement, content growth, information completeness, z-axis layering, and Figma reconstruction metadata without writing implementation code or final design files.

## Authority Model

Natural language layout prose is the canonical layout semantic authority. Structured layout inventories are index and validation skeletons only. They make coverage, reference integrity, and downstream reconstruction checkable, but they cannot override the prose, the approved element universe, approved interaction closure, or approved pattern registry.

## In Scope

- Natural-language layout text that covers carrier, spatial structure, hierarchy, containment, ordering, sizing, scrolling, states, content growth, layering, and constraints.
- Carrier adaptation profiles for `DESKTOP`, `TABLET`, `MOBILE`, `MOBILE_IOS`, and `MOBILE_MATERIAL`.
- Multi-level containment hierarchy with parent, child, order, arrangement, sizing, scroll, width, entry, and return placement context.
- Content growth rules for wrapping, overflow, scroll, truncation recovery, expansion, pagination, and empty behavior.
- Information completeness rules that preserve required information under height constraints and width constraints, including explicit horizontal scroll exceptions for truly wide structures.
- State placement index for every approved interaction message that must appear in layout.
- Z-axis layering with Material elevation intent, blocking behavior, background context, focus restoration, and layer ordering.
- Figma reconstruction metadata as non-authoritative handoff guidance with explicit non-goals.

## Out of Scope

- Creating new elements, messages, component patterns, product capabilities, pages, workflows, roles, permissions, integrations, or data scope.
- Final DRD compiler behavior.
- Figma API writes, renderer implementation, or file generation as canonical authority.
- Repository implementation code.
- `P3_SPEC_LOCK` or `P3_BUILD_LOCK` creation.

## Carrier Rules

Every eligible layout surface must declare a carrier profile that includes desktop, tablet, generic mobile, iOS mobile, and Material mobile. iOS mobile must include safe area, status or home indicator, navigation stack, and keyboard avoidance constraints. Material mobile must include app bar or system bar, edge inset, keyboard inset, Material elevation, dialog, snackbar, and bottom action expectations where relevant.

Carrier differences may change arrangement, navigation placement, and safe-area handling, but they must not remove required information. Mobile and tablet may stack content differently from desktop. Height limitations use vertical scroll, sticky or anchored access, expansion, or same-surface disclosure. Width limitations use wrap, stack, responsive density, or a declared horizontal scroll exception for wide structures.

## Containment Rules

The hierarchy must have exactly one root and at least two levels below it when the surface is not trivial. Child layout cannot contradict parent width or scroll constraints. Nested overlays, drawers, panels, and popovers must name entry context and return placement. Arrangement and order are coupled: if a parent orders children, each child must keep local order and explain how reflow preserves semantic sequence.

## Binding Rules

P3 layout requires non-empty pattern, state placement, z-axis, and Figma metadata bindings even when the generic schema marks those references as optional. Missing `pattern_refs`, `state_variants`, `z_axis_refs`, `figma_metadata_ref`, or composition `z_axis_refs` breaks the package because downstream layout, Figma reconstruction, and compiler conservation can no longer prove reference integrity.

## Completeness Rules

Screen height is not allowed to hide, omit, drop, or remove required information. Required information must remain reachable through vertical scroll, expansion, disclosure, detail view, pagination, or another explicit access path.

Width must be obeyed. Required information cannot simply clip or overflow offscreen. Horizontal scroll is allowed only as a declared exception for wide comparison tables, timelines, canvases, carousels, or other genuinely two-dimensional structures, and the exception must include visible affordance and access recovery.

## Layer Rules

Z-axis layering must be ordered from low to high. Interactive layers such as overlays, modals, drawers, popovers, and menus must declare whether they block lower layers. Material profiles require a material elevation intent. Every blocking layer must preserve or explicitly replace background context and must define focus restoration.

## Downstream Boundary

`P3-SPEC-COMPILER` may consume layout ids, section refs, state placements, pattern refs, and reconstruction metadata, but it cannot invent missing layout references or treat Figma metadata as canonical design output. Implementation work starts only after a P3 spec lock and implementation authorization.
