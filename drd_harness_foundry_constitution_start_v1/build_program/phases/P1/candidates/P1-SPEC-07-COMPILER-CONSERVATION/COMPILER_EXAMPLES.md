# P1-SPEC-07 Compiler Examples

## Positive Example: Approved Inputs Compile

```json
{
  "bundle_id": "CIB-001",
  "compiler_stage_id": "DRD-05",
  "approved_semantic_artifacts": [
    {
      "input_id": "DRD01-APPROVED",
      "input_type": "APPROVED_SEMANTIC_ARTIFACT",
      "stage_id": "DRD-01",
      "path": "artifacts/DRD-01/SECTION_INDEX.md",
      "sha256": "hash-drd01",
      "approval_ref": "reviews/DRD-01-REVIEW_DECISION.json",
      "section_index_ref": "artifacts/DRD-01/section_index.json"
    }
  ],
  "stage_order": [
    {"stage_id": "DRD-01", "stage_order_index": 10},
    {"stage_id": "DRD-02", "stage_order_index": 20},
    {"stage_id": "DRD-03", "stage_order_index": 30},
    {"stage_id": "DRD-03B", "stage_order_index": 40},
    {"stage_id": "DRD-04", "stage_order_index": 50}
  ],
  "closed_input_hash": "closed-hash"
}
```

Why this passes:

- The input type is allowed.
- The input is hash-bound.
- Approval is structured.
- Stage order is explicit.

## Positive Example: Mechanical TOC Entry

```json
{
  "toc_entry_id": "TOC-DRD01-001",
  "stage_id": "DRD-01",
  "section_id": "SEC-OVERVIEW",
  "stage_order_index": 10,
  "section_order_index": 1,
  "heading_text": "Overview",
  "source_path": "artifacts/DRD-01/SECTION_INDEX.md",
  "source_hash": "hash-drd01"
}
```

Why this passes:

- The TOC entry is derived from approved section identity.
- It adds navigation structure only.
- It does not create product semantics.

## Positive Example: Read-Only QA Finding

```json
{
  "qa_finding_id": "QA-001",
  "finding_type": "CONSISTENCY_QUESTION",
  "read_paths": [
    "FINAL_DRD.md",
    "final_drd_manifest.json"
  ],
  "written_paths": [
    "READ_ONLY_QA_REPORT.md",
    "qa_finding_index.json"
  ],
  "mutation_claim": "NO_MUTATION"
}
```

Why this passes:

- `DRD-06` writes only QA outputs.
- It does not patch final or upstream artifacts.
- The finding can be routed to Human Gate.

## Positive Example: Atomic Semantic Unit Inventory

```json
[
  {
    "semantic_unit_id": "UNIT-PAGE-ACCOUNT-SETTINGS",
    "unit_type": "PAGE",
    "unit_class": "Product object",
    "stage_id": "DRD-02",
    "source_path": "artifacts/DRD-02/PAGES.md",
    "source_section_id": "SEC-ACCOUNT-SETTINGS",
    "source_span_ref": "heading:Account settings",
    "source_hash": "hash-pages",
    "approval_ref": "reviews/DRD-02-REVIEW_DECISION.json",
    "lock_ref": "SPEC-LOCK-DRD02",
    "parent_unit_id": null,
    "relationship_kind": "ROOT",
    "canonical_value": "Account settings page exists.",
    "unit_hash": "unit-hash-page",
    "inventory_version": "1.0"
  },
  {
    "semantic_unit_id": "UNIT-CTA-SAVE-ACCOUNT",
    "unit_type": "CTA",
    "unit_class": "Product object",
    "stage_id": "DRD-03",
    "source_path": "artifacts/DRD-03/INTERACTIONS.md",
    "source_section_id": "SEC-ACCOUNT-SAVE",
    "source_span_ref": "clickable:CLK-SAVE-ACCOUNT",
    "source_hash": "hash-interactions",
    "approval_ref": "reviews/DRD-03-REVIEW_DECISION.json",
    "lock_ref": "SPEC-LOCK-DRD03",
    "parent_unit_id": "UNIT-PAGE-ACCOUNT-SETTINGS",
    "relationship_kind": "CONTAINED_BY",
    "canonical_value": "Save account button triggers RX-SAVE-ACCOUNT.",
    "unit_hash": "unit-hash-cta",
    "inventory_version": "1.0"
  }
]
```

