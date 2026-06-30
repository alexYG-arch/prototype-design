# P4-SPEC-03 Self Check

## Scope

- Created a spec-only candidate for golden, integration, and release suite contracts.
- Added v3.1 migration coverage row and summary rules.
- Added package manifest, example project manifest, release readiness packet, and release lock input bundle rules.
- Bound upstream to approved `P4-SPEC-02`, approved `P4-SPEC-01`, and current `P3_BUILD_LOCK`.
- Wrote only under `build_program/phases/P4/candidates/P4-SPEC-03`.

## Boundaries

- No repository implementation code was changed.
- No lock was created or modified.
- No package was built or published.
- No example project files were created.
- No root P4 phase file was changed.
- No P4-SPEC-01 or P4-SPEC-02 file was changed by this candidate.
- No product requirement, page element, layout rule, or business Contract was added.

## Verification Expectations

- `candidate-check` must pass for this candidate.
- JSON outputs must parse.
- Upstream P4-SPEC-02, P4-SPEC-01, and P3_BUILD_LOCK hashes must match manifest bindings.
- Suite contracts must cover `GOLDEN`, `INTEGRATION`, and `RELEASE`.
- Release artifact contracts must cover migration, package, example, readiness, and release lock input bundle artifacts.
- Release lock input bundle must not create or rewrite `DRD_HARNESS_RELEASE_LOCK`.
- Report and readiness hashes must exclude their own hash fields under the declared canonical JSON hash policy.
- Readiness packets must use `release_lock_input_bundle_preview` to avoid circular hashing with release lock input bundles.
- Dirty state classification must be carried by structured `dirty_state_records`.
- P4-IMPL-03, P4-IMPL-04, and P4-IMPL-05 ownership must remain partitioned by suite, package/migration/example, and release lock input surfaces.

## Deferred Scope

- `P4_SPEC_LOCK` creation remains a separate explicit lock step after Human Gate approval.
- P4 implementation remains blocked until `P4_SPEC_LOCK` and explicit implementation authorization.
- `P4_BUILD_LOCK` and `DRD_HARNESS_RELEASE_LOCK` remain later explicit lock steps.
