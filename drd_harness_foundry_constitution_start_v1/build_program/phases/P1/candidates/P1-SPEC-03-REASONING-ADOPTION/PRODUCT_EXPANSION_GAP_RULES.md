# P1-SPEC-03 Product Expansion Gap Rules

## Purpose

Product expansion gaps preserve the boundary between deduction and product decision-making.

Not every required completion is product expansion. If the PRD already requires a page or flow and the missing work is choosing the UX structure needed to make that page executable, the item is a structural completion review. It becomes a product expansion gap only when completing it requires a new capability, integration, role, policy, data scope, pricing rule, workflow promise, or product commitment.

## Gap Types

| Gap Type | Meaning |
|---|---|
| `MISSING_PRODUCT_DECISION` | A required product choice is not present in source or approved decisions. |
| `MISSING_INPUT_PATH` | Task success depends on input with no approved acquisition, entry, selection, or import path. |
| `UNAPPROVED_CAPABILITY` | A candidate requires a new capability or workflow. |
| `UNAPPROVED_INTEGRATION` | A candidate requires an external system or handoff not approved by source. |
| `UNAPPROVED_DATA_SCOPE` | A candidate requires collecting, exposing, or retaining data beyond approved scope. |
| `CONFLICTING_SOURCE` | Source statements conflict and require product judgment. |
| `STRUCTURAL_COMPLETION_ESCALATED` | A required structural completion option crosses into new product capability, data scope, integration, role, policy, or product promise. |

## Rules

### GAP-RULE-001 Route Before Canonical Use

Any unresolved product expansion gap blocks canonical downstream use of the dependent element, state, page, or workflow.

### GAP-RULE-002 Candidate Framing

Gap records may include candidate options, but each option must remain non-canonical until Human Gate approval.

### GAP-RULE-003 Decision Binding

Resolved gaps must cite the approving Human Gate decision before dependent artifacts can consume them.

### GAP-RULE-004 No Layout Escape

A product expansion gap cannot be resolved by hiding it in layout wording, component choice, or presentation pattern.

### GAP-RULE-005 No Compilation Escape

Deterministic compilation must reject approved-section inputs that contain unresolved product expansion gaps.

### GAP-RULE-006 Split Structural Completion From Product Expansion

Validators must distinguish:

- Required UX structure for an already approved page or flow.
- New product scope required by one or more structural options.

The first requires structural completion review. The second requires product expansion gap routing.

## Gap Record Fields

| Field | Requirement |
|---|---|
| `gap_id` | Stable unique ID. |
| `gap_type` | One declared gap type. |
| `source_refs` | Source or upstream references that exposed the gap. |
| `blocked_artifacts` | Artifacts blocked by the gap. |
| `candidate_options` | Optional non-canonical options for Human Gate. |
| `required_decision` | Human decision required to resolve the gap. |
| `status` | `OPEN`, `RESOLVED_APPROVED`, `RESOLVED_REJECTED`, or `SUPERSEDED`. |
| `decision_ref` | Required when resolved. |

## Human Gate Outcomes

Human Gate may:

- Approve one candidate option.
- Reject all options.
- Provide a new product requirement.
- Defer the decision and keep dependents blocked.

Codex may not substitute its own decision for any of these outcomes.