Why this passes:

- The page and CTA are separate atomic rows.
- The CTA has its own source span, approval reference, parent relationship, and unit hash.
- The page row does not claim to prove the CTA.

## Negative Example: Compiler Adds Missing CTA

```json
{
  "compiled_section_id": "SEC-ACCOUNT-DELETE",
  "compiler_added_text": "The account page includes a Delete account button.",
  "source_refs": []
}
```

Expected result: fail with `COMP-CHECK-007`.

Reason:

- A CTA is a semantic product object.
- It has no approved source reference.
- The compiler cannot add missing product capability or UI content.

## Negative Example: Compiler Fixes Layout Gap

```json
{
  "compiled_section_id": "SEC-DASHBOARD-LAYOUT",
  "compiler_added_text": "On mobile, the filter drawer slides from the bottom with Material elevation level 3.",
  "source_refs": []
}
```

Expected result: fail with `COMP-CHECK-007` and `REQUIRES_HUMAN_REVIEW`.

Reason:

- Mobile adaptation and Material z-axis are layout semantics.
- If upstream layout is thin or missing, repair must happen in an upstream Candidate and Human Gate review.

## Negative Example: Unapproved Candidate Input

```json
{
  "input_id": "DRD04-DRAFT",
  "input_type": "UNAPPROVED_CANDIDATE",
  "stage_id": "DRD-04",
  "path": "candidates/DRD-04/DRAFT.md",
  "sha256": "draft-hash",
  "approval_ref": null
}
```

Expected result: fail with `COMP-CHECK-002` and `COMP-CHECK-003`.

Reason:

- `DRD-05` cannot consume unapproved Candidates.
- Candidate text is not canonical evidence for final compilation.

## Negative Example: Hash Drift

```json
{
  "input_id": "DRD03-APPROVED",
  "path": "artifacts/DRD-03/INTERACTION_GRAPH.md",
  "bundled_sha256": "old-hash",
  "current_sha256": "new-hash",
  "approval_ref": "reviews/DRD-03-REVIEW_DECISION.json"
}
```

Expected result: fail with `COMP-CHECK-004`.

Reason:

- The approved input changed after review.
- Compilation must stop until review, promotion, lock, or repair evidence is current.

## Negative Example: Nondeterministic Ordering

```json
{
  "section_sorting": "filesystem_directory_order",
  "stage_order": null,
  "section_order": null
}
```

Expected result: fail with `COMP-CHECK-005`.

Reason:

- Filesystem order is not a stable semantic order.
- The compiler must use explicit stage and section order fields.

## Negative Example: Read-Only QA Mutates Final Output

```json
{
  "drd06_run_id": "QA-RUN-002",
  "written_paths": [
    "READ_ONLY_QA_REPORT.md",
    "qa_finding_index.json",
    "FINAL_DRD.md"
  ]
}
```

Expected result: fail with `COMP-CHECK-014`.

Reason:

- `DRD-06` is read-only.
- Final output repair requires governed repair workflow, not direct QA mutation.

## Negative Example: Non-Atomic Inventory Row

```json
{
  "semantic_unit_id": "UNIT-ACCOUNT-SETTINGS-SCREEN",
  "unit_type": "SCREEN_BUNDLE",
  "source_span_ref": "section:Account settings",
  "canonical_value": "Account settings page includes profile fields, save and cancel buttons, validation messages, mobile layout, and error recovery."
}
```

Expected result: fail with `COMP-CHECK-017`, `COMP-CHECK-018`, and `COMP-CHECK-019`.

Reason:

- The row combines a page, fields, CTAs, copy, layout, validation, and recovery semantics.
- The source span is too broad to prove atomic conservation.
- Each smallest reviewable decision must be inventoried separately.
