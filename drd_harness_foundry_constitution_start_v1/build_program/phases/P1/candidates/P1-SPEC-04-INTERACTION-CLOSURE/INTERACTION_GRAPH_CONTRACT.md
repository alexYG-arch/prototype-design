# P1-SPEC-04 Interaction Graph Contract

## Purpose

This Candidate defines the interaction closure contract for the DRD Harness.

It owns these locked clauses:

- `DRD-CHARTER-005` Interaction closure.
- `RD-RULE-002` Async obligation.
- `RD-RULE-003` Handoff obligation.
- `RD-RULE-004` Click obligation.
- `RD-RULE-005` Exit obligation.
- `RD-RULE-006` Failure obligation.

## Graph Authority

The interaction graph is the mechanical representation of user-executable experience flow.

It must represent:

- Pages.
- Page states.
- Overlays, modals, drawers, panels, menus, and popovers when they affect interaction.
- Async processing states.
- External handoff states.
- Success, failure, blocked, empty, permission, and terminal states.
- Clickable elements and their Reactions.
- Return, cancel, retry, recovery, continuation, and exit paths.

## Node Types

| Node Type | Meaning |
|---|---|
| `PAGE` | Full page or route-level surface. |
| `STATE` | State of a page or flow. |
| `OVERLAY` | Modal, drawer, panel, menu, or popover that changes interaction scope. |
| `PROCESSING` | Async in-progress state. |
| `EXTERNAL_HANDOFF` | User leaves or interacts with an external system. |
| `SUCCESS` | Completed successful outcome. |
| `FAILURE` | Operation failed or was blocked. |
| `TERMINAL` | Explicit end state with no required continuation. |

## Edge Types

| Edge Type | Meaning |
|---|---|
| `NAVIGATES_TO` | Moves to another page or state. |
| `OPENS_OVERLAY` | Opens modal, drawer, panel, menu, or popover. |
| `CLOSES_OVERLAY` | Closes overlay and returns focus or context. |
| `SUBMITS_ACTION` | Executes a user action. |
| `STARTS_ASYNC` | Enters a processing state. |
| `ASYNC_SUCCESS` | Async operation succeeds. |
| `ASYNC_FAILURE` | Async operation fails or times out. |
| `HANDOFF_EXTERNAL` | Enters external system or external flow. |
| `HANDOFF_SUCCESS` | Returns from external system successfully. |
| `HANDOFF_CANCEL` | User cancels or abandons external handoff. |
| `HANDOFF_FAILURE` | External handoff fails or is blocked. |
| `RETRIES` | Attempts recovery after failure. |
| `CANCELS` | Stops current operation and returns or exits. |
| `EXITS` | Leaves the flow by an explicit allowed path. |
| `TERMINATES` | Reaches a declared terminal state. |

## Contract Clauses

### INTERACTION-CONTRACT-001 Click Closure

Every clickable element must have a Reaction with a declared edge, target, success behavior, failure behavior, and cancellation behavior when applicable.

### INTERACTION-CONTRACT-002 Target Integrity

Every edge target must be a declared node, declared terminal condition, or declared external handoff target.

### INTERACTION-CONTRACT-003 Reachability

Every required page, state, overlay, and handoff node must be reachable from an approved entry node unless explicitly marked as an externally resumed node with a valid resume source.

### INTERACTION-CONTRACT-004 Non-Terminal Continuation

Every non-terminal node must provide at least one continuation, recovery, return, cancel, or exit path.

### INTERACTION-CONTRACT-005 Terminal Explicitness

Terminal nodes must state why the interaction can stop and what user outcome is reached.

### INTERACTION-CONTRACT-006 Overlay Closure

Every overlay that captures interaction focus must define close, cancel, submit, or outside-click behavior, plus the context or focus target after closure.

### INTERACTION-CONTRACT-007 Legal Cycles

Cycles are allowed only when they represent understandable navigation, retry, edit, or review loops and include an exit or progress path.

### INTERACTION-CONTRACT-008 Stage Binding

Interaction graph nodes and clickable elements must trace to approved PRD element adoption, derived surface, structural completion, or Human Gate decision records from upstream spec obligations.

## Disallowed Graph States

The graph must not contain:

- Clickable elements without Reactions.
- Reactions without targets.
- Failure nodes without reason and recovery or exit.
- Async actions without processing state and repeat-trigger strategy.
- External handoffs without return, cancel, and failure handling unless a no-return terminal is explicitly justified.
- Modal or overlay traps with no exit.
- Dead-end non-terminal nodes.

