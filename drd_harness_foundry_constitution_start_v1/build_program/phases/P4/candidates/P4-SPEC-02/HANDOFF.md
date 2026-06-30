# P4-SPEC-02 Handoff

## Candidate

- Workpack: `P4-SPEC-02`
- Phase: `P4`
- Lane: `SPEC`
- Module: `recovery_resume_lock_rebuild`
- Upstream spec: `build_program/phases/P4/candidates/P4-SPEC-01/REVIEW_DECISION.json`
- Upstream lock: `control/locks/P3_BUILD_LOCK.json`

## What This Candidate Defines

`P4-SPEC-02` defines how P4 handles failed or partial runs after the integration entry exists:

1. run state records for recovery,
2. resume decisions for skip, replay, block, and Human Gate,
3. invalidation reason codes,
4. review recovery packets for missing or stale review bindings,
5. lock rebuild request packets and dry-run boundaries.

`program_driver.py` remains primarily owned by the P4-SPEC-01 Program Driver contract. P4-SPEC-02 only defines recovery and resume hook integration points for that driver boundary.

## Review Focus

1. Confirm recovery is evidence-driven and does not infer missing state from directory scans.
2. Confirm resume cannot skip or replay through input drift, lock drift, stale review decisions, or unsafe write scope.
3. Confirm review recovery cannot create approval or edit `REVIEW_DECISION.json`.
4. Confirm lock rebuild is request-only and dry-run-only in this workpack.
5. Confirm invalidation records and missing review decision packets have enough structure for deterministic tests.
6. Confirm recovery cannot add product requirements, page elements, layout rules, or business Contract.

## Deferred P4 Scope

The following are intentionally deferred to later P4 spec workpacks:

- golden, integration, and release test suites;
- v3.1 migration coverage;
- packaging and example project;
- release lock schema and release lock creation.

## Next Action

Human review `P4-SPEC-02`. Do not create `P4_SPEC_LOCK`, implement repository code, start `P4-SPEC-03`, commit, or push without explicit authorization.
