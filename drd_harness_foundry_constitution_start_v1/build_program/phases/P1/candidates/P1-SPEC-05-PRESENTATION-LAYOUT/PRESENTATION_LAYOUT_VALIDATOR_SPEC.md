# P1-SPEC-05 Presentation Layout Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `shared_component_registry_validator` | Ensures shared patterns are semantic, registered, and traceable. |
| `presentation_consistency_validator` | Ensures equivalent semantics use consistent presentation modes or justified exceptions. |
| `transient_information_validator` | Blocks sustained decision information from being transient-only. |
| `layout_completeness_validator` | Ensures natural-language layout covers required spatial and state dimensions. |
| `carrier_adaptation_validator` | Ensures desktop, tablet, mobile, iOS, and Material carrier profiles are declared when in scope. |
| `containment_coupling_validator` | Ensures multi-level containment, ordering, arrangement, sizing, and scroll behavior are internally consistent. |
| `content_growth_validator` | Ensures variable content behavior is declared. |
| `information_completeness_validator` | Ensures required information remains accessible under height changes and width constraints. |
| `z_axis_layering_validator` | Ensures overlapping and elevated surfaces declare layer order, occlusion, blocking, and focus restoration. |
| `state_placement_validator` | Ensures interaction messages and states have layout placement. |
| `nested_surface_layout_validator` | Ensures child pages, overlays, drawers, panels, and nested flows have containment and return placement. |
| `figma_compatibility_validator` | Ensures Figma reconstruction metadata is present and derived from layout prose. |
| `figma_boundary_validator` | Ensures no Figma API, renderer, or writer authority is introduced. |

## Checks

### PL-CHECK-001 Shared Pattern Registry Completeness

Fail if a shared pattern lacks semantic role, data structure, operation set, state model, information hierarchy, interaction model, surface constraints, reuse scope, or trace references.

### PL-CHECK-002 Visual-Only Shared Pattern

Fail if shared pattern justification is based only on visual similarity.

### PL-CHECK-003 Presentation Consistency

Fail if equivalent semantic intent, trigger condition, scope, and lifecycle use different presentation modes without a documented reason.

### PL-CHECK-004 Transient-Only Sustained Information

Fail if information needed for sustained user processing or decision-making is only represented by a short-lived unrecoverable message.

### PL-CHECK-005 Interaction Message Placement

Fail if async, failure, validation, disabled, handoff, cancel, exit, empty, permission, or recovery messages from interaction closure lack presentation mode or layout placement.

### PL-CHECK-006 Natural-Language Layout Completeness

Fail if layout prose does not cover carrier profile, spatial structure, hierarchy, multi-level containment, order, sizing, scrolling, state changes, overlays, z-axis layering, and surface constraints.

### PL-CHECK-007 Carrier Adaptation

Fail if a required desktop, tablet, mobile, iOS, Material, or declared carrier profile lacks adaptation rules for width, height/scrolling, navigation placement, safe-area or system-bar constraints, input and keyboard behavior, and platform-specific constraints.

### PL-CHECK-008 Multi-Level Containment Coupling

Fail if containment is flat when nested regions exist, if a child container lacks ordering or arrangement inside its parent, or if child scroll, width, order, or placement contradicts parent constraints.

### PL-CHECK-009 Content Growth

Fail if variable content lacks wrapping, overflow, scroll, collapse, truncation, expansion, pagination, or empty behavior as applicable.

Fail if truncation or collapse has no recovery path for required information.

### PL-CHECK-010 Height-Unbounded Information Completeness

Fail if required information becomes inaccessible because of screen height. Height limits must be handled by scrolling, expansion, pagination, progressive disclosure, or an equivalent declared access path.

Fail if width constraints are ignored rather than handled through wrapping, stacking, responsive arrangement, truncation with recovery, or declared horizontal behavior.

### PL-CHECK-011 State Variant Layout

Fail if required state variants lack layout differences or placement.

### PL-CHECK-012 Nested Surface Layout

Fail if child pages, second-level pages, third-level pages, overlays, drawers, panels, or nested task surfaces lack containment, entry, return, and scroll placement.

### PL-CHECK-013 Z-Axis And Material Elevation

Fail if overlays, drawers, modals, popovers, menus, sticky regions, fixed regions, toasts, snackbars, or loading layers lack z-axis or elevation ordering, occlusion rules, interaction blocking, and focus restoration.

Fail if a Material mobile profile uses layered surfaces without declaring Material-style elevation or z-axis intent.

### PL-CHECK-014 Figma Metadata Completeness

Fail if layout intended for Figma reconstruction lacks frame hierarchy, selection boxes, Auto Layout guidance, component instances, variants, constraints, or scroll frame guidance.

### PL-CHECK-015 Figma Boundary

Fail if the spec authorizes Figma API calls, renderer implementation, file writes, or treats Figma output as canonical authority.

### PL-CHECK-016 Metadata Semantics Drift

Fail if Figma metadata introduces layout, component, state, or product semantics absent from natural-language layout prose.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/presentation/shared_component_registry.schema.json`
- `repository/schemas/presentation/information_presentation_registry.schema.json`
- `repository/schemas/presentation/presentation_consistency_exception.schema.json`
- `repository/schemas/layout/natural_language_layout.schema.json`
- `repository/schemas/layout/carrier_adaptation_profile.schema.json`
- `repository/schemas/layout/containment_hierarchy.schema.json`
- `repository/schemas/layout/layout_composition_index.schema.json`
- `repository/schemas/layout/content_growth_rule.schema.json`
- `repository/schemas/layout/information_completeness_rule.schema.json`
- `repository/schemas/layout/z_axis_layering.schema.json`
- `repository/schemas/layout/state_placement_index.schema.json`
- `repository/schemas/layout/figma_reconstruction_metadata.schema.json`
