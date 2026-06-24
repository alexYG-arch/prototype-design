# P1-SPEC-05 Presentation Layout Projections

## Projection Index

| Projection ID | Source | Target | Purpose |
|---|---|---|---|
| `PL-PROJ-001` | Approved pages, elements, interactions, and messages | Shared component registry | Identifies reusable semantic patterns. |
| `PL-PROJ-002` | Information obligations and interaction messages | Information presentation registry | Selects consistent recoverable presentation modes. |
| `PL-PROJ-003` | Variable content and collection surfaces | Content growth records | Captures wrapping, overflow, scroll, collapse, truncation, expansion, and empty behavior. |
| `PL-PROJ-004` | Approved surfaces and presentation decisions | Natural-language layout sections | Produces authoritative layout prose. |
| `PL-PROJ-005` | Natural-language layout sections | Layout composition index | Makes hierarchy, containment, ordering, state variants, and surface constraints mechanically checkable. |
| `PL-PROJ-006` | Natural-language layout and shared pattern registry | Figma reconstruction metadata | Supports Figma reconstruction without Figma writing. |
| `PL-PROJ-007` | Interaction graph states and message records | State placement index | Ensures async, failure, validation, disabled, handoff, exit, empty, permission, and recovery states are placed. |
| `PL-PROJ-008` | Shared and presentation registries | Consistency exception index | Records justified differences for equivalent semantics. |
| `PL-PROJ-009` | Product carrier requirements | Carrier adaptation profiles | Captures desktop, tablet, mobile, iOS, Material, and declared surface constraints. |
| `PL-PROJ-010` | Layout prose and section index | Multi-level containment hierarchy | Captures nested parent-child structure plus ordering, arrangement, sizing, and scroll coupling. |
| `PL-PROJ-011` | Layered surfaces and platform profiles | Z-axis layering records | Captures Material elevation, overlay order, occlusion, blocking, and focus restoration. |
| `PL-PROJ-012` | Required information and content growth records | Information completeness records | Ensures information remains accessible under height changes and width constraints. |

## Projection Requirements

Each projection must preserve:

- Source snapshot hash.
- Approved upstream artifact hashes.
- Surface IDs.
- Pattern IDs.
- Presentation IDs.
- Layout IDs.
- Carrier profile IDs.
- Containment hierarchy IDs.
- Message IDs when interaction copy is placed.
- Z-axis layer IDs when surfaces overlap or float.
- Information completeness IDs when content can exceed height or width.
- Human Gate decision IDs when layout or pattern semantics are selected.

## Disallowed Projection Behavior

A projection must not:

- Merge components by visual similarity alone.
- Use transient presentation for sustained decision information.
- Produce layout prose without content growth behavior.
- Produce layout prose without carrier adaptation when multiple carriers are in scope.
- Flatten containment when nested regions, child pages, overlays, or repeated item structures exist.
- Let child ordering, scroll, or width behavior contradict parent containment constraints.
- Omit z-axis or Material elevation rules for layered surfaces.
- Hide required information because screen height is limited.
- Produce Figma metadata that adds semantics not in layout prose.
- Drop interaction message placement.
- Treat nested surfaces or overlays as layout-complete without containment and return placement.

## Projection To Validators

The projection set feeds:

- Shared component registry validator.
- Presentation consistency validator.
- Transient-only information validator.
- Natural-language layout completeness validator.
- Carrier adaptation validator.
- Multi-level containment coupling validator.
- Content growth validator.
- Information completeness validator.
- State placement validator.
- Nested surface layout validator.
- Z-axis layering validator.
- Figma compatibility metadata validator.
- Figma non-write boundary validator.
