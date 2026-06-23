# P1-SPEC-00 Candidate: P1 Phase Plan

## Scope

This Candidate plans P1 only. It creates the ownership map, Spec part map, Implementation Workpack map, acceptance matrix, and assembly seed needed to produce locked P1 specifications before any Harness business code is implemented.

The active Workpack is `P1-SPEC-00`. The allowed write scope is `build_program/phases/P1/candidates/P1-SPEC-00/` and `current_capsule/outputs/`. This Candidate does not modify the sealed Constitution, control catalogs, Foundry skills, Program Driver, repository skeleton, references, or tooling.

## Authority And Runtime Discipline

P1 keeps three runtime lanes explicit:

| Lane | Authority | P1 responsibility |
|---|---|---|
| Python Runtime | deterministic control plane | Snapshot, hash binding, JSON schema checks, graph validation, postflight validation, lock assembly, compilation conservation checks. |
| Codex Runtime | candidate semantic reasoning | Natural-language contracts, deductive rule articulation, projection descriptions, examples, implementation blueprint candidates. |
| Human Gate | semantic approval | Scope disputes, inductive candidates, Review A, Review B, final promotion decisions, and any product expansion question. |

Codex produces Candidate artifacts only. Python performs deterministic validation and promotion. Human review remains the authority for high-leverage semantic decisions.

## P1 Objectives

P1 freezes enough specification material to let later P1 Implementation Workpacks build the governed DRD Harness in `repository/` without relying on chat context.

P1 Spec must produce these families for each owned clause group:

1. Contract: input, output, ownership, and boundary obligations.
2. Rule: deterministic or reviewable judgment rules.
3. Projection: how upstream semantics produce downstream artifacts.
4. Validator Spec: independent checks and failure modes.
5. Examples: positive, negative, and boundary examples.
6. Implementation Blueprint: code targets, tests, acceptance commands, and traceability.

## Spec Part Plan

| Spec part | Purpose | Primary clauses | Required output families |
|---|---|---|---|
| `P1-SPEC-01-FOUNDATION` | Architecture, authority, runtime, directory, and output format contracts. | `DRD-CHARTER-012`, `DRD-CHARTER-016` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-02-STAGE-ARTIFACTS` | Source permanence, ordered dependency, DRD-00 through DRD-06 stage contracts, artifact lineage, and hash binding. | `DRD-CHARTER-001`, `DRD-CHARTER-002` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-03-REASONING-ADOPTION` | Deduction-first inference, PRD element validation, element derivation, and product expansion boundaries. | `DRD-CHARTER-003`, `DRD-CHARTER-004`, `DRD-CHARTER-007`, `DRD-CHARTER-018`, `RD-RULE-001` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-04-INTERACTION-CLOSURE` | Interaction graph model, clickable inventory, Reaction rules, handoff behavior, failure recovery, async state, and terminal validation. | `DRD-CHARTER-005`, `RD-RULE-002`, `RD-RULE-003`, `RD-RULE-004`, `RD-RULE-005`, `RD-RULE-006` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-05-PRESENTATION-LAYOUT` | Information presentation consistency, shared component discipline, natural-language layout, Figma compatibility, and content growth handling. | `DRD-CHARTER-006`, `DRD-CHARTER-008`, `DRD-CHARTER-009`, `DRD-CHARTER-017`, `RD-RULE-007`, `RD-RULE-008` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-06-VALIDATION-LOCKS` | Candidate-only workflow, review, promotion, validator independence, lock models, and invalidation. | `DRD-CHARTER-010`, `DRD-CHARTER-015` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-07-COMPILER-CONSERVATION` | Deterministic DRD-05 compilation, compiler input boundaries, output conservation, and final DRD assembly checks. | `DRD-CHARTER-011` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |
| `P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY` | Spec-before-code, spec-to-code traceability, skill version binding, and implementation workpack generation. | `DRD-CHARTER-013`, `DRD-CHARTER-014` | Contract, Rule, Projection, Validator Spec, Examples, Implementation Blueprint. |

## Assembly Order

1. Generate `P1-SPEC-01-FOUNDATION` so every later part inherits runtime, authority, directory, and format boundaries.
2. Generate `P1-SPEC-02-STAGE-ARTIFACTS` so all stage artifacts and hash dependencies have canonical IDs.
3. Generate `P1-SPEC-03-REASONING-ADOPTION` so semantic inference and PRD element adoption are governed before interaction or layout expansion.
4. Generate `P1-SPEC-04-INTERACTION-CLOSURE` so page, state, overlay, handoff, and Reaction graph rules are complete before Review A.
5. Generate `P1-SPEC-05-PRESENTATION-LAYOUT` so shared patterns, information presentation, layout composition, and Figma compatibility are complete before Review B.
6. Generate `P1-SPEC-06-VALIDATION-LOCKS` so validator independence, review, promotion, lock state, and invalidation are governed before any lock is assembled.
7. Generate `P1-SPEC-07-COMPILER-CONSERVATION` so DRD-05 deterministic compilation is separated from validator and workpack concerns.
8. Generate `P1-SPEC-08-SKILLS-WORKPACK-TRACEABILITY` so skill binding and implementation workpack generation are traceable to locked specs.
9. Run P1 phase validation, produce a candidate `SPEC_LOCK`, and wait for Human Gate rather than self-approving.

## Implementation Expansion Model

P1 Implementation Workpacks must be generated from the locked P1 Spec, not from this planning Candidate alone. Each Implementation Workpack binds a SPEC_LOCK hash, exact Contract and Rule IDs, allowed write paths, forbidden write paths, code targets, validators, tests, examples, and acceptance commands.

The first implementation wave should build the control-plane kernel, contract models, artifact lineage, validator suite, and thin CLI. The second wave should build domain validators for reasoning, PRD element adoption, interaction closure, shared component consistency, information presentation consistency, natural-language layout completeness, and compiler conservation. The final P1 implementation wave should add integration tests, example fixtures, and lock-generation utilities.

## Gates

| Gate | Trigger | Owner | Required evidence |
|---|---|---|---|
| Spec Validator | Each Spec part Candidate | Python Runtime | Required IDs, clause coverage, output families, examples, and validator specs are present. |
| Workpack Preflight | Each generated Implementation Workpack | Python Runtime | SPEC_LOCK hash, read scope, write scope, acceptance commands, and forbidden paths are valid. |
| Review A | After interaction contract material is complete | Human Gate | Task, page, state, overlay, handoff, clickable element, and interaction-edge semantics are reviewable. |
| Review B | After presentation and layout contracts are complete | Human Gate | Page elements, shared components, presentation modes, layout descriptions, and Figma compatibility are reviewable. |
| P1 Phase Gate | After all P1 Spec parts and generated maps pass | Python Runtime plus Human Gate | Full clause coverage, traceability, validator independence, examples, and assembly inputs are complete. |

## Non-Goals

This Candidate does not create a SPEC_LOCK, BUILD_LOCK, Release Lock, business Runtime Domain Skill, Figma renderer, Figma writer, or DRD Harness business implementation. Those require later approved workpacks.
