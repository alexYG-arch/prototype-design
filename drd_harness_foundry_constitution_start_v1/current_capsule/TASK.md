# P1-SPEC-00 — Generate P1 Phase Plan and Spec-to-Code Ownership

## Objective

依据锁定宪章，生成可供后续 P1 Spec 分片和 P1 Implementation Workpack 使用的完整阶段计划。

## Required outputs

仅写入：

```text
build_program/phases/P1/candidates/P1-SPEC-00/
```

必须生成：

1. `P1_PHASE_PLAN.md`
2. `P1_CLAUSE_OWNERSHIP.json`
3. `P1_SPEC_PART_MAP.json`
4. `P1_IMPLEMENTATION_WORKPACK_MAP.json`
5. `P1_ACCEPTANCE_MATRIX.json`
6. `P1_ASSEMBLY_SEED.json`
7. `CANDIDATE_MANIFEST.json`
8. `PART_SELF_CHECK.md`
9. `HANDOFF.md`

## Required content

- 覆盖 `control/CLAUSE_INVENTORY.json` 中的全部锁定 Clause；
- 每个 Clause 有唯一 Spec owner；
- P1 Spec 必须同时产出 Contract、Rule、Projection、Validator Spec、Examples 和 Implementation Blueprint；
- P1 Implementation 必须映射到 `repository/` 的真实代码、Validator 和测试路径；
- 显式区分 Python Runtime、Codex Runtime 和 Human Gate；
- 包含 Spec→Code 的 Contract→Rule→Code→Validator→Test 链；
- 不得出现 `TBD`、`TODO`、“后续定义”或无 owner 条目。

## Forbidden

- 不得实现 Harness 代码；
- 不得修改锁定宪章；
- 不得生成 P2–P4 Candidate；
- 不得 Seal 或批准本 Candidate。

## Acceptance commands

```bash
python tooling/validate_p1_spec00_candidate.py
python tooling/preflight_current_workpack.py --post
```
