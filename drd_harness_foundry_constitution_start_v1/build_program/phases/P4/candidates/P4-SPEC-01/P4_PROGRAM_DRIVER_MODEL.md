# P4 Program Driver Model

## Model Summary

The P4 program driver coordinates locked harness capabilities through a deterministic DAG. It does not own product semantics. It schedules existing stages, records command state, evaluates review gates, and stops at lock or Human Gate boundaries.

## Node Types

| Node Type | Purpose | May Mutate |
| --- | --- | --- |
| `INPUT_ADAPTER` | Normalize raw input into source evidence | Adapter output directory only |
| `SOURCE_INTAKE` | Feed source records into locked P3 source intake | Candidate or run output only |
| `STAGE_EXECUTION` | Execute an approved harness stage | Declared output path only |
| `CANDIDATE_VALIDATION` | Run candidate and review binding checks | Validation report only |
| `HUMAN_REVIEW_GATE` | Stop for review decision | Review decision only after human action |
| `LOCK_GATE` | Stop before spec, build, or release lock creation | No mutation |
| `RELEASE_REQUEST` | Build release readiness packet | Release candidate output only |

## Edge Types

| Edge Type | Meaning |
| --- | --- |
| `SOURCE_TO_STAGE` | Source evidence feeds a stage |
| `STAGE_TO_STAGE` | A stage consumes prior stage artifacts |
| `CANDIDATE_TO_REVIEW` | Candidate outputs require review target or decision |
| `REVIEW_TO_LOCK` | Approved review decision is a required lock input |
| `LOCK_TO_PHASE` | Approved build lock authorizes next phase planning |
| `INVALIDATION` | Changed input invalidates dependent nodes |
| `RESUME` | Prior run state permits replay or skip decision |

## Required Driver Records

Each run must record:

- `run_id`
- `program_id`
- `driver_version`
- `invoked_command`
- `adapter_id`
- `source_refs`
- `upstream_lock_refs`
- `dag_nodes`
- `dag_edges`
- `execution_plan`
- `written_paths`
- `review_gate_refs`
- `lock_gate_refs`
- `status`
- `findings`

## Determinism Rules

1. Node ids must be stable across replays with the same input and lock set.
2. Execution order must be derived from topological order, not filesystem order.
3. Command output must sort paths and findings deterministically.
4. A node cannot read a path unless that path is declared in the run input, upstream lock, or prior node output.
5. A node cannot write outside its declared output path.
6. A failed node must record failure type, failed command, exit code, and recovery eligibility.

## Stop Rules

The driver must stop before:

- creating or rewriting any lock,
- mutating a prior phase candidate,
- changing root phase files,
- accepting an unbound review decision,
- running release packaging,
- continuing after unresolved invalidation.

## Resume Envelope

`P4-SPEC-01` reserves the resume envelope but does not define full recovery policy.

Required resume fields:

- `prior_run_id`
- `prior_status_payload`
- `requested_resume_node`
- `input_hashes`
- `lock_hashes`
- `candidate_hashes`
- `invalidation_state`
- `eligible_nodes`
- `blocked_nodes`

Full recovery, replay, and lock rebuild rules belong to `P4-SPEC-02`.

## Review Boundary

The driver may compute review subject hashes and check review decisions. It may not approve a candidate, create a review decision, or promote a phase without Human Gate evidence.
