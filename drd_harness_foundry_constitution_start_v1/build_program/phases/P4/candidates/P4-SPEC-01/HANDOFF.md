# P4-SPEC-01 Handoff

## Candidate

- Workpack: `P4-SPEC-01`
- Phase: `P4`
- Lane: `SPEC`
- Module: `integration_entry`
- Upstream lock: `control/locks/P3_BUILD_LOCK.json`

## What This Candidate Defines

`P4-SPEC-01` defines the first P4 integration contract: program DAG, program driver, public `drdctl` command surface, PRD Harness Adapter, and Markdown PRD Adapter.

## Review Focus

1. Confirm that P4 integration uses the approved P3 build lock and does not rewrite P3 outputs.
2. Confirm that the CLI remains thin and cannot own product semantics or lock mutation.
3. Confirm that adapters preserve source evidence and cannot create product requirements.
4. Confirm that the program DAG and command status payload are deterministic enough for later recovery and release specs.
5. Confirm that release command behavior is limited to readiness request envelope, not release lock creation.

## Deferred P4 Scope

The following are intentionally deferred to later P4 spec workpacks:

- review recovery, run resume internals, and lock rebuild;
- golden, integration, and release test suites;
- packaging, example project, and release lock creation.

## Next Action

Human review `P4-SPEC-01`. Do not create `P4_SPEC_LOCK`, implement repository code, start `P4-SPEC-02`, commit, or push without explicit authorization.
