# P1-SPEC-02 Stage Dependency Rules

## Rule Index

| Rule ID | Clause | Rule |
|---|---|---|
| `STAGE-RULE-006` | `DRD-CHARTER-002` | A stage may consume only approved upstream artifacts, not unapproved Candidates. |
| `STAGE-RULE-007` | `DRD-CHARTER-002` | A stage input bundle must list every required upstream artifact and hash. |
| `STAGE-RULE-008` | `DRD-CHARTER-002` | A downstream artifact is invalid when any bound upstream artifact hash changes. |
| `STAGE-RULE-009` | `DRD-CHARTER-002` | Stage execution order must follow the canonical DRD stage chain unless a locked spec explicitly declares an allowed skip. |
| `STAGE-RULE-010` | `DRD-CHARTER-002` | Human Gate decisions must bind the hash of the reviewed stage artifact or reviewed artifact bundle. |
| `STAGE-RULE-011` | `DRD-CHARTER-002` | `DRD-05` may compile only approved stage artifacts and operational indexes. |
| `STAGE-RULE-012` | `DRD-CHARTER-002` | Stage order must be determined by explicit numeric `stage_order_index`, not lexical stage ID ordering. |
| `STAGE-RULE-013` | `DRD-CHARTER-002` | `DRD-06` may only emit read-only QA artifacts and must not mutate canonical artifacts, manifests, locks, or review decisions. |

## Required Dependency Edges

| Stage | Required upstream |
|---|---|
| `DRD-00` | None. |
| `DRD-01` | `DRD-00` Source snapshot. |
| `DRD-02` | `DRD-00` Source snapshot, approved `DRD-01`. |
| `DRD-03` | `DRD-00` Source snapshot, approved `DRD-01`, approved `DRD-02`. |
| `DRD-03B` | `DRD-00` Source snapshot, approved `DRD-02`, approved `DRD-03`. |
| `DRD-04` | `DRD-00` Source snapshot, approved `DRD-02`, approved `DRD-03`, approved `DRD-03B`. |
| `DRD-05` | Approved `DRD-01`, `DRD-02`, `DRD-03`, `DRD-03B`, `DRD-04`, plus their operational indexes. |
| `DRD-06` | Frozen Source snapshot, approved upstream artifacts, compiled `FINAL_DRD.md`, and final manifest. |

## Dependency Manifest

Every stage execution must produce or update a dependency manifest containing:

- `stage_id`.
- `run_id`.
- `input_artifacts`.
- `input_hashes`.
- `source_prd_snapshot_hash`.
- `output_artifacts`.
- `output_hashes`.
- `validator_result_hash`.
- `review_decision_hash` when applicable.

The dependency manifest schema target is:

```text
repository/schemas/stages/dependency_manifest.schema.json
```

## Stage Order Manifest

The stage order manifest must contain explicit rows for `DRD-00`, `DRD-01`, `DRD-02`, `DRD-03`, `DRD-03B`, `DRD-04`, `DRD-05`, and `DRD-06`, each with a unique numeric `stage_order_index`. `DRD-03B` must sort after `DRD-03` and before `DRD-04`.

## Candidate Versus Approved Inputs

Candidate artifacts may be passed into repair loops or review workflows. They must not be consumed as authority by downstream stages until approved and promoted.

## Invalidation Boundary

This spec defines what must be bound and compared. The lock-state and invalidation engine is specified in `P1-SPEC-06-VALIDATION-LOCKS`.
