# P2 Stage Path Spec

## Stage Sequence

The P2 vertical slice must use this ordered path:

| Stage | Purpose | Required output |
|---|---|---|
| `DRD-00-SOURCE-FREEZE` | Freeze the Tiny Brief Intake PRD as immutable source. | Source snapshot manifest and source hash. |
| `DRD-01-PRD-ELEMENTS` | Convert source semantics into an element inventory and adoption decisions. | PRD element inventory, accepted element decisions, derived element decisions, rejected expansion records. |
| `DRD-02-REASONING` | Derive missing-but-required details without adding product capability. | Inference records and structural completion review. |
| `DRD-03-INTERACTION` | Close the page, state, overlay, clickable, async, and failure graph. | Interaction graph, clickable inventory, async behavior, failure recovery, and interaction messages. |
| `DRD-04-PRESENTATION-LAYOUT` | Specify presentation, shared components, and natural-language layout. | Presentation registry, shared component registry, natural-language layout, carrier profile, containment hierarchy, z-axis layering. |
| `DRD-05-COMPILATION` | Compile reviewed semantic units without adding new content. | Compiler input bundle, semantic unit inventory, conservation report, and `FINAL_DRD.md`. |
| `DRD-06-FINAL-REVIEW` | Bind final output to review evidence. | Final manifest, hash index, reference index, review target, and review decision. |

## Derivation Discipline

Deduction is primary. Induction may only propose candidates for human review. The vertical slice may derive missing elements only when all of these are true:

1. The element is required by the stated user task, page, state, overlay, or failure path.
2. The element does not create a new user task, new page, secondary page, or product capability.
3. The premise can be traced to the PRD fixture or locked P1 rules.
4. The downstream artifact records the source, inference rule, and decision.

If any condition fails, the output must create a human-review-required gap.

## Async And Failure Copy Rule

Async, loading, disabled, failure, retry, partial completion, and exit states must have user-facing copy or an explicit no-copy decision. Missing text is not allowed to pass silently. The copy must be scoped to the same task and must not advertise capabilities absent from the PRD.

## Layout Carrier Rule

The natural-language layout must be carrier-specific:

| Carrier | Required constraints |
|---|---|
| Desktop web | Full page hierarchy, visible primary action, overlay z-axis, and scroll behavior for long content. |
| Tablet | Reflowed hierarchy with preserved ordering and no hidden required information. |
| Mobile iOS | iOS control expectations, safe area awareness, overlay layering, and bottom-action ergonomics. |
| Mobile Material | Material control expectations, elevation or z-axis behavior, snackbar or dialog distinction when applicable. |

Width constraints must be respected. Height constraints may require scroll, progressive disclosure, or anchored actions, but must not drop required information.

## Compiler Conservation Rule

`DRD-05-COMPILATION` may assemble, order, reference, and format approved semantic units. It must not invent new semantic content. Any content not present in an approved source or stage artifact must be reported as a conservation violation.
