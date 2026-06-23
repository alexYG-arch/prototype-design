# DRD Harness Repository Instructions

`repository/` is the product being built. Only active Implementation Workpacks may modify it.

- Do not import from `build_program/` or `references/`.
- Keep CLI thin.
- Python owns deterministic control and validation.
- Codex Runtime owns semantic Candidate generation only.
- Business rules live in locked contracts/rules, not in CLI or hidden Prompt text.
- Tests must map to locked obligations.
