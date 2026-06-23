# P1-SPEC-03 PRD Element Adoption Rules

## Scope

These rules apply to PRD-explicit pages, states, CTA, forms, data inputs, navigation items, messages, permissions, roles, and UI elements.

## Source Element Inventory

Before adoption decisions are validated, the Harness must produce a PRD explicit element inventory. This inventory is the mechanical coverage target for adoption completeness.

Inventory fields:

| Field | Requirement |
|---|---|
| `element_id` | Stable ID for a PRD-explicit page, state, CTA, input, navigation item, message, role, permission, or UI element. |
| `element_type` | Declared element type. |
| `source_refs` | Source PRD references proving the element is explicit. |
| `source_text_hash` | Hash of the cited source text slice or source extraction record. |
| `stage_id` | Stage that extracted the element. |
| `artifact_id` | Artifact that stores the inventory. |

## Adoption Outcomes

| Outcome | Meaning | Downstream Use |
|---|---|---|
| `ADOPT_AS_IS` | The PRD element is consistent, executable, and already precise. | Can feed downstream artifacts. |
| `ADOPT_NORMALIZED` | The PRD element is valid but needs naming, grouping, or wording normalization without semantic change. | Can feed downstream artifacts with normalization record. |
| `REQUEST_CLARIFICATION` | The element is relevant but lacks information required for execution. | Blocks downstream use until answered. |
| `REJECT_CONFLICT` | The element conflicts with source, approved upstream artifacts, platform constraints, or locked rules. | Must not feed downstream artifacts. |
| `ROUTE_PRODUCT_GAP` | The element implies product expansion outside approved authority. | Human Gate required. |

## Validation Dimensions

Each explicit PRD element must be checked for:

- Source citation.
- Semantic consistency with the Source PRD and approved upstream artifacts.
- Executability as a user-visible page, state, CTA, input, or message.
- Required data and input paths.
- Interaction implications.
- Failure, recovery, or exit implications when applicable.
- Product expansion risk.

## Rules

### ADOPT-RULE-001 Validate Before Use

No explicit PRD element may appear in canonical downstream artifacts until it has an adoption decision.

### ADOPT-RULE-002 Normalize Without Semantic Addition

Normalization may rename, group, deduplicate, or clarify an element. It must not add capability, data scope, workflow, role, or promise.

### ADOPT-RULE-003 Clarification Blocks Canonical Use

`REQUEST_CLARIFICATION` blocks canonical use of the unresolved element and any dependent derived element.

### ADOPT-RULE-004 Conflicts Are Explicit

`REJECT_CONFLICT` must cite the conflicting source, upstream artifact, platform constraint, or locked rule.

### ADOPT-RULE-005 Product Expansion Cannot Hide In Adoption

If adoption requires a new product capability or commitment, the outcome must be `ROUTE_PRODUCT_GAP`.

### ADOPT-RULE-006 Input Obligation Check

If adopting the element creates dependency on input `X`, the decision must point to an actionable input path or a product expansion gap.

### ADOPT-RULE-007 Decision Index Required

Every adoption decision must be recorded in a structured decision index so downstream validators can enforce completeness.

### ADOPT-RULE-008 Inventory Coverage Required

Every element in the PRD explicit element inventory must have exactly one current adoption decision. Decisions for non-inventory elements must be treated as derived elements or product gaps, not source-explicit adoption.

## Decision Index Fields

| Field | Requirement |
|---|---|
| `element_id` | Stable source element ID. |
| `source_refs` | PRD source references. |
| `element_type` | Page, state, CTA, input, navigation, message, role, permission, or other declared type. |
| `outcome` | One adoption outcome. |
| `normalized_label` | Required for `ADOPT_NORMALIZED`. |
| `blocking_reason` | Required for clarification, conflict, or gap routing. |
| `input_obligations` | Required when the element depends on user or system input. |
| `inference_refs` | Reasoning records supporting the decision. |

## Coverage Join

The adoption validator must join:

- PRD explicit element inventory by `element_id`.
- PRD element adoption decision index by `element_id`.
- Derived element decision index by `derived_element_id`.

This join prevents source-explicit adoption coverage from depending on manual document reading alone.
