# Spec-to-Code Policy

每个 Spec Package 必须输出：

```text
IMPLEMENTATION_BLUEPRINT.md
CODE_TARGET_MAP.json
TEST_OBLIGATION_MATRIX.json
IMPLEMENTATION_WORKPACK_INDEX.json
```

## Required mapping

```text
Contract Clause
→ Rule
→ Projection
→ Code Module
→ Class / Function
→ Validator
→ Test
→ Acceptance Command
```

## Implementation Workpack rules

每个 Workpack 必须绑定：

- SPEC_LOCK；
- 精确 Contract / Rule / Projection ID；
- 允许和禁止路径；
- 必需文件、类、函数或命令；
- 正例、负例和边界例；
- 测试与 Handoff。

## Builder restrictions

Codex Builder 不得修改锁定 Constitution、Contract、Rule、Independent Validator 或 Golden Test；不得扩大 Workpack；不得自动推进下一任务。

## Spec gap

发现规范不足时，输出 `SPEC_CHANGE_REQUEST.md` 并停止。不得把未批准决定藏进代码或 Prompt。
