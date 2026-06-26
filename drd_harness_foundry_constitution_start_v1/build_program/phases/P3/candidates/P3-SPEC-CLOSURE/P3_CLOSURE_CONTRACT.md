# P3 Interaction Closure Contract

## Objective

`P3-SPEC-CLOSURE` defines the full interaction-closure contract for P3. It turns approved distillation outputs into a closed, testable interaction graph before page element modeling, pattern decisions, layout, compilation, or assurance work can rely on the experience flow.

The module is `interaction_closure`. Its job is to prove that every adopted action, page, state, overlay, async operation, handoff, failure path, recovery target, message, and terminal condition is represented with traceable graph evidence.

## Upstream Authority

| Artifact | Binding |
| --- | --- |
| `control/locks/P2_BUILD_LOCK.json` | `b7a85510c2a7b839ca5461341017da9bcaa3ddd031019936b921bf881af29aad` |
| `P3-SPEC-DISTILL/REVIEW_DECISION.json` | `5c078b9509d48b8eccf863c9cf074b55d355c9bde28ff13a21446f093150e902` |
| `P3-SPEC-DISTILL` subject hash | `9979320f18e0d0de86f4cafd2dffad64634631f6d71ed7bd7bce148220bd8d1c` |
| `P3-SPEC-DISTILL/P3_DISTILLATION_ARTIFACT_CONTRACTS.json` | `eda141d5ce3656377b696f2d5b2796542cee9a88b7c195c2cc0abc83b899fc12` |

`P3-SPEC-CLOSURE` may consume only eligible distilled units and explicit blockers from the distillation handoff. It must not reinterpret rejected or unresolved product expansion gaps as valid interaction behavior.

## Closure Definition

An interaction graph is closed when all of these are true:

1. Every entry path starts from an approved page, state, overlay, or handoff node.
2. Every non-terminal node has at least one continuation edge or an explicit trap justification.
3. Every clickable maps to exactly one reaction record.
4. Every reaction target resolves to a graph node, external handoff, or terminal reason.
5. Every async reaction has duplicate-trigger, timeout, success, failure, and cancellation behavior where applicable.
6. Every failure-prone path has a failure node and at least one recovery target or terminal explanation.
7. Every overlay has closure targets and return context.
8. Every user-visible async, disabled, failure, recovery, success, cancellation, or terminal condition has message coverage.
9. No message or edge introduces product capability outside approved distillation evidence.

## Non Product Capability Boundary

Interaction closure can organize approved behavior into nodes, edges, reactions, and copy obligations. It cannot add a new task, new page, new workflow, new account capability, new integration, new data scope, or unapproved business rule. If closure requires one of those, the graph must preserve a blocker and route to product expansion review.
