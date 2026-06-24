# P1-SPEC-08 Workpack Generation Contract

## Purpose

Implementation workpacks are generated task envelopes. They do not create authority. They carry locked authority into a scoped Codex run.

This contract defines when a workpack may be generated, what it must contain, and how it remains traceable to locked specs.

## Workpack Generation Preconditions

An implementation workpack may enter `READY` only when:

- Every required spec part has a current SPEC_LOCK.
- Required traceability rows are complete.
- Allowed and forbidden write paths are explicit.
- Code targets are listed.
- Validators and tests are listed.
- Acceptance commands are listed.
- Dependency edges to specs, validators, tests, skills, and upstream workpacks are typed.
- No required upstream evidence is invalidated.

If any precondition is missing, the workpack remains `WAITING_UPSTREAM_LOCK` or `REVIEW_REQUIRED`.

## Required Workpack Fields

Every implementation workpack record must include:

- `workpack_id`
- `phase`
- `lane`
- `objective`
- `required_specs`
- `required_spec_locks`
- `traceability_rows`
- `allowed_write_paths`
- `forbidden_write_paths`
- `code_targets`
- `validators`
- `tests`
- `acceptance_commands`
- `skill_bindings`
- `dependency_edges`
- `status`
- `review_policy`
- `promotion_policy`
- `invalidation_policy`

## Workpack Scope Rules

Workpack scope must be narrow enough for review and validation.

A workpack must not:

- Mix unrelated spec families without a declared reason.
- Write outside allowed paths.
- Modify forbidden paths.
- Hide business rules in CLI, templates, scripts, tests, or Skills.
- Implement behavior not covered by traceability rows.
- Generate or modify Skills unless the workpack type explicitly allows Skill generation and Human Gate approves it.

## Workpack Status Model

| Status | Meaning |
|---|---|
| `PLANNED` | Candidate planning record only. |
| `WAITING_UPSTREAM_LOCK` | Required SPEC_LOCK or dependency evidence is missing. |
| `READY` | All generation preconditions are satisfied. |
| `RUNNING` | Codex is producing a scoped Candidate. |
| `CANDIDATE` | Implementation output exists but is not validated or approved. |
| `VALIDATED` | Required validators and tests passed. |
| `REVIEW_REQUIRED` | Human Gate must decide a scope, traceability, skill, or exception issue. |
| `APPROVED` | Human Gate approved the validated Candidate. |
| `PROMOTED` | Python-controlled promotion completed. |
| `INVALIDATED` | Upstream evidence changed or dependency became stale. |

## Generated Workpack Index

`IMPLEMENTATION_WORKPACK_INDEX.json` must list implementation workpacks with:

- Required spec parts.
- Required SPEC_LOCK refs.
- Current readiness state.
- Code target families.
- Validator families.
- Test families.
- Acceptance commands.
- Forbidden path policy.
- Skill binding policy.
- Invalidation dependencies.

The index is operational planning evidence. It does not approve or promote implementation.

## Scope Dispute Policy

If a code target, validator, test, or Skill binding does not clearly fit the workpack scope, the generator must stop and emit `REVIEW_REQUIRED`.

Human Gate decides whether to:

- Split the workpack.
- Add traceability rows through a spec repair Candidate.
- Reject the target.
- Approve a temporary traceability exception.

## Implementation Candidate Boundary

Codex may generate implementation Candidates only after the workpack is `READY`.

Codex must not:

- Declare a workpack complete without tests.
- Self-approve its Candidate.
- Mark BUILD_LOCK readiness.
- Change locked spec artifacts.
- Change Skill source files unless explicitly authorized by a Skill workpack and Human Gate.
