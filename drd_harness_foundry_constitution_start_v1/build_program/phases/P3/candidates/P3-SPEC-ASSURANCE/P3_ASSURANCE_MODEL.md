# P3 Assurance Model

## Model Overview

The assurance model has four rails:

- evidence rail: compiler review decision, compiler output hashes, read-only QA findings, validator results, and human gate decisions
- traceability rail: trace rows, test obligations, code target maps, dependency edges, invalidation policies, and traceability exceptions
- workpack rail: implementation workpack index, allowed paths, forbidden paths, code targets, validators, tests, acceptance commands, and skill bindings
- gate rail: final assurance report and human gate packet

None of these rails creates product semantics. They prove that approved semantics can be implemented and reviewed without scope drift.

## Core Records

### Assurance Input Index

The assurance input index lists every approved input consumed by final assurance. It binds compiler review decision, compiler output package refs, schema refs, validator refs, read-only QA records, trace rows, test obligations, implementation workpack index, skill bindings, and traceability exceptions.

An input not present in the index is not available to the assurance gate.

### Final Review Packet

The final review packet is the human-readable gate packet. It summarizes compiler readiness, QA boundary status, traceability coverage, unresolved findings, exception decisions, lock readiness, and explicit non-promotion status.

It is review evidence, not a lock.

### Trace Row Set

The trace row set is the precise bridge from approved specs to future implementation. Each row must describe one implementation duty and one code target. Broad duties or bundled checks are rejected.

### Test Obligation Matrix

The test obligation matrix mirrors trace rows. Each row must include a positive case and a negative case. The validator check ids must match the trace row exactly.

### Implementation Workpack Index

The implementation workpack index lists future implementation workpacks, status, and traceability rows. It is valid only if every listed trace row exists and no code target is orphaned.

Its `generated_at` value is metadata, but it still affects review and lock evidence when the index is hashed. It must therefore be deterministic or explicitly excluded from semantic and lock-readiness hashes by an approved rule. Wall-clock generated values are invalid for reviewed assurance artifacts.

### Skill Binding Manifest

The skill binding manifest binds helper skills to spec locks, allowed commands, allowed write paths, forbidden write paths, validators, tests, and human gate requirement. It is invalid if it grants semantic or approval authority.

### Traceability Exception Ledger

Traceability exceptions are not silent waivers. Each exception must name the affected trace rows, requested workpack, scope delta, reason, and human gate decision reference.

### Read-Only QA Boundary

The read-only QA boundary proves that DRD-06 reported findings without mutating compiled artifacts. Any write outside the two allowed QA outputs is blocking.

### Final Assurance Report

The final assurance report aggregates all findings. It can report `PASS`, `REVIEW_REQUIRED`, or `BLOCKED`. It cannot repair the underlying issue.

## Invalidation Model

Assurance rows are invalidated by:

- compiler review decision supersession
- compiler output hash drift
- spec lock drift
- build lock drift
- validator drift
- test evidence drift
- workpack scope drift
- skill binding drift
- release dependency drift
- nondeterministic generation metadata

Invalidated rows block promotion until they are regenerated, reviewed, or covered by an explicit traceability exception.

## Lock Readiness

Assurance may say that lock creation is ready. It must not create `P3_SPEC_LOCK` or `P3_BUILD_LOCK` inside this spec candidate. Lock creation remains a separate user-authorized action.
