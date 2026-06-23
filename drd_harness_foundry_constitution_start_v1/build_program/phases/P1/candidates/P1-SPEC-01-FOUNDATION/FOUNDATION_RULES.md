# P1-SPEC-01 Foundation Rules

## Rule Index

| Rule ID | Clause | Rule |
|---|---|---|
| `FND-RULE-001` | `DRD-CHARTER-012` | Every Stage and Workpack must declare primary runtime, Python duties, Codex duties, validator, Human Gate, authority inputs, write scope, and forbidden scope. |
| `FND-RULE-002` | `DRD-CHARTER-012` | Python Runtime owns deterministic control duties; Codex Runtime owns Candidate semantic duties; Human Gate owns semantic approval. |
| `FND-RULE-003` | `DRD-CHARTER-012` | Codex output cannot become canonical without deterministic validation and required Human Gate decision. |
| `FND-RULE-004` | `DRD-CHARTER-016` | Human semantic artifacts must be Markdown. |
| `FND-RULE-005` | `DRD-CHARTER-016` | Operational control artifacts and indexes must be JSON. |
| `FND-RULE-006` | `DRD-CHARTER-016` | Semantic YAML and mixed semantic-operational YAML are prohibited. |
| `FND-RULE-007` | `DRD-CHARTER-016` | JSON may index layout semantics but must not replace natural-language layout authority. |
| `FND-RULE-008` | `DRD-CHARTER-012` | Final runtime code must not import construction-time `build_program`, `current_capsule`, `.agents`, `references`, or `tooling` paths. |
| `FND-RULE-009` | `DRD-CHARTER-012` | CLI code must remain a delegation layer and must not hide domain rules or semantic decisions. |
| `FND-RULE-010` | `DRD-CHARTER-012` | Runtime declarations must conform to `repository/schemas/runtime_declaration.schema.json`. |
| `FND-RULE-011` | `DRD-CHARTER-012` | Final runtime code may read only promoted repository-local contracts, schemas, and templates, never construction authority files directly. |
| `FND-RULE-012` | `DRD-CHARTER-012` | CLI thinness must be mechanically checked through static structure or import analysis, not only through command smoke tests. |

## Enforcement Notes

`FND-RULE-001` through `FND-RULE-003` are enforced by runtime declaration validators and workpack preflight checks.

`FND-RULE-004` through `FND-RULE-007` are enforced by output format validators and artifact manifest checks.

`FND-RULE-008` and `FND-RULE-011` are enforced by import and file-access boundary checks.

`FND-RULE-009` and `FND-RULE-012` are enforced by CLI thinness tests that inspect CLI module structure and allowed imports in addition to smoke tests.

`FND-RULE-010` is enforced by JSON schema validation of runtime declaration records.
