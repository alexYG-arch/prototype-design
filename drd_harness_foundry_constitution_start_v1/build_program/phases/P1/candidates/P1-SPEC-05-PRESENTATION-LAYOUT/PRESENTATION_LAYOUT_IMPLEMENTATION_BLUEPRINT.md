# P1-SPEC-05 Presentation Layout Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/rules/presentation.py` | Shared component and information presentation rule helpers. | `repository/tests/presentation/test_shared_component_registry.py` |
| `repository/src/drd_harness/rules/layout.py` | Natural-language layout, content growth, nested surface, and Figma metadata rule helpers. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/src/drd_harness/validators/presentation_consistency.py` | Shared pattern and information presentation consistency validators. | `repository/tests/presentation/test_information_presentation_consistency.py` |
| `repository/src/drd_harness/validators/layout_completeness.py` | Layout completeness, carrier adaptation, multi-level containment, content growth, information completeness, z-axis, state placement, nested surface, and Figma compatibility validators. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/schemas/presentation/shared_component_registry.schema.json` | Shared pattern registry schema. | `repository/tests/presentation/test_shared_component_registry.py` |
| `repository/schemas/presentation/information_presentation_registry.schema.json` | Information presentation registry schema. | `repository/tests/presentation/test_information_presentation_consistency.py` |
| `repository/schemas/presentation/presentation_consistency_exception.schema.json` | Presentation exception schema. | `repository/tests/presentation/test_information_presentation_consistency.py` |
| `repository/schemas/layout/natural_language_layout.schema.json` | Natural-language layout index schema. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/schemas/layout/carrier_adaptation_profile.schema.json` | Carrier adaptation profile schema for desktop, tablet, mobile, iOS, Material, and declared surfaces. | `repository/tests/layout/test_carrier_adaptation_profile.py` |
| `repository/schemas/layout/containment_hierarchy.schema.json` | Multi-level containment hierarchy schema. | `repository/tests/layout/test_containment_hierarchy.py` |
| `repository/schemas/layout/layout_composition_index.schema.json` | Layout composition index schema. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/schemas/layout/content_growth_rule.schema.json` | Content growth behavior schema. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/schemas/layout/information_completeness_rule.schema.json` | Height-unbounded and width-bounded information completeness schema. | `repository/tests/layout/test_information_completeness.py` |
| `repository/schemas/layout/z_axis_layering.schema.json` | Z-axis and Material elevation layering schema. | `repository/tests/layout/test_z_axis_layering.py` |
| `repository/schemas/layout/state_placement_index.schema.json` | Interaction state and message placement schema. | `repository/tests/layout/test_layout_completeness.py` |
| `repository/schemas/layout/figma_reconstruction_metadata.schema.json` | Figma compatibility metadata schema. | `repository/tests/layout/test_figma_compatibility_metadata.py` |

## Implementation Rules

### IMPL-PL-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-PL-002 Validators Are Pure

Validators must report failures and cannot rewrite presentation or layout artifacts to make them pass.

### IMPL-PL-003 Structured Joins Required

Validators must join shared pattern registry, presentation registry, interaction message coverage, layout index, and Figma metadata rather than relying on manual document reading.

### IMPL-PL-004 Natural Language Remains Canonical

Structured JSON can index layout obligations, but the Markdown layout prose remains the authoritative semantic description.

### IMPL-PL-005 Fixture Coverage

Tests must include positive and negative fixtures for:

- Valid semantic shared component.
- Visual-only shared component rejection.
- Presentation consistency with exception.
- Sustained information rejected as transient-only.
- Complete natural-language layout.
- Thin layout rejection.
- Missing carrier adaptation for required desktop, tablet, mobile, iOS, or Material profiles.
- Flat containment rejection when nested regions exist.
- Child ordering or scroll behavior contradicting parent containment.
- Content growth missing.
- Height-limited information loss.
- Width constraint ignored instead of adapted.
- Missing z-axis or Material elevation record for layered surfaces.
- Interaction message missing layout placement.
- Interaction message placement omitted from state placement index.
- Nested surface missing containment or return placement.
- Figma metadata complete.
- Figma metadata introducing new semantics.
- Figma write authority rejection.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/presentation repository/tests/layout
```

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-006` | Presentation consistency | `rules/presentation.py`, `validators/presentation_consistency.py` | `PL-CHECK-003`, `PL-CHECK-005` |
| `DRD-CHARTER-008` | Natural-language layout completeness, carrier adaptation, containment, and z-axis | `rules/layout.py`, `validators/layout_completeness.py` | `PL-CHECK-006`, `PL-CHECK-007`, `PL-CHECK-008`, `PL-CHECK-011`, `PL-CHECK-012`, `PL-CHECK-013` |
| `DRD-CHARTER-009` | Figma compatibility only | `rules/layout.py`, `validators/layout_completeness.py` | `PL-CHECK-014`, `PL-CHECK-015`, `PL-CHECK-016` |
| `DRD-CHARTER-017` | Shared pattern discipline | `rules/presentation.py`, `validators/presentation_consistency.py` | `PL-CHECK-001`, `PL-CHECK-002` |
| `RD-RULE-007` | Content growth and information completeness | `rules/layout.py`, `validators/layout_completeness.py` | `PL-CHECK-009`, `PL-CHECK-010` |
| `RD-RULE-008` | Sustained information presentation | `rules/presentation.py`, `validators/presentation_consistency.py` | `PL-CHECK-004` |
