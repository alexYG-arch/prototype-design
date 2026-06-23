# P1-SPEC-01 Foundation Implementation Blueprint

## Scope

This blueprint informs later implementation workpacks. It does not implement code.

Primary implementation workpacks:

- `P1-IMPLEMENT-01-FOUNDATION-KERNEL`
- `P1-IMPLEMENT-09-THIN-CLI-TEMPLATES-DOCS`

## Code Target Map

| Contract clause | Rule | Projection | Code target | Validator | Test | Acceptance command |
|---|---|---|---|---|---|---|
| `DRD-CHARTER-012` | `FND-RULE-001` | `FND-PROJ-001` | `repository/src/drd_harness/kernel/runtime.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_authority_runtime.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-012` | `FND-RULE-002` | `FND-PROJ-005` | `repository/src/drd_harness/kernel/authority.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_authority_runtime.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-012` | `FND-RULE-008` | `FND-PROJ-002` | `repository/src/drd_harness/kernel/import_boundaries.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_import_boundaries.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-012` | `FND-RULE-010` | `FND-PROJ-007` | `repository/schemas/runtime_declaration.schema.json` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_runtime_declaration_schema.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-012` | `FND-RULE-011` | `FND-PROJ-008` | `repository/src/drd_harness/kernel/promoted_authority.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_promoted_authority_boundary.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-016` | `FND-RULE-004` | `FND-PROJ-003` | `repository/src/drd_harness/kernel/artifacts.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_artifact_manifest_schema.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-016` | `FND-RULE-005` | `FND-PROJ-003` | `repository/schemas/artifact_manifest.schema.json` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_artifact_manifest_schema.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-016` | `FND-RULE-006` | `FND-PROJ-004` | `repository/src/drd_harness/validators/foundation.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/kernel/test_output_format_policy.py` | `python -m pytest repository/tests/kernel` |
| `DRD-CHARTER-012` | `FND-RULE-009` | `FND-PROJ-006` | `repository/src/drd_harness/cli/main.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/integration/test_cli_smoke.py` | `python -m pytest repository/tests/integration` |
| `DRD-CHARTER-012` | `FND-RULE-012` | `FND-PROJ-006` | `repository/src/drd_harness/cli/main.py` | `repository/src/drd_harness/validators/foundation.py` | `repository/tests/integration/test_cli_thinness.py` | `python -m pytest repository/tests/integration` |

## Required Implementation Artifacts

`P1-IMPLEMENT-01-FOUNDATION-KERNEL` must produce:

- Runtime declaration datatypes.
- Authority role datatypes.
- Artifact manifest datatypes.
- Hash utilities.
- Runtime declaration schema.
- Promoted authority boundary utilities.
- Directory and import boundary utilities.
- Foundation validator.
- Kernel tests.

`P1-IMPLEMENT-09-THIN-CLI-TEMPLATES-DOCS` must produce:

- Thin CLI entrypoint.
- Review decision template.
- Stage manifest template.
- Architecture documentation.
- CLI smoke tests.
- CLI thinness static tests.

## Implementation Restrictions

Implementation workpacks must not:

- Modify Constitution files.
- Modify control catalogs.
- Modify Foundry skills.
- Import `build_program`, `current_capsule`, `.agents`, `references`, or construction `tooling` from final runtime code.
- Read `constitution/` or `control/` directly from final runtime code.
- Add business stage rules not covered by locked specs.
- Hide semantic decisions in CLI parsing code.
