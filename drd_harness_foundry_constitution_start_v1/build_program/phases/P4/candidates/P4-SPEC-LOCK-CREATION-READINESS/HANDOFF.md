# P4 SPEC_LOCK Creation Readiness Handoff

## Candidate

- Workpack: `P4-SPEC-LOCK-CREATION-READINESS`
- Phase: `P4`
- Lane: `SPEC_LOCK_READINESS`
- Source candidate: `P4-SPEC-03`

## What This Candidate Defines

This package prepares the canonical P4 spec lock input bundle and dry-run evidence. It proves that approved P4 spec candidates can be consumed by `tooling/create_spec_lock.py` without writing the real lock.

## Review Focus

1. Confirm all approved P4 spec candidates are included.
2. Confirm each included subject hash and review decision hash is current.
3. Confirm dry-run output root and review-decision root match the proposed canonical lock fields.
4. Confirm the output path `control/locks/P4_SPEC_LOCK.json` is not written by this readiness package.
5. Confirm this readiness package does not authorize P4 implementation, P4_BUILD_LOCK, or DRD_HARNESS_RELEASE_LOCK.

## Next Action

Human review this readiness candidate. Actual `P4_SPEC_LOCK` creation still requires the user to explicitly request lock creation.
