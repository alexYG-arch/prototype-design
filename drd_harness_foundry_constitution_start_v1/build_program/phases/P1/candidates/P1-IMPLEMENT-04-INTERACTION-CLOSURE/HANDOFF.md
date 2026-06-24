# Handoff

## What Changed

The fourth P1 implementation workpack added interaction graph, clickable, Reaction, async, handoff, failure, overlay, reference integrity, edge alignment, schema, and message coverage models with pure closure validators.

## Review Patch

The review optimization pass tightened five areas:

1. Clickable and Reaction records now require bidirectional ID and source-node agreement.
2. Graph entries, edges, clickables, Reactions, messages, message references, and recovery targets now run reference integrity checks.
3. Reactions now require a matching graph edge from their source to their target with an allowed edge type.
4. Message coverage now includes inferred processing, failure, external handoff, success, cancel, exit, and disabled-control copy obligations.
5. Interaction graph, node, reaction, message, and clickable schemas are stricter and bind graph collections to the corresponding item schemas.

## Review Focus

1. Whether `STARTS_ASYNC`, `HANDOFF_EXTERNAL`, and `OPENS_OVERLAY` should count as valid non-terminal continuation edges.
2. Whether copy scope detection should remain keyword-based at this layer or move to a richer approved-scope join.
3. Whether legal cycle classification should be expanded beyond current continuation-edge checks.
4. Whether graph node, clickable, and Reaction trace refs should be joined to reasoning/adoption records in a later traceability workpack.
5. Whether empty-state and permission-state copy should get explicit node types in a later model revision, since the current model can validate those message records but cannot infer them from node type alone.

## Validation

`python3 -m pytest repository/tests/kernel repository/tests/stages repository/tests/reasoning repository/tests/interaction -q` passed with 83 tests.

## Remaining Boundary

This implementation candidate does not create `BUILD_LOCK`, does not implement promotion automation, and does not authorize the next workpack without explicit continuation.
