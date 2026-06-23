# P1-SPEC-03 Reasoning Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/rules/reasoning.py` | Inference classes, eligibility rules, and deduction-first checks. | `repository/tests/reasoning/test_inference_records.py` |
| `repository/src/drd_harness/rules/prd_adoption.py` | PRD element adoption outcomes and validation routing. | `repository/tests/reasoning/test_prd_element_adoption.py` |
| `repository/src/drd_harness/validators/reasoning.py` | Inference schema, citation, induction lockout, rejected inference, and compilation sanity validators. | `repository/tests/reasoning/test_inference_records.py` |
| `repository/src/drd_harness/validators/prd_adoption.py` | Adoption coverage, normalization, clarification, conflict, and product gap checks. | `repository/tests/reasoning/test_prd_element_adoption.py` |
| `repository/schemas/reasoning/inference_record.schema.json` | Structured inference record schema. | `repository/tests/reasoning/test_inference_record_schema.py` |
| `repository/schemas/reasoning/prd_element_inventory.schema.json` | Source-explicit PRD element inventory schema used as adoption coverage universe. | `repository/tests/reasoning/test_prd_element_inventory_schema.py` |
| `repository/schemas/reasoning/prd_element_decision.schema.json` | PRD element adoption decision schema. | `repository/tests/reasoning/test_prd_element_decision_schema.py` |
| `repository/schemas/reasoning/derived_element_decision.schema.json` | Derived element decision schema. | `repository/tests/reasoning/test_derived_element_decision.py` |
| `repository/schemas/reasoning/product_expansion_gap.schema.json` | Product expansion gap schema. | `repository/tests/reasoning/test_product_expansion_gap.py` |
| `repository/schemas/reasoning/input_obligation.schema.json` | Input obligation schema. | `repository/tests/reasoning/test_input_obligation.py` |

## Implementation Rules

### IMPL-REASON-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-REASON-002 JSON Schemas First

Schemas must be implemented before validators depend on the corresponding structured fields.

### IMPL-REASON-003 Pure Validators

Validators must report failures and cannot rewrite candidate artifacts to make them pass.

### IMPL-REASON-004 Explicit Fixture Coverage

Tests must include positive and negative fixtures for:

- Source explicit inference.
- Deductive necessity.
- Deductive necessity with empty unresolved product choices.
- Inductive candidate blocked from canonical use.
- Human-decided inference with decision binding.
- Rejected inference blocking.
- PRD explicit element inventory coverage.
- PRD element adoption coverage.
- Input obligation path or gap.
- Product expansion gap blocking.

### IMPL-REASON-005 Stage Integration

Reasoning validators must integrate with stage dependency manifests from `P1-SPEC-02-STAGE-ARTIFACTS` so they can verify approved upstream hash binding.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/reasoning
```

Additional full-suite commands may be required by later lock and validation specs.

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-003` | Deduction first, induction containment | `rules/reasoning.py`, `validators/reasoning.py` | `REASON-CHECK-003`, `REASON-CHECK-004` |
| `DRD-CHARTER-004` | PRD element inventory and adoption | `rules/prd_adoption.py`, `validators/prd_adoption.py` | `REASON-CHECK-005`, `REASON-CHECK-006`, `REASON-CHECK-013` |
| `DRD-CHARTER-007` | Element derivation | `rules/reasoning.py`, `validators/reasoning.py` | `REASON-CHECK-007` |
| `DRD-CHARTER-018` | Product expansion gaps | `validators/reasoning.py`, `validators/prd_adoption.py` | `REASON-CHECK-009`, `REASON-CHECK-012` |
| `RD-RULE-001` | Input obligation | `rules/reasoning.py`, `validators/reasoning.py` | `REASON-CHECK-008` |
