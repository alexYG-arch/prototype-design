# P1-SPEC-08 Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/orchestrator/workpacks.py` | Generate and evaluate implementation workpack envelopes from locked specs and traceability rows. | `repository/tests/workpacks/test_workpack_generation.py` |
| `repository/src/drd_harness/orchestrator/traceability.py` | Build and query traceability rows, code target maps, test matrices, and dependency edges. | `repository/tests/workpacks/test_code_target_map.py` |
| `repository/src/drd_harness/validators/workpack_scope.py` | Validate workpack readiness, allowed paths, forbidden paths, Skill bindings, and scope disputes. | `repository/tests/workpacks/test_workpack_generation.py` |
| `repository/src/drd_harness/validators/traceability.py` | Validate traceability completeness, orphan code, test obligations, and invalidation propagation. | `repository/tests/workpacks/test_code_target_map.py` |
| `repository/schemas/workpacks/implementation_workpack.schema.json` | Implementation workpack schema. | `repository/tests/workpacks/test_workpack_generation.py` |
| `repository/schemas/workpacks/code_target_map.schema.json` | Code target traceability row schema. | `repository/tests/workpacks/test_code_target_map.py` |
| `repository/schemas/workpacks/test_obligation_matrix.schema.json` | Test obligation matrix schema. | `repository/tests/workpacks/test_test_obligation_matrix.py` |
| `repository/schemas/workpacks/implementation_workpack_index.schema.json` | Workpack index schema. | `repository/tests/workpacks/test_workpack_generation.py` |
| `repository/schemas/workpacks/skill_binding_manifest.schema.json` | Skill binding manifest schema. | `repository/tests/workpacks/test_skill_version_binding.py` |
| `repository/schemas/workpacks/traceability_exception.schema.json` | Human Gate traceability exception schema. | `repository/tests/workpacks/test_code_target_map.py` |
| `repository/schemas/workpacks/workpack_readiness_report.schema.json` | Workpack readiness validation report schema. | `repository/tests/workpacks/test_workpack_generation.py` |

## Implementation Rules

### IMPL-SW-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-SW-002 Generators Do Not Approve

Workpack and traceability generators may emit Candidate workpack records. They cannot approve, promote, or lock implementation output.

### IMPL-SW-003 Traceability Is Structured

Traceability must be machine-readable. Markdown explanation may help reviewers, but lock readiness depends on structured rows.

### IMPL-SW-004 Skills Are Bound Inputs

Skill usage must be recorded as hash-bound input evidence. A Skill cannot create rule authority.

### IMPL-SW-005 Scope Validation Is Mandatory

Every generated workpack must be validated for allowed paths, forbidden paths, required locks, tests, commands, Skill bindings, and invalidation dependencies before Codex runs implementation.

## Fixture Coverage

Tests must include positive and negative fixtures for:

- Workpack blocked before SPEC_LOCK.
- Workpack ready with current SPEC_LOCK refs.
- Missing Contract, Rule, Projection, or Validator Spec lock.
- Complete traceability row.
- Missing clause, rule, projection, code target, validator, test, or command.
- Bundled multi-obligation row rejection.
- Generic module-sized row rejection.
- Trace row to test matrix parity.
- Code target outside allowed paths.
- Forbidden path change.
- Positive and negative test obligation matrix.
- Workpack readiness state mismatch.
- Skill binding manifest complete.
- Skill source hash drift.
- Skill spec lock drift.
- Skill text creating second authority.
- Orphan code target.
- Invalidation propagation to workpack, skill, test, and build evidence.
- CLI hidden business rule rejection.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/workpacks
```

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-013` | Spec before code, Skill lock gate, workpack readiness | `orchestrator/workpacks.py`, `validators/workpack_scope.py`, `implementation_workpack.schema.json`, `implementation_workpack_index.schema.json` | `SW-CHECK-001`, `SW-CHECK-002`, `SW-CHECK-005`, `SW-CHECK-006`, `SW-CHECK-010`, `SW-CHECK-017` |
| `DRD-CHARTER-014` | Traceability rows, code target map, test obligation matrix, orphan code | `orchestrator/traceability.py`, `validators/traceability.py`, `code_target_map.schema.json`, `test_obligation_matrix.schema.json` | `SW-CHECK-003`, `SW-CHECK-004`, `SW-CHECK-007`, `SW-CHECK-008`, `SW-CHECK-009`, `SW-CHECK-015`, `SW-CHECK-016`, `SW-CHECK-018`, `SW-CHECK-019` |
| `DRD-CHARTER-013` and `DRD-CHARTER-014` | Skill version binding and no second authority | `validators/workpack_scope.py`, `validators/traceability.py`, `skill_binding_manifest.schema.json` | `SW-CHECK-011`, `SW-CHECK-012`, `SW-CHECK-013`, `SW-CHECK-014` |
