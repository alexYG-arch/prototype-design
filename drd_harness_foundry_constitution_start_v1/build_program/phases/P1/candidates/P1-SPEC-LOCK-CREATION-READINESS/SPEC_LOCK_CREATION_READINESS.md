# P1 SPEC_LOCK Creation Readiness

## Status

This Candidate is ready for human review before creating a canonical `SPEC_LOCK`.

The P1 specification inputs are ready for lock creation review, and the repository now contains a narrow Python-controlled lock creation tool at `tooling/create_spec_lock.py`. Per P1 validation-lock rules, the tool can create a canonical `SPEC_LOCK`; Codex prose or hand-authored JSON still cannot.

## Ready Inputs

| Item | Value |
| --- | --- |
| Phase | `P1` |
| Approved phase readiness Candidate | `build_program/phases/P1/candidates/P1-PHASE-LOCK-READINESS` |
| Phase readiness review decision | `build_program/phases/P1/candidates/P1-PHASE-LOCK-READINESS/REVIEW_DECISION.json` |
| Phase readiness subject hash | `da2a6acd1c9be5dbfc6a5426a1b467142e6e86b34b15cd042e74934d6cafe4cb` |
| Phase review decision file hash | `14c949af9914dc93463e4f0f5892f2c66b11a4c42af6b34ef0611361b5125590` |
| P1 approved spec input root | `6fabf51bb2990aa630cffedc07c8aa5100b4e177e3a6890e3a31cae386850be1` |
| P1 review decision subject root | `6fabf51bb2990aa630cffedc07c8aa5100b4e177e3a6890e3a31cae386850be1` |
| P1 review decision file root | `2f98caaeab5db11686e58747ed53624f6173798c27b2ef154b590731e8932509` |
| Control schema | `control/schemas/spec_lock.schema.json` |
| Control schema hash | `52542478b091d780e88d2ee6aeedfe5b1319ea4bcf6605f0329d94c8fc25acec` |
| Python lock tool | `tooling/create_spec_lock.py` |
| Python lock tool hash | `053ea4c3cd333e38f33ee91f7cc1f4e26202786e3f1e567d2f425f20b058a58a` |

## Tooling Status

`tooling/create_spec_lock.py` exists and has been tested in dry-run mode and temporary-output mode.

The tool performs the narrow lock creation duty only:

- Recompute each Candidate subject hash from `generated_outputs`.
- Verify every approved `REVIEW_DECISION.json` binding.
- Recompute the P1 phase root and review decision file root.
- Verify the phase-level review decision file hash.
- Validate the lock object against `control/schemas/spec_lock.schema.json`.
- Write only to an explicit `--output` path, and fail if the target already exists.

No implemented promotion module exists at `repository/src/drd_harness/orchestrator/promotion.py`. That remains a later promotion-flow gap, not a reason to hand-write `SPEC_LOCK`.

No repository-side lock schema exists at `repository/schemas/locks/spec_lock.schema.json`; the current lock creation tool treats `control/schemas/spec_lock.schema.json` as the schema authority.

## Required Boundary

Human approval of the phase readiness Candidate means the input bundle may be used by the lock creator. It does not itself create a canonical `SPEC_LOCK`.

The next valid action is to review the narrow Python tool, then explicitly authorize running it against an approved canonical output path.

## Forbidden Shortcuts

- Do not write `SPEC_LOCK` directly by editing JSON in this Candidate.
- Do not treat `P1_SPEC_LOCK_CANDIDATE.json` as canonical lock authority.
- Do not mark implementation workpacks as authorized until a canonical `SPEC_LOCK` exists.
- Do not modify `control/**` or `repository/**` from this Candidate without explicit authorization for implementation work.
