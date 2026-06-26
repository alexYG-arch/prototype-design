# P3 Experience Distillation Contract

## Objective

`P3-SPEC-DISTILL` defines how frozen P3 sources become a reviewable experience model before interaction closure, page element modeling, layout, compiler, or assurance work consumes them.

The module is `prd_experience_distillation`. Its output is not UI code and not a product expansion. It converts eligible source semantics into typed experience evidence, records what is explicit, what is normalized, what is deductively required, and what must go to human review.

## Upstream Authority

| Artifact | Binding |
| --- | --- |
| `control/locks/P2_BUILD_LOCK.json` | `b7a85510c2a7b839ca5461341017da9bcaa3ddd031019936b921bf881af29aad` |
| `P3-SPEC-SOURCE/REVIEW_DECISION.json` | `df6e0860e97a609efccbbdd67764e2dee44b0d36d086633e2f89dac232d7238e` |
| `P3-SPEC-SOURCE` subject hash | `d7468c8379b2860556146940734c0e61280811f72cef4c7b3cc1ed79513eb739` |
| `P3-SPEC-SOURCE/P3_SOURCE_ARTIFACT_CONTRACTS.json` | `4cb5e5533fb7c4462563571411cf23e1c6650c34845538de94ab65ce38a0cd81` |

`P3-SPEC-DISTILL` may consume only eligible source items from source intake, or explicit blocker records that preserve review questions. It must not read unfrozen source bytes directly.

## Primary Semantics Rule

Natural-language source text remains the primary semantic source. Structured inventories are index and verification skeletons. An inventory row can make a semantic claim checkable, but it cannot override source wording or become evidence by itself.

## Distillation Boundary

The distillation stage may classify and normalize source-backed experience facts into these families:

- user task or outcome;
- actor, role, or permission;
- page, surface, flow, or navigation target;
- action, CTA, form input, data object, or user-visible message;
- state, async moment, failure, recovery, or completion condition;
- business, technical, or content constraint;
- missing input obligation;
- product expansion gap or conflicting-source decision.

The stage must not invent a new workflow, page, account ability, payment path, integration, data scope, automation, or business rule. If completion requires any of those, it must route to product expansion review.

## Deduction Discipline

Deduction is primary. Induction may propose candidates but cannot become canonical without human review. Every derived or normalized item must identify premises, rule ids, source refs, and downstream use. If the premise chain is incomplete, the artifact must preserve a blocker instead of silently filling the gap.

## Output Contract

The implementation must produce a compact but complete evidence package: source semantic units, PRD element inventory rows, adoption decisions, input obligations, inference records, derived element decisions, product expansion gaps, structural completion review, and a downstream handoff manifest for `P3-SPEC-CLOSURE`.
