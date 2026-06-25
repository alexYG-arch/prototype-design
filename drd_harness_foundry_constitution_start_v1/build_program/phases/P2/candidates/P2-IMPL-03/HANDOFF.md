# P2-IMPL-03 Handoff

`P2-IMPL-03` wires presentation decisions, shared component patterns, and carrier-specific natural-language layout records for the Tiny Brief Intake fixture.

Review focus:

1. Confirm every interaction message from `interaction_messages.json` has a presentation decision and unknown message refs are rejected.
2. Confirm `brief.validate` and `brief.generate` share the primary action group only for semantic reasons: same task context, state model, and failure recovery, not visual similarity; confirm layout pattern refs bind to shared component patterns.
3. Confirm layout prose remains the canonical semantic authority while inventories are only index and validation skeletons.
4. Confirm desktop, tablet, mobile, mobile iOS, and mobile Material carrier rules preserve width, scroll, safe-area/system-bar, keyboard, and platform constraints.
5. Confirm containment hierarchy is multi-level and does not flatten overlay, state messages, fields, and actions into one thin surface.
6. Confirm height does not hide required information, required information refs resolve to PRD/clickable/message sources, and width does not clip primary fields, actions, required copy, navigation, or overlay controls.
7. Confirm z-axis layering includes Material elevation intent, blocking behavior, background context preservation, focus restoration, and resolvable surface refs.

This candidate does not approve itself, does not create `P2_BUILD_LOCK`, and does not authorize `P2-IMPL-04` before Human Gate approval.

Repair-loop note: R1 findings fixed unknown message refs, unknown state placements, unresolved layout surface refs, and layout/shared-pattern binding gaps; tests and candidate-check were rerun after repair.
Repair-loop note: R2 findings fixed generator input exhaustion in layout package validation and required information ref binding gaps; tests and candidate-check were rerun after repair.
