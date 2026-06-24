# P1-SPEC-08 Spec To Code Traceability Contract

## Purpose

This contract owns `DRD-CHARTER-014` and supports `DRD-CHARTER-013`.

Every implementation obligation must trace from approved specification authority to implementation evidence:

`Contract Clause -> Rule -> Projection -> Code Target -> Validator -> Test -> Acceptance Command`

No code target, validator, test, CLI behavior, template, or Skill may become canonical evidence unless this chain is complete and bound to current SPEC_LOCK inputs.

## Scope

This Candidate defines:

- Traceability row fields and minimum grain.
- Code target map requirements.
- Test obligation matrix requirements.
- Workpack index requirements.
- Skill binding requirements where Skills refer to locked specs.
- Validator requirements for traceability completeness.

This Candidate does not:

- Implement repository code.
- Create, edit, install, or approve Foundry Skills.
- Create SPEC_LOCK or BUILD_LOCK artifacts.
- Modify Constitution, control catalogs, references, tooling, or `.agents/skills`.

## Traceability Minimum Grain

The minimum traceability grain is one row per implementation obligation.

An implementation obligation is the smallest code-affecting duty that can be independently reviewed, validated, tested, and accepted. A workpack-level row is not enough when the workpack contains multiple code targets or rule families.

One module, class, or function may appear in multiple rows. That is expected when the same code target implements multiple duties such as lock gating, readiness state computation, forbidden path rejection, Skill drift detection, and invalidation propagation.

A traceability row is too broad if removing one part of its duty would not remove the whole row. It must be split when it combines any of:

- Lock gating and readiness state computation.
- Allowed path validation and forbidden path validation.
- Scope dispute routing and normal scope validation.
- Trace row field completeness and one-obligation grain validation.
- Validator binding and test obligation validation.
- Skill manifest completeness, Skill source hash drift, and Skill spec lock drift.
- Skill second-authority checks and CLI or template hidden-rule checks.
- Orphan code detection and invalidation propagation.

Each traceability row must include:

- `trace_row_id`
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
- `allowed_write_paths`
- `forbidden_write_paths`
- `dependency_edges`
- `invalidation_policy`

If a field is unknown, the row is not ready for implementation. It may remain a Candidate planning row, but it cannot be used to authorize code.

`implementation_duty` must be a single verb phrase that can fail independently, such as `block_workpack_without_required_spec_locks` or `reject_skill_source_hash_drift`. Generic duties such as `implement workpack system`, `validate traceability`, or `handle skills` are invalid.

## Required Traceability Evidence

| Evidence | Requirement |
|---|---|
| Contract clause | Must identify the clause or contract section that creates the obligation. |
| Rule | Must identify the rule that makes the obligation enforceable. |
| Projection | Must identify how upstream approved semantics become a structured downstream artifact. |
| Code target | Must identify an allowed repository path and expected module responsibility. |
| Validator | Must be independent enough to check the code target or output without becoming the implementation itself. |
| Test | Must prove the obligation, including negative cases when failure is meaningful. |
| Acceptance command | Must be runnable and scoped to the workpack's test family. |
| Lock dependency | Must bind the current SPEC_LOCK hash for every applicable spec part. |

## Traceability States

| State | Meaning |
|---|---|
| `PLANNED` | Row is a Candidate planning record and cannot authorize code. |
| `WAITING_SPEC_LOCK` | Required spec parts are not locked. |
| `READY_FOR_WORKPACK` | Required SPEC_LOCK refs are current and scope is valid. |
| `WORKPACK_CANDIDATE` | Codex may produce a scoped implementation Candidate. |
| `VALIDATED` | Required validators and tests passed for the Candidate. |
| `REVIEW_REQUIRED` | Human Gate must resolve scope, skill, or traceability issue. |
| `APPROVED_FOR_PROMOTION` | Human Gate approved the validated Candidate for Python-controlled promotion. |
| `INVALIDATED` | Upstream hash, spec lock, validator, test, skill, or workpack dependency changed. |

## No Orphan Code

Repository implementation code is orphan code if it lacks a current traceability row. Orphan code must not be promoted or locked.

Examples of orphan code:

- A helper module without a trace row and test obligation.
- A CLI command that hides business rules not present in locked specs.
- A validator that checks behavior not linked to a rule ID.
- A Skill that instructs Codex to create behavior beyond locked specs.

## Traceability Exception Policy

If a code target seems necessary but no locked spec creates the obligation, the workpack must stop with `REVIEW_REQUIRED`.

Human Gate may choose one of:

- Reject the code target.
- Request a spec repair Candidate.
- Split the workpack.
- Approve a traceability exception record with expiry and follow-up spec repair.

Traceability exceptions are not normal evidence for release. They must be visible to invalidation and lock readiness validators.
