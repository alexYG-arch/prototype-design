# SPEC_LOCK Creation Blueprint

## Purpose

Create a deterministic Python path from approved P1 Candidates to a canonical `SPEC_LOCK`.

This Candidate now has a narrow implementation at `tooling/create_spec_lock.py`. The blueprint remains the review contract for checking that implementation.

## Proposed Command

```bash
python3 tooling/create_spec_lock.py \
  --phase P1 \
  --input-bundle build_program/phases/P1/candidates/P1-SPEC-LOCK-CREATION-READINESS/SPEC_LOCK_INPUT_BUNDLE.json \
  --output control/locks/P1_SPEC_LOCK.json
```

The command path and output path are proposed only. They require explicit authorization before `tooling/**` or `control/**` changes are made.

`tooling/**` authorization has been granted for the narrow lock creation tool. `control/**` output authorization has not yet been granted.

## Required Algorithm

1. Load `SPEC_LOCK_INPUT_BUNDLE.json`.
2. Verify `phase` equals `P1`.
3. Verify `source_candidate_review_decision` exists and its file hash equals `phase_review_decision_file_hash`.
4. Load every approved P1 Candidate manifest named by the phase readiness Candidate.
5. For every Candidate, recompute the generated-output subject hash using the approved subject-hash convention.
6. Verify every `REVIEW_DECISION.json` subject hash equals the recomputed subject hash.
7. Recompute the phase root from the ordered approved spec subject hashes.
8. Verify the recomputed phase root equals `proposed_canonical_lock_fields.root_sha256`.
9. Build the canonical lock object with at least the schema-required fields: `lock_id`, `phase`, `root_sha256`, `files`, and `review_decision_hash`.
10. Include extended audit fields for `review_decision_file_root_sha256`, validator identities, source Candidate paths, schema hash, and runtime identity.
11. Validate the lock object against `control/schemas/spec_lock.schema.json`.
12. Write the lock atomically to a new path. Existing lock files must not be overwritten in place.

## Implemented Command Behavior

`tooling/create_spec_lock.py` currently supports:

- `--phase` with explicit phase selection.
- `--input-bundle` for the approved bundle.
- `--dry-run` to print the computed lock JSON without writing.
- `--output` to write a new file only when the target does not already exist.

`--dry-run` and `--output` are mutually exclusive.

The tool uses only Python standard library modules and the local `tooling/_common.py` helpers.

## Minimum Canonical Lock Semantics

| Field | Required meaning |
| --- | --- |
| `lock_id` | Stable identifier for the first P1 spec lock, proposed as `P1-SPEC-LOCK-001`. |
| `phase` | Must be `P1`. |
| `root_sha256` | Root over approved P1 spec subject hashes. |
| `files` | Ordered file or subject entries used to compute and audit the lock. |
| `review_decision_hash` | Hash of the phase-level review decision authorizing lock creation inputs. |
| `review_decision_file_root_sha256` | Extended audit root over individual P1 review decision files. |
| `created_by_runtime` | Must record Python runtime identity. |

## Error Conditions

| Error code | Meaning |
| --- | --- |
| `SPEC_LOCK_TOOL_MISSING` | The requested lock creation tool does not exist. |
| `SPEC_LOCK_INPUT_HASH_MISMATCH` | Recomputed subject hash differs from approved review decision. |
| `SPEC_LOCK_PHASE_REVIEW_MISMATCH` | Phase review decision file hash differs from the input bundle. |
| `SPEC_LOCK_SCHEMA_INVALID` | Output does not validate against the canonical schema. |
| `SPEC_LOCK_OVERWRITE_FORBIDDEN` | Tool attempted to modify an existing canonical lock in place. |
| `SPEC_LOCK_RUNTIME_UNBOUND` | Tool failed to record Python runtime identity. |
| `SPEC_LOCK_OUTPUT_EXISTS` | Tool refused to overwrite an existing output path. |

## Review Questions

- Should `review_decision_hash` in the minimal schema continue to bind the phase-level review decision file hash?
- Should `control/schemas/spec_lock.schema.json` remain the single schema authority?
- Is `control/locks/P1_SPEC_LOCK.json` the authorized canonical output path for P1 locks?
- Should implementation workpacks start only after `P1-SPEC-LOCK-001` exists and validates?
