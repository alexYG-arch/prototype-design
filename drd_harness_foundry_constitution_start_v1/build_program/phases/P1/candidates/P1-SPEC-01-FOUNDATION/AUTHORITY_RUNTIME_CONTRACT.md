# P1-SPEC-01 Foundation: Authority and Runtime Contract

## Authority Order

The Harness must preserve this authority order:

```text
Source PRD and approved platform constraints
→ Human decisions
→ Locked DRD Constitution and Contracts
→ Approved upstream Stage artifacts
→ Rules and Projection Rules
→ Skills and Workpacks
→ Candidate implementation or document output
```

Lower-authority artifacts may reference higher-authority artifacts, but may not silently override them.

## Runtime Declaration

Every Stage, Workpack, Validator, Promotion action, and Compiler action must declare:

- `primary_runtime`: one of `PYTHON`, `CODEX`, `CODEX_PYTHON_LOOP`, or `HUMAN_GATE`.
- `python_duties`: deterministic control duties.
- `codex_duties`: candidate semantic duties.
- `validator`: validator name or validator family.
- `human_gate`: review requirement or explicit absence of review.
- `authority_inputs`: source documents, locks, approved artifacts, and human decisions consumed.
- `write_scope`: paths or artifact families the action may change.
- `forbidden_scope`: paths or artifact families the action must not change.

The canonical machine-readable structure for this declaration must be promoted to:

```text
repository/schemas/runtime_declaration.schema.json
```

Validators must treat this schema as the required shape for runtime declarations instead of relying on informal Python-only conventions.

## Runtime Responsibilities

| Runtime | Owns | Does not own |
|---|---|---|
| Python Runtime | Snapshot, hash, schema validation, graph checks, lock construction, deterministic compilation, promotion, invalidation. | New semantic decisions, product expansion, or hidden UI reasoning. |
| Codex Runtime | Candidate semantic classification, deductive reasoning records, natural-language contracts, scoped repair candidates, code candidates after applicable locks. | Approval, promotion, lock authority, direct canonical mutation, or unsourced product expansion. |
| Human Gate | Review decisions, scope disputes, inductive candidate approval, final semantic acceptance. | Deterministic hash calculation or mechanical validation execution. |

## Candidate Boundary

Codex output is always a Candidate until:

1. Required deterministic validators pass.
2. Required Human Gate decision is recorded.
3. Python promotion writes or assembles the canonical artifact.

This contract does not assign promotion authority to Codex.

## Review Binding

A human review decision must bind a subject hash. The reviewed subject may be a single Candidate file, a Candidate directory digest, an assembled spec package, or a lock input bundle. The subject definition must be explicit enough for deterministic recomputation.

## Runtime Examples

- DRD-00 Source freeze: `PYTHON` primary runtime, no Codex duties, no Human Gate.
- DRD-01 Experience fact extraction: `CODEX` primary runtime with Python context and citation validation.
- DRD-02 Interaction closure: `CODEX_PYTHON_LOOP` because Codex derives semantics and Python validates graph closure.
- DRD-05 Compilation: `PYTHON` primary runtime; Codex may only perform read-only QA after compilation.
