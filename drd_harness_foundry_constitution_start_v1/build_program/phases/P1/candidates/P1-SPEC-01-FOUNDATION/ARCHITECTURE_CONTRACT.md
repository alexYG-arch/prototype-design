# P1-SPEC-01 Foundation: Architecture Contract

## Scope

This contract defines the foundation architecture for the governed DRD Harness target in `repository/`. It owns the structural obligations needed before later stage, reasoning, interaction, presentation, validation, compiler, and workpack specifications can be locked.

Owned clauses:

- `DRD-CHARTER-012` explicit runtime.
- `DRD-CHARTER-016` no semantic YAML.

This contract does not implement runtime code, create locks, approve candidates, or generate domain business skills.

## Architectural Layers

The target Harness architecture is layered as follows:

| Layer | Path family | Responsibility |
|---|---|---|
| Kernel | `repository/src/drd_harness/kernel/` | Core datatypes for authority, runtime declarations, artifact identity, hashes, IDs, and errors. |
| Contracts | `repository/contracts/` and `repository/schemas/` | Locked human-readable contracts and JSON schemas promoted from approved specs. |
| Rules | `repository/src/drd_harness/rules/` | Deterministic and reviewable rules derived from locked contracts. |
| Validators | `repository/src/drd_harness/validators/` | Independent checks for specs, artifacts, graph closure, layout completeness, compiler conservation, and workpack scope. |
| Stages | `repository/src/drd_harness/stages/` | DRD-00 through DRD-06 stage definitions and stage input-output contracts. |
| Orchestrator | `repository/src/drd_harness/orchestrator/` | Stage execution lifecycle, review routing, promotion control, invalidation, and workpack generation after locks exist. |
| Compiler | `repository/src/drd_harness/compiler/` | Deterministic DRD-05 final document assembly from approved artifacts. |
| Runtimes | `repository/src/drd_harness/runtimes/` | Adapters that execute Python control duties and Codex candidate duties under declared boundaries. |
| Adapters | `repository/src/drd_harness/adapters/` | External file, process, and model-adapter boundaries with no product semantics hidden inside them. |
| CLI | `repository/src/drd_harness/cli/` | Thin command surface that delegates to kernel, orchestrator, compiler, and validators. |
| Templates | `repository/templates/` | Governed templates for manifests, review decisions, and operator-facing artifacts. |
| Tests | `repository/tests/` | Contract, validator, unit, integration, and regression tests. |

## Ownership Rules

The architecture must preserve authority boundaries:

1. Locked Constitution and promoted Contracts are authority sources.
2. Rules execute contracts and do not redefine them.
3. Validators check outputs independently from the workpack being implemented.
4. CLI commands delegate to governed modules and do not contain hidden business rules.
5. Adapters translate external calls and do not own product semantics.
6. `build_program/` remains a construction system and is not imported by final runtime code.
7. `references/` remains read-only and is not imported by final runtime code.

## Required Foundation Interfaces

P1 implementation must provide foundation interfaces for:

- Stable artifact IDs.
- Stable clause and rule IDs.
- Runtime declarations.
- Hash calculation and verification.
- Artifact manifest records.
- Directory and import boundary checks.
- Human semantic artifact format checks.
- Operational JSON artifact format checks.

These interfaces are foundation-level only. Domain-stage contracts, interaction graph rules, layout rules, compiler conservation, locks, and skill generation are specified in later P1 parts.

## Non-Goals

This architecture contract does not create a Figma renderer, Figma writer, business PRD parser, DRD semantic stage implementation, or final compiler. It only creates the architecture contract those later parts must follow.
