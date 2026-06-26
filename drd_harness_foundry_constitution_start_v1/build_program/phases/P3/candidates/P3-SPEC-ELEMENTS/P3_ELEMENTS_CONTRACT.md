# P3-SPEC-ELEMENTS Contract

## Workpack

- Workpack: `P3-SPEC-ELEMENTS`
- Phase: `P3`
- Lane: `SPEC`
- Module: `page_element_model`
- Upstream approved candidate: `P3-SPEC-CLOSURE`

## Intent

`P3-SPEC-ELEMENTS` defines the page element model that turns approved source semantics and the approved interaction closure into a verifiable element universe. It answers what page, state, input, command, navigation, message, role, permission, and other UI elements exist, why each one is allowed, and which missing surfaces must be routed to Human Gate review.

## Authority Model

Natural language remains the primary semantic authority. Inventory rows are not the product definition; they are an index and verification skeleton. A row may make coverage measurable, but it cannot override source text, approved closure behavior, or a Human Gate decision.

The element model uses two rails:

1. Natural language rail: source and distillation statements retain human-readable intent, constraints, and task meaning.
2. Inventory rail: atomic element rows, adoption decisions, inference records, and gap records make coverage and downstream conservation checkable.

If the two rails conflict, the natural language rail and approved review decisions win. The inventory rail must be corrected or blocked.

## In Scope

- PRD explicit element inventory derived from source, distillation, and approved interaction closure.
- Adoption decisions for every explicit element row.
- Deductive element completion for required same-task surfaces such as failure messages, recovery actions, disabled states, terminal messages, empty states, overlay close or return controls, and async progress messages.
- Input obligations where an element needs a known input acquisition path or a product gap route.
- Structural completion review when a page or flow is stated but lower-level surfaces are absent.
- Product expansion gaps when completing a missing surface would add product capability, a second or third level page, a new workflow, new integration, new data scope, new role, new permission, or a new product promise.
- Inference records that justify all canonical derived elements and all blocked candidates.

## Out of Scope

- Shared component registry and reusable component pattern selection.
- Natural language layout, carrier adaptation, containment hierarchy, width behavior, vertical content growth, or z-axis layering.
- Final DRD compiler behavior.
- Repository implementation code.
- `P3_SPEC_LOCK` or `P3_BUILD_LOCK` creation.

## Completion Rules

Explicit source and approved closure elements enter the inventory first. Missing elements are then considered by deductive strategy before any inductive strategy is used.

A missing element may become canonical only when all of the following are true:

- It is necessary to complete the already-approved task, state, interaction, failure path, async path, handoff, or message obligation.
- It does not add a new product capability, data scope, integration, workflow, user role, permission rule, page family, or business promise.
- It cites source, upstream closure artifacts, or a Human Gate decision through inference records.
- It is represented as an atomic inventory or derived-decision row.

A missing element must go to Human Gate review when any of the following is true:

- The source says only that a page or flow exists, while child elements or second and third level pages are absent and cannot be deduced without product choice.
- The candidate element would create a new product capability or new surface outside the approved task.
- The only basis is convention, pattern memory, or designer preference.
- The required input path is absent and cannot be acquired inside the same approved task.

Induction is allowed only as auxiliary review material. It cannot make a canonical element by itself.

## Downstream Boundary

`P3-SPEC-ELEMENTS` hands an approved and blocked element universe to `P3-SPEC-PATTERNS` and `P3-SPEC-LAYOUT`. Those later workpacks may decide component reuse and placement rules, but they must not invent elements that are absent from the element universe or an approved gap decision.
