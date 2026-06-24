# P1-SPEC-08 Traceability Projections

## Projection Summary

| Projection ID | From | To | Purpose |
|---|---|---|---|
| `TRACE-PROJ-001` | Locked spec clauses, rules, projections, and validator specs | `CODE_TARGET_MAP.json` | Bind each implementation obligation to code target and validator evidence. |
| `TRACE-PROJ-002` | Code target map | `TEST_OBLIGATION_MATRIX.json` | Bind code targets and rules to positive and negative tests. |
| `TRACE-PROJ-003` | Spec locks, code target map, and test matrix | `IMPLEMENTATION_WORKPACK_INDEX.json` | Generate scoped workpack readiness records. |
| `TRACE-PROJ-004` | Skill source, SPEC_LOCK refs, workpack scopes | Skill binding manifest | Bind Skill versions to locked specs without authority drift. |
| `TRACE-PROJ-005` | Dependency graph edges | Invalidation records | Propagate upstream changes to workpacks, skills, tests, and locks. |

## Code Target Map Projection

`CODE_TARGET_MAP.json` must contain one row per implementation obligation.

Each row must project:

- `implementation_duty`
- `contract_clause_id`
- `source_spec_part`
- `spec_lock_ref`
- `contract_section_id`
- `rule_id`
- `projection_id`
- `implementation_workpack_id`
- `code_target`
- `class_or_function`
- `validator`
- `test`
- `acceptance_command`
- `validator_check_ids`
- `dependency_edges`

Rows may be `PLANNED` before SPEC_LOCK creation, but they cannot authorize implementation until current lock refs are filled.

The projection must split rows by validator-checkable duty. A row that maps to several unrelated `validator_check_ids` is allowed only when the checks prove the same single duty. Otherwise the row must be split and each split row must receive its own test obligation.

## Test Obligation Matrix Projection

`TEST_OBLIGATION_MATRIX.json` must project each trace row to test evidence.

Each obligation must specify:

- Positive fixture or behavior.
- Negative fixture or behavior.
- Required validator.
- Required test path.
- Acceptance command.
- Evidence artifact expected after test execution.

If a rule can fail in a meaningful way, the matrix must include a negative test. A happy-path-only matrix is not sufficient for validator, workpack, Skill, lock, or traceability rules.

## Implementation Workpack Index Projection

`IMPLEMENTATION_WORKPACK_INDEX.json` must project traceability rows into runnable workpack envelopes.

Each workpack row must identify:

- Required spec parts.
- Required spec locks.
- Allowed write paths.
- Forbidden write paths.
- Code target families.
- Validator families.
- Test families.
- Acceptance commands.
- Skill binding policy.
- Readiness state.

The index cannot change write scopes from the locked workpack map. Scope expansion requires Human Gate and spec repair.

## Skill Binding Projection

A Skill binding manifest projects:

- Skill source hash.
- Locked spec refs.
- Allowed workpack types.
- Allowed commands.
- Allowed write paths.
- Forbidden write paths.
- Traceability rows used by the Skill.
- Dependency edges for invalidation.

The Skill binding projection must fail if the Skill text introduces normative instructions not present in locked specs.

## Invalidation Projection

Traceability rows must emit dependency edges for:

- `SPEC_LOCK_DEPENDENCY`
- `WORKPACK_DEPENDENCY`
- `SKILL_DEPENDENCY`
- `VALIDATOR_DEPENDENCY`
- `TEST_EVIDENCE_DEPENDENCY`
- `BUILD_LOCK_DEPENDENCY`

When a dependency hash changes, dependent rows must become `INVALIDATED` unless structured unaffected evidence is accepted under validation lock rules.
