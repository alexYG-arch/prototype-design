# P2 Vertical Slice Contract

## Objective

`P2-SPEC-01` freezes the minimum vertical slice input and boundaries for the first complete harness run from source PRD to `FINAL_DRD.md`.

## Authority Inputs

The slice is authorized by these upstream artifacts:

| Artifact | Role |
|---|---|
| `control/locks/P1_BUILD_LOCK.json` | Locked P1 implementation foundation. |
| `build_program/phases/P1/candidates/P1-BUILD-GATE-READINESS/REVIEW_DECISION.json` | Human Gate approval for `P1_BUILD_GATE_APPROVED`. |
| `build_program/phases/P2/VERTICAL_SLICE_SCOPE.md` | P2 phase-level minimum slice scope. |

## Scope Boundary

The slice must cover one user task, one real page, one system handoff or overlay, every clickable element on that page, three to five user-visible states, one failure recovery path, PRD element validation, one shared component or presentation pattern decision, one natural-language layout, and one `FINAL_DRD.md`.

The slice must not add product capability to satisfy missing information. When completion requires a new user task, new page, secondary page, new business workflow, or unmentioned product ability, the artifact must create a human-review-required gap instead of silently expanding scope.

## Required Stage Outputs

The final P2 implementation must produce these output families for the fixture:

| Family | Required evidence |
|---|---|
| Source freeze | Source snapshot, hash, and immutable PRD reference. |
| PRD element adoption | Element inventory, accepted elements, rejected expansions, and derived element decisions. |
| Reasoning | Deduction-first inference records with premises, rule IDs, conclusions, and confidence boundaries. |
| Interaction | Page node, state nodes, overlay node, clickable inventory, interaction edges, async behavior, copy, and failure recovery. |
| Presentation | Information presentation registry, shared component decision, and presentation exception records when needed. |
| Layout | Natural-language layout, carrier adaptation profile, containment hierarchy, z-axis layering, scroll behavior, and content growth rules. |
| Compilation | Compiler input bundle, semantic unit inventory, conservation report, `FINAL_DRD.md`, final manifest, hash index, and reference index. |
| Final review | Review target, validation evidence, and human review decision for the completed vertical slice. |

## Verification Rule

Every required output must be verifiable from local files. Chat context is not evidence. A downstream P2 claim is invalid unless it names the source file, hash or subject hash, and validator or review basis.

## Non-Goals

`P2-SPEC-01` does not implement repository code, create `P2_SPEC_LOCK`, create `P2_BUILD_LOCK`, mutate P1 artifacts, or approve itself.
