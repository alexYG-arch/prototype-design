# P2 SPEC_LOCK Creation Blueprint

## Command

```bash
python3 tooling/create_spec_lock.py --phase P2 --input-bundle build_program/phases/P2/candidates/P2-SPEC-LOCK-CREATION-READINESS/SPEC_LOCK_INPUT_BUNDLE.json --output control/locks/P2_SPEC_LOCK.json
```

## Required Human Boundary

Run the output command only after explicit user authorization to create `P2_SPEC_LOCK`.

## Expected Tool Behavior

1. Re-read P2-SPEC-01, P2-SPEC-02, and P2-SPEC-03 manifests.
2. Recompute subject hashes from generated outputs.
3. Re-read each `REVIEW_DECISION.json` and verify `APPROVED` plus subject hash binding.
4. Recompute the P2 root hash and review decision file root.
5. Validate against `control/schemas/spec_lock.schema.json`.
6. Write the lock only if the output path does not already exist.

## Preflight Before Real Write

Before running the real output command:

1. Confirm `control/locks/P2_SPEC_LOCK.json` does not exist.
2. Re-run the dry-run command and parse the JSON output.
3. Confirm dry-run `root_sha256` is `93eddcc641eaceb0d9793b2fb6eaa833a1526e4dc9d90345e2b018cc5beb1580`.
4. Confirm dry-run `review_decision_file_root_sha256` is `be11efe1ee5313854168eb7f2ebc76b6c6294cedaee24facfaa00605acf03b13`.
5. Confirm all P2 review IDs still match the values recorded in `SPEC_LOCK_INPUT_BUNDLE.json`.
