# P3 Pattern Model

## Inputs

The pattern model consumes:

- the approved `P3-SPEC-ELEMENTS` canonical projection rule,
- canonical element ids from source-explicit and eligible derived elements,
- approved interaction messages from `P3-SPEC-CLOSURE`,
- Human Gate decisions resolving product expansion or presentation consistency exceptions.

Blocked, open-gap, rejected, superseded, structural-review-only, and inductive-unapproved elements are not eligible for pattern reuse or presentation decisions except as blocked evidence.

## Shared Pattern Registry

`p3.patterns.shared_component_registry` records reusable semantic patterns. A pattern row is valid only when it contains:

- `semantic_role`: why the pattern exists in task meaning,
- `data_structure`: data or content fields needed by the pattern,
- `operation_set`: actions or operations supported,
- `state_model`: states the pattern must support,
- `information_hierarchy`: semantic priority of information inside the pattern,
- `interaction_model`: allowed interaction behavior,
- `surface_constraints`: constraints that affect downstream layout but do not decide exact placement,
- `reuse_scope`: canonical elements or message ids that consume the pattern,
- `trace_refs`: source, element, closure, or Human Gate evidence.

`LAYOUT_PATTERN` is allowed only as a semantic pre-layout grouping. It may say that a set of elements forms a field group or action group, but it cannot decide columns, breakpoints, scroll behavior, viewport placement, or z-axis.

## Information Presentation Registry

`p3.patterns.information_presentation_registry` decides the presentation mode for user-visible information. It covers at least:

- interaction messages from closure,
- disabled and unavailable reasons,
- validation, async, timeout, failure, recovery, and terminal information,
- user-decision information,
- status and confirmation messages,
- empty or table/list states when present in the canonical element universe.

The registry must make information lifecycle explicit. Persistent, until-resolved, audit, session, sustained processing, and user-decision information must remain recoverable and discoverable. Transient-only modes are allowed only for low-risk information that does not require a user decision and does not become unrecoverable after timeout.

## Consistency Exceptions

Equivalent information is keyed by semantic intent, trigger condition, scope, and lifecycle. Different presentation modes for the same key require a consistency exception. The exception must name allowed modes and cite a real difference such as unsaved work risk, blocking handoff, legal/audit persistence, or recovery burden.

## Conservation Rule

Downstream layout and compiler artifacts must preserve pattern ids and presentation ids. If a downstream artifact references a pattern id, it must resolve to `p3.patterns.shared_component_registry`. If it references a message presentation, it must resolve to `p3.patterns.information_presentation_registry` or an approved exception.
