# P3-SPEC-ASSURANCE Self Check

- Scope is limited to `build_program/phases/P3/candidates/P3-SPEC-ASSURANCE/**`.
- The candidate defines `assurance_traceability` only.
- `P3-SPEC-COMPILER` review decision is bound by sha256 and subject hash.
- Assurance is defined as an evidence and traceability gate, not a semantic authoring stage.
- Trace rows, test obligations, implementation workpack index, skill binding, traceability exceptions, read-only QA boundary, and final assurance report are covered.
- Positive and negative test obligations are required for every trace row.
- Reviewed `generated_at` metadata is constrained to deterministic sources.
- Read-only QA cannot mutate final DRD, manifests, indexes, review decisions, source snapshots, or locks.
- Lock readiness is separated from lock creation.
- No repository code, root P3 files, prior P3 candidates, P1/P2 files, or control locks are modified by this candidate.
- Open blockers: none.
