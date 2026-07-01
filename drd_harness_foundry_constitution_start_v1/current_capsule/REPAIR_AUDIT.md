# Repair Audit - External PRD Harness Isolation

## Audit Scope

本审计只覆盖当前 workpack `P4-PROGRAM-CLOSURE-STATUS-SYNC` 内的外部 PRD harness install contract 修复。

审计对象：

- 执行包入口和当前 capsule 约束；
- `drd-harness run` 的最小 receipt 行为；
- `drd-harness generate-drd` 的 DRD-00 到 DRD-06 文档生成行为；
- runtime boundary checker；
- editable install 后的源码树卫生。

## Finding

`LOCAL_SEQUENCE_INVERSION`

在一次 F 修复中，局部出现了先修改 `repository/**`，再补充 `START_HERE.md`、`current_capsule/TASK.md` 和 `current_capsule/context_manifest.json` 的倒序。

这不是功能层面的失败，但削弱了过程审计可信度，因为最严格的正规流程要求：

```text
先修改执行包和当前 capsule 约束
-> 再安装或更新 harness
-> 再修改 repository 实现和测试
-> 再跑验收命令
```

## Impact Assessment

- 当前 harness 行为没有因此失效；
- 当前执行包和 harness 的最终状态已经重新绑定；
- 未修改 `constitution/**`、`control/**`、`build_program/**`、`references/**` 或 `tooling/**`；
- 风险集中在过程可审计性，而不是输出正确性。

## Final Binding

最终状态已重新绑定到当前 capsule：

- `current_capsule/TASK.md` 声明外部 PRD run 只允许最小 `run_receipt.json`；
- `current_capsule/context_manifest.json` 声明外部 PRD 输出只能位于 `current_capsule/outputs/**`；
- `repository/src/drd_harness/orchestrator/program_driver.py` 使用外部 PRD 输出边界校验；
- `repository/src/drd_harness/compiler/external_prd.py` 使用同一输出边界校验；
- `repository/src/drd_harness/kernel/import_boundaries.py` 补强 runtime boundary path 检查；
- `repository/setup.cfg` 将 editable install 元数据导向 `.venv`，避免污染源码树。

## Future Repair Rule

`FUTURE_REPAIR_SEQUENCE`

后续 F 修复必须遵守：

1. 先更新执行包或当前 capsule 中的约束、允许路径、验收命令和 required file 绑定；
2. 再修改 `repository/**` 实现或测试；
3. 每次新增或修改必需文件后，必须同步 `current_capsule/context_manifest.json` 的 sha256；
4. 修复完成后必须运行 context manifest 中的 acceptance commands；
5. 如果再次发生局部倒序，必须立即更新本审计文件并明确说明影响范围。

## Current Status

`AUDIT_RECORDED_AND_BOUND`

本审计不批准 harness 结果，也不创建 lock，不推进下一个 workpack。它只记录过程缺口和后续修复纪律。
