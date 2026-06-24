# P1-SPEC-08 Skills Workpack Examples

## Positive Example: Ready Implementation Workpack

```json
{
  "workpack_id": "P1-IMPLEMENT-08-SKILLS-WORKPACK-TRACEABILITY",
  "phase": "P1",
  "lane": "IMPLEMENT",
  "required_specs": [
    "P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY",
    "P1-SPEC-06-VALIDATION-LOCKS"
  ],
  "required_spec_locks": [
    {"spec_part": "P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY", "lock_hash": "spec08-lock"},
    {"spec_part": "P1-SPEC-06-VALIDATION-LOCKS", "lock_hash": "spec06-lock"}
  ],
  "code_targets": [
    "repository/src/drd_harness/orchestrator/workpacks.py"
  ],
  "validators": [
    "repository/src/drd_harness/validators/workpack_scope.py"
  ],
  "tests": [
    "repository/tests/workpacks/test_workpack_generation.py"
  ],
  "acceptance_commands": [
    "python -m pytest repository/tests/workpacks"
  ],
  "status": "READY"
}
```

Why this passes:

- Required spec locks are present.
- Code target, validator, test, and command are scoped.
- Workpack is ready but not self-approved.

## Positive Example: Skill Binding Manifest

```json
{
  "skill_id": "drd-harness-workpack-builder",
  "skill_version": "1.0.0",
  "skill_source_hash": "skill-source-hash",
  "bound_spec_locks": [
    {"spec_part": "P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY", "lock_hash": "spec08-lock"}
  ],
  "allowed_workpack_types": ["IMPLEMENT"],
  "allowed_write_paths": ["repository/src/drd_harness/orchestrator/**"],
  "forbidden_write_paths": ["constitution/**", "control/**", ".agents/skills/**", "references/**", "tooling/**"],
  "traceability_rows": ["TRACE-P1IMPL08-001"],
  "human_gate_required": true
}
```

Why this passes:

- The Skill binds to exact locked specs.
- It does not expand authority.
- It remains invalidatable when the Skill or spec lock changes.

## Negative Example: Code Before Spec Lock

```json
{
  "workpack_id": "P1-IMPLEMENT-05-PRESENTATION-LAYOUT",
  "required_specs": ["P1-SPEC-05-PRESENTATION-LAYOUT"],
  "required_spec_locks": [],
  "status": "READY"
}
```

Expected result: fail with `SW-CHECK-001`.

Reason:

- The workpack is marked ready without required SPEC_LOCK evidence.

## Negative Example: Skill Adds Rule

```markdown
When building layout validators, treat mobile z-axis metadata as optional unless it is easy to infer.
```

Expected result: fail with `SW-CHECK-014`.

Reason:

- The Skill relaxes a locked layout obligation.
- Skills cannot become a second authority.

## Negative Example: Orphan Code Target

```json
{
  "code_target": "repository/src/drd_harness/orchestrator/auto_fix.py",
  "traceability_rows": []
}
```

Expected result: fail with `SW-CHECK-015`.

Reason:

- The target has no clause, rule, projection, validator, test, or command mapping.

## Negative Example: Broad Workpack

```json
{
  "workpack_id": "P1-IMPLEMENT-ALL",
  "code_targets": [
    "repository/src/drd_harness/kernel/authority.py",
    "repository/src/drd_harness/compiler/final_drd.py",
    "repository/src/drd_harness/cli/main.py"
  ],
  "scope_reason": "Do all P1 implementation together."
}
```

Expected result: fail with `SW-CHECK-004` and `SW-CHECK-017`.

Reason:

- The workpack bundles unrelated implementation obligations.
- It prevents focused validation and review.

## Negative Example: CLI Hidden Business Rule

```python
if stage_id == "DRD-05":
    allow_unapproved_inputs = True
```

Expected result: fail with `SW-CHECK-018`.

Reason:

- CLI logic changes a business rule.
- Business rules must remain in locked specs, rule modules, validators, or schemas, not hidden in CLI glue.
