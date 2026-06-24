# P1-SPEC-08 Skill Version Binding Contract

## Purpose

Skills are reusable execution flows. They are not fact sources and cannot override locked specifications.

This contract defines how a Skill may reference locked DRD Harness specs without becoming a second authority.

## Skill Authority Boundary

| Skill may | Skill must not |
|---|---|
| Describe a repeatable workflow for Codex. | Define new product, stage, validation, lock, compiler, or traceability rules. |
| Reference SPEC_LOCK hashes and accepted workpack types. | Replace Contract, Rule, Projection, Validator Spec, or Human Gate decisions. |
| Invoke commands that are already accepted by locked specs. | Add hidden implementation scope, write forbidden paths, or bypass review. |
| Emit Candidate outputs. | Approve, promote, seal, or lock its own outputs. |

## Skill Binding Manifest

Any business Skill generated for this Harness must include a structured binding manifest before use.

Required fields:

- `skill_id`
- `skill_version`
- `skill_source_path`
- `skill_source_hash`
- `bound_spec_locks`
- `allowed_workpack_types`
- `allowed_write_paths`
- `forbidden_write_paths`
- `allowed_commands`
- `traceability_rows`
- `validator_refs`
- `test_refs`
- `human_gate_required`
- `invalidation_dependencies`

`bound_spec_locks` must identify exact SPEC_LOCK IDs and hashes. A Skill that only names a spec part without lock hash is not current.

## Business Skill Introduction Gate

No business Skill may be generated or used until the applicable Contract, Rule, Projection, and Validator Spec have SPEC_LOCK coverage.

Skill introduction requires Human Gate when:

- The Skill changes Codex workflow for business implementation.
- The Skill writes or proposes writing repository code.
- The Skill introduces a new workpack type.
- The Skill covers more than one spec family.
- The Skill claims an exception to normal workpack scope.

## Skill Version Drift

If a Skill source hash changes, its binding manifest becomes invalid until revalidated.

If a bound SPEC_LOCK is superseded, the Skill becomes invalidated unless a structured unaffected claim proves the Skill does not depend on the changed lock.

Unvalidated Skill drift must block:

- Implementation workpack generation using that Skill.
- Promotion of code produced by that Skill.
- BUILD_LOCK evidence that cites that Skill.

## No Second Authority

A Skill may restate locked rules for operational convenience only when it cites the locked source. If the Skill text conflicts with the locked spec, the locked spec wins and the Skill must be repaired or disabled.

The following Skill behavior is forbidden:

- Inventing acceptance criteria.
- Relaxing validator requirements.
- Expanding allowed write paths.
- Treating examples as normative rules when the spec does not.
- Recommending direct edits to Constitution, control catalogs, references, tooling, or `.agents/skills`.
- Promoting Candidate code without Python validation and Human Gate approval.

## Skill Output Labeling

Skill-generated artifacts must remain Candidate outputs until validation, review, and promotion occur under lock rules.

Skill output records must name:

- The Skill binding manifest hash.
- The workpack ID.
- The traceability rows used.
- The SPEC_LOCK hashes used.
- Any Human Gate requirement.
