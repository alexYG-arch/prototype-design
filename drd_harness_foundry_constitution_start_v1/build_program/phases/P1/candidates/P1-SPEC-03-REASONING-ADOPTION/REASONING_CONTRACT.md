# P1-SPEC-03 Reasoning Contract

## Purpose

This Candidate defines the contract for reasoning, PRD element adoption, element derivation, and product expansion gap routing in the DRD Harness.

It owns these locked clauses:

- `DRD-CHARTER-003` Deduction first.
- `DRD-CHARTER-004` PRD element validation.
- `DRD-CHARTER-007` Element derivation.
- `DRD-CHARTER-018` No silent product expansion.
- `RD-RULE-001` Input obligation.

## Authority Boundary

The Harness may:

- Convert explicit PRD facts into auditable inference records.
- Derive necessary UX obligations from explicit facts, platform constraints, approved upstream artifacts, and locked reasoning rules.
- Propose inductive candidates as review material.
- Route unresolved product expansion questions to a Human Gate.

The Harness must not:

- Use common-product expectation as the sole reason to add pages, states, CTA, data inputs, components, or product capabilities.
- Promote an inductive candidate into a canonical artifact without Human Gate approval.
- Accept an explicit PRD element before validating consistency and executability.
- Hide product expansion inside normalization, layout, component selection, or copy editing.

## Runtime Split

| Responsibility | Runtime |
|---|---|
| Inference classification and natural-language reasoning records | Codex |
| Schema validation, duplicate detection, hash and citation checks | Python |
| Product expansion decisions, inductive candidate approval, unresolved input acquisition choices | Human Gate |

## Inference Classes

| Class | Meaning | Canonical Eligibility |
|---|---|---|
| `SOURCE_EXPLICIT` | Directly stated by the immutable Source PRD and validated for consistency. | Eligible after validation. |
| `DEDUCTIVE_NECESSITY` | Necessarily follows from explicit source facts, approved upstream artifacts, platform constraints, or locked reasoning rules. | Eligible after validator acceptance. |
| `INDUCTIVE_CANDIDATE` | Pattern-based candidate or one of multiple viable presentations. | Not eligible until Human Gate approval. |
| `HUMAN_DECIDED` | Approved or selected by Human Gate. | Eligible with decision binding. |
| `REJECTED_INFERENCE` | Explicitly rejected inference. | Not eligible and must not be reused. |

## Canonical Reasoning Record

Each reasoning decision must have a durable record with:

- Stable `inference_id`.
- `inference_class`.
- Source stage and artifact references.
- Premises.
- Applied rules or obligations.
- Conclusion.
- Alternative rejected or deferred paths, when relevant.
- Canonical eligibility.
- Required Human Gate decision, when relevant.

The record is audit prose plus structured metadata. It must not expose model-private reasoning chains; it records only reviewable premises, rule applications, conclusions, citations, and decisions.

## Contract Clauses

### REASON-CONTRACT-001 Deduction First

All canonical additions must be either `SOURCE_EXPLICIT`, `DEDUCTIVE_NECESSITY`, or `HUMAN_DECIDED`.

### REASON-CONTRACT-002 Induction Is Non-Canonical By Default

`INDUCTIVE_CANDIDATE` records may appear in candidate review material, but cannot feed canonical artifacts until linked to a Human Gate approval.

### REASON-CONTRACT-003 Explicit PRD Element Validation

Every PRD-explicit page, state, CTA, or element must receive an adoption decision before it can enter `PAGE_ELEMENT_BLUEPRINT.md` or equivalent downstream artifacts.

### REASON-CONTRACT-004 Derivation Boundaries

Missing elements may be derived only from tasks, states, information obligations, feedback, recovery, navigation, exit paths, accessibility obligations, approved upstream artifacts, or locked reasoning rules.

### REASON-CONTRACT-005 Input Obligation

If task success depends on input `X`, the DRD must include an actionable path to obtain, enter, select, import, or acquire `X`, or route the missing path as a gap.

### REASON-CONTRACT-006 Product Expansion Routing

Any capability, data collection, workflow, integration, or product promise not supported by source, approved decisions, or deductive necessity must be routed as a product expansion gap.

