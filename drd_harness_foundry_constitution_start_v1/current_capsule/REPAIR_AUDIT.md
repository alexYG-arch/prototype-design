# Repair Audit - External PRD Harness Isolation

## Audit Scope

本审计只覆盖当前 workpack `P4-PROGRAM-CLOSURE-STATUS-SYNC` 内的外部 PRD harness install contract 修复。

审计对象：

- 执行包入口和当前 capsule 约束；
- `drd-harness run` 的最小 receipt 行为；
- `drd-harness compile-source-preserving-drd` 的 DRD-00 到 DRD-06 文档生成行为；`generate-drd` 只保留为兼容 alias；
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

`RF_SOURCE_PRESERVING_NAMING_REPAIR`

后续 R/F 复查发现 source-preserving 外部 PRD 编译入口命名存在语义混淆：

- `generate-drd` 看起来像完整 staged execution，而实际只做 source-preserving DRD compile；
- 产物名 `FINAL_DRD.md` 容易和 `staged-run` 的 `DRD-05/FINAL_DRD.md` 混淆；
- 首次命令命名不精确会让 check、memory 和执行记录看起来像完整 run 包。

修复后：

- 正式入口改为 `drd-harness compile-source-preserving-drd`；
- `generate-drd` 只保留为兼容 alias，不再出现在主 help 的 canonical 命令列表中；
- source-preserving 输出改为 `SOURCE_PRESERVING_DRD.md`；
- 完整 staged execution 的 `DRD-05/FINAL_DRD.md` 名称保持不变，只能由 `staged-run` 链路生成。

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

## RF Review Finding

`RF_CODEX_RUNTIME_CONTINUATION_EXECUTOR_REPAIR`

后续 R/F 复查发现 staged-run 修复后仍存在更深一层的执行缺口：

- 宪章 runtime chain 要求 `DRD-01`、`DRD-02`、`DRD-03`、`DRD-03B`、`DRD-04` 和 `DRD-06` 由 Codex 或 Codex+Python loop 负责候选语义推理 / 只读 QA；
- 当前 `staged-run` 能诚实停在 `DRD-01 CODEX_RUNTIME_GATE`，但 harness 没有正式 continuation executor 把该 gate 接到 Codex CLI 或显式 runtime command；
- 这导致运行者容易把当前聊天中的手工 continuation 或 Python materialization 误认为正式 stage runtime，削弱 `CODEX` runtime 声明和实际执行之间的可审计性。

修复要求：

- 保持 `staged-run` 的 DRD-00 + runtime gate stop 行为不变；
- 新增 `drd-harness codex-stage` continuation 入口；
- `codex-stage` 必须读取 `run_state.json` 和 `stage_execution_plan.json`，只允许执行 plan 中声明为 `CODEX`、`CODEX_PYTHON_LOOP` 或 `CODEX_READ_ONLY` 的 stage；
- Python 只负责生成/绑定 prompt、调用 Codex runtime、校验预期 candidate outputs、记录 invocation/result sidecars 和更新 run_state；
- `codex-stage` 不得 review、approval、promotion、compile `FINAL_DRD.md`、创建 lock/release 或发布 package；
- 没有可用 Codex runtime 时必须返回 `CODEX_RUNTIME_UNAVAILABLE`，不得降级为 Python 语义生成。

修复后：

- `repository/src/drd_harness/runtimes/codex_cli.py` 提供 Codex CLI / runtime command adapter；
- `repository/src/drd_harness/orchestrator/codex_stage.py` 提供 stage continuation 编排；
- `repository/src/drd_harness/cli/main.py` 暴露 `codex-stage`；
- `repository/tests/p4/test_external_prd_staged_run.py` 覆盖 dry-run、无 runtime 停止和 fake runtime candidate-ready 更新。

`RF_STAGE_COMPILE_AND_QA_COMPLETION_REPAIR`

真实 staged execution 继续到 DRD-05/DRD-06 时暴露两个缺口：

- promoted approved semantic artifact 仍保留部分 candidate/status/run/source hash 过程标记，导致 DRD-05 reader-facing compiler 可能拒绝或污染 `FINAL_DRD.md`；
- harness 有 deterministic compiler 函数和 DRD-06 read-only boundary validator，但缺少正式 staged continuation CLI 将 DRD-05 编译、DRD-06 QA PASS 和 `staged_execution_complete=true` 串起来。

修复要求：

- `promote-stage` 在生成 `APPROVED_SEMANTIC_ARTIFACT.md` 时必须删除 candidate status、run id、source hash、stage boundary 等过程行；
- 新增 `drd-harness compile-stage`，只允许 `DRD-05`，只消费 promoted approved semantic artifacts，调用现有 deterministic compiler，写出 `DRD-05/FINAL_DRD.md` 与 compiler sidecars，不调用 Codex、不创建 lock/release/package；
- 新增 `drd-harness qa-complete-stage`，只允许 `DRD-06`，必须在 QA status PASS、DRD-05 canonical output hash 未漂移、DRD-06 只写 read-only QA outputs 时才声明 staged execution complete；
- `codex-stage` 对 `DRD-06` 必须返回 read-only QA ready 状态，而不是 semantic candidate promotion 状态。

修复后：

- `repository/src/drd_harness/orchestrator/stage_compilation.py` 提供 DRD-05 compile continuation；
- `repository/src/drd_harness/orchestrator/qa_completion.py` 提供 DRD-06 completion validation；
- `repository/src/drd_harness/orchestrator/stage_promotion.py` 清理 approved body 的候选过程标记；
- `repository/src/drd_harness/orchestrator/codex_stage.py` 支持 DRD-06 `CODEX_READ_ONLY_QA_READY`；
- `repository/tests/p4/test_external_prd_staged_run.py` 覆盖 DRD-05 compile 和 DRD-06 completion。

## Final Binding

最终状态已重新绑定到当前 capsule：

- `current_capsule/TASK.md` 声明外部 PRD run 只允许最小 `run_receipt.json`；
- `current_capsule/context_manifest.json` 声明外部 PRD 输出只能位于 `current_capsule/outputs/**`；
- `repository/src/drd_harness/orchestrator/program_driver.py` 使用外部 PRD 输出边界校验；
- `repository/src/drd_harness/compiler/external_prd.py` 使用同一输出边界校验；
- `repository/src/drd_harness/orchestrator/external_staged_run.py` 只完成 DRD-00，并在 DRD-01 Codex runtime gate 停止；
- `repository/src/drd_harness/orchestrator/codex_stage.py` 负责从 Codex runtime gate 继续到 stage candidate-ready，但不做 approval/promotion；
- `repository/src/drd_harness/orchestrator/stage_promotion.py` 负责人工批准后的 approved semantic artifact promotion；
- `repository/src/drd_harness/orchestrator/stage_compilation.py` 负责 DRD-05 deterministic compile continuation；
- `repository/src/drd_harness/orchestrator/qa_completion.py` 负责 DRD-06 read-only QA completion validation；
- `repository/src/drd_harness/runtimes/codex_cli.py` 负责 Codex CLI / explicit runtime command 调用边界；
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
