# P4 Release Readiness Contract

## Purpose

`P4-SPEC-03` defines the final P4 specification surface for regression suites, v3.1 migration coverage, package readiness, example project readiness, release readiness packets, and `DRD_HARNESS_RELEASE_LOCK` input rules.

This candidate is spec-only. It does not create `P4_SPEC_LOCK`, `P4_BUILD_LOCK`, or `DRD_HARNESS_RELEASE_LOCK`. It does not publish a package, write repository implementation code, or approve itself.

## Upstream Authority

This candidate continues from the approved P4 recovery and resume specification.

Required upstream binding:

- P4-SPEC-02 review decision: `build_program/phases/P4/candidates/P4-SPEC-02/REVIEW_DECISION.json`
- P4-SPEC-02 review decision sha256: `b8e63fc5417845e1dfc59f46b668f703f74250de3806af067d47fda975f2d7c4`
- P4-SPEC-02 reviewed subject hash: `ad3cd18be72e36a8775ddf227df6bad0016207c7a294f93dd8b47aac193a9f34`
- P4-SPEC-01 review decision: `build_program/phases/P4/candidates/P4-SPEC-01/REVIEW_DECISION.json`
- P4-SPEC-01 review decision sha256: `9c7d9b84164ef55a8dd16de4845984f42728864c9dab8fa763cb72a2586e87e8`
- P3 build lock path: `control/locks/P3_BUILD_LOCK.json`
- P3 build lock sha256: `52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e`

## Owned Surface

`P4-SPEC-03` owns these contracts:

1. Golden regression suite requirements.
2. Integration suite requirements across CLI, adapters, program driver, recovery, and lock gates.
3. Release suite requirements for package dry-run, example project smoke, and release readiness.
4. v3.1 capability migration coverage map and gap rules.
5. Package manifest and example project manifest requirements.
6. `DRD_HARNESS_RELEASE_LOCK` input bundle and eligibility rules.

It does not own:

- program driver core DAG semantics from P4-SPEC-01,
- recovery and resume semantics from P4-SPEC-02,
- creation of any lock file,
- publishing to an external package registry,
- adding product requirements or business contracts.

## Release Readiness Invariants

1. Release readiness is evidence-driven and cannot be inferred from a passing test count alone.
2. Golden tests must be deterministic and must not update expected outputs during a release check.
3. Integration tests must prove CLI, adapters, program driver, recovery, and lock gates work together without bypassing Human Gate.
4. Release tests must run package dry-run and example project smoke checks before release lock eligibility.
5. v3.1 migration coverage must classify each legacy capability as `MIGRATED`, `REPLACED_BY_LOCKED_CAPABILITY`, `DROPPED_WITH_RATIONALE`, or `BLOCKED_REQUIRES_HUMAN_REVIEW`.
6. Release lock eligibility requires approved P4 spec inputs, approved P4 build lock input, passing release suite evidence, package evidence, example project evidence, and migration coverage evidence.
7. This candidate can define release lock inputs and readiness packets, but cannot write the release lock.

## Test Suite Families

| Suite | Purpose | Required Stop Rule |
| --- | --- | --- |
| `GOLDEN` | Prove stable canonical outputs for locked fixtures. | Stop if expected output would be rewritten. |
| `INTEGRATION` | Prove end-to-end P4 command and adapter flow. | Stop if Human Gate, lock, or write scope is bypassed. |
| `RELEASE` | Prove package, example project, release readiness, and migration coverage. | Stop before publishing or release lock creation. |

## Release Lock Boundary

The release lock input bundle must include:

- approved P4 spec decisions,
- approved P4 build lock reference,
- release suite report hash,
- package manifest hash,
- example project smoke report hash,
- v3.1 migration coverage report hash,
- release readiness packet hash,
- source git commit and dirty-state policy,
- explicit human authorization evidence for lock creation.

Without explicit separate authorization, the only allowed output is a release readiness packet or release lock candidate input bundle.

## Non-Goals

`P4-SPEC-03` does not implement tests, package code, release code, or lock creation code. It does not create `P4_SPEC_LOCK`, `P4_BUILD_LOCK`, `DRD_HARNESS_RELEASE_LOCK`, a package artifact, or a pull request.
