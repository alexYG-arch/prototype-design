# P1-SPEC-01 Foundation Validator Spec

## Validator Family

`foundation_validator` checks foundation architecture, runtime declarations, directory boundaries, output formats, and CLI thinness.

## Inputs

- Foundation contracts.
- Runtime declaration records.
- Artifact manifests.
- Workpack descriptors.
- Target repository source tree.
- Target repository templates and schemas.

## Checks

| Check ID | Rule IDs | Deterministic | Failure code | Description |
|---|---|---:|---|---|
| `FND-CHECK-001` | `FND-RULE-001` | Yes | `FND001` | Runtime declaration includes primary runtime, duties, validator, gate, authority inputs, write scope, and forbidden scope. |
| `FND-CHECK-002` | `FND-RULE-002` | Yes | `FND002` | Runtime responsibilities do not assign deterministic control to Codex or semantic approval to Python. |
| `FND-CHECK-003` | `FND-RULE-003` | Yes | `FND003` | Candidate status is not represented as approved, promoted, locked, or sealed without required review and promotion evidence. |
| `FND-CHECK-004` | `FND-RULE-004`, `FND-RULE-005` | Yes | `FND004` | Artifact format matches authority role: Markdown for human semantics, JSON for operational control. |
| `FND-CHECK-005` | `FND-RULE-006` | Yes | `FND005` | Semantic or mixed semantic-operational YAML is absent. |
| `FND-CHECK-006` | `FND-RULE-007` | Reviewable plus deterministic anchors | `FND006` | Layout JSON indexes do not replace required natural-language layout text. |
| `FND-CHECK-007` | `FND-RULE-008` | Yes | `FND007` | Runtime source files do not import construction-time package paths. |
| `FND-CHECK-008` | `FND-RULE-009`, `FND-RULE-012` | Hybrid | `FND008` | CLI modules delegate and do not embed domain rules, graph algorithms, compiler conservation logic, promotion decisions, or review decision constructors. |
| `FND-CHECK-009` | `FND-RULE-010` | Yes | `FND009` | Runtime declaration records conform to `repository/schemas/runtime_declaration.schema.json`. |
| `FND-CHECK-010` | `FND-RULE-011` | Yes | `FND010` | Runtime code reads only promoted repository-local contracts, schemas, and templates, and never construction authority files directly. |

## Validator Output

The validator emits JSON:

```json
{
  "validator": "foundation_validator",
  "status": "PASS",
  "checked_rules": ["FND-RULE-001"],
  "findings": []
}
```

Failure output uses:

```json
{
  "validator": "foundation_validator",
  "status": "FAIL",
  "findings": [
    {
      "code": "FND001",
      "path": "example/path",
      "message": "Runtime declaration is missing human_gate."
    }
  ]
}
```

## Independence Rule

An implementation workpack may add or modify runtime declarations and CLI code only when the applicable validator spec is already locked. The same implementation workpack must not weaken the locked validator or its golden tests.

CLI thinness validation must include at least one static check over `repository/src/drd_harness/cli/**`. A smoke test alone is insufficient evidence for `FND-CHECK-008`.
