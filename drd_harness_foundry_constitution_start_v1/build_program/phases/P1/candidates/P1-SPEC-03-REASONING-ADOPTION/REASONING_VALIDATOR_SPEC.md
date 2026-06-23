# P1-SPEC-03 Reasoning Validator Spec

## Validator Families

| Validator | Responsibility |
|---|---|
| `inference_record_schema_validator` | Checks required fields, class enums, stable IDs, and downstream scope. |
| `inference_citation_validator` | Ensures eligible inferences cite source, upstream artifacts, rules, or Human Gate decisions. |
| `deductive_necessity_validator` | Rejects conclusions that are only plausibility or convention. |
| `non_canonical_induction_validator` | Blocks inductive candidates from canonical downstream use without approval. |
| `prd_element_inventory_validator` | Validates the PRD explicit element inventory used as adoption coverage input. |
| `prd_element_adoption_validator` | Ensures every PRD-explicit element has a valid adoption outcome. |
| `derived_element_obligation_validator` | Ensures derived elements trace to allowed obligations and inference records. |
| `input_obligation_validator` | Enforces `RD-RULE-001` for tasks depending on input `X`. |
| `product_expansion_gap_validator` | Blocks unresolved product expansion gaps from canonical artifacts. |
| `human_gate_binding_validator` | Confirms approved semantic decisions are bound to Human Gate decision IDs. |

## Checks

### REASON-CHECK-001 Inference Record Completeness

Fail if an inference record lacks ID, class, stage, artifact, premise, rule, conclusion, eligibility, or downstream scope.

### REASON-CHECK-002 Citation Completeness

Fail if an eligible canonical inference lacks a source, upstream, rule, or Human Gate citation.

### REASON-CHECK-003 Deduction First

Fail if a canonical artifact consumes an inference that is not `SOURCE_EXPLICIT`, `DEDUCTIVE_NECESSITY`, or `HUMAN_DECIDED`.

For `DEDUCTIVE_NECESSITY`, fail if `necessity_basis` is absent or if `unresolved_product_choices` is not empty.

### REASON-CHECK-004 Inductive Candidate Lockout

Fail if `INDUCTIVE_CANDIDATE` has `ELIGIBLE` canonical status without a Human Gate decision.

### REASON-CHECK-005 PRD Element Adoption Coverage

Fail if any PRD-explicit page, state, CTA, input, or element lacks an adoption decision.

### REASON-CHECK-006 Adoption Outcome Integrity

Fail if a normalized, clarified, rejected, or gap-routed element lacks the required supporting fields.

### REASON-CHECK-007 Derived Element Trace

Fail if a derived element cannot trace to an allowed derivation source and inference record.

### REASON-CHECK-008 Input Obligation Path

Fail if task success depends on input `X` and no entry, selection, import, acquisition, or gap route exists.

### REASON-CHECK-009 Product Expansion Gap Blocking

Fail if unresolved product expansion gaps are consumed by canonical downstream artifacts.

### REASON-CHECK-010 Human Decision Binding

Fail if `HUMAN_DECIDED` or resolved product gaps lack decision references.

### REASON-CHECK-011 Rejected Inference Blocking

Fail if downstream artifacts consume a `REJECTED_INFERENCE` conclusion.

### REASON-CHECK-012 Compilation Input Sanity

Fail if deterministic compilation inputs include unresolved clarification, conflict, gap, or inductive candidate records.

### REASON-CHECK-013 PRD Element Inventory Coverage

Fail if the PRD explicit element inventory is missing, if an inventory element lacks exactly one current adoption decision, or if an adoption decision claims source-explicit status for an element outside the inventory.

## Required Schemas

Implementation must provide schemas for:

- `repository/schemas/reasoning/inference_record.schema.json`
- `repository/schemas/reasoning/prd_element_inventory.schema.json`
- `repository/schemas/reasoning/prd_element_decision.schema.json`
- `repository/schemas/reasoning/derived_element_decision.schema.json`
- `repository/schemas/reasoning/product_expansion_gap.schema.json`
- `repository/schemas/reasoning/input_obligation.schema.json`
