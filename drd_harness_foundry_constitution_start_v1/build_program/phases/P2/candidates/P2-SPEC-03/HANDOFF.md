# P2-SPEC-03 Handoff

P2-SPEC-03 prepares the P2 lock input and implementation readiness evidence for the Tiny Brief Intake vertical slice.

## What This Candidate Does
- Binds the approved P2-SPEC-01 and P2-SPEC-02 review decisions as upstream inputs.
- Defines the P2 implementation workpack index from P2-IMPL-01 through P2-IMPL-05.
- Maps every P2 fixture validation row to implementation workpacks, artifacts, and minimum tests.
- Covers every implementation `code_target`, `test_target`, and required artifact contract path in `allowed_write_paths_after_lock`.
- Records direct and cumulative workpack dependencies in machine-readable fields.
- States the criteria that must be true before `P2_SPEC_LOCK` can be created.

## What This Candidate Does Not Do
- It does not create `control/locks/P2_SPEC_LOCK.json`.
- It does not start repository implementation work.
- It does not promote P2 implementation workpacks.
- It does not change approved P2-SPEC-01 or P2-SPEC-02 artifacts.

## Repair Notes
- The implementation index now includes missing code paths for P2-IMPL-01 through P2-IMPL-04.
- Missing artifact output paths are now included for product expansion gaps, async behavior, interaction messages, and final review artifacts.
- Candidate-only null hashes for P2-SPEC-03 are explicitly marked as pending; final lock tooling must recompute concrete hashes and reject pending rows.

## Next Step
P2-SPEC-03 is approved by the human gate. Lock creation remains a separate explicit step and must recompute concrete P2-SPEC-03 file hashes from disk.
