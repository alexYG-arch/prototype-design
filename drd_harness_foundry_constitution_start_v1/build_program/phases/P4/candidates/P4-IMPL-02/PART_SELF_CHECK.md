# P4-IMPL-02 Self Check

- The implementation owns only P4 recovery, resume, review recovery, invalidation, and lock rebuild request boundaries from P4-SPEC-02.
- Resume decisions are evidence-driven and fail closed on missing state, hash drift, write scope drift, Human Gate, and lock boundary conditions.
- Review recovery recomputes subject hashes and reports missing/stale/hash-changed decisions without writing approvals.
- Lock rebuild produces request and dry-run evidence only; it does not create or rewrite locks.
- Program driver default P3 build lock binding resolves from the start package root, while DAG evidence keeps the canonical relative lock ref.
- Recovery rejects product semantic fill fields and does not create business contracts, page elements, or layout rules.
- Full regression and runtime boundary checks pass.
