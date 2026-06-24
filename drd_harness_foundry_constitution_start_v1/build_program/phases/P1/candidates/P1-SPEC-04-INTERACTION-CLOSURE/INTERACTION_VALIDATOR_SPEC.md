# P1-SPEC-04 Interaction Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `interaction_graph_schema_validator` | Checks node, edge, terminal, and graph document shape. |
| `clickable_inventory_validator` | Ensures clickables are inventoried and bound to Reactions. |
| `reaction_target_validator` | Ensures every Reaction has a valid target and required outcome fields. |
| `graph_reachability_validator` | Ensures required nodes are reachable and dangling nodes are justified. |
| `non_terminal_exit_validator` | Ensures every non-terminal node has continuation, recovery, return, cancel, or exit. |
| `async_behavior_validator` | Enforces processing state, duplicate-trigger strategy, and async outcomes. |
| `handoff_behavior_validator` | Enforces external success, cancel, failure, no-return, and resume handling. |
| `failure_recovery_validator` | Ensures failures explain reason and provide recovery or terminal justification. |
| `overlay_closure_validator` | Ensures overlays can close and restore context or focus. |
| `legal_cycle_validator` | Ensures cycles have progress, retry, edit, navigation, or exit semantics. |
| `interaction_message_validator` | Ensures async, failure, validation, disabled, cancel, exit, handoff, empty, permission, and recovery states have required user-visible messages. |
| `message_scope_validator` | Ensures user-visible copy does not add product scope beyond approved authority. |

## Checks

### INTERACTION-CHECK-001 Node Completeness

Fail if any graph node lacks ID, type, source references, terminal flag, and required state metadata.

### INTERACTION-CHECK-002 Clickable Coverage

Fail if a clickable user action exists in approved inputs but is missing from the clickable inventory.

### INTERACTION-CHECK-003 Reaction Coverage

Fail if any current clickable lacks exactly one current Reaction or guarded non-overlapping Reaction set.

### INTERACTION-CHECK-004 Reaction Target Integrity

Fail if a Reaction target does not resolve to a declared node, terminal condition, or external handoff target.

### INTERACTION-CHECK-005 Success Failure Cancel

Fail if a Reaction lacks success behavior, failure behavior for failure-prone actions, or cancel behavior for cancellable actions.

Fail if failure, cancellation, async, or handoff applicability is missing or marked `UNKNOWN_REQUIRES_REVIEW` in canonical inputs.

### INTERACTION-CHECK-006 Reachability

Fail if required nodes cannot be reached from approved entry nodes or declared resume sources.

### INTERACTION-CHECK-007 Non-Terminal Exit

Fail if a non-terminal node has no continuation, recovery, return, cancel, or exit path.

### INTERACTION-CHECK-008 Async Processing

Fail if a non-immediate operation has no processing node, duplicate-trigger strategy, or success/failure/timeout handling.

### INTERACTION-CHECK-009 External Handoff

Fail if an external handoff lacks success, cancel, failure, resume, or explicit no-return terminal behavior.

### INTERACTION-CHECK-010 Failure Recovery

Fail if a failure or blocked node lacks user-visible reason and recovery, return, retry, alternate path, or terminal justification.

Fail if the reason and recovery are not bound to message records.

### INTERACTION-CHECK-011 Overlay Closure

Fail if an overlay lacks close, cancel, submit, escape, outside-click, or explicit trap justification plus return context.

### INTERACTION-CHECK-012 Legal Cycles

Fail if a cycle has no progress, retry, edit, navigation, or exit semantics.

### INTERACTION-CHECK-013 Disabled And Conditional Controls

Fail if disabled, hidden, role-gated, or conditionally rendered clickables lack conditions and user-visible alternatives when needed.

### INTERACTION-CHECK-014 Stage Trace Binding

Fail if graph nodes, clickables, or Reactions cannot trace to approved upstream source, adoption, derivation, structural completion, or Human Gate records.

### INTERACTION-CHECK-015 Applicability Declaration

Fail if a Reaction does not declare:

- `failure_applicability`
- `cancel_applicability`
- `async_applicability`
- `handoff_applicability`

Fail if those declarations contradict the Reaction type, edge type, async behavior, handoff behavior, failure behavior, or cancel behavior.

### INTERACTION-CHECK-016 Async Message Coverage

Fail if a `PROCESSING` node or `NON_IMMEDIATE` Reaction lacks processing copy, duplicate-trigger copy when needed, or waiting-state next-step guidance.

### INTERACTION-CHECK-017 Failure And Validation Message Coverage

Fail if a failure, blocked, permission, or validation state lacks user-visible reason, affected field or action when applicable, correction path, recovery path, or terminal explanation.

### INTERACTION-CHECK-018 Handoff Exit Cancel Message Coverage

Fail if external handoff, cancel, back, close, or exit paths that affect user work lack copy explaining consequence, return target, abandonment, success, failure, or no-return terminal behavior.

### INTERACTION-CHECK-019 Disabled Empty Permission Message Coverage

Fail if disabled controls, empty states, or permission-blocked states lack user-visible reason and next available action when the user needs that state to continue the task.

### INTERACTION-CHECK-020 Copy Scope Boundary

Fail if interaction copy introduces product capability, data scope, integration, role, policy, pricing rule, or product promise not supported by approved upstream artifacts.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/interaction/interaction_graph.schema.json`
- `repository/schemas/interaction/interaction_node.schema.json`
- `repository/schemas/interaction/interaction_edge.schema.json`
- `repository/schemas/interaction/clickable_inventory.schema.json`
- `repository/schemas/interaction/reaction_record.schema.json`
- `repository/schemas/interaction/reaction_applicability.schema.json`
- `repository/schemas/interaction/interaction_message.schema.json`
- `repository/schemas/interaction/message_coverage_index.schema.json`
- `repository/schemas/interaction/async_behavior.schema.json`
- `repository/schemas/interaction/handoff_behavior.schema.json`
- `repository/schemas/interaction/failure_recovery.schema.json`
- `repository/schemas/interaction/overlay_closure.schema.json`
