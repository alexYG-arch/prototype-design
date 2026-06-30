# P4 Recovery State Model

## Model Summary

The P4 recovery model represents a governed run as a deterministic state machine. It exists to decide whether a prior run can be skipped, replayed, blocked, or sent to Human Gate using recorded evidence.

The model is not a semantic authority. It cannot infer product meaning from input text, CLI flags, markdown formatting, or missing artifacts.

## State Types

| State Type | Purpose | Required Evidence |
| --- | --- | --- |
| `RUN_CREATED` | Command envelope and run id exist. | `run_id`, command, adapter, output root |
| `ADAPTER_RECORDED` | Input adapter emitted source evidence. | source refs, input hashes, normalization report |
| `DAG_RECORDED` | Program DAG was captured. | node ids, edge ids, DAG hash |
| `NODE_PLANNED` | A node has declared reads and writes. | read refs, write refs, dependency refs |
| `NODE_COMPLETED` | Node output was written and hashed. | output paths, output hashes, exit code |
| `NODE_FAILED` | Node failed with recovery evidence. | failure type, failed command, exit code, partial writes |
| `REVIEW_GATE_REACHED` | Review is required before continuation. | candidate dir, subject hash, review target |
| `LOCK_GATE_REACHED` | Lock action is requested or required. | lock kind, source inputs, dry-run packet |
| `RUN_STOPPED` | Run ended before completion. | stop reason, blocked nodes, next allowed command |

## Resume Decision Inputs

A resume decision must read only:

- the prior run state,
- the prior command status payload,
- declared current input refs,
- declared upstream lock refs,
- declared candidate dirs and review decisions,
- declared output paths from the prior run.

It must not scan unrelated directories to discover undeclared work.

## Node Decision Rules

| Decision | Required Conditions |
| --- | --- |
| `SKIP` | Node completed, dependency hashes match, output hashes match, write scope matches, and no gate blocks the node. |
| `REPLAY` | Node is invalidated only by missing or stale output, all inputs and locks match, and declared write paths are still allowed. |
| `BLOCK_HUMAN_GATE` | Review binding is missing, stale, changed, or needed for an action. |
| `BLOCK_INVALIDATION` | Input, lock, DAG, plan, or dependency drift changes the meaning of replay. |
| `BLOCK_LOCK_BOUNDARY` | Requested continuation would create, rebuild, or rewrite a lock. |
| `BLOCK_UNSAFE_STATE` | Evidence is missing, contradictory, or unverifiable. |

## Hash Records

All hash records must identify what was hashed:

- `hash_kind`
- `path`
- `sha256`
- `recorded_at`
- `producer_node_id`
- `source_authority`

The same hash value cannot be reused across different meanings without a separate `hash_kind`.

## Recovery History

Every resume attempt appends a recovery history record:

- `attempt_id`
- `requested_resume_node`
- `prior_run_state_hash`
- `current_evidence_hash`
- `decision`
- `blocked_reason_codes`
- `skipped_nodes`
- `replayed_nodes`
- `written_paths`
- `next_allowed_actions`

Recovery history is append-only within the new run output directory. It must not edit prior run evidence.

## Stop Rules

The recovery model must stop before:

- writing a review decision,
- approving a candidate,
- creating or rewriting any lock,
- changing prior phase candidates,
- changing root phase files,
- replaying a node with unbound input drift,
- silently accepting missing failure records.

## Determinism Rules

1. Resume ordering is derived from the recorded DAG topological order.
2. Blocked nodes are sorted by node id.
3. Invalidation records are sorted by reason code, then node id, then path.
4. Dry-run lock rebuild packets sort candidate and review inputs by path.
5. Status payloads use stable field names and machine-readable reason codes.
