# P1-SPEC-04 Interaction Copy Rules

## Purpose

Interaction closure is incomplete when the graph path exists but the user-visible message is missing.

These rules define copy obligations for async, failure, disabled, blocked, validation, cancellation, exit, handoff, empty, loading, and recovery states.

## Message Types

| Message Type | Meaning |
|---|---|
| `PROCESSING_MESSAGE` | Explains that a non-immediate operation is in progress. |
| `SUCCESS_MESSAGE` | Confirms a completed action when confirmation is needed for user confidence or next action. |
| `FAILURE_MESSAGE` | Explains why an operation failed or was blocked. |
| `VALIDATION_MESSAGE` | Explains invalid, missing, or conflicting input and how to fix it. |
| `DISABLED_REASON` | Explains why a visible control is unavailable when the reason is not obvious. |
| `CANCEL_CONFIRMATION` | Explains consequence of canceling or abandoning work. |
| `EXIT_CONSEQUENCE` | Explains what happens to unsaved, pending, or partial work. |
| `HANDOFF_NOTICE` | Explains that the user is entering or returning from an external system. |
| `RECOVERY_INSTRUCTION` | Tells the user how to retry, edit, choose another path, return, or exit. |
| `EMPTY_STATE_MESSAGE` | Explains why a surface has no content and what can be done next. |
| `PERMISSION_BLOCK_MESSAGE` | Explains role, permission, or access blocking in user-understandable terms. |

## Message Record Fields

| Field | Requirement |
|---|---|
| `message_id` | Stable ID for the user-visible message. |
| `message_type` | One declared message type. |
| `node_id` | Node where the message appears. |
| `reaction_id` | Reaction that caused the message, when applicable. |
| `trigger_condition` | State, failure, disabled condition, validation rule, handoff event, or exit event that displays the message. |
| `user_visible_summary` | Plain-language message intent; final UI copy may refine wording later. |
| `required_user_next_step` | Retry, edit, select, import, return, exit, wait, contact support, or no action. |
| `recovery_targets` | Target nodes or Reactions available from the message. |
| `trace_refs` | Source, rule, inference, adoption, derivation, Reaction, or Human Gate references. |

## Rules

### COPY-RULE-001 Async Copy Required

Every `PROCESSING` node or `NON_IMMEDIATE` Reaction must provide a processing message that tells the user the operation is in progress and what they can or cannot do while waiting.

### COPY-RULE-002 Duplicate Trigger Copy

If an async duplicate-trigger strategy disables, ignores, queues, retries, cancels, or restarts the action, the user-visible state must explain that strategy when it affects the user.

### COPY-RULE-003 Failure Copy Required

Every failure or blocked node must provide a failure message with user-understandable reason and at least one recovery instruction or terminal explanation.

### COPY-RULE-004 Validation Copy Required

Every validation failure must identify the invalid or missing input, describe the needed correction, and provide a path back to editing.

### COPY-RULE-005 Disabled Copy Required When Non-Obvious

Visible disabled controls must provide a disabled reason when the reason is not visually or contextually obvious.

### COPY-RULE-006 Cancel And Exit Consequence Copy

Cancel, close, back, and exit paths must explain consequences for unsaved, pending, or partial work when loss, discard, draft preservation, or external abandonment can occur.

### COPY-RULE-007 Handoff Copy Required

External handoff must provide a handoff notice before leaving or opening external context, and return-state copy after success, cancel, failure, or abandonment.

### COPY-RULE-008 Empty And Permission States

Empty states and permission-blocked states must explain why the user sees no content or cannot continue, plus the next available action.

### COPY-RULE-009 Copy Must Not Add Product Scope

Interaction copy must not introduce new product promises, capabilities, data scope, integrations, or policy commitments that are not authorized by approved upstream artifacts.

### COPY-RULE-010 Message Coverage Index

The Harness must maintain a message coverage index joining nodes, Reactions, failure states, async states, disabled controls, handoffs, validation rules, and exit paths to required message records.

## Disallowed Copy Gaps

The validator must reject:

- Processing states with no visible waiting or progress message.
- Failure states that only say "failed" without reason or next step.
- Validation errors that do not identify the field or correction path.
- External handoffs that leave the user without notice or return-state copy.
- Exit paths that discard work without consequence copy.
- Disabled controls with no reason when the user needs the control to complete a task.
- Copy that silently adds product promises beyond approved scope.

