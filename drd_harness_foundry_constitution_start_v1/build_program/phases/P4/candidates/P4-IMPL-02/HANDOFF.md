# P4-IMPL-02 Handoff

This candidate implements P4 recovery and resume behavior.

Review focus:
1. Confirm `recovery.py` uses declared run state and current evidence only; it does not discover undeclared files to guess state.
2. Confirm skip/replay/block decisions match P4-SPEC-02 and use structured invalidation reason codes.
3. Confirm `review_recovery.py` detects target/decision missing, stale, invalid, hash changed, and non-approved states without writing review decisions.
4. Confirm `lock_rebuild.py` is request-only and cannot create, rewrite, delete, or publish locks.
5. Confirm `program_driver.py` was only extended for recovery integration and cwd-independent P3 lock binding; it does not redefine P4-IMPL-01 DAG ownership.

Next action after approval: P4-IMPL-03 release suite runner contracts require explicit continuation.
