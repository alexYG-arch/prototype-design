# P1-SPEC-03 Reasoning Projections

## Projection Index

| Projection ID | Source | Target | Purpose |
|---|---|---|---|
| `REASON-PROJ-001` | Source PRD explicit statements | `SOURCE_EXPLICIT` inference records | Preserves explicit facts as auditable records. |
| `REASON-PROJ-002` | Explicit facts plus approved upstream artifacts | `DEDUCTIVE_NECESSITY` inference records | Captures necessary conclusions. |
| `REASON-PROJ-003` | Pattern observations or multiple valid presentations | `INDUCTIVE_CANDIDATE` records | Keeps candidates reviewable but non-canonical. |
| `REASON-PROJ-004` | PRD-explicit pages, states, CTA, inputs, and elements | PRD element adoption decision index | Ensures every explicit element has a validation outcome. |
| `REASON-PROJ-005` | Tasks, states, information, feedback, recovery, navigation, exit, and accessibility obligations | Derived element decision index | Adds only necessary UX elements. |
| `REASON-PROJ-006` | Tasks requiring input `X` | Input obligation records | Requires entry, selection, import, acquisition, or gap routing. |
| `REASON-PROJ-007` | Unsupported capability or unresolved product choice | Product expansion gap queue | Blocks silent product expansion. |
| `REASON-PROJ-008` | Human Gate approval | `HUMAN_DECIDED` inference records and resolved gaps | Allows approved semantic decisions to flow downstream. |
| `REASON-PROJ-009` | Source PRD plus DRD-01 fact index | PRD explicit element inventory | Provides the coverage universe for adoption decisions. |

## Projection Requirements

Each projection must preserve:

- Source snapshot hash.
- Stage ID and artifact ID.
- Source or upstream citations.
- PRD explicit element inventory IDs when adoption coverage applies.
- Inference IDs.
- Adoption or derivation decision IDs.
- Human Gate decision IDs when a semantic choice is approved.

## Disallowed Projection Behavior

A projection must not:

- Convert `INDUCTIVE_CANDIDATE` directly into canonical output.
- Treat normalization as permission to add capability.
- Treat missing input paths as optional when task success depends on them.
- Drop rejected inferences from audit records.
- Allow unresolved product gaps into deterministic compilation inputs.

## Projection To Validators

The projection set feeds these validator families:

- Inference record validator.
- Inference citation validator.
- PRD element adoption validator.
- Derived element obligation validator.
- Input obligation validator.
- Product expansion gap validator.
- Human Gate binding validator.
- Non-canonical induction validator.
