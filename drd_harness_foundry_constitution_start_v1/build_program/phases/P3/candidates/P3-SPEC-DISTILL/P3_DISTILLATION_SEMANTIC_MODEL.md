# P3 Distillation Semantic Model

## Two-Lane Representation

Distillation has two lanes:

| Lane | Role | Canonical status |
| --- | --- | --- |
| Natural source semantics | Primary source meaning from frozen source items | Authoritative when source is eligible |
| Structured inventory | Index, normalization, and verification skeleton | Authoritative only as evidence of how the source was represented |

A downstream module must cite both the frozen source reference and the structured row when it relies on a distilled claim.

## Atomic Semantic Units

The distillation inventory must decompose source claims into atomic rows. A row is atomic when it has one stable subject, one semantic type, one source basis, and one downstream adoption decision. Compound rows that mix task, page, CTA, state, and copy in one record are invalid for downstream traceability.

Allowed semantic unit families are:

- `experience.task`
- `experience.actor`
- `experience.role_or_permission`
- `experience.surface`
- `experience.navigation`
- `experience.action`
- `experience.input`
- `experience.message`
- `experience.state`
- `experience.async_or_failure`
- `experience.recovery`
- `experience.constraint`
- `experience.data_object`
- `experience.open_question`

When a row maps into the current PRD element schemas, it must use one of the existing element types: `PAGE`, `STATE`, `CTA`, `INPUT`, `NAVIGATION`, `MESSAGE`, `ROLE`, `PERMISSION`, or `UI_ELEMENT`. P3-specific semantic families stay in the distillation semantic unit map instead of changing the schema field values.

## Conflict And Ambiguity

A conflict exists when two eligible sources claim incompatible task, surface, flow, field, state, or constraint semantics. A conflict must create a review record and block canonical adoption for the affected rows unless a human decision resolves it.

Ambiguity exists when a source gives enough evidence that a row may matter, but not enough to choose label, behavior, scope, or priority. Ambiguity can create an input obligation or an inductive candidate, but cannot become canonical without review.

## Artifact Envelope Rule

Every distillation file is an artifact envelope with provenance fields and a `records` payload. Schema-bound record fields are validated inside `records`; the envelope carries source refs, upstream hashes, validator identity, review gate, promotion state, and invalidation inputs needed for cross-stage verification.
