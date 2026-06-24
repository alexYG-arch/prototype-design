# Handoff

## What Changed

The sixth P1 implementation workpack adds validation and lock readiness helpers for candidate state, output coverage, review binding, validator identity, scope postflight, promotion readiness, SPEC_LOCK readiness, BUILD_LOCK readiness, dependency invalidation, recovery plans, partial unaffected claims, invalidated evidence blocking, and lock supersession cycles.

It also adds JSON schemas for lock, validation, promotion, invalidation, dependency graph, dependency edge, partial unaffected claim, and supersession records.

## Review Patch

The strict review pass repaired five validation gaps:

1. Validation results now use the schema field `checked_subject_hash` instead of a divergent `subject_hash`.
2. Candidate `generated_outputs` are rejected when they use absolute paths or parent-directory traversal to escape the candidate package.
3. SPEC_LOCK validator evidence and BUILD_LOCK test evidence now require `exit_code` 0.
4. SPEC_LOCK and BUILD_LOCK readiness now verify `root_sha256` against canonical lock content.
5. Dependency edge validation now rejects undeclared edge types at runtime.

## Review Focus

1. Whether the candidate-only validator is strict enough about self approval, promoted state, and lock claims without blocking legitimate human-approved but not locked candidates.
2. Whether required output coverage should scan only candidate package outputs or also bind repository implementation files directly in the same subject hash.
3. Whether validator identity should require stronger runtime environment capture than the current `runtime_identity` string.
4. Whether SPEC_LOCK and BUILD_LOCK readiness should verify canonical root hashes immediately or leave root calculation to the later lock creation tool.
5. Whether dependency graph extraction should remain manual/structured at this layer or be generated from manifests in a later orchestrator workpack.
6. Whether partial unaffected claims need human review by default when the changed dependency is a lock or review decision.

## Validation

`python3 -m pytest repository/tests/validators repository/tests/orchestrator -q` passed with 34 tests.

`python3 -m pytest repository/tests/kernel repository/tests/stages repository/tests/reasoning repository/tests/interaction repository/tests/presentation repository/tests/layout repository/tests/validators repository/tests/orchestrator -q` passed with 158 tests.

## Remaining Boundary

This candidate does not create `BUILD_LOCK`, does not mutate existing locks, does not promote any candidate, and does not approve itself. Human review is still required before approval, and a separate Python lock step is required before any build lock authority exists.
