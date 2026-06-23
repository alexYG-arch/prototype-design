# P1-SPEC-03 Inference Record Rules

## Record Purpose

Inference records make the Harness auditable. They explain what was concluded, why the conclusion is allowed, and what cannot yet be promoted.

## Required Fields

| Field | Requirement |
|---|---|
| `inference_id` | Stable unique ID, scoped to the stage or artifact. |
| `inference_class` | One of the classes defined in `REASONING_CONTRACT.md`. |
| `stage_id` | Stage that produced the inference. |
| `artifact_id` | Artifact or section that contains the inference. |
| `source_refs` | Source PRD references, upstream artifact IDs, rule IDs, or Human Gate decision IDs. |
| `premises` | Reviewable facts or constraints. |
| `applied_rules` | Locked rules or obligations applied to the premises. |
| `necessity_basis` | Required for `DEDUCTIVE_NECESSITY`; explains why the conclusion is required rather than merely useful. |
| `unresolved_product_choices` | Required for `DEDUCTIVE_NECESSITY`; must be empty for canonical eligibility. |
| `conclusion` | Natural-language conclusion. |
| `canonical_eligibility` | `ELIGIBLE`, `BLOCKED_PENDING_HUMAN`, `BLOCKED_INVALID`, or `REJECTED`. |
| `downstream_use` | Downstream artifacts allowed to consume the inference. |

## Rules

### REASON-RULE-001 Stable Identity

An inference ID must not be reused for a different conclusion. If the conclusion changes, a new version or replacement record is required.

### REASON-RULE-002 Citation Required

Every `SOURCE_EXPLICIT`, `DEDUCTIVE_NECESSITY`, or `HUMAN_DECIDED` inference must cite at least one durable source reference.

### REASON-RULE-003 Premise Transparency

Premises must be written as externally reviewable facts, constraints, or approved decisions. Private chain-of-thought is not a valid premise.

### REASON-RULE-004 Deductive Necessity Test

`DEDUCTIVE_NECESSITY` requires a necessary relationship between premise and conclusion. If multiple plausible product choices remain, the record is not deductive.

The record must include `necessity_basis` and must keep `unresolved_product_choices` empty before canonical use.

### REASON-RULE-005 Inductive Containment

`INDUCTIVE_CANDIDATE` may be used for comparison, pattern discovery, or review prompts. Its `canonical_eligibility` must remain `BLOCKED_PENDING_HUMAN` until an approving decision is bound.

### REASON-RULE-006 Rejection Propagation

`REJECTED_INFERENCE` records must be preserved for audit and must block downstream reuse of the rejected conclusion.

### REASON-RULE-007 Downstream Scope

`downstream_use` must list the exact artifact families allowed to consume the inference. Empty or broad values are invalid.

### REASON-RULE-008 Human Decision Binding

`HUMAN_DECIDED` records must cite a review decision, decision ID, or approved gap resolution.

## Disallowed Records

The validator must reject records that:

- Have no source reference.
- Use `INDUCTIVE_CANDIDATE` with canonical eligibility.
- Use ambiguous language such as "normally", "probably", or "best practice" as sole support for a canonical conclusion.
- Claim a PRD element was adopted without a PRD element decision.
- Create a new input requirement without an input path or gap route.
