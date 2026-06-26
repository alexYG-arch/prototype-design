# P3 Interaction Closure Graph Model

## Core Objects

The graph model has five primary object families:

| Family | Role |
| --- | --- |
| Nodes | Pages, states, overlays, processing nodes, failures, successes, external handoff points, and terminal conditions. |
| Edges | Directed transitions between nodes or terminal targets. |
| Clickables | User-triggerable controls or affordances tied to source nodes. |
| Reactions | The behavior produced by a clickable, including target, preconditions, messages, async, failure, cancel, and handoff applicability. |
| Messages | User-visible copy obligations for processing, disabled states, failures, recovery, success, cancellation, and terminal outcomes. |

## Closure Discipline

Graph closure is stricter than inventory coverage. A clickable present in inventory is not closed until it has a reaction, target, trace refs, message refs, and applicable failure or async behavior. A state present in distillation is not closed until it is reachable from an entry path or explicitly terminal.

## Artifact Envelope Rule

Every interaction closure file is an artifact envelope with provenance fields and a payload key. Schema-bound records are validated inside the payload; the envelope carries source refs, upstream hashes, validator identity, review gate, promotion state, and invalidation inputs needed for cross-stage verification.

## Message Scope Rule

Messages must be same-task scoped. They can explain processing, disabled conditions, failures, recovery, success, cancellation, or terminal outcomes, but cannot advertise capability absent from approved distillation evidence. Product-scope expansion in message copy is a closure violation.

## Handoff Rule

External handoffs require explicit success, cancel, failure, and no-return terminal behavior. A handoff with no return path must name the terminal reason instead of leaving the graph ambiguous.
