# P1-SPEC-05 Information Presentation Contract

## Purpose

This contract defines how information must be presented consistently and recoverably.

It owns:

- `DRD-CHARTER-006`
- `RD-RULE-008`

## Presentation Keys

Information presentation decisions must be keyed by:

- Semantic intent.
- Trigger condition.
- Scope.
- Information lifecycle.
- User decision need.
- Recoverability need.
- Persistence requirement.

## Presentation Modes

| Mode | Use |
|---|---|
| `INLINE_MESSAGE` | Local field, row, card, or section-level information. |
| `BANNER` | Page-level or flow-level information that must remain visible. |
| `TOAST` | Short-lived confirmation or low-risk transient notice. |
| `MODAL_DIALOG` | Interruptive decision or confirmation requiring focus. |
| `EMPTY_STATE` | Explains absence of content and next action. |
| `TABLE_OR_LIST_STATE` | Represents per-row or collection-level status. |
| `DETAIL_PANEL` | Sustained information inspection or comparison. |
| `HELP_TEXT` | Persistent guidance near the relevant control or surface. |
| `STATUS_BADGE` | Compact state indicator that must be supported by accessible explanation when needed. |
| `ERROR_SUMMARY` | Aggregated validation or failure information. |

## Contract Clauses

### INFO-CONTRACT-001 Consistency Key

Equivalent semantic intent, trigger condition, scope, and lifecycle must use one presentation mode unless an explicit exception exists.

### INFO-CONTRACT-002 Sustained Decision Information

Information required for sustained user processing or decision-making must not be represented only by transient, unrecoverable feedback.

### INFO-CONTRACT-003 Trigger Scope Match

Presentation mode must match the trigger scope. Field-level issues should not become global interruptions unless the impact is global.

### INFO-CONTRACT-004 Lifecycle Match

Information that remains relevant after the triggering event must be persistent, recoverable, or reachable from the relevant surface.

### INFO-CONTRACT-005 Message Trace Binding

Interaction message records from `P1-SPEC-04-INTERACTION-CLOSURE` must map to presentation modes before layout can place them.

### INFO-CONTRACT-006 Accessibility And Recoverability

Critical, error, permission, validation, and decision-support information must be available in a recoverable form and not only as visual styling.

## Required Presentation Decision Fields

| Field | Requirement |
|---|---|
| `presentation_id` | Stable ID. |
| `semantic_intent` | Meaning of the information. |
| `trigger_condition` | Event, state, condition, or user action that creates the information. |
| `scope` | Field, control, row, card, section, page, flow, account, or global. |
| `information_lifecycle` | Momentary, session, until resolved, persistent, audit, or declared equivalent. |
| `presentation_mode` | One declared mode. |
| `recoverability` | Whether and how the information can be found again. |
| `reason_for_difference` | Required when similar information uses a different mode. |
| `trace_refs` | Source, interaction message, rule, Human Gate, or upstream references. |

