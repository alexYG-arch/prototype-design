# P3-SPEC-COMPILER Handoff

## Status

- Workpack: `P3-SPEC-COMPILER`
- Module: `drd_compiler`
- State: candidate ready for human review
- Upstream approved candidate: `P3-SPEC-LAYOUT`
- Upstream review subject hash: `191b22af853d316b1e447fd32c649bcc744f18878b2e0c0a0cb800b76499a319`

## What This Candidate Defines

`P3-SPEC-COMPILER` defines the closed-input and semantic-conservation contract for deterministic final DRD assembly. It binds approved P3 source, distillation, closure, element, pattern, and layout review decisions; then it specifies how future implementation must build the input bundle, semantic inventory, final DRD text, manifest, indexes, conservation report, and read-only QA boundary.

## What It Does Not Do

This candidate does not implement compiler code, generate final DRD outputs, create locks, mutate approved upstream candidates, or start implementation work.

## Next Step

If accepted, continue with `P3-SPEC-ASSURANCE`. Do not create `P3_SPEC_LOCK`, `P3_BUILD_LOCK`, or repository implementation code from this candidate alone.
