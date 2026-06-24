# P1-SPEC-08 Spec Before Code Rules

## Rules

| Rule ID | Clause | Rule |
|---|---|---|
| `SBC-RULE-001` | `DRD-CHARTER-013` | Business code must not be implemented until applicable Contract, Rule, Projection, and Validator Spec outputs are locked by SPEC_LOCK. |
| `SBC-RULE-002` | `DRD-CHARTER-013` | Business Skills must not be generated, installed, or used until applicable specs are locked and Skill binding is reviewed. |
| `SBC-RULE-003` | `DRD-CHARTER-013` | Workpacks blocked by missing locks must remain `WAITING_UPSTREAM_LOCK` and cannot run implementation. |
| `SBC-RULE-004` | `DRD-CHARTER-013` | Codex may produce implementation Candidates only from `READY` workpacks with current traceability rows. |
| `SBC-RULE-005` | `DRD-CHARTER-013` | No workpack may write Constitution, control catalogs, references, tooling, or `.agents/skills` unless a later explicit governed Skill workpack allows the Skill path and Human Gate approves it. |
| `SBC-RULE-006` | `DRD-CHARTER-014` | Every implementation obligation must have a complete traceability row. |
| `SBC-RULE-007` | `DRD-CHARTER-014` | Code target maps must bind code targets to clause, rule, projection, validator, test, and acceptance command. |
| `SBC-RULE-008` | `DRD-CHARTER-014` | Test obligation matrices must include positive and negative evidence for meaningful rule failures. |
| `SBC-RULE-009` | `DRD-CHARTER-014` | Skills may reference locked specs but cannot become a second authority. |
| `SBC-RULE-010` | `DRD-CHARTER-014` | Invalidation must propagate to workpacks, traceability rows, Skill bindings, tests, and BUILD_LOCK evidence. |

## Applicable Spec Lock Rule

A spec part is applicable when one of its clauses, rules, projections, validator specs, schemas, examples, or implementation blueprint rows create an obligation for the code target.

The workpack generator must require all applicable spec locks, not just the nearest spec title.

Examples:

- A final compiler module requires `P1-SPEC-07-COMPILER-CONSERVATION` and stage lineage rules from `P1-SPEC-02-STAGE-ARTIFACTS`.
- A validation lock module requires `P1-SPEC-06-VALIDATION-LOCKS` and may require stage artifact lineage rules when validating stage dependencies.
- A thin CLI target requires foundation rules and traceability rules because CLI must stay thin and cannot hide business logic.

## Business Code Definition

Business code includes:

- Runtime behavior.
- Validators.
- Orchestrators.
- Compiler modules.
- Schemas used for canonical validation.
- Templates used as governed output inputs.
- CLI behavior that affects workflow or acceptance.
- Skill workflows that guide Codex implementation.

Tests alone do not authorize business code. Tests must trace to locked rules.

## Spec Repair Before Code

If implementation needs behavior not covered by locked specs, the workpack must stop.

Allowed next actions:

- Generate a spec repair Candidate.
- Split the workpack to isolate covered behavior.
- Route to Human Gate for scope decision.

Forbidden actions:

- Implement the missing behavior and backfill the spec later.
- Add acceptance tests for behavior not present in locked specs.
- Encode the missing behavior in a Skill, CLI, or template.

## Invalidation Rule

When a SPEC_LOCK, validator identity, schema hash, test obligation, Skill binding, or workpack dependency changes, all dependent traceability rows become suspect.

Dependent rows must be:

- Revalidated.
- Repaired.
- Marked unaffected with structured evidence.
- Or invalidated.

They cannot remain silently current.
