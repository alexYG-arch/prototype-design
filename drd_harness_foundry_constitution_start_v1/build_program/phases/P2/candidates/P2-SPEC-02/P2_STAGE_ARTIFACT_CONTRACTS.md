# P2-SPEC-02 Stage Artifact Contracts

## Scope

`P2-SPEC-02` turns the approved `P2-SPEC-01` skeleton into exact stage artifact obligations for the Tiny Brief Intake vertical slice. It does not implement repository code, create `P2_SPEC_LOCK`, create `P2_BUILD_LOCK`, or modify P1 artifacts.

## Upstream Authority

| Authority | Path | Binding |
|---|---|---|
| P2-SPEC-01 review | `build_program/phases/P2/candidates/P2-SPEC-01/REVIEW_DECISION.json` | `ca6356eb90a410915bdbf670bb79d69d7d08cc10152a664bb8085f06a8be1f03` |
| P2-SPEC-01 subject hash | `P2-SPEC-01` generated outputs | `ce3c5f5fdd9afca9e7fbcfb08a5ad7afc83b5e3e8823f6058b98223a3b840a0e` |
| P2 artifact skeleton | `P2_ARTIFACT_INVENTORY.json` | `73458134a4533a541b6d8f979482eda4648082101ea9cd896849be12e6faf207` |
| P2 PRD inventory | `P2_PRD_ELEMENT_INVENTORY.json` | `94671b7fb0cd2dccf1d0b4aa51297055c85ceb3f06d882472bb3a0159a8f1a12` |
| P2 interaction edges | `P2_INTERACTION_EDGE_TABLE.json` | `0d5d9397ddbd90dd3c580b6f7a25f7ac4a2b6de5ed109ab215198a90017d1668` |
| P2 layout parameters | `P2_LAYOUT_VALIDATION_PARAMETERS.json` | `0638673f42dc3394e7d7f1023158476db0774e41e454abd43ffbfd241d959368` |

## Universal Artifact Contract

Every P2 vertical slice artifact must declare:

- `artifact_id`.
- `stage_id`.
- `fixture_id` equal to `tiny_brief_intake`.
- `path`.
- `schema_ref` or explicit `schema_ref: null` with a validator explanation.
- `source_refs`.
- `upstream_artifact_refs`.
- `upstream_hashes`.
- `validator_ref`.
- `review_gate`.
- `promotion_state`.
- `invalidation_inputs`.

`P2_ARTIFACT_FIELD_CONTRACTS.json` makes this obligation machine-checkable for each artifact. `P2_SCHEMA_VALIDATOR_COVERAGE.json` records whether each non-null schema and validator reference currently resolves to a repository-local file, and records explicit reasons for artifacts whose `schema_ref` is `null`.

Artifacts that carry semantic content must also declare whether the content is copied from the PRD, deduced from locked rules and fixture premises, or a human-review-required gap. No artifact may add a second page, second primary task, new workflow, or product capability without a human review gap record.

## Stage Contracts

| Stage | Required artifact paths | Review gate | Main validator |
|---|---|---|---|
| `DRD-00-SOURCE-FREEZE` | `repository/fixtures/p2/tiny_brief_intake/source/source_prd.md`, `repository/fixtures/p2/tiny_brief_intake/source_snapshot_manifest.json` | none | `repository/src/drd_harness/stages/source_snapshot.py` |
| `DRD-01-PRD-ELEMENTS` | `prd_element_inventory.json`, `derived_element_decisions.json`, `product_expansion_gaps.json` | Human review only for expansion gaps | `repository/src/drd_harness/validators/prd_adoption.py` |
| `DRD-02-REASONING` | `inference_records.json`, `structural_completion_review.json` | Human review for unresolved or inductive candidates | `repository/src/drd_harness/validators/reasoning.py` |
| `DRD-03-INTERACTION` | `interaction_graph.json`, `clickable_inventory.json`, `async_behavior.json`, `failure_recovery.json`, `interaction_messages.json` | Review A if edge closure or copy scope is disputed | `repository/src/drd_harness/validators/interaction_closure.py` |
| `DRD-04-PRESENTATION-LAYOUT` | `information_presentation_registry.json`, `shared_component_registry.json`, `natural_language_layout.json`, `carrier_adaptation_profile.json`, `containment_hierarchy.json`, `z_axis_layering.json` | Review B if layout or shared pattern judgment is disputed | `repository/src/drd_harness/validators/layout_completeness.py` |
| `DRD-05-COMPILATION` | `compiler_input_bundle.json`, `compiler_semantic_unit_inventory.json`, `compiler_conservation_report.json`, `FINAL_DRD.md` | final review input | `repository/src/drd_harness/validators/compiler_conservation.py` |
| `DRD-06-FINAL-REVIEW` | `final_drd_manifest.json`, `final_drd_hash_index.json`, `final_drd_reference_index.json`, `final_review_target.json`, `final_review_decision.json` | final Human Gate | `repository/src/drd_harness/validators/spec_validator.py` |

## Stage Order

The P2 vertical slice uses strict order:

```text
DRD-00 -> DRD-01 -> DRD-02 -> DRD-03 -> DRD-04 -> DRD-05 -> DRD-06
```

No later stage may consume an unapproved semantic artifact. `DRD-05` may consume only approved or validator-passing upstream semantic units plus their hashes.

## Source Permanence Rule

`source_prd.md` is the immutable PRD source for the fixture after `DRD-00`. Natural-language source remains the primary semantic authority; structured inventories are indexes and verification skeletons.

## Non-Goals

This candidate does not generate the fixture artifacts themselves. It specifies exact obligations so P2 implementation workpacks can create those artifacts only after `P2_SPEC_LOCK`.
