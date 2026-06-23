# P1-SPEC-03 Element Derivation Rules

## Purpose

Element derivation fills necessary UX gaps without silently expanding the product.

The term `element` is broad in this Candidate. It does not mean only a button, state, or input path. It covers any missing UX surface required to make an approved page or flow executable.

Examples include:

- Page sections and page regions.
- Child pages, second-level pages, third-level pages, detail pages, create pages, and edit pages.
- CTA and navigation targets.
- Inputs, selections, imports, upload paths, and acquisition paths.
- List/detail relationships, filters, sorting, tables, cards, and data views.
- Empty, loading, error, success, blocked, permission, and recovery states.
- Feedback messages, validation messages, help text, and decision-support information.
- Accessibility affordances and keyboard or focus obligations when required by the surface.

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

## Derivation Strategy

The primary strategy is deductive:

```text
explicit PRD fact
+ approved upstream artifact
+ task or stage obligation
+ platform or accessibility constraint
+ locked reasoning rule
-> required UX surface
```

The secondary strategy is inductive:

```text
under-specified page or flow
+ known pattern or comparable structure
-> candidate completion option
```

Inductive output is review material only. It must not become canonical unless a Human Gate approves it.

## Derivation Rules

### DERIVE-RULE-001 Explicit Elements First

Validated PRD-explicit elements have priority over derived elements.

### DERIVE-RULE-002 Necessary UX Surface Only

A derived UX surface must be necessary for task success, interaction closure, comprehension, feedback, recovery, navigation, exit, accessibility, or execution of a PRD-required page or flow.

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

### DERIVE-RULE-008 Missing Surface Sweep

For each PRD-required page or flow, the Harness must check whether the executable UX surface is complete across:

- Primary page purpose.
- Required user tasks.
- Required information and data surfaces.
- Required actions and reaction targets.
- Required inputs and input acquisition paths.
- Required child pages or nested task surfaces.
- Required lifecycle states.
- Required failure, recovery, exit, and navigation paths.

The check must not stop at buttons, states, or input paths.

### DERIVE-RULE-009 Deductive Primary, Inductive Auxiliary

The Harness must first attempt deductive completion from explicit PRD facts and locked obligations. Inductive reasoning may only propose candidate structures when the PRD-required page or flow is under-specified.

### DERIVE-RULE-010 Required Structural Completion Review

If a PRD names a page or flow but omits elements, sections, second-level pages, third-level pages, or child task surfaces required to make it executable, the Harness must not silently canonicalize those additions.

The Harness must either:

- Mark a single required surface as `DEDUCTIVE_NECESSITY` when no product choice remains.
- Or create a structural completion review record with non-canonical candidate options for Human Gate selection.

### DERIVE-RULE-011 Structural Completion Is Not Automatically Product Expansion

Adding a necessary page section or child surface to make an already approved page executable is a structural completion problem by default.

It becomes a product expansion gap when the completion requires a new capability, role, policy, integration, data scope, pricing rule, or product promise not authorized by PRD or Human Gate.

## Derivation Decision Fields

| Field | Requirement |
|---|---|
| `derived_element_id` | Stable ID for the derived element. |
| `derived_surface_type` | Page section, child page, detail page, edit page, create page, CTA, input, data view, state, message, navigation path, recovery path, accessibility affordance, or declared equivalent. |
| `derivation_source` | Task, state, information, feedback, recovery, navigation, exit, accessibility, upstream artifact, rule, or PRD-required page execution. |
| `obligation_refs` | Rule or obligation references. |
| `inference_refs` | Reasoning records supporting the element. |
| `derivation_strategy` | `DEDUCTIVE_PRIMARY` or `INDUCTIVE_AUXILIARY`. |
| `structural_completion_review` | Required when a necessary addition is under-specified and needs Human Gate selection. |
| `canonical_eligibility` | Eligibility state. |
| `blocked_by` | Required if eligibility is blocked. |

## Structural Completion Review Fields

| Field | Requirement |
|---|---|
| `review_id` | Stable ID for the review item. |
| `required_page_or_flow` | PRD-required page or flow that cannot execute without completion. |
| `missing_surface_summary` | Missing elements, sections, child pages, states, or data surfaces. |
| `deductive_obligations` | Obligations proving completion is required. |
| `candidate_options` | Candidate structures produced by bounded induction or explicit alternatives. |
| `product_expansion_risk` | Whether any option adds capability, integration, role, policy, or data scope. |
| `canonical_eligibility` | Must be `BLOCKED_PENDING_HUMAN` until Human Gate approval. |

## Examples Of Allowed Derivation

- A required address input implies an address entry, selection, import, or acquisition path.
- A non-terminal edit state implies save, cancel, or exit behavior.
- A destructive action implies confirmation or recovery information when required by approved interaction rules.
- A PRD-required "Project Detail" page with approved project fields implies a readable project information surface.
- A PRD-required "Manage Team" flow implies a visible member list or equivalent member selection surface when team membership is the object being managed.

## Examples Requiring Human Review

- The PRD says "Dashboard page" but does not define the dashboard sections, data cards, charts, or second-level drilldown pages. The Harness may propose candidate dashboard structures, but Human Gate must select or approve them.
- The PRD says "Admin settings page" but does not define which settings categories exist. Category pages or third-level detail pages must be reviewed unless each category is explicitly supported by source or prior approval.
- The PRD says "User can manage projects" but does not specify whether project creation, editing, archiving, members, and permissions are in scope. The Harness must split necessary structural completion from product expansion gaps.

## Examples Of Disallowed Derivation

- Adding account sharing because similar products often have it.
- Adding a payment integration because a checkout page usually needs one when the PRD does not authorize payment.
- Adding an analytics dashboard because the role would benefit from it but no approved obligation requires it.
- Adding a third-level automation builder under a settings page when the PRD only authorized viewing settings and no approved obligation requires automation.
