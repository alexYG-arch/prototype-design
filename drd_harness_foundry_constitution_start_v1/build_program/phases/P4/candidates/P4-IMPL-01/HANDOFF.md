# P4-IMPL-01 Handoff

This candidate implements and approves the P4 integration entry surface.

Approved boundary:
1. `repository/src/drd_harness/orchestrator/program_driver.py` provides deterministic DAG planning, status payloads, upstream P3 build lock binding, output scope checks, and gate stops.
2. `repository/src/drd_harness/adapters/markdown_prd.py` normalizes Markdown PRD input into stable source section evidence while preserving source hash.
3. `repository/src/drd_harness/adapters/prd_harness.py` normalizes structured harness bundles into source ref evidence while checking declared source hashes.
4. `repository/src/drd_harness/cli/main.py` exposes `run`, `review`, `resume`, and `release` command envelopes and delegates implementation logic to P4 modules.
5. This approval does not create P4_BUILD_LOCK, does not create DRD_HARNESS_RELEASE_LOCK, and does not update root P4 phase files.

Next action: P4-IMPL-02 recovery and resume implementation is separately bounded to P4-SPEC-02.
