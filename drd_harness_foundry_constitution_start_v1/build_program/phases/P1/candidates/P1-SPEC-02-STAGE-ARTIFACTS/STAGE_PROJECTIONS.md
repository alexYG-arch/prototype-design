# P1-SPEC-02 Stage Projections

## Projection Index

| Projection ID | Source | Target | Purpose |
|---|---|---|---|
| `STAGE-PROJ-001` | Source PRD file | Source snapshot manifest | Freezes immutable input identity and hash. |
| `STAGE-PROJ-002` | Source snapshot plus DRD-01 contract | `PRD_EXPERIENCE_BRIEF.md` and fact index | Projects source PRD into experience facts without replacing the source. |
| `STAGE-PROJ-003` | Approved DRD-01 plus source snapshot | `USER_TASK_FLOW.md`, `INTERACTION_CLOSURE_REPORT.md`, and graph index | Projects facts into tasks, states, clickable elements, and closure edges. |
| `STAGE-PROJ-004` | Approved DRD-01 and DRD-02 plus source snapshot | `PAGE_ELEMENT_BLUEPRINT.md` and element decision index | Projects source elements and deductive obligations into page elements. |
| `STAGE-PROJ-005` | Approved DRD-02 and DRD-03 plus source snapshot | Shared component and presentation registries | Projects equivalent semantics into shared patterns and presentation modes. |
| `STAGE-PROJ-006` | Approved DRD-02, DRD-03, DRD-03B plus source snapshot | Layout spec, Figma guidance, and layout anchor index | Projects approved page semantics into natural-language layout. |
| `STAGE-PROJ-007` | Approved DRD-01 through DRD-04 | `FINAL_DRD.md` and final manifest | Deterministically compiles approved sections without semantic rewrite. |
| `STAGE-PROJ-008` | Frozen source, approved artifacts, and final DRD | Read-only QA report and finding index | Projects consistency findings without mutating canonical artifacts. |
| `STAGE-PROJ-009` | Canonical stage chain | Stage order index | Projects human-readable stage order into explicit numeric ordering for mechanical validation. |
| `STAGE-PROJ-010` | Source snapshot and dependency contracts | Stage schemas | Projects manifest contracts into `source_snapshot_manifest.schema.json`, `stage_manifest.schema.json`, and `dependency_manifest.schema.json`. |

## Projection Requirements

Each projection must preserve:

- Source snapshot hash.
- Required upstream hashes.
- Stage ID.
- Artifact IDs.
- Review decision hash when a gate applies.

## Disallowed Projection Behavior

A projection must not:

- Treat a summary as a replacement for Source PRD.
- Consume an unapproved Candidate as downstream authority.
- Drop upstream artifact hashes.
- Change stage order without locked spec authority.
- Add semantic decisions during deterministic compilation.
- Infer `DRD-03B` order by string sorting.
- Allow `DRD-06` read-only QA to mutate canonical artifacts.

## Projection To Validators

`STAGE-PROJ-001` through `STAGE-PROJ-008` feed these validator families:

- Source snapshot validator.
- Stage input bundle validator.
- Dependency manifest validator.
- Artifact lineage validator.
- Review binding validator.
- Compilation input validator.
- Stage order index validator.
- Read-only QA boundary validator.
