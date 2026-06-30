# P4-IMPL-03 Self Check

- The implementation owns only P4 release suite runner contracts in `repository/src/drd_harness/release/suites.py`.
- Shared suite reports require self-excluding sha256 `report_hash` and sha256 `input_hashes`; input hash drift changes `run_id`.
- Golden suite checks compare hashes, reject invalid hash shapes, and block update requests; they never rewrite expected outputs.
- Integration suite checks CLI, adapters, program driver, recovery, Human Gate, lock gate, write-scope evidence, and machine-readable command payload shape together.
- Release suite report shape requires package dry-run, example smoke, migration coverage, and readiness evidence hashes but does not build packages or locks.
- Packaging, migration, release readiness packet construction, release lock input bundles, example fixtures, package publishing, and lock creation remain out of scope.
- P4 tests, full regression, runtime-boundary-check, py_compile, and git diff checks pass.
