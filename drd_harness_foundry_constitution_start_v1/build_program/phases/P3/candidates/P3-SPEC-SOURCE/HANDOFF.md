# P3-SPEC-SOURCE Handoff

## Candidate

- Workpack: `P3-SPEC-SOURCE`
- Phase: `P3`
- Lane: `SPEC`
- Module: `source_intake`
- Upstream lock: `control/locks/P2_BUILD_LOCK.json`

## What This Candidate Defines

`P3-SPEC-SOURCE` defines how full P3 runs register, inspect, freeze, classify, and hand off sources before any semantic distillation or downstream module consumes them.

## Review Focus

1. Confirm that source intake only freezes and classifies evidence, without inventing product requirements.
2. Confirm that natural-language source remains primary semantics and inventory rows remain index and verification skeleton.
3. Confirm that inaccessible, risky, conflicting, unsupported, or expansion-triggering sources route to human review.
4. Confirm that downstream modules may consume only eligible source items or explicit blockers.
5. Confirm that future implementation remains blocked until P3 spec lock and implementation authorization exist.

## Review Outcome

Human Gate approved `P3-SPEC-SOURCE` after review of source intake authority, artifact contracts, pipeline rules, validation obligations, traceability, schema alignment, and implementation handoff boundaries.

## Next Action

Continue with `P3-SPEC-DISTILL` when the user explicitly asks to continue. Do not create `P3_SPEC_LOCK`, `P3_BUILD_LOCK`, or repository implementation code from this candidate alone.
