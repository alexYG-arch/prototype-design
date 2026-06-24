# P1-SPEC-04 Interaction Projections

## Projection Index

| Projection ID | Source | Target | Purpose |
|---|---|---|---|
| `INTERACTION-PROJ-001` | Approved tasks and pages | Interaction node index | Creates page, state, overlay, processing, handoff, success, failure, and terminal nodes. |
| `INTERACTION-PROJ-002` | PRD element inventory plus adoption and derivation decisions | Clickable inventory | Defines the coverage universe for click closure. |
| `INTERACTION-PROJ-003` | Clickable inventory | Reaction records | Binds every clickable to behavior, target, success, failure, and cancel handling. |
| `INTERACTION-PROJ-004` | Reaction records | Graph edges | Converts Reactions into mechanically checkable edges. |
| `INTERACTION-PROJ-005` | Non-immediate operations | Async processing subgraph | Adds processing, success, failure, timeout, duplicate-trigger, and cancellation behavior. |
| `INTERACTION-PROJ-006` | External operations | Handoff subgraph | Adds success, cancel, failure, no-return, and resume paths. |
| `INTERACTION-PROJ-007` | Non-terminal nodes | Exit and recovery paths | Ensures every unfinished state can continue, return, recover, cancel, or exit. |
| `INTERACTION-PROJ-008` | Failure-prone actions | Failure state index | Ensures reason, recovery, and exit are explicit. |
| `INTERACTION-PROJ-009` | Overlay nodes | Overlay closure records | Prevents modal, drawer, menu, and popover traps. |
| `INTERACTION-PROJ-010` | Graph nodes and edges | Closure report | Reports reachability, dangling targets, legal cycles, terminal conditions, and blockers. |
| `INTERACTION-PROJ-011` | Async, failure, disabled, validation, handoff, cancel, exit, empty, and permission states | Interaction message coverage index | Ensures required user-visible copy is present and traceable. |

## Projection Requirements

Each projection must preserve:

- Source snapshot hash.
- Approved upstream artifact hash.
- Node IDs.
- Clickable IDs.
- Reaction IDs.
- Edge IDs.
- Human Gate decision IDs when interaction semantics are selected or approved.
- Message IDs when the interaction requires user-visible copy.

## Disallowed Projection Behavior

A projection must not:

- Create graph edges from clickables that are not inventoried.
- Create clickables without Reactions.
- Treat a disabled or hidden element as unspecified.
- Drop failure, cancel, or exit handling for actions that can fail, be cancelled, or leave the flow.
- Treat external handoff as complete without return, cancel, failure, or explicit no-return terminal handling.
- Treat a modal, drawer, menu, or popover as closed without target context restoration.
- Treat an async, failure, validation, disabled, handoff, cancel, exit, empty, or permission state as closed without required user-visible copy.

## Projection To Validators

The projection set feeds:

- Node schema validator.
- Clickable inventory validator.
- Reaction target validator.
- Graph reachability validator.
- Non-terminal exit validator.
- Async behavior validator.
- Handoff behavior validator.
- Failure recovery validator.
- Overlay closure validator.
- Legal cycle validator.
- Interaction message validator.
