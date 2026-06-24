# P1-SPEC-04 Async Handoff Exit Failure Rules

## Purpose

These rules implement `RD-RULE-002`, `RD-RULE-003`, `RD-RULE-005`, and `RD-RULE-006`.

## Async Rules

### AHEF-RULE-001 Processing State Required

If an operation is not immediate, it must enter a declared `PROCESSING` node or equivalent in-progress state.

The processing state must have user-visible copy that explains the operation is in progress.

### AHEF-RULE-002 Repeat Trigger Strategy

Async actions must define what happens when the user triggers the action again while it is processing.

Allowed strategies:

- Disable duplicate trigger.
- Ignore duplicate trigger with visible state.
- Queue duplicate trigger.
- Treat duplicate trigger as idempotent retry.
- Cancel and restart, if safe and explicit.

If the strategy affects what the user can do, the visible copy must explain it.

### AHEF-RULE-003 Async Outcomes

Async operations must define success, failure, timeout, and cancellation behavior when applicable.

## Handoff Rules

### AHEF-RULE-004 External Handoff Contract

If an operation enters an external system, the graph must define:

- External target.
- What user sees before leaving or opening external context.
- Success return path.
- Cancel or abandon path.
- Failure or blocked path.
- No-return terminal, if the handoff intentionally ends the flow.

The handoff must also define user-visible copy before leaving or opening external context and after success, cancel, failure, or abandonment.

### AHEF-RULE-005 Handoff State Binding

External return paths must bind to known nodes and preserve relevant source or session context when required by the user task.

## Exit Rules

### AHEF-RULE-006 Non-Terminal Exit Obligation

If a node is not terminal, the user must have continuation, recovery, return, or exit.

### AHEF-RULE-007 Exit Consequence

Exit paths must state whether unsaved work is saved, discarded, preserved as draft, or requires confirmation.

When the consequence can affect user work, the consequence must be visible in copy before or during the exit.

### AHEF-RULE-008 Return Target

Back, cancel, close, and return controls must identify the exact target node or context restoration rule.

## Failure Rules

### AHEF-RULE-009 Failure Reason

Failure or blocked states must explain the reason in user-understandable terms.

The explanation must be represented as an interaction message record.

### AHEF-RULE-010 Failure Recovery

Failure or blocked states must provide retry, edit, choose another path, contact support, return, or exit when applicable.

### AHEF-RULE-011 Irrecoverable Failure Terminal

If a failure has no recovery path, it must be declared terminal and explain why no continuation is available.

### AHEF-RULE-012 Validation Failure

Validation failures must identify the invalid input, the needed correction, and the path back to editing.

Validation copy must bind to the invalid or missing field, section, or action.
