# P4-IMPL-04 Self Check

- The implementation owns only package manifest validation, example project smoke validation, and v3.1 migration coverage validation.
- Package validation rejects forbidden paths, path escapes, untracked release inputs, unsupported dirty states, invalid hashes, and semantic payloads.
- Package dry-run evidence refuses package publishing, artifact upload, and lock creation.
- Example smoke validation binds source refs and expected outputs by hash and never creates product semantics.
- Migration coverage validates every row, summary count, blocked Human Gate row, duplicate id, report hash, and semantic boundary.
- Release readiness packets, dirty-state readiness policy, release lock input bundles, P4_BUILD_LOCK, DRD_HARNESS_RELEASE_LOCK, and package publishing remain out of scope.
- P4 tests, full regression, runtime-boundary-check, py_compile, and git diff checks pass.
