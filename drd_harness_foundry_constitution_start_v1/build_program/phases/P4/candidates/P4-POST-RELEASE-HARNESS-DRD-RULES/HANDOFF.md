# P4 Post-Release Harness DRD Rules Handoff

Review focus:

1. Confirm the four planned repairs are traceable to DRD-CHARTER-019 through DRD-CHARTER-022.
2. Confirm the installed harness can run external PRD `generate-drd` under package-root `current_capsule/outputs`.
3. Confirm page detail inventory preserves visible page text, controls, example values, state copy, priority markers, and visual order.
4. Confirm page/state derivation origin and page arrangement rules are enforced by schema and validators.
5. Confirm this candidate does not create a release lock, publish a package, or embed the 奇彩 PRD as repository fixture data.

Observed verification:

- Constitution validation passed.
- Full repository tests passed: 523 tests.
- Editable harness install passed.
- 奇彩 PRD isolated `generate-drd` passed with 2325 page detail records.
- Staged run produced DRD-00 outputs and stopped at DRD-01 human/Codex gate with resume invalidation state clear.
