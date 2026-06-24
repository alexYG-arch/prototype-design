# P1-SPEC-07 Compiler Implementation Blueprint

## Implementation Scope

This blueprint is for future implementation only. It does not authorize repository code changes before the relevant Spec Lock exists.

## Code Targets

| Target | Purpose | Tests |
|---|---|---|
| `repository/src/drd_harness/compiler/final_drd.py` | Deterministic final DRD assembly from closed approved input bundles. | `repository/tests/compiler/test_final_drd_compilation.py` |
| `repository/src/drd_harness/compiler/conservation.py` | Semantic unit inventory comparison, hash partitions, and conservation reports. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/src/drd_harness/validators/compiler_conservation.py` | Input bundle, approval, hash drift, deterministic ordering, semantic addition, semantic omission, idempotence, manifest, and read-only QA boundary validators. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/compiler_input_bundle.schema.json` | Closed compiler input bundle schema. | `repository/tests/compiler/test_final_drd_compilation.py` |
| `repository/schemas/compiler/final_drd_manifest.schema.json` | Final DRD manifest schema. | `repository/tests/compiler/test_final_drd_compilation.py` |
| `repository/schemas/compiler/final_drd_toc.schema.json` | Deterministic TOC schema. | `repository/tests/compiler/test_final_drd_compilation.py` |
| `repository/schemas/compiler/final_drd_reference_index.schema.json` | Final reference index schema. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/final_drd_hash_index.schema.json` | Final hash index schema. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/compiler_conservation_report.schema.json` | Conservation report schema. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/compiler_semantic_unit_inventory.schema.json` | Semantic unit inventory schema. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/compiler_atomic_semantic_unit.schema.json` | Atomic semantic unit row schema. | `repository/tests/compiler/test_compiler_conservation.py` |
| `repository/schemas/compiler/read_only_qa_boundary.schema.json` | DRD-06 read-only output boundary schema. | `repository/tests/compiler/test_compiler_conservation.py` |

## Implementation Rules

### IMPL-COMP-001 No Business Code Before Lock

Implementation workpacks may not implement these targets until this Candidate is approved and locked under the package process.

### IMPL-COMP-002 Compiler Is Pure Assembly

`final_drd.py` must assemble from approved input bundles only. It cannot call Codex, LLM APIs, source-reading semantic inference, or repair functions.

### IMPL-COMP-003 Conservation Is Independent

`conservation.py` and `compiler_conservation.py` must be able to validate compiler outputs independently from the original compile invocation.

### IMPL-COMP-004 Structured Parsing Required

Validators must use structured indexes and semantic unit inventories where available. Prose scanning may assist detection, but approval binding, input closure, ordering, and hash drift must be structured checks.

Atomic inventory validation must not rely on paragraph-level text matching. It must check row-level unit type, source span, parent relationship, canonical value, and unit hash.

### IMPL-COMP-005 Fail Closed

Any missing approval, missing hash, hash drift, nondeterministic ordering, semantic addition, semantic omission, conflict, or read-only QA mutation must fail the compiler or validator and route to Human Gate.

### IMPL-COMP-006 Deterministic Serialization

JSON outputs must use deterministic serialization with sorted keys, stable separators, stable newline handling, and no machine-local ordering. Markdown output must use fixed templates and stable line endings.

### IMPL-COMP-007 Audit Fields Are Non-Semantic

If implementation records run time, host, or command metadata, those fields must be explicitly marked audit-only and excluded from semantic conservation hashes.

## Fixture Coverage

Tests must include positive and negative fixtures for:

- Closed approved input bundle.
- Missing approval reference.
- Prose-only approval rejection.
- Unapproved Candidate input rejection.
- Direct Source PRD semantic read rejection.
- Hash drift in semantic artifact.
- Hash drift in review decision or schema.
- Stable stage and section ordering.
- Filesystem order rejection.
- Mechanical TOC generation.
- Mechanical reference index generation.
- Final DRD assembled from approved sections.
- Atomic inventory row accepted for page plus separate CTA.
- Atomic inventory row accepted for copy string.
- Atomic inventory row accepted for containment edge.
- Atomic inventory row accepted for z-axis or Material elevation decision.
- Paragraph-level inventory rejection.
- Screen bundle inventory rejection.
- Flow bundle inventory rejection.
- Layout bundle inventory rejection.
- Parent page row rejected as proof of child CTA conservation.
- Compiler-added CTA rejection.
- Compiler-added page or state rejection.
- Compiler-added interaction rejection.
- Compiler-added layout or z-axis rule rejection.
- Compiler-added user-facing copy rejection.
- Approved semantic unit omission rejection.
- Approved text paraphrase or summary rejection.
- Conflict routed to Human Gate.
- Recompile idempotence pass.
- Recompile nondeterminism failure.
- Manifest completeness.
- Hash partition completeness.
- `DRD-06` read-only QA pass.
- `DRD-06` mutation rejection.

## Acceptance Commands

Future implementation workpacks must run:

```bash
python -m pytest repository/tests/compiler
```

## Traceability Matrix

| Clause | Rule Families | Code Targets | Validator Checks |
|---|---|---|---|
| `DRD-CHARTER-011` | Closed approved compiler inputs | `compiler/final_drd.py`, `validators/compiler_conservation.py`, `compiler_input_bundle.schema.json` | `COMP-CHECK-001`, `COMP-CHECK-002`, `COMP-CHECK-003`, `COMP-CHECK-004` |
| `DRD-CHARTER-011` | Deterministic final DRD assembly | `compiler/final_drd.py`, `final_drd_manifest.schema.json`, `final_drd_toc.schema.json` | `COMP-CHECK-005`, `COMP-CHECK-006`, `COMP-CHECK-011`, `COMP-CHECK-012`, `COMP-CHECK-013` |
| `DRD-CHARTER-011` | Atomic conservation detection | `compiler/conservation.py`, `validators/compiler_conservation.py`, `compiler_conservation_report.schema.json`, `compiler_semantic_unit_inventory.schema.json`, `compiler_atomic_semantic_unit.schema.json` | `COMP-CHECK-007`, `COMP-CHECK-008`, `COMP-CHECK-009`, `COMP-CHECK-010`, `COMP-CHECK-015`, `COMP-CHECK-016`, `COMP-CHECK-017`, `COMP-CHECK-018`, `COMP-CHECK-019`, `COMP-CHECK-020` |
| `DRD-CHARTER-011` | Read-only QA boundary | `validators/compiler_conservation.py`, `read_only_qa_boundary.schema.json` | `COMP-CHECK-014` |
