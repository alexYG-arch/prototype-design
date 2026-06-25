# P2 SPEC_LOCK Creation Readiness

## Status

This Candidate is approved by human review as the P2 SPEC_LOCK creation readiness input. It does not create `P2_SPEC_LOCK`.

## Ready Inputs

| Item | Value |
| --- | --- |
| Phase | `P2` |
| Approved readiness Candidate | `build_program/phases/P2/candidates/P2-SPEC-03` |
| Readiness review decision | `build_program/phases/P2/candidates/P2-SPEC-03/REVIEW_DECISION.json` |
| Readiness subject hash | `1b2a2145ec44c7f9a523166c635c22b7b26fe54108c58545ff36254ba386c2a7` |
| Readiness review decision file hash | `3ff4b137cb489b188eff2bf0b4f726c622c77dbea993a3386196b26b1f4812b1` |
| P2 approved spec input root | `93eddcc641eaceb0d9793b2fb6eaa833a1526e4dc9d90345e2b018cc5beb1580` |
| P2 review decision file root | `be11efe1ee5313854168eb7f2ebc76b6c6294cedaee24facfaa00605acf03b13` |
| Control schema | `control/schemas/spec_lock.schema.json` |
| Control schema hash | `52542478b091d780e88d2ee6aeedfe5b1319ea4bcf6605f0329d94c8fc25acec` |
| Python lock tool | `tooling/create_spec_lock.py` |
| Python lock tool hash | `053ea4c3cd333e38f33ee91f7cc1f4e26202786e3f1e567d2f425f20b058a58a` |

## Boundary

The next real lock action still requires an explicit user instruction to create `P2_SPEC_LOCK`. A generic continue instruction or this approval is not enough because lock creation writes canonical control state.

## Tooling Result

`tooling/create_spec_lock.py` is expected to accept `SPEC_LOCK_INPUT_BUNDLE.json` in dry-run mode and recompute all candidate subject hashes from disk.

## Additional Machine Checks

This package now validates more than a dry-run exit code:

- The dry-run lock JSON is parsed and checked for lock id, phase, root hash, review file root, schema, source candidate, and file count.
- Each P2 review `review_id`, review decision file hash, and subject hash is bound against the current review decision file.
- The intended output path `control/locks/P2_SPEC_LOCK.json` is checked as absent before real lock creation.
