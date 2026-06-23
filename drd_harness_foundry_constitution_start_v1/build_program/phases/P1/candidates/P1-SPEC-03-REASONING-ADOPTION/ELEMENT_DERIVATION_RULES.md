# P1-SPEC-03 Element Derivation Rules

## Purpose

Element derivation fills necessary UX gaps without silently expanding the product.

## Allowed Derivation Sources

A missing element may be derived from:

- User task requirements.
- Required state transitions.
- Information needed for user decision-making.
- Feedback obligations.
- Recovery obligations.
- Navigation obligations.
- Exit obligations.
- Accessibility obligations.
- Approved upstream artifacts.
- Locked reasoning rules, including `RD-RULE-001`.

## Derivation Rules

### DERIVE-RULE-001 Explicit Elements First

Validated PRD-explicit elements have priority over derived elements.

### DERIVE-RULE-002 Necessary UX Only

A derived element must be necessary for task success, interaction closure, comprehension, feedback, recovery, navigation, exit, or accessibility.

### DERIVE-RULE-003 Input Path Obligation

If a task requires input `X`, the derivation must provide a user-operable or system-supported path for `X`, or route the missing path as a product expansion gap.

### DERIVE-RULE-004 No Capability Expansion

Derived elements must not introduce new product capabilities, policies, external integrations, roles, pricing logic, or data collection scope unless approved by Human Gate.

### DERIVE-RULE-005 Alternative Candidate Handling

When multiple valid presentations satisfy the same obligation, they must be represented as candidates, not silently selected, unless the choice is already constrained by approved upstream artifacts.

### DERIVE-RULE-006 Trace To Obligation

Every derived element must cite at least one obligation and one inference record.

### DERIVE-RULE-007 Dependent Derivation Blocking

If a derived element depends on a blocked PRD element decision or unresolved gap, it is blocked from canonical downstream use.

## Derivation Decision Fields

| Field | Requirement |
|---|---|
| `derived_element_id` | Stable ID for the derived element. |
| `derivation_source` | Task, state, information, feedback, recovery, navigation, exit, accessibility, upstream artifact, or rule. |
| `obligation_refs` | Rule or obligation references. |
| `inference_refs` | Reasoning records supporting the element. |
| `canonical_eligibility` | Eligibility state. |
| `blocked_by` | Required if eligibility is blocked. |

## Examples Of Allowed Derivation

- A required address input implies an address entry, selection, import, or acquisition path.
- A non-terminal edit state implies save, cancel, or exit behavior.
- A destructive action implies confirmation or recovery information when required by approved interaction rules.

## Examples Of Disallowed Derivation

- Adding account sharing because similar products often have it.
- Adding a payment integration because a checkout page usually needs one when the PRD does not authorize payment.
- Adding an analytics dashboard because the role would benefit from it but no approved obligation requires it.

