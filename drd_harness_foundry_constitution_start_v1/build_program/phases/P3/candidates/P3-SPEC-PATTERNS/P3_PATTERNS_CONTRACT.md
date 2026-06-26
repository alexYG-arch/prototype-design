# P3-SPEC-PATTERNS Contract

## Workpack

- Workpack: `P3-SPEC-PATTERNS`
- Phase: `P3`
- Lane: `SPEC`
- Module: `shared_component_and_information_patterns`
- Upstream approved candidate: `P3-SPEC-ELEMENTS`

## Intent

`P3-SPEC-PATTERNS` defines reusable semantic component patterns and information presentation decisions for the approved element universe. It decides when multiple elements can share the same component or presentation treatment, and when equivalent information may intentionally use different presentation modes.

## Authority Boundary

This workpack consumes the canonical element projection from `P3-SPEC-ELEMENTS`. It may reference only canonical element ids, approved interaction messages, or resolved Human Gate decisions. It cannot create new elements, new pages, new user tasks, new capabilities, layout placements, carrier-specific adaptations, or z-axis rules.

Pattern reuse is semantic, not visual. Two surfaces may share a component or presentation pattern only when they share traceable semantic role, data structure, operation set, state model, information hierarchy, interaction model, and surface constraints. Visual similarity, color, icon choice, shadows, gradients, or rounded shape are never sufficient.

## In Scope

- Shared component registry for semantic component, presentation, interaction, and pre-layout grouping patterns.
- Information presentation registry for messages, actions, statuses, empty states, errors, help text, and decision-critical information.
- Presentation consistency exceptions where equivalent information intentionally uses different modes.
- Validation rules binding pattern reuse to canonical element ids and interaction message coverage.
- Handoff rules for `P3-SPEC-LAYOUT` so layout may reference patterns without inventing new elements.

## Out of Scope

- Screen layout, carrier adaptation, width behavior, containment hierarchy, ordering, vertical content growth, and z-axis layering.
- Final DRD compiler sectioning or rendering.
- Repository implementation code.
- `P3_SPEC_LOCK` or `P3_BUILD_LOCK` creation.

## Pattern Rules

A shared pattern is reusable only when its semantic role, required data, operations, states, information hierarchy, interactions, constraints, reuse scope, and trace refs are all present. If reuse is rejected, the non-reuse reason must explain the semantic difference, not a visual preference.

A presentation decision must state semantic intent, trigger condition, scope, lifecycle, presentation mode, recoverability, and trace refs. Sustained or decision-critical information cannot rely on transient-only presentation without a recoverable persistent surface. Every approved interaction message must have presentation coverage, and message refs must resolve to known messages.

Equivalent information must use the same presentation mode unless an approved `presentation_consistency_exception` names the consistency key, allowed modes, reason, and trace refs.

## Downstream Boundary

`P3-SPEC-LAYOUT` may consume pattern ids and presentation decisions, but it owns carrier-specific placement, containment hierarchy, responsive behavior, z-axis layering, and complete-on-height behavior. `P3-SPEC-PATTERNS` must leave those decisions as constraints rather than final layout instructions.
