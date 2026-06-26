# P3-SPEC-ASSURANCE Contract

## Scope

`P3-SPEC-ASSURANCE` owns the P3 `assurance_traceability` module. It defines the final assurance layer that checks compiler output readiness, read-only QA boundaries, trace rows, test obligations, implementation workpack handoff, skill binding, and human gate evidence.

This workpack does not compile the DRD, implement validators, create product behavior, repair upstream gaps, create locks, or promote anything. It defines the conditions under which a future explicit `P3_SPEC_LOCK` creation request can be evaluated.

## Upstream Boundary

The direct upstream gate is `P3-SPEC-COMPILER/REVIEW_DECISION.json`.

| upstream | review decision sha256 | subject hash |
| --- | --- | --- |
| `P3-SPEC-COMPILER` | `1b9c2a9d7e115f8230bee406cdafb83b5315722dfef138de7a410f50c594b71f` | `3e6c8cb04f4572d9182f5df3974d5094193f9a2708dfcf09b14993cfa50b71ce` |

The assurance layer may inspect compiler contracts and review decisions. It must not alter compiler output, compiler input bundles, final DRD text, review decisions, source snapshots, or locks.

## Assurance Authority

Assurance is an evidence gate, not a semantic authoring stage.

It may assert:

- whether every implementation duty has a trace row
- whether every trace row has a matching positive and negative test obligation
- whether code targets are inside allowed paths and outside forbidden paths
- whether dependency edges declare invalidation behavior
- whether read-only QA stayed read-only
- whether human gate review has the required evidence
- whether a traceability exception is explicitly reviewed

It must not assert new product semantics, page semantics, interaction semantics, presentation semantics, layout semantics, copy, or compiler semantics.

## Trace Row Rule

Every future implementation duty must have one focused trace row. A trace row must bind:

- contract clause
- source spec part
- spec lock reference
- contract section
- rule id
- projection id
- implementation workpack id
- code target
- class or function
- validator
- test
- acceptance command
- validator check id
- allowed write paths
- forbidden write paths
- dependency edges
- invalidation policy

One trace row cannot bundle independent implementation duties. Generic duties such as "implement everything" are invalid.

## Test Obligation Rule

Every trace row must have a matching test obligation row with:

- same trace row id
- same implementation duty
- same validator check ids
- positive case
- negative case
- test path
- acceptance command

Positive-only tests are insufficient. Negative cases are required because assurance must prove that invalid scope, missing refs, unapproved inputs, and mutation attempts are rejected.

## Workpack Handoff Rule

Every implementation workpack produced from this assurance layer must be generated from an approved spec lock and must declare:

- required specs
- required spec locks
- traceability rows
- allowed write paths
- forbidden write paths
- code targets
- validators
- tests
- acceptance commands
- skill bindings
- dependency edges
- review policy
- promotion policy
- invalidation policy

Implementation workpacks cannot broaden scope beyond their trace rows. A traceability exception requires a human gate decision and a precise scope delta.

Generation metadata used by assurance must be deterministic. `generated_at` in implementation workpack indexes must come from a reviewed release identity, assurance run id, or input-bundle-derived generation id. It must not come from wall-clock time, local machine time, current user, current branch, or filesystem metadata when that value participates in reviewed hashes or lock readiness.

## Skill Binding Rule

Skills are execution helpers only. A skill binding may constrain commands, paths, tests, and trace rows. It cannot override specs, validators, locks, review gates, write paths, promotion policy, or source authority.

Any skill text that claims approval authority, relaxes validation, bypasses review, or creates new accepted paths is invalid.

## Read-Only QA Rule

`DRD-06` assurance reads compiled final DRD outputs and reports findings. It may write only:

- `READ_ONLY_QA_REPORT.md`
- `qa_finding_index.json`

It must not mutate final DRD text, compiler manifests, compiler indexes, review decisions, spec locks, build locks, source snapshots, or approved upstream artifacts.

If assurance finds an issue, it routes the finding to human gate and a governed repair workpack. It cannot patch compiled artifacts in place.

## Final Gate Rule

The final assurance gate passes only when:

- compiler review decision is approved and current
- compiler output package has passing conservation status
- read-only QA has no mutation
- trace rows validate
- test obligations match trace rows
- implementation workpack index has no orphan or broad workpacks
- skill bindings remain subordinate to specs and validators
- traceability exceptions are either absent or explicitly human-reviewed
- no unresolved invalidation remains
- generation metadata used in reviewed indexes is deterministic

Passing assurance does not create a lock by itself. Lock creation requires a separate explicit user request.
