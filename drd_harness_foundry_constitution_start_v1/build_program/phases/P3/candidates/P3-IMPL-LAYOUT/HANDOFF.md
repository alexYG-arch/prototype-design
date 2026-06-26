# P3-IMPL-LAYOUT Handoff

`P3-IMPL-LAYOUT` implements the P3 natural-language layout boundary as an additive validator around the existing locked layout primitives.

Review focus:

1. Confirm the additive wrapper is inside P3 layout intent and does not modify P2 locked `layout_completeness.py`.
2. Confirm natural language is canonical authority and structured layout records are only index and validation skeleton.
3. Confirm carrier coverage includes desktop, tablet, mobile, iOS, and Material constraints.
4. Confirm containment is multi-level and preserves order, width, scroll, and parent-child consistency.
5. Confirm required information remains reachable under height and width constraints, with horizontal scroll only as a declared exception.
6. Confirm approved messages have state placement and z-axis layering has Material elevation intent.
7. Confirm Figma metadata is reconstruction-only and cannot write files, call Figma APIs, or become canonical authority.
8. Confirm tests and full regression pass.

This candidate is ready for Human Gate review, does not create `P3_BUILD_LOCK`, and does not authorize `P3-IMPL-COMPILER` without explicit continuation.
