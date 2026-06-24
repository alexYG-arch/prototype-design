# P1-SPEC-08 Skills Workpack Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `spec_before_code_validator` | Ensures implementation workpacks cannot run until applicable spec outputs have current SPEC_LOCK refs. |
| `workpack_scope_validator` | Ensures allowed paths, forbidden paths, code targets, validators, tests, and commands match the workpack scope. |
| `traceability_map_validator` | Ensures code target map rows contain complete clause, rule, projection, target, validator, test, and command fields. |
| `test_obligation_matrix_validator` | Ensures each implementation obligation has positive and negative test obligations where meaningful. |
| `implementation_workpack_index_validator` | Ensures workpack index readiness state matches lock, dependency, and scope evidence. |
| `skill_binding_validator` | Ensures Skills bind exact spec lock hashes, source hashes, allowed scopes, and invalidation dependencies. |
| `skill_second_authority_validator` | Ensures Skill text does not create rules or scope beyond locked specs. |
| `traceability_invalidation_validator` | Ensures changed spec, skill, validator, test, or workpack hashes invalidate dependent traceability rows. |

## Checks

### SW-CHECK-001 Spec Lock Required Before Code

Fail if an implementation workpack is `READY`, `RUNNING`, `CANDIDATE`, `VALIDATED`, `APPROVED`, or `PROMOTED` without current SPEC_LOCK refs for every applicable spec part.

### SW-CHECK-002 Required Output Family Lock Coverage

Fail if the applicable Contract, Rule, Projection, or Validator Spec output is not covered by SPEC_LOCK.

### SW-CHECK-003 Complete Traceability Row

Fail if a traceability row lacks contract clause, source spec part, spec lock ref, contract section, rule ID, projection ID, implementation workpack ID, code target, validator, test, acceptance command, allowed paths, forbidden paths, or dependency edges.

### SW-CHECK-004 One Obligation Per Row

Fail if one row bundles multiple independent implementation obligations that require separate validators, tests, or code targets.

Fail if `implementation_duty` is generic, module-sized, workpack-sized, or combines duties with different failure modes.

Fail if one row maps to unrelated validator check IDs that can pass or fail independently.

### SW-CHECK-005 Code Target In Allowed Scope

Fail if a code target is outside allowed write paths or inside forbidden paths.

### SW-CHECK-006 Forbidden Path Change

Fail if a workpack attempts to modify Constitution, control catalogs, references, tooling, or `.agents/skills` without explicit later Skill workpack authority and Human Gate approval.

### SW-CHECK-007 Validator And Test Binding

Fail if a code target lacks an independent validator or test obligation.

### SW-CHECK-008 Negative Test Coverage

Fail if a meaningful rule failure lacks a negative test obligation.

### SW-CHECK-009 Acceptance Command Present

Fail if a workpack or trace row lacks a runnable acceptance command.

### SW-CHECK-010 Workpack Readiness State

Fail if workpack readiness state does not match lock state, dependency state, traceability completeness, and invalidation state.

### SW-CHECK-011 Skill Binding Manifest Completeness

Fail if a Skill used for business implementation lacks skill ID, version, source hash, bound SPEC_LOCK hashes, allowed workpack types, allowed commands, allowed write paths, forbidden write paths, traceability rows, validators, tests, and invalidation dependencies.

### SW-CHECK-012 Skill Source Hash Drift

Fail if the current Skill source hash differs from the binding manifest hash.

### SW-CHECK-013 Spec Lock Drift In Skill Binding

Fail if a Skill binding references a superseded or hash-drifted SPEC_LOCK without accepted unaffected evidence.

### SW-CHECK-014 Skill Becomes Second Authority

Fail if Skill text defines new rules, acceptance criteria, allowed paths, business behavior, validator relaxations, or promotion authority absent from locked specs.

### SW-CHECK-015 Orphan Code

Fail if repository code, template behavior, CLI behavior, validator behavior, or Skill behavior lacks a current traceability row.

### SW-CHECK-016 Invalidation Propagation

Fail if changed spec locks, validator identities, tests, Skill hashes, workpack scopes, or code target maps do not invalidate dependent rows.

### SW-CHECK-017 Scope Dispute Requires Human Gate

Fail if scope disputes, traceability exceptions, Skill introduction, or multi-spec workpack expansion proceed without Human Gate routing.

### SW-CHECK-018 No CLI Hidden Business Rules

Fail if CLI or templates contain business rules that should live in repository rule modules, validators, schemas, or locked specs.

### SW-CHECK-019 Trace Row To Test Matrix Parity

Fail if a `CODE_TARGET_MAP.json` trace row lacks exactly corresponding test obligation rows for its implementation duty and validator check IDs.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/workpacks/implementation_workpack.schema.json`
- `repository/schemas/workpacks/code_target_map.schema.json`
- `repository/schemas/workpacks/test_obligation_matrix.schema.json`
- `repository/schemas/workpacks/implementation_workpack_index.schema.json`
- `repository/schemas/workpacks/skill_binding_manifest.schema.json`
- `repository/schemas/workpacks/traceability_exception.schema.json`
- `repository/schemas/workpacks/workpack_readiness_report.schema.json`
