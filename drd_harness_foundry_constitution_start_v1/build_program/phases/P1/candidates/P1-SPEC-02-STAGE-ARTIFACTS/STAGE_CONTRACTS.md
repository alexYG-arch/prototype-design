# P1-SPEC-02 Stage Contracts

## Scope

This Candidate defines DRD stage contracts and stage artifact lineage for the governed DRD Harness. It owns:

- `DRD-CHARTER-001` source permanence.
- `DRD-CHARTER-002` ordered dependency.

This Candidate does not implement stage runtime code, create locks, approve artifacts, or write Harness business logic.

## Stage Chain

The canonical DRD stage chain is:

```text
DRD-00 Source freeze
→ DRD-01 PRD experience fact extraction
→ DRD-02 user task and interaction closure
→ DRD-03 PRD element validation, adoption, and necessary completion
→ DRD-03B shared component and information presentation patterning
→ DRD-04 natural-language layout and Figma compatibility
→ DRD-05 deterministic DRD compilation
→ DRD-06 read-only consistency QA
```

## Universal Stage Contract

Every stage from `DRD-00` through `DRD-06` must declare:

- `stage_id`.
- `purpose`.
- `primary_runtime`.
- `source_prd_snapshot_id` or explicit reason it does not consume source PRD directly.
- `required_upstream_artifacts`.
- `required_upstream_hashes`.
- `authority_inputs`.
- `candidate_outputs`.
- `validator`.
- `human_gate`.
- `promotion_target`.
- `invalidation_inputs`.

## Stage Responsibilities

| Stage | Purpose | Primary runtime | Required source rule | Required upstream rule | Gate |
|---|---|---|---|---|---|
| `DRD-00` | Freeze Source PRD snapshot. | `PYTHON` | Creates immutable source snapshot. | None. | None. |
| `DRD-01` | Extract PRD experience facts. | `CODEX` | Must read Source PRD snapshot. | Consumes `DRD-00` snapshot hash. | Conditional. |
| `DRD-02` | Derive user tasks and close interactions. | `CODEX_PYTHON_LOOP` | Must read Source PRD snapshot. | Consumes approved `DRD-01` artifact hashes. | Review A. |
| `DRD-03` | Validate PRD elements and derive necessary missing elements. | `CODEX` | Must read Source PRD snapshot. | Consumes approved `DRD-01` and `DRD-02` artifact hashes. | Conditional. |
| `DRD-03B` | Establish shared components and information presentation patterns. | `CODEX_PYTHON_LOOP` | Must read Source PRD snapshot. | Consumes approved `DRD-02` and `DRD-03` artifact hashes. | Part of Review B. |
| `DRD-04` | Write natural-language layout and Figma reconstruction guidance. | `CODEX` | Must read Source PRD snapshot. | Consumes approved `DRD-02`, `DRD-03`, and `DRD-03B` artifact hashes. | Review B. |
| `DRD-05` | Compile approved sections into final DRD. | `PYTHON` | Consumes source snapshot hash through approved artifacts. | Consumes only approved DRD-01 through DRD-04 artifacts and control indexes. | Final Review. |
| `DRD-06` | Perform read-only consistency QA. | `CODEX` | Reads frozen source and compiled outputs. | Consumes final compiled artifact and approved upstream hashes. | Final Review input. |

## Source Permanence

Every semantic reasoning stage must read the immutable Source PRD snapshot. A brief, summary, extracted fact list, or previous Candidate cannot replace the Source PRD snapshot.

`DRD-05` is the exception only because it is a deterministic compiler. It must not make semantic decisions and must preserve the Source PRD snapshot hash through approved upstream artifact lineage.

## Ordered Dependency

Later stages may consume only approved upstream artifacts. Candidate artifacts may inform review but cannot be treated as upstream authority until promoted.

Each downstream stage must bind the exact hash of every approved upstream artifact it consumes.

## Stage Non-Goals

This Candidate does not define detailed reasoning rules for PRD element adoption, interaction closure, presentation consistency, layout completeness, compiler conservation, validation locks, or skill generation. Those are owned by later P1 Spec parts.
