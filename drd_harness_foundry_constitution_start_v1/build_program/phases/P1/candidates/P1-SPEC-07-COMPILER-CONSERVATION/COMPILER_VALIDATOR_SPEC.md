# P1-SPEC-07 Compiler Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `compiler_input_bundle_validator` | Ensures `DRD-05` inputs are closed, allowed, hash-bound, and approved. |
| `compiler_approval_binding_validator` | Ensures each semantic input is bound to review decision, lock, or allowed transitional approval reference. |
| `compiler_hash_drift_validator` | Detects current hash mismatch against approved input hashes, review decisions, locks, schemas, and control indexes. |
| `compiler_ordering_validator` | Ensures stage order and section order are explicit and deterministic. |
| `final_drd_assembly_validator` | Ensures final output contains only approved section semantics and allowed mechanical labels. |
| `atomic_semantic_unit_inventory_validator` | Ensures semantic inventory uses one row per smallest reviewable semantic decision. |
| `semantic_addition_validator` | Detects pages, states, CTAs, components, interactions, copy, presentation, or layout semantics absent from approved inputs. |
| `semantic_omission_validator` | Detects approved semantic units missing from compiled output. |
| `compiler_idempotence_validator` | Recompiles from the same input bundle and compares outputs for deterministic equivalence. |
| `compiler_manifest_validator` | Ensures final manifest binds outputs, hashes, compiler identity, schema hashes, conservation report, and readiness state. |
| `read_only_qa_boundary_validator` | Ensures `DRD-06` emits only read-only QA outputs and mutates no final or approved input artifact. |

## Checks

### COMP-CHECK-001 Closed Input Bundle

Fail if `compiler_input_bundle.json` omits any semantic artifact, operational index, review decision, lock ref, validator result, schema, or control index used by compilation.

### COMP-CHECK-002 Allowed Input Types

Fail if compiler inputs include unapproved Candidates, drafts, manual final fragments, Codex rewrite suggestions, direct Source PRD semantic reads, unhashed files, invalidated evidence, or superseded lock refs.

### COMP-CHECK-003 Approval Binding

Fail if a semantic input lacks a structured approval reference whose hash binds to the current input set.

Fail if approval is prose-only, stale, superseded, invalidated, or not tied to the current subject hash.

### COMP-CHECK-004 Hash Drift

Fail if any input path, schema path, review decision path, lock ref, validator result, or control index hash differs from the approved or bundled hash.

### COMP-CHECK-005 Deterministic Ordering

Fail if a compiled section lacks `stage_order_index`, `section_order_index`, or stable `section_id`.

Fail if ordering depends on filesystem order, modification time, locale, random ID, git status, or JSON object iteration order.

### COMP-CHECK-006 Allowed Mechanical Text

Fail if compiler-added text is outside fixed mechanical templates for title, TOC, section separators, source attribution, reference index, hash index, or manifest metadata.

### COMP-CHECK-007 Semantic Addition

Fail if final output contains a page, state, CTA, component, interaction, presentation mode, layout decision, user-facing copy, product promise, acceptance decision, or implementation recommendation not present in approved semantic inputs.

### COMP-CHECK-008 Semantic Omission

Fail if any approved semantic unit expected by the input bundle is absent from compiled final output and not explicitly marked excluded by an approved upstream artifact.

### COMP-CHECK-009 Approved Text Preservation

Fail if approved prose is summarized, paraphrased, merged, normalized for style, or rewritten in a way that changes or could change semantic meaning.

### COMP-CHECK-010 Conflict Handling

Fail if the compiler resolves conflicting approved inputs by choosing, merging, or rewriting semantics instead of reporting `REQUIRES_HUMAN_REVIEW`.

### COMP-CHECK-011 Manifest Completeness

Fail if `final_drd_manifest.json` omits output hashes, input bundle hash, compiler identity, schema hashes, conservation status, or conservation report reference.

### COMP-CHECK-012 Hash Partition Completeness

Fail if `semantic_hash`, `mechanical_hash`, or `full_output_hash` is missing, unreproducible, or computed from undocumented inputs.

### COMP-CHECK-013 Idempotence

Fail if recompilation from the same closed input bundle and same compiler identity produces different semantic output, structured indexes, or conservation findings.

### COMP-CHECK-014 Read-Only QA Boundary

Fail if `DRD-06` writes anything except `READ_ONLY_QA_REPORT.md` and `qa_finding_index.json`.

Fail if `DRD-06` mutates approved artifacts, source snapshots, `FINAL_DRD.md`, final manifests, review decisions, locks, compiler indexes, or input bundles.

### COMP-CHECK-015 Human Review Routing

Fail if unresolved missing input, conflict, semantic addition, semantic omission, hash drift, or nondeterminism is treated as passed without Human Gate routing.

### COMP-CHECK-016 Atomic Inventory Presence

Fail if a semantic artifact containing product, interaction, presentation, layout, or copy semantics lacks atomic inventory records or a validator-produced atomic inventory projection.

### COMP-CHECK-017 Atomic Inventory Granularity

Fail if one inventory row combines multiple reviewable semantic decisions.

Examples that must fail:

- A page row that also includes page states, CTAs, inputs, copy, interactions, or layout.
- A flow row that includes multiple graph nodes or edges.
- A component row that includes variants, row actions, empty state, loading state, pagination, and permission behavior.
- A layout row that combines containment, ordering, scrolling, carrier adaptation, and z-axis decisions.
- A failure handling row that combines failure reason, copy, retry, exit, and recovery path.

### COMP-CHECK-018 Atomic Unit Required Fields

Fail if an atomic unit omits `semantic_unit_id`, `unit_type`, `unit_class`, `stage_id`, `source_path`, `source_section_id`, `source_span_ref`, `source_hash`, `approval_ref`, `canonical_value`, `unit_hash`, or `inventory_version`.

### COMP-CHECK-019 Atomic Unit Type Coverage

Fail if the inventory uses a generic catch-all type instead of the required atomic type for page, state, CTA, component, input, copy string, interaction node, interaction edge, Reaction, layout containment, order, sizing, scroll, carrier adaptation, z-axis, Material elevation, presentation mode, or trace binding.

### COMP-CHECK-020 Parent Does Not Prove Child

Fail if a parent semantic unit is used as proof that child states, elements, copy, interactions, or layout decisions are conserved without separate child atomic unit records.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/compiler/compiler_input_bundle.schema.json`
- `repository/schemas/compiler/final_drd_manifest.schema.json`
- `repository/schemas/compiler/final_drd_toc.schema.json`
- `repository/schemas/compiler/final_drd_reference_index.schema.json`
- `repository/schemas/compiler/final_drd_hash_index.schema.json`
- `repository/schemas/compiler/compiler_conservation_report.schema.json`
- `repository/schemas/compiler/compiler_semantic_unit_inventory.schema.json`
- `repository/schemas/compiler/compiler_atomic_semantic_unit.schema.json`
- `repository/schemas/compiler/read_only_qa_boundary.schema.json`

## Validator Result Requirements

Every compiler validation result must include:

- `validator_id`
- `validator_version`
- `validator_code_hash`
- `schema_hashes`
- `input_bundle_hash`
- `checked_output_hashes`
- `status`
- `findings`
- `created_artifacts`
- `mutated_artifacts`

`mutated_artifacts` must be empty for validators and for `DRD-06` read-only QA.
