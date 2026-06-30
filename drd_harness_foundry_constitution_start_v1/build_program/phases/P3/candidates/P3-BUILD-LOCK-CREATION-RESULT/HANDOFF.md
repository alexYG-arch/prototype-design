# P3 BUILD_LOCK Creation Handoff

## What Changed

`control/locks/P3_BUILD_LOCK.json` was created by a Python-controlled BUILD_LOCK construction step.

## Important Hashes

| Item | Hash |
| --- | --- |
| BUILD_LOCK file | `52936deb8a497b4749434bfcb049555c0595748ff8bf7ac27b97273ffbdf917e` |
| BUILD_LOCK root | `0ef47227a39e3eb75923e7506523b734769485431c2a7c3a1e1265f9d937fa8f` |
| Bound git commit | `f966182b4670520d2ba69e6f69eecca0bbc1d9b3` |
| SPEC_LOCK file | `d8b45ecdc5417b4aab89c39038077d79da8b056f5c9558c97ecbe57d2f0cbff1` |
| Latest implementation review decision | `46632b4402f3e329f063a53b0edead4e693e14845ef7d0929eea0b84d3967127` |

## Human Review Focus

1. Confirm that `control/locks/P3_BUILD_LOCK.json` is the intended canonical BUILD_LOCK path.
2. Confirm that the BUILD_LOCK should bind 202 current P3 runtime, schema, fixture, and test files.
3. Confirm that `invalidates_on` should include P3_SPEC_LOCK, all P3 candidate review decisions, review subject hashes, file hash drift, and test result hash drift.
4. Confirm that the bound git commit contains the locked P3 runtime input files, while the result candidate remains unapproved and does not start P4.

## Remaining Boundary

This result does not create a release lock, does not promote the phase, does not start P4, and does not self-approve the result candidate.
