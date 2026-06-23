# P1-SPEC-02 Artifact Contracts

## Artifact Identity

Every stage artifact must have:

- `artifact_id`.
- `stage_id`.
- `artifact_type`.
- `format`.
- `path`.
- `source_prd_snapshot_id`.
- `source_prd_snapshot_hash`.
- `upstream_artifact_hashes`.
- `candidate_hash`.
- `promotion_hash` when promoted.
- `review_decision_id` when a Human Gate applies.
- `status`.

Machine-readable artifact identity and dependency records must be represented by promoted repository-local schemas:

```text
repository/schemas/stages/source_snapshot_manifest.schema.json
repository/schemas/stages/stage_manifest.schema.json
repository/schemas/stages/dependency_manifest.schema.json
```

## Artifact Status Values

Allowed artifact statuses:

- `SOURCE_FROZEN`
- `CANDIDATE`
- `VALIDATED`
- `APPROVED`
- `PROMOTED`
- `REJECTED`
- `INVALIDATED`

Only Python promotion can move an approved Candidate to `PROMOTED`.

## Canonical Stage Artifacts

| Stage | Candidate semantic artifact | Operational index |
|---|---|---|
| `DRD-00` | Source PRD snapshot copy. | `source_snapshot_manifest.json` |
| `DRD-01` | `PRD_EXPERIENCE_BRIEF.md` | `experience_fact_index.json` |
| `DRD-02` | `USER_TASK_FLOW.md`, `INTERACTION_CLOSURE_REPORT.md` | `interaction_graph.json` |
| `DRD-03` | `PAGE_ELEMENT_BLUEPRINT.md` | `prd_element_decision_index.json` |
| `DRD-03B` | `SHARED_COMPONENT_REGISTRY.md`, `INFORMATION_PRESENTATION_REGISTRY.md` | `shared_pattern_index.json` |
| `DRD-04` | `LAYOUT_COMPOSITION_SPEC.md`, `FIGMA_RECONSTRUCTION_GUIDANCE.md` | `layout_anchor_index.json` |
| `DRD-05` | `FINAL_DRD.md` | `final_drd_manifest.json` |
| `DRD-06` | `READ_ONLY_QA_REPORT.md` | `qa_finding_index.json` |

`DRD-06` has no canonical mutation target. Its QA report and finding index are review inputs only.

## Hash Binding

Every artifact manifest must bind:

- The immutable Source PRD snapshot hash.
- The hashes of approved upstream artifacts.
- The hash of the current artifact content.
- The hash of the review decision when applicable.

A downstream artifact is invalid when any bound upstream hash changes.

## Format Rule

Human semantic artifacts must be Markdown. Operational indexes and manifests must be JSON. JSON indexes may point to Markdown sections, but cannot replace the semantic Markdown artifact.

## Promotion Boundary

Candidate files become canonical artifacts only through Python promotion after required validation and required Human Gate decisions. A promoted artifact must preserve the exact Candidate content hash or record a deterministic assembly transformation that has no semantic rewrite authority.
