# P1-SPEC-02 Source Snapshot Rules

## Rule Index

| Rule ID | Clause | Rule |
|---|---|---|
| `STAGE-RULE-001` | `DRD-CHARTER-001` | `DRD-00` must create an immutable Source PRD snapshot before semantic stages execute. |
| `STAGE-RULE-002` | `DRD-CHARTER-001` | Every semantic reasoning stage must read the immutable Source PRD snapshot directly. |
| `STAGE-RULE-003` | `DRD-CHARTER-001` | Derived briefs, summaries, indexes, or prior Candidates cannot replace the Source PRD snapshot. |
| `STAGE-RULE-004` | `DRD-CHARTER-001` | Every semantic artifact must bind `source_prd_snapshot_id` and `source_prd_snapshot_hash`. |
| `STAGE-RULE-005` | `DRD-CHARTER-001` | If the Source PRD changes, a new Source snapshot is required and all downstream artifacts bound to the old hash become invalid. |

## Source Snapshot Manifest

`DRD-00` must produce a JSON manifest with:

- `source_prd_snapshot_id`.
- `source_path`.
- `snapshot_path`.
- `snapshot_hash`.
- `created_at`.
- `byte_size`.
- `content_type`.
- `normalization_method`.
- `source_identity`.

## Normalization

The snapshot process may normalize file encoding and line endings only when the normalization method is declared in the snapshot manifest. It must not summarize, rewrite, delete, reorder, or reinterpret PRD content.

## Semantic Stage Input

`DRD-01`, `DRD-02`, `DRD-03`, `DRD-03B`, and `DRD-04` must include the Source PRD snapshot in their input bundle.

`DRD-06` must read the frozen source and final compiled output for consistency QA.

`DRD-05` must not read source for new semantic decisions. It consumes source identity through approved upstream artifact manifests.

## Failure Conditions

Source snapshot validation fails when:

- A semantic stage lacks a Source PRD snapshot hash.
- A semantic stage uses a derived brief as source replacement.
- A downstream artifact binds a source hash that does not match the active Source snapshot.
- A source file changes without creating a new snapshot.
- A Candidate hides source changes by reusing an old source snapshot hash.
