# P2 SPEC_LOCK Creation Readiness Self Check

## Scope
- Writes are constrained to `build_program/phases/P2/candidates/P2-SPEC-LOCK-CREATION-READINESS/**`.
- No `control/**`, `repository/**`, P1, or earlier P2 spec candidate files are modified.
- This package is not a lock and does not authorize implementation.

## Lock Tool Compatibility
- The canonical input bundle uses the shape required by `tooling/create_spec_lock.py`.
- P2-SPEC-01, P2-SPEC-02, and P2-SPEC-03 are all approved by human review.
- P2 review IDs are recorded as `review_id`; `review_decision_id` is omitted intentionally to avoid a false decision_id mismatch.

## Review Boundary
- This readiness package is approved by human review.
- Real lock creation still requires explicit user authorization.

## Repair Coverage
- Review IDs are machine-checked even though the existing lock tool does not consume `review_id` directly.
- Dry-run output is parsed and bound to expected lock roots, not only checked for exit code 0.
- Real lock output path availability is recorded and must remain true before lock creation.
