# P1-SPEC-05 Presentation Layout Rules

## Shared Component Rules

### PL-RULE-001 Compare Semantics Before Reuse

Shared pattern decisions must compare semantic role, data structure, operation set, state model, information hierarchy, interaction model, access constraints, and surface constraints.

### PL-RULE-002 No Visual-Only Merge

Do not merge surfaces into a shared component only because they look similar.

### PL-RULE-003 Difference Requires Trace

Equivalent semantic cases using different presentation or component patterns require a traceable reason.

## Information Presentation Rules

### PL-RULE-004 Presentation Consistency Key

The same semantic intent, trigger condition, scope, and lifecycle must map to one presentation mode unless a documented exception exists.

### PL-RULE-005 No Transient-Only Critical Information

Information required for sustained user processing or decision-making cannot appear only in a short-lived, unrecoverable message.

### PL-RULE-006 Interaction Copy Placement

Messages required by interaction closure must have presentation mode and layout placement.

## Natural-Language Layout Rules

### PL-RULE-007 Layout Prose Completeness

Layout prose must describe spatial structure, hierarchy, containment, ordering, sizing, scrolling, state changes, overlays, and surface constraints.

### PL-RULE-008 Carrier Adaptation

Layouts must declare required carrier profiles and adaptation behavior for desktop, tablet, mobile, iOS, and Material when those carriers are in scope.

Each required carrier must define width behavior, height/scroll behavior, safe-area or system-bar constraints, keyboard/input handling, navigation placement, and platform-specific constraints.

### PL-RULE-009 Multi-Level Containment Coupling

Containment must be represented as a multi-level tree. Ordering, arrangement, sizing, and scroll behavior must be defined within each parent-child level and must not contradict parent constraints.

### PL-RULE-010 Content Growth Behavior

Variable content must define wrapping, overflow, scroll, collapse, truncation with recovery, expansion, pagination, or empty behavior as applicable.

Required information must remain accessible when screen height is insufficient. Layout may use vertical scroll, expansion, pagination, or progressive disclosure, but must not silently omit required content.

### PL-RULE-011 State Variant Layout

Empty, loading, error, disabled, permission, success, validation, handoff, and recovery states must state what changes in the layout.

### PL-RULE-012 Nested Surface Layout

Second-level pages, third-level pages, overlays, drawers, panels, and nested task surfaces must state entry context, containment, return path placement, and scroll behavior.

### PL-RULE-013 Z-Axis And Elevation

Overlays, drawers, modals, popovers, menus, sticky regions, fixed regions, toasts, snackbars, and loading layers must declare z-axis or elevation ordering, occlusion, interaction blocking, and focus restoration.

Material mobile layouts must declare Material-style elevation or z-axis intent for layered surfaces.

## Figma Compatibility Rules

### PL-RULE-014 Figma Metadata Required

Layouts intended for reconstruction must provide frame hierarchy, selection box hierarchy, Auto Layout guidance, component instances, variants, constraints, and scroll frame guidance.

### PL-RULE-015 No Figma Write Authority

Figma compatibility metadata cannot authorize API calls, renderer implementation, or direct design file writes.

### PL-RULE-016 Metadata Does Not Add Semantics

Figma metadata must not introduce layout, component, or product semantics absent from the natural-language layout authority.
