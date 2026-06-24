# P1-SPEC-07 Final DRD Assembly Rules

## Assembly Rule Families

| Rule ID | Clause | Rule |
|---|---|---|
| `COMP-RULE-001` | `DRD-CHARTER-011` | `DRD-05` final DRD assembly is performed by Python. |
| `COMP-RULE-002` | `DRD-CHARTER-011` | `DRD-05` consumes only approved stage artifacts, approved operational indexes, review decisions, locks, and control indexes. |
| `COMP-RULE-003` | `DRD-CHARTER-011` | The compiler must not add pages, states, CTAs, components, interactions, presentation modes, layout decisions, or user-facing copy. |
| `COMP-RULE-004` | `DRD-CHARTER-011` | Final output ordering must be deterministic and driven by explicit stage order and section order fields. |
| `COMP-RULE-005` | `DRD-CHARTER-011` | Compiler-added headings, separators, TOC rows, references, and hash rows must be mechanical and non-semantic. |
| `COMP-RULE-006` | `DRD-CHARTER-011` | Every compiled semantic unit must map back to approved input path, source section ID, input hash, and review or lock reference. |
| `COMP-RULE-007` | `DRD-CHARTER-011` | The compiler must fail when it detects semantic additions, semantic omissions, hash drift, unapproved inputs, or nondeterministic assembly. |
| `COMP-RULE-008` | `DRD-CHARTER-011` | Optional `DRD-06` QA is read-only and cannot mutate compiled outputs or approved inputs. |
| `COMP-RULE-009` | `DRD-CHARTER-011` | Semantic conservation must be checked with atomic semantic unit inventory, not paragraph-level or section-level inventory. |

## Assembly Plan

`final_drd_manifest.json` must contain an `assembly_plan` with:

- `compiler_id`
- `compiler_version`
- `compiler_code_hash`
- `schema_hashes`
- `stage_order`
- `section_order`
- `input_bundle_ref`
- `output_files`
- `conservation_report_ref`
- `semantic_hash`
- `mechanical_hash`
- `full_output_hash`

`stage_order` must use the declared stage order from upstream stage contracts:

1. `DRD-01`
2. `DRD-02`
3. `DRD-03`
4. `DRD-03B`
5. `DRD-04`

`DRD-00` source snapshot identity is carried through manifests and hashes, but `DRD-05` must not reread source to make new semantic decisions. `DRD-06` may read frozen source only for read-only QA.

## Section Ordering

Each compiled section must declare:

| Field | Requirement |
|---|---|
| `section_id` | Stable ID from an approved input artifact or approved operational index. |
| `stage_id` | One of the approved upstream semantic stages. |
| `stage_order_index` | Numeric order inherited from stage contracts. |
| `section_order_index` | Numeric order inside the approved stage artifact. |
| `source_path` | Approved upstream path. |
| `source_hash` | Current sha256 of the approved source path. |
| `approved_hash_ref` | Review decision, SPEC_LOCK, or approved manifest hash field. |
| `semantic_unit_count` | Count of semantic units expected from the source section. |
| `atomic_inventory_ref` | Reference to atomic semantic unit records for the section. |
| `atomic_inventory_hash` | Deterministic hash of atomic semantic unit records for the section. |

Sorting must use `stage_order_index`, then `section_order_index`, then `section_id`. Sorting by filesystem order, JSON object iteration order, current locale, modification time, git status, or human-readable title is forbidden.

## Atomic Inventory Assembly

The compiler must assemble and compare atomic semantic unit inventories before writing a passing final manifest.

Each approved source section must provide or derive an atomic inventory with one row per smallest reviewable semantic decision. The compiler may copy and join atomic inventory rows, but it must not merge rows to make conservation easier.

Required inventory partitions:

- Product inventory.
- Interaction inventory.
- Presentation inventory.
- Layout inventory.
- Copy inventory.
- Trace inventory.

The final compiled output must produce a compiled atomic inventory with the same semantic unit IDs or approved replacement mappings. The conservation report must compare input and output inventory by `semantic_unit_id`, `unit_type`, `canonical_value`, `unit_hash`, `source_hash`, and approval reference.

If atomic inventory is missing for a section that contains reviewable semantic decisions, the compiler must stop with `REQUIRES_HUMAN_REVIEW`. It must not downgrade to paragraph-level conservation.

## Allowed Mechanical Text

The compiler may add mechanical text only for:

- Final document title.
- Generated table of contents labels.
- Section source attribution labels.
- Reference index labels.
- Hash index labels.
- Deterministic section separators.

Allowed mechanical text must use fixed templates. Template variables are limited to source IDs, file paths, section IDs, stage IDs, hashes, and ordering numbers.

Forbidden mechanical text includes:

- New explanatory product paragraphs.
- New UI labels or CTA labels.
- New error messages or empty-state copy.
- New interaction descriptions.
- New layout guidance.
- New reviewer conclusions.
- New implementation recommendations.

## Final DRD Manifest

`final_drd_manifest.json` must bind:

- `final_drd_path`
- `final_drd_hash`
- `semantic_hash`
- `mechanical_hash`
- `input_bundle_hash`
- `toc_hash`
- `reference_index_hash`
- `hash_index_hash`
- `conservation_report_hash`
- `approved_input_count`
- `compiled_section_count`
- `compiled_semantic_unit_count`
- `omitted_semantic_unit_count`
- `added_semantic_unit_count`
- `hash_drift_count`
- `unapproved_input_count`
- `conservation_status`

`conservation_status` may be:

- `PASS`
- `FAIL_SEMANTIC_ADDITION`
- `FAIL_SEMANTIC_OMISSION`
- `FAIL_HASH_DRIFT`
- `FAIL_UNAPPROVED_INPUT`
- `FAIL_NONDETERMINISTIC_OUTPUT`
- `REQUIRES_HUMAN_REVIEW`

## Hash Partitions

The compiler must partition hashes:

| Hash | Includes | Excludes |
|---|---|---|
| `semantic_hash` | Approved semantic source content in compiled order. | Mechanical headings, TOC, reference index, hash index, audit-only fields. |
| `mechanical_hash` | Allowed mechanical wrappers and generated indexes. | Approved semantic source content. |
| `full_output_hash` | Full final artifact bytes. | None. |

Conservation checks compare `semantic_hash` and semantic unit inventory. Full output hash alone is not sufficient because it cannot prove no semantic drift.

## Idempotence Rule

Running the compiler twice with the same input bundle and same compiler identity must produce the same:

- `FINAL_DRD.md`
- `final_drd_manifest.json`, excluding explicitly marked audit-only runtime fields.
- `final_drd_toc.json`
- `final_drd_reference_index.json`
- `final_drd_hash_index.json`
- `compiler_conservation_report.json`

If rerun output differs, the compiler must fail `FAIL_NONDETERMINISTIC_OUTPUT`.
