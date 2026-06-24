# P1-SPEC-06 Validation Contract

## Purpose

This Candidate defines validation duties for Candidate artifacts before review, promotion, lock creation, and downstream use.

It owns:

- `DRD-CHARTER-010` Candidate only.
- `DRD-CHARTER-015` Invalidation.

## Validation Authority

Validation is independent from Candidate generation. Codex may generate or repair Candidates, but it must not validate by declaration, approve itself, promote itself, or create canonical authority.

Python validators may:

- Check output completeness.
- Check schema validity.
- Check scope and forbidden path boundaries.
- Check source hash binding.
- Check upstream review or lock binding.
- Check Candidate-only state.
- Check downstream invalidation requirements.
- Report pass, fail, blockers, and invalidation effects.

Python validators must not:

- Add missing semantic content to make a Candidate pass.
- Promote a Candidate without Human Gate approval.
- Seal a lock when review state is not ready.
- Rewrite source, constitution, control, or approved upstream artifacts.

## Validation Layers

| Layer | Purpose |
|---|---|
| `preflight` | Verifies required source files, allowed paths, forbidden paths, and current workpack context before generation. |
| `candidate_shape` | Verifies required outputs, manifest fields, JSON syntax, and placeholder absence. |
| `scope_postflight` | Verifies generated changes stayed in allowed Candidate scope. |
| `semantic_validator` | Verifies spec-specific required tokens, schemas, projections, and validator obligations. |
| `review_binding` | Verifies Human Gate decision binds to the reviewed Candidate subject hash. |
| `lock_readiness` | Verifies approved Candidate can be included in SPEC_LOCK or BUILD_LOCK inputs. |
| `invalidation_check` | Verifies downstream dependencies are invalidated when locked upstream hashes change. |

## Validator Identity

Every validation result must identify the validator itself, not only the command that was run.

Required identity fields:

| Field | Requirement |
|---|---|
| `validator_id` | Stable validator ID. |
| `validator_kind` | Python module, schema, CLI command, or external deterministic checker. |
| `validator_version` | Semantic version, git commit, package version, or declared equivalent. |
| `validator_code_hash` | Hash of validator code, schema, or executable definition used for the result. |
| `schema_hashes` | Hashes of schemas used by the validator. |
| `runtime_identity` | Python version, package environment, or runtime declaration needed to reproduce the result. |
| `result_hash` | Hash of validator output, findings, and checked subject hash. |

## Contract Clauses

### VALIDATION-CONTRACT-001 Candidate State Is Default

All Codex outputs remain `CANDIDATE` until Human Gate approval and Python promotion checks complete.

### VALIDATION-CONTRACT-002 Validator Independence

The validator that approves a Candidate must be independent from the generation action being checked. A Candidate cannot pass because the generating agent claims it passes.

### VALIDATION-CONTRACT-003 No Semantic Repair During Validation

Validators may produce findings and repair requirements, but must not silently edit semantic artifacts to satisfy checks.

### VALIDATION-CONTRACT-004 Scope Enforcement

Postflight validation must reject changes outside the current workpack allowed paths and must report forbidden path changes.

### VALIDATION-CONTRACT-005 Hash Binding

Validation results, review decisions, lock readiness, and invalidation state must bind to concrete hashes of reviewed outputs and upstream dependencies.

Validator identity must also be hash-bound. If validator code or schema changes, prior validation results cannot be reused without explicit compatibility proof or revalidation.

### VALIDATION-CONTRACT-006 Failure Is Blocking

Failed validation blocks review approval, promotion, lock creation, and downstream consumption until repaired and revalidated.
