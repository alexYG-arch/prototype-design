# P1-SPEC-02 Stage Examples

## Positive Example: Source Snapshot Manifest

```json
{
  "source_prd_snapshot_id": "SRC-PRD-2026-06-23-001",
  "source_path": "inputs/product_prd.md",
  "snapshot_path": "runs/RUN-001/source/source_prd.md",
  "snapshot_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "byte_size": 42188,
  "content_type": "text/markdown",
  "normalization_method": "utf-8 line ending normalization",
  "source_identity": "product_prd.md"
}
```

This passes because source identity and immutable content hash are explicit.

## Negative Example: Summary Replaces Source

```json
{
  "stage_id": "DRD-02",
  "authority_inputs": [
    "PRD_EXPERIENCE_BRIEF.md"
  ],
  "source_prd_snapshot_hash": null
}
```

This fails with `STAGE002` because a derived brief cannot replace Source PRD.

## Positive Example: Approved Upstream Dependency

```json
{
  "stage_id": "DRD-03",
  "input_artifacts": [
    {
      "artifact_id": "DRD-01-EXPERIENCE-BRIEF",
      "status": "APPROVED",
      "hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    },
    {
      "artifact_id": "DRD-02-INTERACTION-CLOSURE",
      "status": "APPROVED",
      "hash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    }
  ]
}
```

This passes because downstream input is approved and hash-bound.

## Negative Example: Candidate Used As Authority

```json
{
  "stage_id": "DRD-04",
  "input_artifacts": [
    {
      "artifact_id": "DRD-03B-SHARED-PATTERNS",
      "status": "CANDIDATE",
      "hash": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    }
  ]
}
```

This fails with `STAGE005` because Candidates are not downstream authority.

## Negative Example: DRD-05 Adds Semantic Input

```json
{
  "stage_id": "DRD-05",
  "compiler_inputs": [
    "approved DRD artifacts",
    "new layout decision entered during compilation"
  ]
}
```

This fails with `STAGE009` because deterministic compilation cannot introduce new semantic decisions.

## Positive Example: Review Decision Binding

```json
{
  "decision_id": "DRD-02-REVIEW-A-001",
  "subject_hash": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "decision": "APPROVED",
  "reviewer": "human-user",
  "open_blockers": []
}
```

This passes when the subject hash matches the reviewed artifact bundle.

## Positive Example: Stage Order Index

```json
[
  {"stage_id": "DRD-03", "stage_order_index": 30},
  {"stage_id": "DRD-03B", "stage_order_index": 35},
  {"stage_id": "DRD-04", "stage_order_index": 40}
]
```

This passes because `DRD-03B` is explicitly ordered between `DRD-03` and `DRD-04`.

## Negative Example: Lexical Stage Ordering

```python
sorted(["DRD-03", "DRD-03B", "DRD-04"])
```

This is insufficient as an authority mechanism because stage ordering must come from `stage_order_index`, not string sorting behavior.

## Negative Example: DRD-06 Mutates Final DRD

```json
{
  "stage_id": "DRD-06",
  "output_artifacts": [
    "READ_ONLY_QA_REPORT.md",
    "FINAL_DRD.md"
  ]
}
```

This fails with `STAGE011` because `DRD-06` may report findings but must not mutate `FINAL_DRD.md` or any canonical artifact.
