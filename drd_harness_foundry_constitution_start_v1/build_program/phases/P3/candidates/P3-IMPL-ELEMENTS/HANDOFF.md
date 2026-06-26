# P3-IMPL-ELEMENTS Handoff

`P3-IMPL-ELEMENTS` implements the P3 page element model as an additive validator around the existing locked PRD adoption and reasoning primitives.

Review focus:

1. Confirm the additive wrapper is inside P3 elements intent and does not modify P2 locked `prd_adoption.py`.
2. Confirm natural language and approved closure remain the primary semantic authority, while inventory rows are only an index and verification skeleton.
3. Confirm every approved closure page, state, and message maps to a canonical element or blocked gap.
4. Confirm declared upstream hashes bind to actual invalidation input file bytes and schema record keys are enforced.
5. Confirm missing product details, unknown source refs, unknown closure-like source refs, and page child-surface ambiguity remain Human Gate blocked and do not become canonical elements.
6. Confirm downstream references are restricted to the canonical projection.
7. Confirm tests and full regression pass.

This candidate is approved by Human Gate, does not create `P3_BUILD_LOCK`, and does not authorize `P3-IMPL-PATTERNS` without explicit continuation.
