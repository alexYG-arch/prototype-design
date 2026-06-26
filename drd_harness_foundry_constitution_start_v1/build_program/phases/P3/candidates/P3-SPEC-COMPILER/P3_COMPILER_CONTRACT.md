# P3-SPEC-COMPILER Contract

## Scope

`P3-SPEC-COMPILER` owns the P3 `drd_compiler` module. It defines how approved P3 source, distillation, closure, element, pattern, and layout outputs are closed into a deterministic final DRD package.

The compiler is not a product authoring stage. It may assemble, order, attribute, hash, index, and validate approved content. It must not invent missing product semantics, rewrite approved natural-language authority, infer new screens, create layout rules, or repair upstream gaps.

## Approved Upstream Boundary

The direct upstream gate is `P3-SPEC-LAYOUT/REVIEW_DECISION.json`.

| upstream | review decision sha256 | subject hash |
| --- | --- | --- |
| `P3-SPEC-SOURCE` | `df6e0860e97a609efccbbdd67764e2dee44b0d36d086633e2f89dac232d7238e` | `d7468c8379b2860556146940734c0e61280811f72cef4c7b3cc1ed79513eb739` |
| `P3-SPEC-DISTILL` | `5c078b9509d48b8eccf863c9cf074b55d355c9bde28ff13a21446f093150e902` | `9979320f18e0d0de86f4cafd2dffad64634631f6d71ed7bd7bce148220bd8d1c` |
| `P3-SPEC-CLOSURE` | `3f0a9eb31b0fe77b1ef29979b88d01ff13d83f5c2f8a0de1ed09c49e39c67422` | `e163a9a47f71860955b9df12d790d64b234780ea22eca9c48a1a5f26f538ee6d` |
| `P3-SPEC-ELEMENTS` | `ac1305c8213f46b9b72af928fbf24f216a7a87cd28eff4a50e3b693815256c57` | `d326d4925b39299c9137d70968e7a749007460154942b1e197aa38c35937627c` |
| `P3-SPEC-PATTERNS` | `cef82d8eeab608d7bed3c04d50dacfe0f2b36799c22fbb5bfa42f2146195df96` | `f70abec15e06d121de485dac91b3efad19367a3eada31ee31133354112a683be` |
| `P3-SPEC-LAYOUT` | `46a9b20fd3b05510036f64024389487be3d90e4c2fb68731514fc93cb577881a` | `191b22af853d316b1e447fd32c649bcc744f18878b2e0c0a0cb800b76499a319` |

## Compiler Authority

Natural-language approved sections remain the primary semantic authority. Structured inventories and indexes are validation skeletons: they prove coverage, order, references, hashes, and conservation, but they cannot replace the approved prose.

The compiler may add only mechanical wrapper text:

- final document title
- table of contents
- section headings from approved section metadata
- source attribution lines
- separators
- reference index
- hash index
- conservation report

Any text that changes product behavior, UI elements, interaction paths, layout placement, copy meaning, validation rules, async or failure handling, permissions, or information hierarchy is semantic text and is forbidden unless already present in an approved upstream section.

## Closed Input Rule

Every compiler input must be represented as a closed input record with:

- allowed input type
- path
- sha256
- approval, review decision, or lock reference
- semantic role
- invalidation state that is not invalidated

Allowed input types are limited to `APPROVED_SEMANTIC_ARTIFACT`, `APPROVED_OPERATIONAL_INDEX`, `REVIEW_DECISION`, `SPEC_LOCK_REF`, `CONTROL_INDEX`, `VALIDATOR_RESULT`, and `SCHEMA`.

Forbidden inputs include unapproved candidates, local drafts, manual final fragments, rewrite suggestions, direct source PRD semantic reads, unhashed files, hash-drifted files, superseded locks without current references, and invalidated evidence.

## Deterministic Assembly Rule

The final DRD must be reproducible from the same closed input bundle. Section order must be explicit and stable. Filesystem order, modified time, locale collation, random values, git working tree status, and JSON object iteration order are not valid ordering sources.

The stage order is fixed:

1. `DRD-01`
2. `DRD-02`
3. `DRD-03`
4. `DRD-03B`
5. `DRD-04`

Section order inside a stage must be explicit. Duplicate stage and section slots are rejected.

## Semantic Conservation Rule

Every compiled section must reference approved `semantic_unit_ids`. A semantic unit may be compiled once. Unknown, duplicated, omitted, or added semantic units are blocking findings.

The conservation report must fail when it detects:

- semantic addition
- semantic omission
- hash drift
- unapproved input
- non-atomic semantic units
- nondeterministic output
- ordering conflict

Human review is allowed only to decide an upstream ambiguity or approval conflict. It is not a repair path that lets the compiler add missing product meaning.

## Output Package

The compiler output package must include:

- `FINAL_DRD.md`
- `compiler_input_bundle.json`
- `compiler_semantic_unit_inventory.json`
- `compiler_conservation_report.json`
- `final_drd_manifest.json`
- `final_drd_toc.json`
- `final_drd_reference_index.json`
- `final_drd_hash_index.json`
- `read_only_qa_boundary.json`

The output package is valid only when the final manifest, hash index, reference index, semantic inventory, and conservation report agree on the same input bundle and output hashes.

## Boundary

This spec candidate does not create `P3_SPEC_LOCK`, `P3_BUILD_LOCK`, repository implementation code, compiler output fixtures, final DRD files, or QA reports. Those belong to future gates after human review and lock creation.
