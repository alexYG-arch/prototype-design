# P1 BUILD_LOCK Creation Handoff

## What Changed

`control/locks/P1_BUILD_LOCK.json` was created by a Python-controlled BUILD_LOCK construction step.

## Important Hashes

| Item | Hash |
| --- | --- |
| BUILD_LOCK file | `c57528ba0736eab4cece6c14c0c1d13956e97b45cdfa7ae1fad956d0b58cceb2` |
| BUILD_LOCK root | `163dee6ac68384c6dc605a946a79702694b8fc9992c1ade02f3e7080acd1df3c` |
| Bound git commit | `6c2a5e66385364a6a11b8991960bc7d950f0454d` |
| SPEC_LOCK file | `ce311e07011987b6016abd15a0a3239a61e4ef653fc1d4b54fd330c475771b17` |
| Input matrix | `62d97de87249ecfbe574574ad71b348b6a5ae0013bc017de496d08328caa3269` |

## Human Review Focus

1. Confirm that `control/locks/P1_BUILD_LOCK.json` is the intended canonical BUILD_LOCK path.
2. Confirm that the BUILD_LOCK should bind 161 repository implementation output files from commit `6c2a5e66385364a6a11b8991960bc7d950f0454d`.
3. Confirm that `invalidates_on` should include SPEC_LOCK, implementation review subject/file hashes, test result hashes, and validator identity hashes.

## Remaining Boundary

This result does not create a release lock, does not promote the phase, and does not self-approve the result candidate.
