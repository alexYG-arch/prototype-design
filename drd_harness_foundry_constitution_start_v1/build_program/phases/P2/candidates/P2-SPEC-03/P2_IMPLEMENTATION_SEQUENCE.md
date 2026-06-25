# P2 Implementation Sequence

## Precondition
P2 implementation is not allowed to start until `P2_SPEC_LOCK` exists and binds the approved P2-SPEC-01, P2-SPEC-02, and P2-SPEC-03 review decisions.

## Sequence
1. `P2-IMPL-01` creates source snapshot and PRD element inventory fixtures, then validates source hash, PRD inventory coverage, and product-expansion handling.
2. `P2-IMPL-02` creates deduction records, interaction closure, async behavior, failure recovery, and interaction messages, then validates reasoning trace, clickable closure, and failure copy.
3. `P2-IMPL-03` creates presentation and layout records, including desktop, tablet, mobile iOS, mobile Material, containment hierarchy, and z-axis layering, then validates presentation pattern and layout carrier coverage.
4. `P2-IMPL-04` creates compiler input, semantic unit inventory, conservation report, and final DRD output, then validates compiler conservation.
5. `P2-IMPL-05` validates the end-to-end vertical slice and prepares P2 build lock readiness evidence.

## Coupling Rule
Each workpack must cite stage IDs, validation IDs, artifact IDs, artifact paths, and dependency fields from `P2_IMPLEMENTATION_WORKPACK_INDEX.json`; free-form restatement is not enough for lock evidence.

## Path Rule
Every implementation `code_target`, `test_target`, and required artifact path must be covered by `allowed_write_paths_after_lock` before the workpack can run. This prevents a workpack from requiring an output that its own scope policy forbids.

## Dependency Rule
`direct_depends_on_workpacks` and `requires_completed_workpacks` are the machine-readable execution authority. The numbered list in this file is explanatory only.

## Build Lock Rule
`P2_BUILD_LOCK` must not be created until all ten obligations in `P2_TEST_OBLIGATION_MATRIX.json` pass or have an approved human-review exception that names the exact validation and artifact IDs.
