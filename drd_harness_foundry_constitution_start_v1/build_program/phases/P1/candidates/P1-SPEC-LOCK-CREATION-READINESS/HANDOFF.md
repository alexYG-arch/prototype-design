# Handoff

## What This Candidate Adds

This Candidate records that P1 spec inputs and phase readiness approval are available, and that a narrow Python lock creation tool now exists at `tooling/create_spec_lock.py`.

## What A Reviewer Should Decide

1. Accept the proposed interpretation that `review_decision_hash` binds the phase-level review decision file hash.
2. Decide the canonical output path for P1 lock files.
3. Review whether `tooling/create_spec_lock.py` is acceptable as the Python-controlled lock creation path.
4. Authorize or reject writing the canonical P1 lock file to the chosen `control/**` path.
5. Decide whether repository-side schema mirroring is required after lock creation.

## Next Valid Step If Approved

Run `tooling/create_spec_lock.py` with the approved input bundle and the authorized output path.

## Current Boundary

No canonical `SPEC_LOCK` exists yet. Implementation workpacks remain blocked until a canonical P1 `SPEC_LOCK` is created and validated.
