# P1-SPEC-07 Compiler Conservation Contract

## Purpose

This contract owns `DRD-CHARTER-011` for deterministic final DRD compilation.

`DRD-05` is a Python compiler stage. It assembles already approved DRD section artifacts, operational indexes, tables of contents, references, hashes, and final manifests into final DRD outputs. It has no authority to create new product, page, state, CTA, component, interaction, information presentation, or layout decisions.

## Scope

This Candidate defines:

- Allowed `DRD-05` compiler inputs.
- Deterministic final DRD assembly.
- Conservation checks that prove output semantics are fully sourced from approved inputs.
- Read-only post-compile QA boundary for `DRD-06`.
- Future implementation traceability for compiler modules, schemas, validators, and tests.

This Candidate does not define:

- Stage artifact lineage rules already owned by `P1-SPEC-02-STAGE-ARTIFACTS`.
- Review, promotion, SPEC_LOCK, BUILD_LOCK, or invalidation mechanics already owned by `P1-SPEC-06-VALIDATION-LOCKS`.
- New product semantics, interaction semantics, presentation semantics, layout semantics, Figma rendering, or repository business implementation.

## Authority Model

| Actor | Authority | Prohibited |
|---|---|---|
| Python compiler | Deterministically assembles approved inputs, writes final artifacts, writes manifests and conservation reports. | Making semantic decisions, rewriting approved prose, inventing missing content, accepting unapproved inputs. |
| Compiler conservation validator | Compares final outputs to source input hashes, approved section hashes, assembly plan, and semantic token inventories. | Repairing final output, approving unresolved drift, changing locks or review decisions. |
| Codex | Performs optional `DRD-06` read-only QA when a governed workpack requests it. | Mutating `FINAL_DRD.md`, manifests, approved sections, locks, or compiler inputs. |
| Human Gate | Reviews final readiness, unresolved compiler findings, and final QA findings. | Delegating approval to compiler output text or Codex self-claims. |

## Compiler Conservation Principle

Compilation is conservative when every semantic unit in the compiled final output is traceable to exactly one approved upstream source or to an allowed mechanical assembly label.

Allowed mechanical assembly labels are limited to:

- Deterministic heading wrappers.
- Deterministic table of contents entries.
- Deterministic reference index entries.
- Deterministic hash index entries.
- Deterministic section separators.
- Deterministic manifest metadata.

Mechanical labels must not add product meaning. They can describe position, source, identity, or hash, but cannot introduce pages, states, CTA labels, components, interactions, layouts, user promises, error copy, platform behavior, or acceptance decisions that are absent from approved inputs.

## Required Compiler Inputs

`DRD-05` must consume only:

- Approved `DRD-01`, `DRD-02`, `DRD-03`, `DRD-03B`, and `DRD-04` semantic artifacts.
- Their approved operational indexes.
- Review decisions bound to current subject hashes.
- Stage manifests that preserve source snapshot identity.
- Required SPEC_LOCK or approved Candidate references when lock tooling is not yet available in the build program.
- Control indexes needed only for ordering, identity, and clause traceability.

The compiler must reject:

- Unapproved Candidates.
- Local drafts.
- Direct PRD source reads for new semantic decisions.
- Codex-generated rewrite suggestions.
- Manually edited final DRD fragments.
- Inputs whose current hash differs from the hash in their review decision, lock, or approved manifest.

## Required Compiler Outputs

`DRD-05` may produce:

- `FINAL_DRD.md`
- `final_drd_manifest.json`
- `final_drd_toc.json`
- `final_drd_reference_index.json`
- `final_drd_hash_index.json`
- `compiler_input_bundle.json`
- `compiler_conservation_report.json`

No other final-stage output is allowed unless a later approved Spec explicitly extends this contract.

## Semantic Unit Classes

The conservation validator must compare the following semantic unit classes:

| Class | Examples | Conservation requirement |
|---|---|---|
| Product object | Page, state, overlay, component, element, CTA, input, data object. | Must originate from approved upstream semantic artifacts. |
| Interaction object | Node, edge, Reaction, async path, handoff path, exit path, failure path. | Must originate from approved interaction closure outputs. |
| Presentation object | Shared pattern, information presentation mode, message placement, state placement. | Must originate from approved presentation outputs. |
| Layout object | Region, containment, order, carrier adaptation, z-axis/elevation, scroll rule. | Must originate from approved layout outputs. |
| Copy object | User-facing message, label, error, empty state, processing text, recovery instruction. | Must originate from approved upstream artifacts. |
| Trace object | Clause reference, source hash, review decision, validator result, lock reference. | Must originate from approved manifests, control indexes, or lock evidence. |

## Atomic Semantic Unit Inventory

Semantic unit inventory must be atomic. Atomic means one inventory row represents one smallest reviewable semantic decision, not a paragraph, section, screen, or mixed bundle of decisions.

The compiler must reject paragraph-level or section-level inventory if smaller product, interaction, presentation, copy, or layout decisions are present inside it.

### Atomicity Rules

