# P1-SPEC-04 Clickable Inventory Rules

## Purpose

The clickable inventory is the coverage universe for `RD-RULE-004`. If a user can click, tap, press, choose, open, close, submit, retry, cancel, or navigate through an element, the inventory must include it.

## Inventory Sources

Clickable elements may come from:

- PRD-explicit element adoption decisions.
- Derived element decisions.
- Structural completion review approvals.
- Human Gate decisions.
- Approved upstream page, state, and interaction obligations.

## Required Fields

| Field | Requirement |
|---|---|
| `clickable_id` | Stable ID for the clickable element. |
| `source_node_id` | Node where the clickable appears. |
| `label_or_affordance` | Human-visible label or affordance description. |
| `clickable_type` | Button, link, tab, menu item, card, row, icon button, checkbox, radio, toggle, close control, retry control, or declared equivalent. |
| `source_refs` | PRD, upstream artifact, inference, adoption, derivation, or Human Gate references. |
| `enabled_conditions` | Conditions under which the element is active. |
| `disabled_behavior` | Required when the element may be disabled. |
| `reaction_id` | Reaction record that handles the click. |

## Rules

### CLICK-RULE-001 Inventory Before Closure

The Harness must build the clickable inventory before validating interaction closure.

### CLICK-RULE-002 One Current Reaction

Each current clickable must bind to exactly one current Reaction. Conditional variants may have separate guarded Reactions only if each guard is explicit and non-overlapping.

### CLICK-RULE-003 Disabled Is Still Specified

If a clickable element can be disabled, the disabled condition must be explicit and the user-visible explanation or alternative path must be specified when needed.

### CLICK-RULE-004 Hidden Or Conditional Clickables

Hidden, permission-gated, role-gated, and conditionally rendered clickables must still appear in the inventory with their visibility conditions.

### CLICK-RULE-005 Reused Components

Reusable components may share a Reaction template, but each instance must bind source node, target, conditions, and failure behavior in its actual context.

### CLICK-RULE-006 Non-Interactive Elements

Visual elements that are not interactive must not be placed in the clickable inventory. If they look clickable, the spec must either make them non-clickable explicitly or provide a Reaction.

### CLICK-RULE-007 Overlay Controls

Overlay close, cancel, confirm, escape-key, and outside-click behaviors must be inventoried when they affect interaction closure.

## Inventory Coverage Join

Validators must join:

- Interaction graph nodes.
- Clickable inventory.
- Reaction records.
- Adoption and derivation records from upstream reasoning artifacts.

The join is required so closure coverage does not depend on manual reading alone.

