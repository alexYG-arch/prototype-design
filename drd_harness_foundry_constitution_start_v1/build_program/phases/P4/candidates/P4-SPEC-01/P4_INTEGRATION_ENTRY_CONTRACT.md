# P4 Integration Entry Contract

## Purpose

`P4-SPEC-01` defines the integration entry surface for the DRD Harness after P3 build lock approval. It covers the program DAG, the program driver, the public `drdctl` command surface, and the PRD input adapters that feed the already locked harness stages.

This candidate does not define new product requirements, UX semantics, page elements, layout rules, or business contracts. It only specifies how P4 orchestration invokes, reviews, resumes, and releases locked harness capabilities.

## Upstream Authority

The only upstream build authority for this candidate is `control/locks/P3_BUILD_LOCK.json`.

Required upstream binding:

- P3 build lock path: `control/locks/P3_BUILD_LOCK.json`
- P3 build lock sha256: `52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e`
- P3 build lock root: `0ef47227a39e3eb75923e7506523b734769485431c2a7c3a1e1265f9d937fa8f`
- P3 build lock git commit: `f966182b4670520d2ba69e6f69eecca0bbc1d9b3`
- P3 build lock review decision: `build_program/phases/P3/candidates/P3-BUILD-LOCK-CREATION-RESULT/REVIEW_DECISION.json`
- P3 build lock review decision sha256: `4dd59a16355e5dc5c549de47e5abd77c8ec39343e6592f0bc258c4269330d291`

P4 integration may read P3 locked outputs. It may not rewrite P3 candidates, P3 locks, P3 fixtures, or root P3 phase files.

## Owned Surface

`P4-SPEC-01` owns these integration contracts:

1. Program DAG and program driver contract.
2. Public CLI contract for `drdctl run`, `drdctl review`, `drdctl resume`, and `drdctl release`.
3. PRD Harness Adapter contract.
4. Markdown PRD Adapter contract.
5. Entry validation, input normalization, and adapter evidence handoff.

It does not own:

- review recovery and lock rebuild semantics beyond command boundary declarations,
- regression, golden, integration, or release test suites,
- packaging, example projects, or release lock construction,
- any domain product contract.

Those surfaces remain for later P4 spec workpacks.

## Integration Invariants

1. The program driver is an orchestrator, not a semantic authority.
2. The CLI is thin: parsing, dispatch, structured output, and exit code mapping only.
3. Adapters normalize input into source evidence; they do not infer product capabilities.
4. Every command must emit deterministic machine-readable status.
5. Every command that can create or mutate artifacts must expose dry-run and boundary evidence.
6. A failed or partial run must produce enough evidence for later recovery specs to resume without guessing.
7. Release command behavior is declaration-only in this workpack; actual release lock rules belong to later P4 specs.

## Required Commands

### `drdctl run`

Purpose: create or continue a governed harness run from declared input sources.

Required inputs:

- project root or work directory,
- adapter id,
- source path or source bundle path,
- target phase or workpack when bounded execution is needed,
- output directory,
- optional dry-run flag.

Required outputs:

- run id,
- adapter result manifest,
- program DAG snapshot,
- stage execution plan,
- command status payload,
- evidence paths written or planned.

### `drdctl review`

Purpose: inspect a candidate review target and produce review packet evidence for Human Gate.

Required inputs:

- candidate directory,
- optional review target path,
- optional decision path.

Required outputs:

- candidate subject hash,
- generated section list,
- review target status,
- review decision binding status when supplied,
- machine-readable findings.

### `drdctl resume`

Purpose: resume a previously recorded run from explicit state.

Required inputs:

- run id or run state path,
- previous command status payload,
- requested resume point,
- upstream lock refs.

Required outputs:

- resume eligibility,
- skipped and replayed node list,
- invalidation state,
- next command plan.

Detailed recovery rules are owned by `P4-SPEC-02`; this candidate only reserves the command envelope and evidence boundary.

### `drdctl release`

Purpose: request release readiness evaluation.

Required inputs:

- build lock refs,
- release scope,
- package target,
- evidence bundle path.

Required outputs:

- release readiness packet,
- missing gate list,
- release lock eligibility state.

Actual release lock schema, package assembly, and release lock creation are owned by later P4 specs.

## Adapter Boundary

Adapters convert input formats to source evidence records.

Adapters must:

- preserve original input bytes or source hash,
- declare normalization steps,
- record unsupported content,
- route ambiguous or risky content to Human Gate,
- never create downstream product semantics directly,
- never mutate the source file.

The PRD Harness Adapter may consume structured harness bundles. The Markdown PRD Adapter may consume markdown files and split them into stable source sections. Both adapters emit source intake input records for existing P3 source handling.

## Human Review Boundaries

Human Gate is required when:

- adapter input is incomplete, inaccessible, conflicting, or unsafe to normalize,
- the requested command would cross a lock boundary,
- a command requests release lock creation,
- CLI flags imply mutation without explicit output directory,
- an adapter would need to infer product requirements from formatting alone.

## Non-Goals

`P4-SPEC-01` does not implement CLI code, create P4 locks, create release locks, update root P4 files, or approve itself.
