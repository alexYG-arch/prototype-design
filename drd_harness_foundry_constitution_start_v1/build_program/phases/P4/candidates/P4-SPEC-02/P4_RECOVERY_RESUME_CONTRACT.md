# P4 Recovery and Resume Contract

## Purpose

`P4-SPEC-02` defines governed recovery, run resume, invalidation handling, and lock rebuild request boundaries for the P4 integration layer.

This workpack continues from the approved `P4-SPEC-01` integration entry contract. It does not add product requirements, product semantics, UI elements, layout rules, or business contracts. It only specifies how a stopped or failed harness run can be inspected, resumed, replayed, or routed to Human Gate without guessing.

## Upstream Authority

This candidate is authorized by the approved P4 integration entry spec and the approved P3 build lock chain.

Required upstream binding:

- P4-SPEC-01 review decision: `build_program/phases/P4/candidates/P4-SPEC-01/REVIEW_DECISION.json`
- P4-SPEC-01 review decision sha256: `9c7d9b84164ef55a8dd16de4845984f42728864c9dab8fa763cb72a2586e87e8`
- P4-SPEC-01 reviewed subject hash: `e57488d92627fd98b9db1700987284985224035ee34b680a726a2ebc5c74c975`
- P3 build lock path: `control/locks/P3_BUILD_LOCK.json`
- P3 build lock sha256: `52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e`
- P3 build lock root: `0ef47227a39e3eb75923e7506523b734769485431c2a7c3a1e1265f9d937fa8f`
- P3 build lock git commit: `f966182b4670520d2ba69e6f69eecca0bbc1d9b3`

P4 recovery may read run evidence, review metadata, candidate manifests, and lock files. It may not rewrite prior phase candidates, prior locks, root phase files, or review decisions.

## Owned Surface

`P4-SPEC-02` owns these recovery contracts:

1. Run state record shape for stopped, failed, partial, and completed runs.
2. Resume eligibility rules for skip, replay, block, and Human Gate outcomes.
3. Invalidation classification for inputs, locks, review decisions, candidate subjects, execution plans, and outputs.
4. Review recovery behavior for missing, stale, or mismatched review target and review decision bindings.
5. Lock rebuild request packet shape and dry-run evidence boundary.

It does not own:

- golden, integration, and release test suite coverage,
- packaging or example project shape,
- release lock schema or release lock creation,
- automatic lock creation,
- automatic review approval.

Those surfaces remain for later P4 spec workpacks.

## Recovery Invariants

1. Recovery is evidence-driven: every resume decision must cite recorded hashes, lock refs, candidate subject hashes, and written path evidence.
2. Resume must never infer missing state from filesystem layout alone.
3. Skip is allowed only when recorded inputs, upstream locks, execution plan, and output hashes still match.
4. Replay is allowed only for nodes whose write paths are declared and whose upstream dependencies are valid.
5. Human Gate is required for stale review decisions, changed reviewed subjects, ambiguous input changes, lock drift, and requested lock creation.
6. Lock rebuild is a request packet and dry-run result in this workpack, not lock mutation.
7. Recovery must preserve the P4 integration boundary: no business Contract supplementation and no product semantic creation.

## Resume Outcomes

Every resume attempt must resolve to exactly one outcome:

| Outcome | Meaning | May Mutate |
| --- | --- | --- |
| `SKIP` | Node output is already valid and all bound evidence matches. | No |
| `REPLAY` | Node can be rerun because inputs are valid and output path is declared. | Declared output path only |
| `BLOCK_HUMAN_GATE` | Human review or explicit authorization is required. | No |
| `BLOCK_INVALIDATION` | Dependency drift is unresolved. | No |
| `BLOCK_LOCK_BOUNDARY` | Requested action would create or rewrite a lock. | No |
| `BLOCK_UNSAFE_STATE` | Run state is incomplete, contradictory, or unverifiable. | No |

## Required Run State Fields

Each recorded run state must include:

- `run_id`
- `program_id`
- `driver_version`
- `original_command`
- `adapter_id`
- `source_refs`
- `input_hashes`
- `upstream_lock_refs`
- `candidate_subject_hashes`
- `review_decision_hashes`
- `dag_snapshot_hash`
- `execution_plan_hash`
- `node_states`
- `written_paths`
- `output_hashes`
- `gate_states`
- `failure_records`
- `recovery_history`

Missing required fields force `BLOCK_UNSAFE_STATE`.

## Review Recovery

Review recovery may:

- recompute a candidate subject hash from `CANDIDATE_MANIFEST.generated_outputs`,
- check whether `REVIEW_TARGET.json` points to the current subject hash,
- check whether a supplied `REVIEW_DECISION.json` approves the current subject hash,
- emit a review recovery packet with stale, missing, or mismatched binding findings.

Review recovery may not:

- create a review decision,
- edit a review decision,
- approve a candidate,
- promote a candidate,
- create any lock.

If the candidate content changed after review, recovery must stop at `BLOCK_HUMAN_GATE`.

## Invalidation Classes

Recovery must classify invalidation with a stable reason code:

- `INPUT_HASH_CHANGED`
- `INPUT_SOURCE_MISSING`
- `ADAPTER_NORMALIZATION_CHANGED`
- `UPSTREAM_LOCK_HASH_CHANGED`
- `CANDIDATE_SUBJECT_HASH_CHANGED`
- `REVIEW_DECISION_HASH_CHANGED`
- `DAG_SNAPSHOT_CHANGED`
- `EXECUTION_PLAN_CHANGED`
- `OUTPUT_HASH_CHANGED`
- `OUTPUT_MISSING`
- `WRITE_SCOPE_CHANGED`
- `FAILURE_RECORD_INCOMPLETE`
- `REQUESTED_NODE_NOT_IN_DAG`

Each invalidation record must cite the affected node, prior value, current value, and required stop rule.

## Lock Rebuild Request Boundary

P4 recovery can prepare a lock rebuild request packet only when it has enough evidence to prove what changed.

Required packet fields:

- `request_id`
- `lock_kind`
- `source_lock_path`
- `source_lock_sha256`
- `requested_lock_path`
- `candidate_inputs`
- `review_decision_inputs`
- `drift_report`
- `dry_run_result`
- `required_human_authorization`
- `forbidden_without_authorization`

The packet may report eligibility. It cannot create, replace, or rewrite a lock. Any lock write requires a separate explicit user request and a later lock creation step.

## Human Gate Triggers

Human Gate is required when:

- run state lacks any required evidence field,
- a reviewed candidate subject hash changed,
- a review decision hash changed,
- upstream lock hash changed,
- replay would write outside declared output paths,
- a lock rebuild packet would add or remove candidate inputs,
- a command asks to create or rewrite a lock,
- recovery would need product semantic inference to continue.

## Non-Goals

`P4-SPEC-02` does not implement repository code, create P4 locks, create release locks, update root P4 files, approve itself, commit, or push.
