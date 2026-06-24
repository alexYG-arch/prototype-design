# P1-SPEC-07 Compiler Projections

## Projection Summary

| Projection ID | From | To | Purpose |
|---|---|---|---|
| `COMP-PROJ-001` | Approved semantic artifacts | `compiler_input_bundle.json` | Close and hash all allowed compiler inputs. |
| `COMP-PROJ-002` | Stage order and section order | `final_drd_toc.json` | Produce deterministic TOC without semantic invention. |
| `COMP-PROJ-003` | Approved sections | `FINAL_DRD.md` | Assemble approved semantics in deterministic order. |
| `COMP-PROJ-004` | Input paths, hashes, approvals, locks | `final_drd_reference_index.json` | Preserve traceability to approved sources. |
| `COMP-PROJ-005` | Input hashes, output hashes, schema hashes | `final_drd_hash_index.json` | Support reproducible verification. |
| `COMP-PROJ-006` | Semantic unit inventory comparison | `compiler_conservation_report.json` | Detect additions, omissions, drift, and nondeterminism. |
| `COMP-PROJ-007` | Compiler outputs and conservation status | `final_drd_manifest.json` | Bind final artifact identity and readiness state. |
| `COMP-PROJ-008` | Final compiled outputs | `READ_ONLY_QA_REPORT.md`, `qa_finding_index.json` | Optional `DRD-06` read-only QA findings. |
| `COMP-PROJ-009` | Approved atomic semantic unit inventories | `compiler_semantic_unit_inventory.json` | Preserve one row per smallest reviewable semantic decision. |

## Input Bundle Projection

`compiler_input_bundle.json` must project all allowed inputs into deterministic records.

Each record must include:

- `input_id`
- `input_type`
- `stage_id`
- `path`
- `sha256`
- `semantic_role`
- `approval_ref`
- `lock_ref`
- `schema_ref`
- `order_ref`
- `dependency_edges`

Dependency edges must use typed dependency edge rules from `P1-SPEC-06-VALIDATION-LOCKS`.

## Atomic Semantic Unit Inventory Projection

`compiler_semantic_unit_inventory.json` must project approved source semantics into atomic rows before final DRD assembly is considered conserved.

Each row must include:

- `semantic_unit_id`
- `unit_type`
- `unit_class`
- `stage_id`
- `source_path`
- `source_section_id`
- `source_span_ref`
- `source_hash`
- `approval_ref`
- `lock_ref`
- `parent_unit_id`
- `relationship_kind`
- `canonical_value`
- `unit_hash`
- `inventory_version`

The projection must preserve atomicity:

- One CTA per row.
- One copy string per row.
- One interaction node per row.
- One interaction edge per row.
- One Reaction per row.
- One guard, success, failure, cancel, async, handoff, retry, return, or exit path per row.
- One layout containment edge per row.
- One order, arrangement, sizing, width, height, scroll, content growth, carrier adaptation, safe-area, z-axis, or Material elevation decision per row.
- One presentation mode, shared pattern, message placement, or state placement per row.

Rows may reference parent rows, but parent rows do not absorb child semantics. A page row does not prove its CTAs, states, copy, interactions, or layout are conserved.

`unit_hash` must be computed from canonical unit fields, not from the paragraph containing the unit. If a paragraph contains three CTAs and two copy strings, the inventory must contain at least five corresponding atomic rows plus any required relationship rows.

## Final DRD Projection

`FINAL_DRD.md` is projected from approved section content.

Allowed transforms:

- Insert deterministic final title.
- Insert deterministic TOC generated from approved section IDs and titles.
- Insert deterministic section separators.
- Insert deterministic source attribution lines.
- Preserve approved section body text without semantic rewrite.
- Append deterministic reference and hash index sections.

Forbidden transforms:

- Summarizing approved text.
- Paraphrasing approved text.
- Filling missing UI states.
- Adding CTA, interaction, presentation, or layout details.
- Resolving contradictions by choosing one semantic side.
- Silently dropping approved sections.

If two approved inputs conflict, the compiler must report conflict and route to Human Gate. It cannot harmonize them.

## TOC Projection

`final_drd_toc.json` must include:

- `toc_entry_id`
- `stage_id`
- `section_id`
- `stage_order_index`
- `section_order_index`
- `heading_text`
- `source_path`
- `source_hash`

TOC heading text must come from approved source headings or fixed mechanical templates. It cannot be rewritten for style.

## Reference Index Projection

`final_drd_reference_index.json` must include:

- `reference_id`
- `compiled_section_id`
- `source_stage_id`
- `source_path`
- `source_hash`
- `approval_ref`
- `lock_ref`
- `validator_result_refs`
- `source_snapshot_identity`

The reference index is operational trace data. It must not introduce product semantics.

## Hash Index Projection

`final_drd_hash_index.json` must include:

- `input_bundle_hash`
- `semantic_hash`
- `mechanical_hash`
- `full_output_hash`
- `toc_hash`
- `reference_index_hash`
- `conservation_report_hash`
- `schema_hashes`
- `compiler_code_hash`

Hashes must be computed from deterministic canonical byte streams or deterministic JSON serialization with sorted keys and stable separators.

## Conservation Report Projection

`compiler_conservation_report.json` must include:

- `status`
- `approved_input_semantic_units`
- `compiled_output_semantic_units`
- `matched_semantic_units`
- `added_semantic_units`
- `omitted_semantic_units`
- `non_atomic_semantic_units`
- `hash_drift`
- `unapproved_inputs`
- `ordering_findings`
- `nondeterminism_findings`
- `read_only_qa_boundary_status`
- `human_review_required`

Every finding must point to path, section ID, semantic unit ID, and rule or check ID where applicable.

`non_atomic_semantic_units` must list inventory rows that combine multiple reviewable decisions or use source spans too broad to prove conservation.

## Manifest Projection

`final_drd_manifest.json` must be the entry point for downstream validation and Final Review.

It must bind:

- Output paths and hashes.
- Input bundle hash.
- Compiler identity.
- Schema hashes.
- Conservation report status.
- Approval and lock references for inputs.
- Read-only QA output references if `DRD-06` has run.

The manifest cannot declare final approval. Final approval remains Human Gate authority under review and promotion contracts.
