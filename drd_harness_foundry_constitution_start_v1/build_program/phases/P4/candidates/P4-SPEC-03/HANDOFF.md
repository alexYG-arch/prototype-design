# P4-SPEC-03 Handoff

## Candidate

- Workpack: `P4-SPEC-03`
- Phase: `P4`
- Lane: `SPEC`
- Module: `release_readiness_packaging_migration`
- Upstream spec: `build_program/phases/P4/candidates/P4-SPEC-02/REVIEW_DECISION.json`
- Upstream lock: `control/locks/P3_BUILD_LOCK.json`

## What This Candidate Defines

`P4-SPEC-03` defines the final P4 spec surface:

1. golden, integration, and release suite contracts,
2. v3.1 migration coverage map rules,
3. package manifest and example project manifest rules,
4. release readiness packet rules,
5. release lock input bundle and eligibility boundaries.

## Review Focus

1. Confirm golden tests cannot rewrite expected outputs during release checks.
2. Confirm integration tests cover CLI, adapters, program driver, recovery, review gates, lock gates, and write scope.
3. Confirm release readiness requires package dry-run, example smoke, migration coverage, missing-gate evidence, and dirty-state classification.
4. Confirm every v3.1 capability row must be mapped, rationalized, or routed to Human Gate.
5. Confirm readiness packet and release lock input bundle avoid circular hashing.
6. Confirm dirty state is represented by structured dirty-state records.
7. Confirm P4-IMPL-03, P4-IMPL-04, and P4-IMPL-05 implementation ownership stays partitioned.
8. Confirm release lock eligibility is not release lock creation.
9. Confirm package and example rules cannot add product requirements, page elements, layout rules, or business Contract.

## Deferred P4 Scope

The following are intentionally not performed by this candidate:

- `P4_SPEC_LOCK` creation;
- repository implementation;
- `P4_BUILD_LOCK` creation;
- `DRD_HARNESS_RELEASE_LOCK` creation;
- package publishing.

## Next Action

Human review `P4-SPEC-03`. Do not create `P4_SPEC_LOCK`, implement repository code, commit, or push without explicit authorization.
