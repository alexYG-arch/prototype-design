# P2 SPEC_LOCK Creation Readiness Handoff

This Candidate converts the approved P2 spec candidates into the canonical input bundle expected by `tooling/create_spec_lock.py`.

## What Is Ready
- P2-SPEC-01, P2-SPEC-02, and P2-SPEC-03 subject hashes are recomputable from disk.
- Their `REVIEW_DECISION.json` files are approved and hash-bound.
- `SPEC_LOCK_INPUT_BUNDLE.json` is shaped for `tooling/create_spec_lock.py --phase P2`.

## What Is Not Done
- `control/locks/P2_SPEC_LOCK.json` has not been written.
- P2 implementation workpacks remain blocked.
- Root P2 phase files remain unchanged.

## Next Step
This readiness package is approved by human review. Actual lock creation remains a separate explicit command.

## Repair Coverage
- `SPEC_LOCK_INPUT_BUNDLE.json` now records the real output path preflight and dry-run passed status.
- `SPEC_LOCK_DRY_RUN_VALIDATION_REPORT.json` now records parsed lock object checks.
- `VALIDATION_EVIDENCE.json` includes review ID binding and dry-run object binding commands.
