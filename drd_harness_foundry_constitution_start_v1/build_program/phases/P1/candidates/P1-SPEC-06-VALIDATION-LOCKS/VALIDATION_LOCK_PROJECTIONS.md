# P1-SPEC-06 Validation Lock Projections

## Projection Index

| Projection ID | Source | Target | Purpose |
|---|---|---|---|
| `VLOCK-PROJ-001` | Candidate output files | Candidate subject hash | Binds review and validation to exact generated outputs. |
| `VLOCK-PROJ-002` | Candidate manifest | Required output coverage report | Confirms required files exist and are non-empty. |
| `VLOCK-PROJ-003` | Git/worktree changes | Scope postflight report | Detects allowed and forbidden path changes. |
| `VLOCK-PROJ-004` | Validator commands | Validation result record | Captures command, exit code, result hash, and blocker list. |
| `VLOCK-PROJ-005` | Human Gate decision | Review decision record | Binds decision to subject hash and approved sections. |
| `VLOCK-PROJ-006` | Validated Candidate plus review decision | Promotion readiness record | Determines if promotion may proceed. |
| `VLOCK-PROJ-007` | Approved spec files plus validator results | SPEC_LOCK readiness record | Identifies files and hashes ready for lock creation. |
| `VLOCK-PROJ-008` | Implementation outputs plus tests | BUILD_LOCK readiness record | Identifies build outputs and test evidence ready for lock creation. |
| `VLOCK-PROJ-009` | Upstream dependency hashes | Dependency graph | Maps downstream subjects to upstream hash bindings. |
| `VLOCK-PROJ-010` | Changed upstream hashes | Invalidation records | Marks affected downstream subjects and required action. |
| `VLOCK-PROJ-011` | Superseding locks | Supersession index | Links new lock to old lock and affected dependents. |
| `VLOCK-PROJ-012` | Validator code, schema, runtime, and command | Validator identity records | Binds validation results to reproducible validator identity. |
| `VLOCK-PROJ-013` | Dependency graph edges | Typed dependency edge index | Distinguishes source, review, spec lock, build lock, validator, test, workpack, skill, and release dependencies. |
| `VLOCK-PROJ-014` | Partial invalidation analysis | Partial unaffected claim records | Structures affected and unaffected paths plus proof. |
| `VLOCK-PROJ-015` | Invalidated subjects | Invalidation recovery plan | Assigns owner and required command or workflow. |
| `VLOCK-PROJ-016` | Lock supersession index | Acyclic supersession graph | Detects direct and transitive self-supersession. |

## Projection Requirements

Each projection must preserve:

- Source or upstream hash.
- Candidate subject hash.
- Review decision hash.
- Validator result hash.
- Validator identity hash.
- Lock root hash when a lock applies.
- Typed dependency graph edges.
- Invalidation IDs when a downstream subject is affected.
- Partial unaffected claim IDs when a subject is only partly affected.
- Recovery owner and required command when a subject is invalidated.

## Disallowed Projection Behavior

A projection must not:

- Bind review to a stale subject hash.
- Treat Candidate output as canonical without approval and promotion readiness.
- Create a lock from incomplete file lists.
- Drop validator command or result evidence.
- Drop validator code hash, schema hash, runtime identity, or version.
- Ignore old downstream subjects when an upstream hash changes.
- Use untyped dependency edges.
- Accept prose-only unaffected claims.
- Mark invalidation ready without owner and required command or workflow.
- Create a cyclic lock supersession chain.
- Edit old lock records in place.

## Projection To Validators

The projection set feeds:

- Candidate-only validator.
- Required output validator.
- Scope postflight validator.
- Review binding validator.
- Promotion readiness validator.
- SPEC_LOCK readiness validator.
- BUILD_LOCK readiness validator.
- Dependency graph validator.
- Invalidation propagation validator.
- Lock supersession validator.
- Validator identity validator.
- Dependency edge type validator.
- Partial unaffected claim validator.
- Invalidation recovery plan validator.
- Supersession acyclicity validator.
