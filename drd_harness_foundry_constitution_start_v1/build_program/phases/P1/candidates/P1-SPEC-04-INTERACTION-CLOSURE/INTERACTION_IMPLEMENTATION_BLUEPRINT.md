# P1-SPEC-04 Interaction Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/rules/interaction.py` | Node, edge, clickable, Reaction, async, handoff, exit, and failure rule helpers. | `repository/tests/interaction/test_reaction_targets.py` |
| `repository/src/drd_harness/validators/interaction_closure.py` | Graph closure, target integrity, reachability, overlay, async, handoff, exit, and failure validators. | `repository/tests/interaction/test_graph_closure.py` |
| `repository/schemas/interaction/interaction_graph.schema.json` | Graph root schema. | `repository/tests/interaction/test_interaction_graph_schema.py` |
| `repository/schemas/interaction/clickable_inventory.schema.json` | Clickable inventory schema. | `repository/tests/interaction/test_clickable_inventory_schema.py` |
| `repository/schemas/interaction/reaction_record.schema.json` | Reaction record schema. | `repository/tests/interaction/test_reaction_targets.py` |
| `repository/schemas/interaction/reaction_applicability.schema.json` | Reaction applicability schema for failure, cancel, async, and handoff declarations. | `repository/tests/interaction/test_reaction_applicability_schema.py` |
| `repository/schemas/interaction/interaction_message.schema.json` | User-visible interaction message schema. | `repository/tests/interaction/test_interaction_message_schema.py` |
| `repository/schemas/interaction/message_coverage_index.schema.json` | Message coverage index schema joining states and Reactions to required copy. | `repository/tests/interaction/test_message_coverage_index.py` |
| `repository/schemas/interaction/async_behavior.schema.json` | Async behavior schema. | `repository/tests/interaction/test_async_handoff_failure.py` |
| `repository/schemas/interaction/handoff_behavior.schema.json` | External handoff schema. | `repository/tests/interaction/test_async_handoff_failure.py` |
| `repository/schemas/interaction/failure_recovery.schema.json` | Failure recovery schema. | `repository/tests/interaction/test_async_handoff_failure.py` |
| `repository/schemas/interaction/overlay_closure.schema.json` | Overlay closure schema. | `repository/tests/interaction/test_graph_closure.py` |

## Implementation Rules

### IMPL-INTERACTION-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-INTERACTION-002 Graph Validators Are Pure

Validators must report failures and must not rewrite graph artifacts to make them pass.

### IMPL-INTERACTION-003 Graph Algorithms Required

Reachability, dangling target, non-terminal exit, overlay trap, and cycle checks must use graph traversal rather than document string scanning.

### IMPL-INTERACTION-004 Fixture Coverage

Tests must include positive and negative fixtures for:

- Clickable with valid Reaction.
- Clickable without Reaction.
- Reaction with dangling target.
- Reaction with missing or contradictory applicability declarations.
- Non-terminal node with no exit.
- Async action without processing state.
- Async duplicate trigger strategy.
- Async processing without required user-visible copy.
- External handoff without return handling.
- Failure without recovery.
- Failure or validation state without message record.
- Interaction copy that adds unapproved product scope.
- Modal trap.
- Legal retry cycle with exit.
- Conditional clickable with guards.

### IMPL-INTERACTION-005 Upstream Trace Integration

Interaction validators must integrate with stage dependency and reasoning artifacts so nodes, clickables, and Reactions can be traced to approved upstream records.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/interaction
```

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-005` | Graph closure, click closure, reachability | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-002`, `INTERACTION-CHECK-003`, `INTERACTION-CHECK-004`, `INTERACTION-CHECK-006` |
| `RD-RULE-002` | Async behavior | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-008` |
| `RD-RULE-003` | External handoff | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-009` |
| `RD-RULE-004` | Click obligation, Reaction target, and applicability | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-002`, `INTERACTION-CHECK-003`, `INTERACTION-CHECK-004`, `INTERACTION-CHECK-005`, `INTERACTION-CHECK-015` |
| `RD-RULE-005` | Exit obligation | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-007`, `INTERACTION-CHECK-011` |
| `RD-RULE-006` | Failure reason, recovery, and user-visible copy | `rules/interaction.py`, `validators/interaction_closure.py` | `INTERACTION-CHECK-010`, `INTERACTION-CHECK-017`, `INTERACTION-CHECK-020` |
