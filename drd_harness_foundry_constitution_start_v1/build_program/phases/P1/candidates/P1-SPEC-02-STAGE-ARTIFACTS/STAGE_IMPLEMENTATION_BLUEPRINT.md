# P1-SPEC-02 Stage Implementation Blueprint

## Scope

This blueprint informs later implementation workpacks. It does not implement code.

Primary implementation workpack:

- `P1-IMPLEMENT-02-SOURCE-STAGE-LINEAGE`

## Code Target Map

| Contract clause | Rule | Projection | Code target | Validator | Test | Acceptance command |
|---|---|---|---|---|---|---|
| `DRD-CHARTER-001` | `STAGE-RULE-001` | `STAGE-PROJ-001` | `repository/src/drd_harness/stages/source_snapshot.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_source_snapshot.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-001` | `STAGE-RULE-001` | `STAGE-PROJ-010` | `repository/schemas/stages/source_snapshot_manifest.schema.json` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_source_snapshot_manifest_schema.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-001` | `STAGE-RULE-002` | `STAGE-PROJ-002` | `repository/src/drd_harness/stages/contracts.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_stage_source_inputs.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-001` | `STAGE-RULE-003` | `STAGE-PROJ-002` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_summary_not_source.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-001` | `STAGE-RULE-004` | `STAGE-PROJ-003` | `repository/schemas/stages/stage_manifest.schema.json` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_stage_manifest_schema.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-006` | `STAGE-PROJ-003` | `repository/src/drd_harness/stages/contracts.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_approved_upstream_only.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-007` | `STAGE-PROJ-004` | `repository/src/drd_harness/kernel/hashline.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_stage_lineage.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-007` | `STAGE-PROJ-010` | `repository/schemas/stages/dependency_manifest.schema.json` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_dependency_manifest_schema.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-010` | `STAGE-PROJ-008` | `repository/src/drd_harness/stages/review_binding.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_review_binding.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-011` | `STAGE-PROJ-007` | `repository/src/drd_harness/stages/compile_inputs.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_compile_inputs.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-012` | `STAGE-PROJ-009` | `repository/src/drd_harness/stages/stage_order.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_stage_order_index.py` | `python -m pytest repository/tests/stages` |
| `DRD-CHARTER-002` | `STAGE-RULE-013` | `STAGE-PROJ-008` | `repository/src/drd_harness/stages/read_only_qa.py` | `repository/src/drd_harness/validators/stage_lineage.py` | `repository/tests/stages/test_read_only_qa_boundary.py` | `python -m pytest repository/tests/stages` |

## Required Implementation Artifacts

`P1-IMPLEMENT-02-SOURCE-STAGE-LINEAGE` must produce:

- Source snapshot model and manifest helpers.
- Stage contract model.
- Stage input bundle model.
- Source snapshot manifest schema.
- Artifact manifest schema.
- Dependency manifest schema.
- Stage order index model.
- Stage lineage validator.
- Review binding validator helpers.
- Read-only QA boundary checks.
- Tests for source permanence and ordered dependencies.

## Implementation Restrictions

Implementation workpacks must not:

- Implement reasoning, adoption, interaction closure, presentation, layout, compiler conservation, or skill generation rules owned by later P1 Spec parts.
- Treat Candidate artifacts as approved stage authority.
- Read mutable source PRD instead of frozen Source PRD snapshot during semantic stages.
- Infer stage order by lexical sorting of stage IDs.
- Let `DRD-06` mutate approved artifacts, final DRD, manifests, locks, source snapshots, or review decisions.
- Weaken review binding or hash binding checks.
