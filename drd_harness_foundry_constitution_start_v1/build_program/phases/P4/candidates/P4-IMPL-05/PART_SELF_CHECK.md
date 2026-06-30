# P4-IMPL-05 Self Check

- The implementation owns only release readiness packet validation, dirty state record validation, and release lock input bundle construction without lock writes.
- Readiness packets require P4 spec/build lock refs, suite report hashes, package/example/migration evidence hashes, missing gate list, dirty state policy, preview consistency, human authorization requirement, and self-excluding readiness hash.
- Dirty state policy accepts CLEAN and DOCUMENTED_DIRTY only when dirty records are excluded non-release inputs; release-input dirty records and BLOCKED_DIRTY block readiness.
- Release lock input bundles require P4-SPEC-01/02/03 review decisions, build decision evidence, suite/package/example/migration/readiness hashes, source git commit, human authorization requirement, and self-excluding bundle hash.
- Release lock input bundles reject lock creation, package publishing, real lock output path declarations, readiness packet embedding, and semantic payloads.
- P4_BUILD_LOCK creation, DRD_HARNESS_RELEASE_LOCK creation, package publishing, package manifest validation, migration coverage validation, example fixtures, and golden output updates remain out of scope.
- Target tests, P4 tests, full regression, runtime-boundary-check, py_compile, and git diff checks pass.
