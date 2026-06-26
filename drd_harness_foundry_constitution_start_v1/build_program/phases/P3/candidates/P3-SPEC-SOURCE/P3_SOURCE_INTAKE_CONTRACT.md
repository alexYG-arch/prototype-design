# P3 Source Intake Contract

## Objective

`P3-SPEC-SOURCE` defines the full-capability source intake contract for P3. It generalizes the P2 single PRD fixture into a governed intake stage that can freeze source packages, preserve provenance, expose missing-input obligations, and hand a stable source bundle to downstream distillation.

## Upstream Authority

| Artifact | Binding |
| --- | --- |
| `control/locks/P2_BUILD_LOCK.json` | `b7a85510c2a7b839ca5461341017da9bcaa3ddd031019936b921bf881af29aad` |
| `control/locks/P2_SPEC_LOCK.json` | `0704164683e6c2253c2b34e05d50ee9cb59cd330837dab3f6dae020def852dcd` |
| `build_program/phases/P3/PHASE_MANIFEST.json` | `34f854ae71bdfedd52a52de2d86edb2ea4dfc921492869b56e6e41f4ada447f7` |
| `build_program/phases/P3/MODULE_MAP.md` | `3d71cdbc4bfb2ade280b4565ff5640b51c7b8f8574349b1586d9ee5236658e10` |

P3 source intake may only start from a valid P2 build lock. The P2 vertical slice proves one complete source-to-final path; P3 extends the harness breadth while keeping the same lock and review discipline.

## Source Intake Purpose

The stage must create a frozen, hash-addressed source package for every accepted input before any distillation, reasoning, layout, compiler, adapter, or skill step consumes it.

A valid source package must identify:

- source item id and stable local path;
- media or document kind;
- origin description without secrets;
- capture timestamp or explicit unknown-time decision;
- file hash or content hash;
- schema-compatible source snapshot fields when `source_snapshot_manifest.schema.json` is used;
- source role in the run;
- access and permission boundary;
- redaction or exclusion decisions;
- downstream eligibility state.

## Non Product Capability Boundary

This workpack defines harness intake behavior. It must not add user-facing product features to an application being specified. If a source implies a new product workflow, new page, new account capability, new payment path, or new user task, the intake stage must record a human-review-required expansion gap and keep the source frozen without adopting that product capability.

## Accepted Source Families

| Family | Intake rule |
| --- | --- |
| PRD text or markdown | Freeze as text with line-oriented hash and source anchors. |
| Structured JSON or manifests | Freeze with canonical JSON hash and schema claim when available. |
| Screenshots or images | Freeze file hash and require separate visual extraction evidence before semantics are adopted. |
| Existing DRD or design artifacts | Freeze as reference source and record whether it is authoritative, comparative, or historical. |
| External links | Record URL and retrieval metadata only when content is locally snapshotted; link text alone is not evidence. |

## Rejection And Review Rules

The intake stage must reject or route to human review when a source is inaccessible, mutable without snapshot, secret-bearing, license-restricted, outside the run scope, or ambiguous about authority. Rejection must preserve a reason record and must not silently discard a source that influenced downstream decisions.

## Output Contract

The implementation must produce local artifacts that let a reviewer reproduce what was accepted, what was rejected, why a source was eligible, and which downstream stage consumed it.

## Existing Schema Compatibility

`source_snapshot_manifest` must keep the existing required fields from `repository/schemas/stages/source_snapshot_manifest.schema.json`: `source_prd_snapshot_id`, `source_path`, `snapshot_path`, `snapshot_hash`, `created_at`, `byte_size`, `content_type`, `normalization_method`, and `source_identity`. P3 multi-source metadata must be represented by adjacent intake artifacts, not by changing that schema shape inside this workpack.

`downstream_handoff_manifest` must keep the existing `dependency_manifest.schema.json` shape. Eligibility and blocker detail is referenced through artifact hashes and source authority records instead of replacing dependency manifest fields.
