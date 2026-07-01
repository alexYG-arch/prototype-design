# Repair Audit - External PRD Harness Isolation

## Audit Scope

本审计只覆盖当前 workpack `P4-PROGRAM-CLOSURE-STATUS-SYNC` 内的外部 PRD harness install contract 修复。

审计对象：

- 执行包入口和当前 capsule 约束；
- `drd-harness run` 的最小 receipt 行为；
- `drd-harness generate-drd` 的 DRD-00 到 DRD-06 文档生成行为；
- `drd-harness staged-run` 的宪章 runtime 边界；
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

## RF Review Finding

`RF_STAGE_RUNTIME_BINDING_REPAIR`

后续 R/F 复查发现 staged-run 初版存在更具体的 runtime 绑定问题：

- 宪章 runtime model 要求 `DRD-01` 的体验事实提炼由 Codex 负责；
- 初版 staged-run 用 Python 生成 `DRD-01/PRD_EXPERIENCE_BRIEF.md` 和 `DRD-01/experience_fact_index.json`，并把 `DRD-01` 标记为 completed；
- 这会把 source-preserving preparation 误当成真实 DRD-01 semantic stage execution，削弱宪章到 harness 的溯源可信度。

修复后：

- `staged-run` 只真实完成 `DRD-00` source freeze；
- `DRD-01` 停在 `CODEX_RUNTIME_GATE`；
- Python 只产出 `DRD-00/**`、`stage_execution_plan.json`、`review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json`、`codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md` 和 `run_state.json`；
- `staged-run` 不再用 Python 产出 DRD-01 canonical semantic artifacts。

## RF Review Finding

`RF_FINAL_DRD_READER_STRUCTURE_REPAIR`

后续 R/F 复查发现 `DRD-05/FINAL_DRD.md` 存在 reader-facing 结构缺口：

- `FINAL_DRD.md` 允许把已批准 stage 文档原文、hash/source/review gate 证据和 inventory 摘要混入正文；
- QA 只能证明 hash、边界和 no-lock/no-release，没有证明最终文档是可读规格；
- 这会削弱可维护性和可实现性，因为实现/设计读者需要最终规格，而不是审计证据包。

修复要求：

- 先在当前 capsule/执行包入口规则中声明 `FINAL_DRD.md` 是 reader-facing final spec；
- 再更新 compiler 与 validator，使 source/hash/review/gate/run_state 等过程证据只能进入 manifest/reference/hash/QA sidecar；
- 最后安装 editable harness 并执行 R/F loop 复查。

## RF Review Finding

`RF_STAGE_DUAL_ROLE_APPROVED_SEMANTIC_ARTIFACT_REPAIR`

后续 R/F 复查发现 `DRD-01` 到 `DRD-04/03B` 存在 stage 双角色问题：

- stage candidate 文档既承担 review/gate 证据，又被 `DRD-05` 当作最终正文来源；
- candidate 文档天然会包含“候选”、source hash、review path、gate 状态、validator 摘要等过程证据；
- 直接拼接 candidate 会让 `FINAL_DRD.md` 在语义完整性和 reader-facing 结构之间冲突，导致 D5 conservation 可通过但 D6 reader-facing QA 失败。

修复要求：

- 执行包声明 `candidate artifacts` 与 `approved semantic artifacts` 是两个产物身份；
- DRD-01 到 DRD-04/03B candidate 只供 review/gate 使用；
- gate 通过后必须 promotion 为 `APPROVED_SEMANTIC_ARTIFACT`，该产物绑定 source candidate、review decision、semantic body hash 和 process evidence sidecars；
- `DRD-05` compiler bundle 在 staged execution 中必须设置 `requires_approved_stage_semantic_artifacts=true`；
- compiler validator 必须拒绝把 candidate 文档当作 approved semantic body。

修复后：

- `repository/src/drd_harness/validators/compiler_conservation.py` 增加 approved stage semantic artifact bundle 校验；
- `repository/src/drd_harness/compiler/final_drd.py` 在 reference index 中保留 approved semantic artifact manifest 引用；
- `repository/schemas/stages/approved_semantic_artifact.schema.json` 定义 promoted artifact 结构；
- `repository/tests/compiler/test_final_drd_compilation.py` 覆盖 raw candidate 被拒绝、approved semantic body 被接受、candidate 过程标记被拒绝。

## Final Binding

最终状态已重新绑定到当前 capsule：

- `current_capsule/TASK.md` 声明外部 PRD run 只允许最小 `run_receipt.json`；
- `current_capsule/context_manifest.json` 声明外部 PRD 输出只能位于 `current_capsule/outputs/**`；
- `repository/src/drd_harness/orchestrator/program_driver.py` 使用外部 PRD 输出边界校验；
- `repository/src/drd_harness/compiler/external_prd.py` 使用同一输出边界校验；
- `repository/src/drd_harness/orchestrator/external_staged_run.py` 只完成 DRD-00，并在 DRD-01 Codex runtime gate 停止；
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
