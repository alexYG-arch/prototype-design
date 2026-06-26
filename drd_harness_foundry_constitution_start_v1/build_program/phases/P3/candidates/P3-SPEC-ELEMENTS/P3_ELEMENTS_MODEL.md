# P3 Element Model

## Canonical Element Set

The canonical element set is a deterministic projection, not an informal judgment. It includes only:

- explicit inventory rows whose `p3.elements.prd_element_decisions.outcome` is `ADOPT_AS_IS` or `ADOPT_NORMALIZED`,
- derived rows whose `canonical_eligibility` is `ELIGIBLE`, whose `derivation_strategy` is `DEDUCTIVE_PRIMARY`, and whose `blocked_by` list is empty,
- Human Gate approved expansion rows only when the matching product expansion gap is `RESOLVED_APPROVED` and has a non-null `decision_ref`.

It excludes `REQUEST_CLARIFICATION`, `REJECT_CONFLICT`, `ROUTE_PRODUCT_GAP`, open gaps, rejected gaps, superseded gaps, structural completion review rows, blocked derived rows, and inductive auxiliary candidates without Human Gate approval. Everything excluded is non-canonical and must be blocked from downstream pattern, layout, and compiler consumption.

## Atomic Inventory Grain

Each inventory row describes exactly one semantic element. A row cannot combine a page with its fields, a form with its submit button, a state with its failure copy, or an overlay with all of its recovery controls. Parent-child relationships are downstream references, not row bundling.

The atomic unit must have:

- one stable `element_id`,
- one schema `element_type`,
- source refs or upstream closure refs,
- a source text hash when the row is source explicit,
- an adoption or derivation decision that explains eligibility.

## Element Type Mapping

Closure and source objects map to existing schema types as follows:

| Source or closure object | Element type |
| --- | --- |
| real page, child page, page-like required surface | `PAGE` |
| state node, terminal state, processing state, failure state | `STATE` |
| command button, primary action, recovery action | `CTA` |
| field, selector, editable value, upload, typed input | `INPUT` |
| link, tab, menu entry, route change | `NAVIGATION` |
| user-visible copy for async, failure, disabled, terminal, validation, or empty states | `MESSAGE` |
| role named by source or approved decision | `ROLE` |
| permission named by source or approved decision | `PERMISSION` |
| overlay, container affordance, visual-only affordance, or surface that lacks a narrower schema type | `UI_ELEMENT` |

A future implementation may add richer internal labels, but it must preserve the schema element type and the source-bound row identity.

## Deductive Completion Strategy

Deduction starts from obligations already approved by source, distillation, and interaction closure. Examples include:

- a failure-prone reaction requires a same-task failure message and recovery element,
- an async reaction requires visible progress, duplicate-trigger behavior, and timeout messaging,
- a disabled affordance requires a disabled state or disabled message,
- an overlay requires close, cancel, return, or terminal closure behavior,
- a required input path requires an input obligation if acquisition is not already explicit.

These completions are not product additions when they only make an approved interaction usable. They must still be recorded with `DEDUCTIVE_PRIMARY` and inference evidence.

## Human Review Strategy

Structural completion review is mandatory when a missing surface cannot be deduced from the approved task. A page name alone does not authorize child pages, dashboards, settings pages, role management, integrations, analytics, exports, payments, or workflow branching. Those candidates become product expansion gaps until Human Gate approves or rejects them.

## Conservation Rule

Downstream artifacts must conserve this element universe. If a downstream workpack references an element, it must match a canonical element id or cite a resolved Human Gate decision. If it omits a canonical element, it must explain the omission with a blocked status, superseded decision, or explicit non-rendered reason.
