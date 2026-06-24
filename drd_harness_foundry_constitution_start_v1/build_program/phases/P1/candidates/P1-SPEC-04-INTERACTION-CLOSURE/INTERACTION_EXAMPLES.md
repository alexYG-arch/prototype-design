# P1-SPEC-04 Interaction Examples

## Positive Example: Simple Navigation

```json
{
  "clickable_id": "CLK-PROJECT-ROW-001",
  "source_node_id": "NODE-PROJECT-LIST",
  "label_or_affordance": "Project row",
  "clickable_type": "row",
  "reaction_id": "RX-PROJECT-ROW-OPEN"
}
```

```json
{
  "reaction_id": "RX-PROJECT-ROW-OPEN",
  "clickable_id": "CLK-PROJECT-ROW-001",
  "source_node_id": "NODE-PROJECT-LIST",
  "reaction_type": "NAVIGATE",
  "target_ref": "NODE-PROJECT-DETAIL",
  "failure_applicability": "CAN_FAIL",
  "cancel_applicability": "NOT_CANCELLABLE",
  "async_applicability": "IMMEDIATE",
  "handoff_applicability": "INTERNAL_ONLY",
  "success_behavior": "Open selected project detail page.",
  "failure_behavior": "If project is unavailable, show failure state with return to project list.",
  "cancel_behavior": "Not applicable for direct navigation."
}
```

Why this passes:

- The clickable has a Reaction.
- The Reaction target is a declared node.
- Failure behavior exists for unavailable project.

## Positive Example: Async Submit

```json
{
  "reaction_id": "RX-SAVE-PROJECT",
  "reaction_type": "START_ASYNC",
  "target_ref": "NODE-PROJECT-SAVING",
  "failure_applicability": "CAN_FAIL",
  "cancel_applicability": "CANCELLABLE",
  "async_applicability": "NON_IMMEDIATE",
  "handoff_applicability": "INTERNAL_ONLY",
  "success_behavior": "Navigate to NODE-PROJECT-DETAIL with saved confirmation.",
  "failure_behavior": "Navigate to NODE-PROJECT-SAVE-FAILED with reason and retry/edit choices.",
  "cancel_behavior": "Cancel returns to NODE-PROJECT-EDIT without saving.",
  "exception_behavior": "Timeout shows retry and exit paths.",
  "repeat_trigger_strategy": "Disable duplicate trigger while saving.",
  "message_refs": [
    "MSG-PROJECT-SAVING",
    "MSG-PROJECT-SAVE-FAILED"
  ]
}
```

Why this passes:

- Non-immediate save enters processing.
- Duplicate trigger behavior is explicit.
- Success, failure, timeout, and cancel behavior are defined.
- Processing and failure states bind to message records.

Message records:

```json
[
  {
    "message_id": "MSG-PROJECT-SAVING",
    "message_type": "PROCESSING_MESSAGE",
    "node_id": "NODE-PROJECT-SAVING",
    "reaction_id": "RX-SAVE-PROJECT",
    "trigger_condition": "Save is in progress.",
    "user_visible_summary": "The project is being saved. The save button is disabled until the operation finishes.",
    "required_user_next_step": "wait",
    "recovery_targets": []
  },
  {
    "message_id": "MSG-PROJECT-SAVE-FAILED",
    "message_type": "FAILURE_MESSAGE",
    "node_id": "NODE-PROJECT-SAVE-FAILED",
    "reaction_id": "RX-SAVE-PROJECT",
    "trigger_condition": "Save failed or timed out.",
    "user_visible_summary": "The project could not be saved. The user can retry or return to editing.",
    "required_user_next_step": "retry_or_edit",
    "recovery_targets": ["RX-SAVE-PROJECT", "NODE-PROJECT-EDIT"]
  }
]
```

## Negative Example: Click Without Reaction

```json
{
  "clickable_id": "CLK-EXPORT",
  "source_node_id": "NODE-REPORT",
  "label_or_affordance": "Export",
  "clickable_type": "button"
}
```

Expected result: fail.

Reason:

- The clickable lacks `reaction_id`.
- There is no target, success, failure, or cancellation behavior.

## Negative Example: External Handoff Without Return

```json
{
  "reaction_id": "RX-CONNECT-CRM",
  "reaction_type": "HANDOFF",
  "target_ref": "Salesforce OAuth",
  "failure_applicability": "UNKNOWN_REQUIRES_REVIEW",
  "cancel_applicability": "UNKNOWN_REQUIRES_REVIEW",
  "async_applicability": "UNKNOWN_REQUIRES_REVIEW",
  "handoff_applicability": "EXTERNAL_HANDOFF"
}
```

Expected result: fail.

Reason:

- External handoff has no success return, cancel path, failure path, or no-return terminal justification.
- Applicability is unresolved for canonical use.

## Negative Example: Failure Without User Copy

```json
{
  "node_id": "NODE-UPLOAD-FAILED",
  "node_type": "FAILURE",
  "failure_reason": "Upload failed.",
  "recovery_paths": [
    "Retry upload"
  ],
  "message_refs": []
}
```

Expected result: fail.

Reason:

- The graph has a failure node, but no message record tells the user why it failed or what to do next.

## Negative Example: Copy Adds Product Scope

```json
{
  "message_id": "MSG-EXPORT-FAILED",
  "message_type": "FAILURE_MESSAGE",
  "node_id": "NODE-EXPORT-FAILED",
  "user_visible_summary": "Export failed. Connect Salesforce to automatically sync future exports.",
  "required_user_next_step": "connect_salesforce"
}
```

Expected result: fail unless Salesforce sync is already approved.

Reason:

- The failure copy introduces an integration and product promise not proven by approved upstream artifacts.

## Negative Example: Modal Trap

```json
{
  "node_id": "NODE-DELETE-CONFIRM-MODAL",
  "node_type": "OVERLAY",
  "edges": [
    "EDGE-CONFIRM-DELETE"
  ]
}
```

Expected result: fail.

Reason:

- The modal has no cancel, close, escape, outside-click behavior, or explicit trap justification.

## Positive Example: Failure Recovery

```json
{
  "node_id": "NODE-UPLOAD-FAILED",
  "node_type": "FAILURE",
  "failure_reason": "The selected file type is not supported.",
  "recovery_paths": [
    "Choose a different file",
    "Return to project detail"
  ],
  "exit_paths": [
    "Cancel upload"
  ]
}
```

Why this passes:

- User can understand the failure.
- Recovery and exit paths are explicit.
