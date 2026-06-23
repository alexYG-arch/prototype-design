# P1-SPEC-01 Foundation: Directory Contract

## Construction Root

The Foundry start package contains construction-time paths:

| Path | Role | Runtime import allowed |
|---|---|---|
| `constitution/` | Locked top-level authority. | No. |
| `control/` | Catalogs, schemas, and locks for Foundry control. | No direct runtime import from `repository/src/`. |
| `build_program/` | P1 through P4 construction program. | No. |
| `current_capsule/` | Active workpack execution context. | No. |
| `.agents/skills/` | Foundry skills for construction workflow. | No. |
| `references/` | Read-only prior-version references. | No. |
| `tooling/` | Construction-time deterministic tools. | No. |
| `repository/` | Target DRD Harness product. | Yes, within product package rules. |

## Target Repository Layout

The final Harness code lives under `repository/`:

| Path | Contract |
|---|---|
| `repository/src/drd_harness/kernel/` | Foundation datatypes and low-level deterministic utilities. |
| `repository/src/drd_harness/rules/` | Rule execution modules derived from locked contracts. |
| `repository/src/drd_harness/validators/` | Independent validators. |
| `repository/src/drd_harness/stages/` | Stage contracts and execution descriptors. |
| `repository/src/drd_harness/orchestrator/` | Run lifecycle, review, promotion, invalidation, and workpack orchestration. |
| `repository/src/drd_harness/compiler/` | Deterministic final DRD assembly. |
| `repository/src/drd_harness/runtimes/` | Python and Codex runtime adapters. |
| `repository/src/drd_harness/adapters/` | External system boundaries. |
| `repository/src/drd_harness/cli/` | Thin CLI delegation layer. |
| `repository/contracts/` | Promoted contracts. |
| `repository/schemas/` | Product runtime JSON schemas. |
| `repository/templates/` | Runtime artifact templates. |
| `repository/tests/` | Product tests. |

## Import Boundaries

The final runtime package under `repository/src/drd_harness/` must not import:

- `build_program`.
- `current_capsule`.
- `.agents`.
- `references`.
- construction `tooling`.

The final runtime package may load promoted contracts or schemas from inside `repository/` through explicit file APIs. It must not treat construction package files as runtime dependencies.

Runtime code may consume only repository-local promoted authority artifacts:

```text
repository/contracts/**
repository/schemas/**
repository/templates/**
```

Runtime code must not directly read `constitution/`, `control/`, `build_program/`, `current_capsule/`, `.agents/skills/`, `references/`, or construction `tooling/`. Promotion is the boundary that copies or generates approved authority material into `repository/`; runtime code consumes only the promoted copy.

## CLI Boundary

CLI modules must remain thin. They may parse arguments, call orchestrator or validator functions, render concise user output, and return process exit codes. They must not contain domain rules, stage semantics, graph algorithms, compiler conservation logic, or hidden review decisions.

CLI thinness must be mechanically checked. A valid CLI module may import and call approved facade modules, but must not define domain dataclasses, graph traversal algorithms, compiler conservation logic, review decision construction, promotion decisions, or rule evaluation tables.

## Reference Boundary

Prior-version references may inform migration during approved workpacks, but runtime code may not import or execute reference code. Any migrated behavior must be re-expressed through locked contracts, rules, validators, and tests.