| Rule ID | Rule |
|---|---|
| `ATOM-RULE-001` | A page is one atomic unit. Each page state on that page is a separate atomic unit. |
| `ATOM-RULE-002` | A CTA, button, menu item, link, row action, icon action, gesture, or keyboard action is a separate atomic unit. |
| `ATOM-RULE-003` | A component definition, component instance, component variant, and component state are separate atomic units. |
| `ATOM-RULE-004` | An input field, selectable option set, validation rule, disabled rule, permission rule, and data binding are separate atomic units. |
| `ATOM-RULE-005` | Each user-facing copy string is a separate atomic unit, including label, helper text, placeholder, processing text, success text, failure text, empty text, recovery instruction, and terminal explanation. |
| `ATOM-RULE-006` | Each interaction graph node, edge, Reaction, guard condition, success path, failure path, cancel path, async path, handoff path, retry path, return path, and exit path is a separate atomic unit. |
| `ATOM-RULE-007` | Each presentation mode decision, shared pattern decision, message placement, and state placement is a separate atomic unit. |
| `ATOM-RULE-008` | Each layout region, containment parent-child edge, sibling order rule, arrangement rule, sizing rule, width behavior, height or scroll behavior, content growth rule, carrier adaptation rule, safe-area or system-bar rule, and z-axis or Material elevation rule is a separate atomic unit. |
| `ATOM-RULE-009` | A relationship is a separate atomic unit when removing it changes meaning, reachability, hierarchy, containment, ordering, visibility, or user action. |
| `ATOM-RULE-010` | Trace-only units are atomic when they bind one source, approval, lock, validator, schema, or hash relationship. |

### Required Atomic Unit Fields

Every atomic semantic unit record must include:

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

`source_span_ref` may be a line range, structured object ID, table row ID, graph node ID, or schema pointer. It must be specific enough to locate the approved source decision. A whole file or whole section reference is insufficient when smaller source spans exist.

### Atomic Unit Type Minimum Set

The inventory schema must include at least these unit types:

- `PAGE`
- `PAGE_STATE`
- `OVERLAY`
- `REGION`
- `COMPONENT_DEFINITION`
- `COMPONENT_INSTANCE`
- `COMPONENT_VARIANT`
- `ELEMENT`
- `CTA`
- `INPUT_FIELD`
- `OPTION`
- `VALIDATION_RULE`
- `DATA_OBJECT`
- `DATA_FIELD`
- `COPY_STRING`
- `GRAPH_NODE`
- `GRAPH_EDGE`
- `REACTION`
- `GUARD_CONDITION`
- `ASYNC_PATH`
- `HANDOFF_PATH`
- `FAILURE_PATH`
- `CANCEL_PATH`
- `RETRY_PATH`
- `RETURN_PATH`
- `EXIT_PATH`
- `PRESENTATION_MODE`
- `SHARED_PATTERN`
- `MESSAGE_PLACEMENT`
- `STATE_PLACEMENT`
- `CONTAINMENT_EDGE`
- `ORDER_RULE`
- `ARRANGEMENT_RULE`
- `SIZING_RULE`
- `WIDTH_BEHAVIOR`
- `HEIGHT_SCROLL_BEHAVIOR`
- `CONTENT_GROWTH_RULE`
- `CARRIER_ADAPTATION_RULE`
- `SAFE_AREA_RULE`
- `Z_AXIS_LAYER`
- `MATERIAL_ELEVATION`
- `TRACE_BINDING`

Future implementation may add unit types only by approved schema evolution. Added unit types must remain atomic and must not become catch-all containers.

### Non-Atomic Inventory Rejection

The following inventory records are invalid:

- One row for "account settings page" that also contains its states, actions, inputs, copy, and layout.
- One row for "checkout flow" that contains multiple graph nodes and edges.
- One row for "mobile layout" that contains containment, order, scrolling, safe-area, and z-axis decisions.
- One row for "error handling" that contains multiple failure reasons, messages, recovery actions, and exits.
- One row for "table component" that contains row actions, columns, empty state, loading state, sorting, pagination, and permission behavior.

The compiler must fail if conservation can only be proven at these coarse levels.

## Determinism Requirements

Compilation must be reproducible. Given the same approved inputs, same assembly rules, same validator version and schema hashes, the compiler must produce byte-identical semantic output and equivalent structured manifests.

The compiler must not place wall-clock timestamps, machine-local paths, nondeterministic UUIDs, random ordering, current git branch names, or current user names in semantic output. Build-time metadata may appear only in structured audit fields that are excluded from semantic conservation hashes and explicitly marked as non-semantic.

## `DRD-06` Read-Only QA Boundary

`DRD-06` reads the compiled final DRD, final manifest, approved upstream hashes, and frozen source identity to report consistency findings.

`DRD-06` may produce only:

- `READ_ONLY_QA_REPORT.md`
- `qa_finding_index.json`

`DRD-06` must not mutate:

- Approved upstream artifacts.
- `FINAL_DRD.md`.
- Any final DRD manifest or compiler index.
- Review decisions.
- SPEC_LOCK or BUILD_LOCK artifacts.
- Source snapshots.

If `DRD-06` discovers an issue, the issue is routed to Human Gate and repair workpack generation under validation lock rules. It cannot patch the compiled artifact in place.

## Failure Policy

The compiler must fail closed. If required input is missing, unapproved, hash-drifted, ambiguous, or semantically incomplete, `DRD-05` must stop and emit a structured failure report. It must not fill the gap.

If a final DRD cannot be compiled without adding semantics, the compiler must report `REQUIRES_HUMAN_REVIEW` and identify the missing approved source. Human review may approve a repair Candidate or authorize a new upstream stage Candidate, but the compiler itself remains non-authoritative.
