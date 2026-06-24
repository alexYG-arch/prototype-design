# P1-SPEC-04 Reaction Rules

## Purpose

A Reaction explains what happens when a clickable element is activated.

## Reaction Types

| Reaction Type | Meaning |
|---|---|
| `NAVIGATE` | Moves to a page, state, or route. |
| `OPEN_OVERLAY` | Opens modal, drawer, popover, menu, or panel. |
| `CLOSE_OVERLAY` | Closes overlay and returns context or focus. |
| `SUBMIT` | Sends or commits user input. |
| `START_ASYNC` | Starts a non-immediate operation. |
| `SELECT` | Selects an option or item. |
| `TOGGLE` | Switches binary state. |
| `RETRY` | Attempts a failed or blocked operation again. |
| `CANCEL` | Cancels current operation or handoff. |
| `EXIT` | Leaves current flow through an explicit path. |
| `HANDOFF` | Enters an external system. |
| `TERMINATE` | Ends the interaction in a declared terminal state. |

## Required Reaction Fields

| Field | Requirement |
|---|---|
| `reaction_id` | Stable ID. |
| `clickable_id` | Triggering clickable element. |
| `source_node_id` | Node where trigger occurs. |
| `reaction_type` | One declared Reaction type. |
| `target_ref` | Declared node, terminal, or external handoff target. |
| `preconditions` | Required data, role, state, permission, or selection conditions. |
| `failure_applicability` | `CAN_FAIL`, `CANNOT_FAIL`, or `UNKNOWN_REQUIRES_REVIEW`. |
| `cancel_applicability` | `CANCELLABLE`, `NOT_CANCELLABLE`, or `UNKNOWN_REQUIRES_REVIEW`. |
| `async_applicability` | `IMMEDIATE`, `NON_IMMEDIATE`, or `UNKNOWN_REQUIRES_REVIEW`. |
| `handoff_applicability` | `INTERNAL_ONLY`, `EXTERNAL_HANDOFF`, or `UNKNOWN_REQUIRES_REVIEW`. |
| `success_behavior` | Required resulting node or state on success. |
| `failure_behavior` | Required for actions that can fail or be blocked. |
| `cancel_behavior` | Required when user can cancel or abandon. |
| `exception_behavior` | Timeout, validation error, permission block, network failure, or equivalent. |
| `message_refs` | User-visible message records required for processing, success, failure, validation, disabled, cancel, exit, handoff, or recovery states. |
| `trace_refs` | Source, inference, adoption, derivation, or Human Gate references. |

## Rules

### REACTION-RULE-001 Reaction Target Required

Every Reaction must resolve to a declared graph node, declared terminal, or declared handoff target.

### REACTION-RULE-002 Preconditions Are User-Relevant

When a Reaction depends on data, role, selection, or state, the spec must say how the user sees or satisfies that condition.

### REACTION-RULE-002A Applicability Is Explicit

Each Reaction must declare whether failure, cancellation, async processing, and external handoff apply. `UNKNOWN_REQUIRES_REVIEW` blocks canonical use until Human Gate or upstream proof resolves it.

### REACTION-RULE-003 Success Must Advance Or Close

Every successful Reaction must advance the flow, update state, close an overlay, return to a known context, or reach a terminal condition.

### REACTION-RULE-004 Failure Must Explain And Recover

Every failure-prone Reaction must define user-visible reason and recovery or exit path.

The user-visible reason and recovery or exit path must bind to message records when the failure can be seen by the user.

### REACTION-RULE-005 Cancellation Is Explicit

Any cancellable action, overlay, edit, async operation, or external handoff must define cancel behavior and return target.

### REACTION-RULE-006 No Ambiguous Multi-Target

A Reaction must not list multiple possible targets without guards, priority, or Human Gate decision.

### REACTION-RULE-007 Data Mutation Visibility

If a Reaction changes saved data or durable system state, success and failure behavior must make the outcome visible to the user.

### REACTION-RULE-009 Message Binding

Reactions that enter processing, success confirmation, failure, validation, disabled, cancel, exit, external handoff, or recovery states must bind to the corresponding interaction message records.

### REACTION-RULE-008 Destructive Reaction Guard

Destructive or irreversible Reactions must define confirmation, undo, recovery, or explicit terminal consequences according to approved upstream obligations.
