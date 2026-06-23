# P1-SPEC-02 Stage Validator Spec

## Validator Families

P1 stage and artifact contracts require these validator families:

- `source_snapshot_validator`.
- `stage_input_bundle_validator`.
- `stage_dependency_validator`.
- `artifact_lineage_validator`.
- `review_binding_validator`.
- `stage_order_index_validator`.
- `read_only_qa_boundary_validator`.

## Checks

| Check ID | Rule IDs | Deterministic | Failure code | Description |
|---|---|---:|---|---|
| `STAGE-CHECK-001` | `STAGE-RULE-001` | Yes | `STAGE001` | `DRD-00` produced an immutable Source PRD snapshot and manifest. |
| `STAGE-CHECK-002` | `STAGE-RULE-002`, `STAGE-RULE-003` | Hybrid | `STAGE002` | Semantic stages include Source PRD snapshot in input and do not rely on derived summaries as replacement. |
| `STAGE-CHECK-003` | `STAGE-RULE-004` | Yes | `STAGE003` | Semantic artifacts bind source snapshot ID and hash. |
| `STAGE-CHECK-004` | `STAGE-RULE-005`, `STAGE-RULE-008` | Yes | `STAGE004` | Source or upstream hash drift invalidates dependent artifacts. |
| `STAGE-CHECK-005` | `STAGE-RULE-006` | Yes | `STAGE005` | Downstream stage input bundle contains approved upstream artifacts only. |
| `STAGE-CHECK-006` | `STAGE-RULE-007` | Yes | `STAGE006` | Required upstream artifacts and hashes are complete. |
| `STAGE-CHECK-007` | `STAGE-RULE-009` | Yes | `STAGE007` | Stage execution order follows canonical chain. |
| `STAGE-CHECK-008` | `STAGE-RULE-010` | Yes | `STAGE008` | Human Gate decision binds the reviewed artifact or bundle hash. |
| `STAGE-CHECK-009` | `STAGE-RULE-011` | Yes | `STAGE009` | `DRD-05` compiles only approved upstream artifacts and operational indexes. |
| `STAGE-CHECK-010` | `STAGE-RULE-012` | Yes | `STAGE010` | Stage ordering uses explicit numeric `stage_order_index`, with `DRD-03B` between `DRD-03` and `DRD-04`. |
| `STAGE-CHECK-011` | `STAGE-RULE-013` | Yes | `STAGE011` | `DRD-06` emits only read-only QA artifacts and does not mutate canonical artifacts, manifests, locks, or review decisions. |
| `STAGE-CHECK-012` | `STAGE-RULE-001`, `STAGE-RULE-007` | Yes | `STAGE012` | Source snapshot and dependency manifests conform to promoted repository-local schemas. |

## Validator Inputs

Validators consume:

- Source snapshot manifest.
- Stage input bundle.
- Artifact manifests.
- Dependency manifests.
- Source snapshot manifest schema.
- Dependency manifest schema.
- Stage order index.
- Review decision records.
- Current stage output manifest.

## Validator Output

Validator output is JSON:

```json
{
  "validator": "stage_dependency_validator",
  "status": "PASS",
  "checked_rules": ["STAGE-RULE-006"],
  "findings": []
}
```

Failure output:

```json
{
  "validator": "stage_dependency_validator",
  "status": "FAIL",
  "findings": [
    {
      "code": "STAGE005",
      "path": "stage_input_bundle.json",
      "message": "DRD-03 attempted to consume an unapproved DRD-02 candidate."
    }
  ]
}
```

## Independence Rule

An implementation workpack may implement stage models and validators only after this Validator Spec is locked. The same implementation workpack must not weaken the locked validator spec or its golden tests.
