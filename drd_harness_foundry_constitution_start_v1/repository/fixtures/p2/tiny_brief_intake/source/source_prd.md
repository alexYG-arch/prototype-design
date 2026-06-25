# P2 Vertical Slice PRD

## Fixture Name

Tiny Brief Intake.

## Purpose

This PRD is a controlled P2 fixture for proving one complete `PRD -> FINAL_DRD` path through the harness. It is not a new harness product feature and must not require new repository capabilities outside the locked P1 build foundation.

## User Task

A product owner submits a one-page design brief so the harness can produce a complete DRD for a single product page.

## Real Page

Page name: `Brief Intake`.

The page collects the minimum information needed to describe one product page:

- Project name.
- Audience.
- Page type.
- Primary user goal.
- Business constraint.

## Clickable Inventory

All clickable elements for the fixture are listed here and must appear in the downstream interaction inventory:

| Element ID | Label | Type | Primary effect |
|---|---|---|---|
| `brief.page_type.select` | Page type | select | Chooses the requested page category. |
| `brief.save_draft` | Save draft | button | Stores the current draft without starting validation. |
| `brief.validate` | Validate brief | button | Starts PRD element validation and opens the validation overlay. |
| `brief.generate` | Generate DRD | button | Starts the governed DRD generation path after required inputs pass validation. |
| `overlay.retry` | Retry | button | Retries validation or generation after a recoverable failure. |
| `overlay.edit_brief` | Edit brief | button | Returns focus to the editable brief fields. |
| `overlay.close` | Close | button | Closes the overlay without deleting draft content. |

Text inputs and textareas are editable fields, not clickable command elements, and must still appear in the PRD element inventory.

## States

The fixture uses exactly five user-visible states:

| State ID | Name | Meaning |
|---|---|---|
| `state.empty` | Empty draft | Required fields are blank and generate is unavailable. |
| `state.editing` | Editing draft | User has entered at least one field and can save a draft. |
| `state.validating` | Validation overlay | The system is checking source completeness and possible expansion gaps. |
| `state.recoverable_failure` | Recoverable failure | Validation or generation failed and the user can retry or edit. |
| `state.final_ready` | Final DRD ready | `FINAL_DRD.md` has been produced and review evidence is available. |

## Handoff Or Overlay

The validation overlay is the required system handoff. It appears after `brief.validate` or `brief.generate`, shows progress, displays missing required inputs or recoverable failures, and hands validated input to the reasoning stage.

## Failure Recovery

If validation or generation fails because of a transient runtime error, the overlay must show:

- A plain-language failure message.
- `Retry`.
- `Edit brief`.
- No loss of draft content.

If the failure is caused by missing required information, the system must return a specific missing-field message and keep the user in the same task, not invent a new page or new product capability.

## PRD Element Validation

The downstream PRD element inventory must distinguish:

- Explicit elements copied from this PRD.
- Deductively derived elements required to complete the stated task.
- Rejected expansion candidates.
- Human-review-required gaps where completion would require a new user task, new page, secondary page, or new product capability.

Natural-language PRD semantics are the primary source. Inventory rows are the index and verification skeleton.

## Shared Component Or Presentation Pattern

The vertical slice must decide whether `brief.validate` and `brief.generate` share the same primary-action pattern or require distinct presentation treatment. The decision must be recorded in the presentation registry with evidence from state, task priority, and failure behavior.

## Natural-Language Layout Requirement

The final DRD must include a natural-language layout for:

- Desktop web.
- Tablet.
- Mobile iOS.
- Mobile Material.

The layout must preserve full information access under limited height, respect width constraints, and explicitly describe containment hierarchy, ordering, scroll behavior, and z-axis overlay behavior.

## Required Final Output

The P2 vertical slice is complete only when the harness can produce a source-backed `FINAL_DRD.md` plus hash and reference evidence for this PRD.
