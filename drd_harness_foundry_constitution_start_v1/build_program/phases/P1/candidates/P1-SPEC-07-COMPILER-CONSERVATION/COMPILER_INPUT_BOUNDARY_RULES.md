# P1-SPEC-07 Compiler Input Boundary Rules

## Input Boundary

`DRD-05` must compile from a closed input bundle. The bundle is closed when every input file, hash, approval reference, lock reference, validator result reference, schema hash, and control index reference is listed before compilation starts.

The compiler must not discover semantic input dynamically while rendering final output.

## Allowed Input Types

| Input type | Required fields | Notes |
|---|---|---|
| `APPROVED_SEMANTIC_ARTIFACT` | `stage_id`, `path`, `sha256`, `review_decision_ref` or `lock_ref`, `section_index_ref` | Main semantic content source. |
| `APPROVED_OPERATIONAL_INDEX` | `stage_id`, `path`, `sha256`, `schema_ref`, `approval_ref` | Used for stable IDs, ordering, and trace joins. |
| `REVIEW_DECISION` | `path`, `sha256`, `subject_hash`, `decision`, `approved_sections` | Must approve the exact input subject. |
| `SPEC_LOCK_REF` | `lock_id`, `lock_hash`, `covered_paths`, `supersession_state` | Required once lock tooling exists. |
| `CONTROL_INDEX` | `path`, `sha256`, `purpose` | May support ordering or clause traceability only. |
| `VALIDATOR_RESULT` | `path`, `sha256`, `validator_identity`, `status` | Required when used as readiness evidence. |
| `SCHEMA` | `path`, `sha256`, `schema_id` | Required for structured compiler outputs. |

## Forbidden Input Types

The compiler must reject:

- `UNAPPROVED_CANDIDATE`
- `LOCAL_DRAFT`
- `MANUAL_FINAL_FRAGMENT`
- `CODEX_REWRITE_SUGGESTION`
- `DIRECT_SOURCE_PRD_SEMANTIC_READ`
- `UNHASHED_FILE`
- `HASH_DRIFTED_FILE`
- `SUPERSEDED_LOCK_WITHOUT_CURRENT_REF`
- `INVALIDATED_EVIDENCE`

## Input Bundle Schema Requirements

Future implementation must provide `repository/schemas/compiler/compiler_input_bundle.schema.json`.

The schema must require:

- `bundle_id`
- `bundle_version`
- `compiler_stage_id` with value `DRD-05`
- `source_snapshot_identity`
- `approved_semantic_artifacts`
- `approved_operational_indexes`
- `review_decisions`
- `lock_refs`
- `validator_results`
- `control_indexes`
- `schemas`
- `stage_order`
- `section_order`
- `closed_input_hash`

`closed_input_hash` must be computed from deterministic ordered records containing path, type, sha256, approval reference, and semantic role.

## Atomic Inventory Input Boundary

Every approved semantic artifact that contributes product, interaction, presentation, layout, or copy semantics must include an atomic inventory reference or a validator-produced atomic inventory projection.

Atomic inventory inputs must be listed in the closed input bundle with:

- `inventory_path`
- `inventory_hash`
- `inventory_schema_ref`
- `inventory_version`
- `source_artifact_ref`
- `source_artifact_hash`
- `approval_ref`
- `validator_result_ref`

The compiler must reject inventory that is:

- Generated after final compilation starts.
- Not tied to the approved source artifact hash.
- Not tied to the same approval or lock lineage as the source artifact.
- Coarser than the unit types required by the atomic inventory rules.
- Missing required unit fields.
- Produced by Codex without independent validator evidence.

## Approval Binding

Every semantic artifact must be approved by one of:

- A `REVIEW_DECISION` whose `subject_hash` matches the deterministic hash of the reviewed output set.
- A `SPEC_LOCK_REF` that covers the exact path and hash.
- A transitional approved Candidate reference explicitly allowed by the current build program before lock tooling exists.

The compiler must fail if an input only says "approved" in prose. Approval must be structured and hash-bound.

## Source PRD Boundary

The Source PRD identity must be present through upstream manifests and locks. `DRD-05` must not read the Source PRD to infer, supplement, or repair final content.

Allowed source-related fields:

- Source snapshot ID.
- Source snapshot path.
- Source snapshot hash.
- Upstream artifact lineage references.

Forbidden source-related behavior:

- Reading source text to add a missing page.
- Reading source text to write new layout instructions.
- Reading source text to create new failure copy.
- Reading source text to resolve interaction gaps.
- Reading source text to rewrite approved artifact language.

If approved artifacts appear incomplete relative to source identity, `DRD-05` must emit a conservation or readiness failure and route to Human Gate.

## Control Index Boundary

Control indexes may supply:

- Clause IDs.
- Stage IDs.
- Stage order indexes.
- Required output names.
- Ownership and traceability mappings.

Control indexes must not be treated as semantic product sources. If a control index mentions a stage or clause, that mention cannot become product content in `FINAL_DRD.md` unless an approved semantic artifact already contains the semantic content.

## Missing Input Policy

Missing input must not be patched by the compiler.

| Missing condition | Compiler action |
|---|---|
| Approved stage artifact missing | Stop with `REQUIRES_HUMAN_REVIEW`. |
| Required operational index missing | Stop with `FAIL_UNAPPROVED_INPUT` or `REQUIRES_HUMAN_REVIEW`, depending on approval state. |
| Review decision missing | Stop with `FAIL_UNAPPROVED_INPUT`. |
| Hash drift detected | Stop with `FAIL_HASH_DRIFT`. |
| Section order ambiguous | Stop with `FAIL_NONDETERMINISTIC_OUTPUT`. |
| Semantic unit inventory missing | Stop with `REQUIRES_HUMAN_REVIEW`; do not infer inventory from prose alone. |
| Atomic inventory too coarse | Stop with `REQUIRES_HUMAN_REVIEW`; do not accept paragraph-level or section-level conservation. |

## Read-Only QA Inputs

`DRD-06` may read:

- `FINAL_DRD.md`
- `final_drd_manifest.json`
- `compiler_input_bundle.json`
- `compiler_conservation_report.json`
- Approved upstream artifacts and indexes.
- Frozen source snapshot for consistency checking.

It may not use those inputs to rewrite final output.
