# P4-SPEC-02 Self Check

## Scope

- Created a spec-only candidate for recovery, resume, invalidation classification, review recovery, and lock rebuild request boundaries.
- Bound upstream to approved `P4-SPEC-01` and current `P3_BUILD_LOCK`.
- Wrote only under `build_program/phases/P4/candidates/P4-SPEC-02`.

## Boundaries

- No repository implementation code was changed.
- No lock was created or modified.
- No review decision was created.
- No root P4 phase file was changed.
- No P3 candidate or lock was changed by this candidate.
- No product requirement, page element, layout rule, or business Contract was added.

## Verification Expectations

- `candidate-check` must pass for this candidate.
- JSON outputs must parse.
- Upstream P4-SPEC-01 review decision hash and P3_BUILD_LOCK hash must match the manifest bindings.
- Recovery rules must fail closed on missing run evidence, stale review bindings, lock drift, unsafe replay, and lock write requests.
- Invalidation records must have declared reason code, affected node/path, prior/current value, stop rule, and Human Gate fields.
- Missing review decisions must use explicit packet status/nullability rules rather than empty strings or fake paths.
- P4-SPEC-02 may only integrate recovery hooks into `program_driver.py`; P4-SPEC-01 keeps primary Program Driver ownership.

## Deferred Scope

- P4-SPEC-03 retains golden, integration, release suite, v3.1 migration coverage, packaging, example project, and release lock creation rules.
- P4 implementation remains blocked until P4 spec lock and explicit implementation authorization.
