# P4-IMPL-04 Handoff

This candidate implements package manifest validation, example project smoke validation, and v3.1 migration coverage validation.

Review focus:
1. Confirm `packaging.py` validates package manifests and emits dry-run evidence only.
2. Confirm forbidden paths, path escapes, untracked release inputs, invalid hashes, dirty-state values, and semantic payloads are rejected.
3. Confirm the example fixture stays inside `repository/examples/p4_release_smoke` and smoke validation only compares expected output hashes.
4. Confirm `migration.py` validates row contract, summary consistency, blocked Human Gate rows, duplicate legacy ids, and report hash.
5. Confirm P4-IMPL-05 surfaces remain separately gated: release readiness packet validation, dirty state readiness policy, and release lock input bundle construction.

Next action after approval: P4-IMPL-05 release readiness and release-lock input boundary implementation requires explicit continuation.
