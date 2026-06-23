# P1-SPEC-01 Foundation Projections

## Projection Index

| Projection ID | From | To | Purpose |
|---|---|---|---|
| `FND-PROJ-001` | Constitution authority model | Runtime declaration schema | Ensures every executable unit states authority, duties, validator, gate, and scope. |
| `FND-PROJ-002` | Directory contract | Import boundary validator | Ensures final runtime code is independent from construction-time package paths. |
| `FND-PROJ-003` | Output format contract | Artifact manifest schema | Ensures Markdown and JSON artifacts are classified by authority role. |
| `FND-PROJ-004` | No semantic YAML rule | Format validator | Rejects YAML as a semantic or mixed semantic-operational artifact format. |
| `FND-PROJ-005` | Runtime responsibility table | Workpack preflight | Ensures a workpack cannot assign promotion, approval, or lock authority to Codex. |
| `FND-PROJ-006` | CLI boundary | CLI smoke, import, and AST thinness tests | Ensures CLI delegates to governed modules and does not embed domain logic. |
| `FND-PROJ-007` | Runtime declaration contract | Runtime declaration schema | Promotes `repository/schemas/runtime_declaration.schema.json` as the canonical shape for runtime declarations. |
| `FND-PROJ-008` | Promoted authority boundary | Runtime file-access validator | Ensures runtime code reads only repository-local promoted contracts, schemas, and templates. |

## Projection Details

### FND-PROJ-001 Runtime Declaration

Each Stage or Workpack produces or consumes a runtime declaration containing:

- Primary runtime.
- Python duties.
- Codex duties.
- Validator.
- Human Gate.
- Authority inputs.
- Write scope.
- Forbidden scope.

The projection is valid only when these fields are explicit and non-empty for executable work.

### FND-PROJ-002 Directory Isolation

The directory contract projects to a validator that scans runtime source imports. Any import from construction-time paths fails validation.

### FND-PROJ-003 Format Manifest

The output format contract projects to artifact manifest records with:

- Artifact ID.
- Path.
- Format.
- Authority role.
- Source hash.
- Validation status.

### FND-PROJ-004 YAML Rejection

Any semantic artifact path ending in `.yaml` or `.yml` fails unless the artifact is a third-party external input preserved only as source evidence and not adopted as a Harness semantic or operational artifact.

### FND-PROJ-005 Workpack Authority Check

Workpack preflight rejects any Candidate workpack that grants Codex authority to approve, promote, seal, or mutate locked artifacts.

### FND-PROJ-006 CLI Delegation

CLI modules project command names to orchestrator or validator entrypoints. If a CLI command embeds domain rules directly, the projection is invalid.

The projection is checked by both command smoke tests and static checks that reject CLI-local domain dataclasses, graph traversal functions, compiler conservation logic, review decision constructors, promotion decisions, and rule evaluation tables.

### FND-PROJ-007 Runtime Declaration Schema

The runtime declaration contract projects to `repository/schemas/runtime_declaration.schema.json`. Runtime declaration records are valid only when they conform to this promoted schema.

### FND-PROJ-008 Promoted Authority Boundary

Construction authority files project into promoted repository-local contracts, schemas, and templates. Runtime code may read the promoted files but must not read `constitution/` or `control/` directly.
