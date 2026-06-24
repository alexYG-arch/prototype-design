# P1-SPEC-05 Shared Component Contract

## Purpose

This contract defines when pages, states, interactions, or information surfaces must share a component or presentation pattern, and when they must stay separate.

It owns `DRD-CHARTER-017`.

## Shared Pattern Authority

Shared components and shared patterns are semantic decisions, not visual shortcuts.

The Harness may recommend sharing when surfaces match on:

- Semantic role.
- Data structure.
- Operation set.
- State model.
- Information hierarchy.
- Interaction model.
- Access or permission constraints.
- Content lifecycle.
- Surface constraints.

The Harness must not merge surfaces only because they look similar.

## Registry Requirement

Shared components and patterns must be recorded in a registry before downstream layout can depend on them.

Required registry fields:

| Field | Requirement |
|---|---|
| `pattern_id` | Stable ID. |
| `pattern_kind` | Component, presentation pattern, layout pattern, or interaction pattern. |
| `semantic_role` | What job the pattern performs for the user. |
| `data_structure` | Data shape and required fields. |
| `operation_set` | Actions the pattern supports. |
| `state_model` | Required states, including empty, loading, error, disabled, permission, and success when applicable. |
| `information_hierarchy` | Primary, secondary, supporting, and meta information. |
| `interaction_model` | Clickables, Reactions, async behavior, handoff, or failure behavior inherited from upstream. |
| `surface_constraints` | Page, overlay, sidebar, table row, card, mobile, desktop, or equivalent constraints. |
| `reuse_scope` | Where the pattern may be reused. |
| `non_reuse_reason` | Required when visually similar surfaces must not share. |
| `trace_refs` | Source, adoption, derivation, interaction, or Human Gate references. |

## Contract Clauses

### SHARED-CONTRACT-001 Semantic Match Required

Shared components require semantic compatibility across role, data, operations, state, information hierarchy, and surface constraints.

### SHARED-CONTRACT-002 Visual Similarity Is Insufficient

Visual similarity alone cannot justify sharing.

### SHARED-CONTRACT-003 Unique Presentation For Same Semantics

If two surfaces have the same semantic intent, trigger condition, scope, and information lifecycle, they should use the same presentation pattern unless a traceable exception exists.

### SHARED-CONTRACT-004 Difference Requires Reason

If equivalent semantics use different patterns, the decision must cite a scenario, constraint, lifecycle, risk, or Human Gate decision.

### SHARED-CONTRACT-005 Shared Does Not Flatten Context

A shared component may expose context-specific labels, values, actions, and states, but must not change the underlying semantic contract per instance.

### SHARED-CONTRACT-006 Registry Before Layout

Natural-language layout must reference registered shared patterns rather than inventing new reusable component semantics inline.

## Disallowed Behavior

The validator must reject:

- Components shared only because they have similar shape or color.
- Separate components for equivalent semantics without a documented reason.
- Shared components that hide incompatible actions or state models.
- Layouts that imply new shared components without registry entries.

