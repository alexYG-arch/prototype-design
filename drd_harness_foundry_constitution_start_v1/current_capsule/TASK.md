# Harness Install Contract — External PRD Isolation

## Objective

按“先修改执行包，再安装 harness”的正规流程，修正外部 PRD harness 合约：

- 删除外部 PRD run 中的证据链 stage；
- 外部 PRD run 只保留最小 `run_receipt.json`；
- source-preserving 文档生成必须使用清晰命名，显式声明不是完整 staged execution；
- 新增外部 PRD 的真实 staged-run 边界，用 `DRD-00` 到 `DRD-06` 作为唯一 stage chain；
- 新增外部 PRD 的 Codex runtime continuation 入口，使 `CODEX`、`CODEX_PYTHON_LOOP` 和 `CODEX_READ_ONLY` stage 能通过正式 runtime adapter 产出 candidate，而不是停留在 gate/prompt 文档；
- 完整 staged execution 的 `DRD-05/FINAL_DRD.md` 必须是面向读者的最终规格文档，不得退化为候选产物拼接、证据包、hash/source/review 日志或 inventory dump；
- lock/release 保留给执行包治理，不放进外部 PRD run。

## Scope guardrail

`P4-PROGRAM-CLOSURE-STATUS-SYNC` 只表示执行包自身的治理来源标签，不表示外部 PRD run 属于 P4，也不得把外部 PRD 产物写入 `build_program/phases/P4/**`。

本任务必须先修改执行包入口说明、当前 capsule 说明和 context manifest，再安装/更新 harness。不得绕过执行包直接把旧证据链模型留在 harness 中。

本任务可以修改 harness 代码、测试、compiler fixture、当前 capsule 说明、根启动说明和安装入口提示，但不得修改宪章、control locks、release lock，也不得把外部 PRD 业务内容写入执行包治理目录。

外部 PRD 运行产物只能写入 `current_capsule/outputs/**`。PRD 转 DRD 的生成过程不得新增 PRD 产品能力；若需要推导缺失页面、二三级页面、元素或业务能力，必须进入人工 review，而不能由 harness 自动补全。

完整 harness stage run 不能由保源编译入口代替。`compile-source-preserving-drd` 只是 source-preserving compile；完整 stage 执行必须使用 `drd-harness staged-run`，并且在缺少 Codex/Human Gate 输入时停在相应 stage，而不是伪造后续语义产物。旧入口名 `generate-drd` 只能作为兼容 alias，不得作为主入口命名。

`staged-run` 本身仍不得静默跨过 Codex runtime gate。继续执行 Codex-owned stage 必须使用独立的 `drd-harness codex-stage` continuation 入口。该入口只负责调用 Codex runtime 生成 stage candidate、校验预期 candidate 输出存在、记录 runtime sidecar 并更新 `run_state.json`；不得批准、promotion、编译 `FINAL_DRD.md`、创建 lock/release 或发布 package。

DRD-01 到 DRD-04/03B 必须拆分两个产物身份：

- `candidate artifacts`：Codex 或 Codex+Python 生成的待审阅产物，可以包含候选标签、输入绑定、review focus、validator 摘要和过程证据；它只供 gate/review 使用。
- `approved semantic artifact`：gate 通过后由 promotion 形成的可编译语义产物，必须绑定 source candidate、review decision、semantic body hash 和 process evidence sidecars；正文只能包含最终语义，不得包含候选标签、hash/source/review/gate/run_state 等过程证据。

同一个文件不得同时充当 candidate artifact 和 approved semantic artifact。`DRD-05` 只能消费 `APPROVED_SEMANTIC_ARTIFACT`，不得直接拼接 `DRD-01` 到 `DRD-04` 的 candidate 文档。若 approved semantic artifact 不存在，完整 staged execution 必须停住，而不是用 candidate 代替。

`DRD-05` 汇编必须执行 reader-facing structure gate：

- 完整 staged execution 的 `FINAL_DRD.md` 只能包含最终规格正文、确定性目录和必要章节标题；
- 证据引用、hash、source path、review decision、gate 状态、run_state 和 approval 绑定必须保存在 manifest/reference/hash/QA sidecar 中，不得进入最终正文主体；
- 不得把 `DRD-01` 到 `DRD-04` 的候选文档原文整段拼接进最终正文；
- 不得出现多个一级标题，不得保留“候选/CANDIDATE”过程标签；
- 页面变体完整 inventory 应保存在结构化 index 或附录 sidecar；最终正文只能保留面向实现/设计阅读的分组规格，不得逐行 dump `renderable_page_variants`。

若修复过程中出现先改 harness 再补执行包约束的局部倒序，必须记录到 `current_capsule/REPAIR_AUDIT.md`，并在 context manifest 中绑定该审计文件。

## Required run outputs

运行目录由调用方指定，必须位于：

```text
current_capsule/outputs/
```

每次标准 run 至少产出：

1. `run_receipt.json`

`run_receipt.json` 必须只包含：

- 输入源路径、源 hash、适配器 id、适配器状态；
- source section 计数和 source ref 计数；
- DRD-00 到 DRD-06 文档生成 stage 顺序；
- 输出目录和写入边界；
- `lock_in_external_prd_run=false`；
- `release_in_external_prd_run=false`；
- `package_publish_in_external_prd_run=false`。

## Required DRD generation outputs

`drd-harness compile-source-preserving-drd` 的输出目录由调用方指定，实际使用时必须位于：

```text
current_capsule/outputs/
```

每次标准 DRD 生成至少产出：

1. `external_prd_section_index.json`
2. `external_prd_review_decision.json`
3. `external_prd_source_snapshot_binding.json`
4. `external_prd_validation_report.json`
5. `drd_generation_stage_plan.json`
6. `compiler_input_bundle.json`
7. `SOURCE_PRESERVING_DRD.md`
8. `final_drd_manifest.json`
9. `final_drd_toc.json`
10. `final_drd_reference_index.json`
11. `final_drd_hash_index.json`
12. `compiler_conservation_report.json`
13. `compiler_semantic_unit_inventory.json`

`compile-source-preserving-drd` 的 status payload 必须显式包含：

- `source_preserving_compile_only=true`
- `staged_execution_complete=false`
- `staged_execution_command=staged-run`
- `canonical_command=compile-source-preserving-drd`
- `legacy_command_aliases=["generate-drd"]`

## Required staged-run outputs

`drd-harness staged-run` 的输出目录由调用方指定，实际使用时必须位于：

```text
current_capsule/outputs/
```

在没有 Codex 运行时，或尚未存在已批准 DRD-01 语义候选时，标准 staged run 必须只真实完成 `DRD-00`，然后停在 `DRD-01` 的 Codex runtime gate。它必须产出：

1. `stage_execution_plan.json`
2. `DRD-00/source_prd_snapshot.md`
3. `DRD-00/source_snapshot_manifest.json`
4. `DRD-00/stage_receipt.json`
5. `review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json`
6. `codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md`
7. `run_state.json`

标准 staged run 的 status 必须是 `STAGE_GATE_STOPPED`，并声明：

- `completed_stage_ids=["DRD-00"]`
- `blocked_stage_id=DRD-01`
- `blocked_gate_id=CODEX_RUNTIME_GATE`
- `next_required_runtime=CODEX`
- `staged_execution_complete=false`
- 不创建 control lock、release lock，不发布 package。

标准 staged run 不得产出 `FINAL_DRD.md` 或 `SOURCE_PRESERVING_DRD.md`，也不得用 Python 产出 `DRD-01/PRD_EXPERIENCE_BRIEF.md` 或 `DRD-01/experience_fact_index.json`。只有 Codex 产出并通过校验的 DRD-01 candidate、后续 DRD-02 到 DRD-04/03B candidate、对应 gate decision，以及每个 stage 的 `approved semantic artifact` 都存在后，DRD-05 才能编译；DRD-05/DRD-06 通过后才能声明 staged execution complete。

## Required Codex stage continuation outputs

`drd-harness codex-stage` 的输入必须是现有 `run_state.json` 和目标 `stage_id`。它只能用于 `stage_execution_plan.json` 中声明为 `CODEX`、`CODEX_PYTHON_LOOP` 或 `CODEX_READ_ONLY` 的 stage。

每次非 dry-run continuation 至少产出：

1. `runtime_invocations/<STAGE_ID>_codex_runtime_invocation.json`
2. `runtime_results/<STAGE_ID>_codex_runtime_result.json`
3. 目标 stage 的预期 candidate outputs；`DRD-06` 使用只读 QA canonical outputs。
4. 更新后的 `run_state.json`

`codex-stage` status 必须区分：

- `CODEX_STAGE_DRY_RUN`：只报告 invocation plan，不写文件；
- `CODEX_RUNTIME_UNAVAILABLE`：找不到 Codex runtime 或 runtime command 不可执行；
- `CODEX_STAGE_FAILED`：runtime 返回非零或预期 candidate outputs 缺失；
- `CODEX_STAGE_CANDIDATE_READY`：Codex candidate 输出齐全，`run_state` 中对应 stage 进入 human review / downstream gate 状态。

`codex-stage` 不得把 candidate promotion 为 `APPROVED_SEMANTIC_ARTIFACT`，不得把 candidate 交给 `DRD-05` 编译，也不得声明 `staged_execution_complete=true`。

## Required behavior

- `run` 不得产出 `stage_execution_plan.json`、`harness_run_result.json`、`validation_report.json` 或 lock/review gate 证据；
- `run` status payload 不得包含 `program_dag_snapshot`、`stage_execution_plan`、`upstream_lock_refs`、`gate_states` 或 release/package 字段；
- `output_hashes` 必须绑定实际落盘的 `run_receipt.json`；
- `input_hashes` 必须绑定源 PRD 与 section refs；
- run 不得新增 PRD 产品能力，只能做输入适配和最小 receipt。
- `compile-source-preserving-drd` 必须直接调用 DRD 编译器，不得调用 release；
- `compile-source-preserving-drd` 的 status payload 必须显式声明不会创建 release lock、不会发布 package；
- `compile-source-preserving-drd` 只能做 source-preserving 编译和原文行级 inventory，不得根据缺失内容推导新增产品能力；
- `compile-source-preserving-drd` 必须输出 DRD-00 到 DRD-06 的文档生成 stage plan；
- `generate-drd` 只能作为兼容 alias，payload 必须暴露 `canonical_command=compile-source-preserving-drd`；
- 外部 PRD 生成的 compiler bundle、section index、validation report、final DRD 均必须保持在 `current_capsule/outputs/**`。
- `SOURCE_PRESERVING_DRD.md` 必须通过 reader-facing structure validator；过程证据必须落在 `final_drd_manifest.json`、reference index、hash index、conservation report 或 sidecar，不能混进正文。完整 staged execution 的 `DRD-05/FINAL_DRD.md` 命名保持不变。
- `staged-run` 才是完整 harness stage 链路的外部 PRD 入口；它必须落盘 stage plan、stage receipt、run state 和下一 stage 的 Codex runtime gate 证据。
- `staged-run` 不得把 source-preserving compile 当作 DRD-02 到 DRD-04 的语义执行结果。
- `codex-stage` 是 Codex runtime continuation 入口；它必须通过 Codex CLI 或显式 runtime command 调用模型/代理来生成 candidate，Python 只负责准备 prompt、校验输出、记录 sidecar 和更新 run_state。
- `codex-stage` 支持 `DRD-01`、`DRD-02`、`DRD-03`、`DRD-03B`、`DRD-04` 和 `DRD-06`；其中 `DRD-02` 和 `DRD-03B` 的 Python 职责限于 loop-side 校验，不得替代 Codex 语义推理。
- `DRD-01` 到 `DRD-04/03B` 的 stage candidate 通过 review 后，必须 promotion 为 `APPROVED_SEMANTIC_ARTIFACT` 后才能进入 compiler bundle；compiler bundle 必须设置 `requires_approved_stage_semantic_artifacts=true`。
- `compile-stage` 是 `DRD-05` deterministic compiler continuation；它只能消费 promoted approved semantic artifacts，必须写出 `DRD-05/FINAL_DRD.md` 和 compiler sidecars，不得调用 Codex、创建锁、release 或 package publish。
- `qa-complete-stage` 是 `DRD-06` read-only QA completion；它只能在 QA status PASS、DRD-05 canonical output hash 未漂移、DRD-06 仅写 QA outputs 时声明 `staged_execution_complete=true`。
- `stage_execution_plan.json` 必须把 `DRD-01` 到 `DRD-04/03B` 的 `candidate_outputs` 与 review 后的 `promotion_outputs` 分开列出；完整语义 stage 的 `canonical_outputs` 必须同时包含两者。`DRD-05` 的 `canonical_outputs` 必须包含 `FINAL_DRD.md` 及 manifest、toc、reference index、hash index、conservation report、semantic unit inventory、compiler input bundle sidecar。
- `staged-run` 的 `run_state.json` 必须具备 recovery/resume 校验所需字段，至少能证明当前停在 `DRD-01` Codex runtime gate。
- 安装 harness 后不得在源码树留下 `repository/src/drd_harness.egg-info/`。
- 当前 repair audit 必须记录局部倒序、影响评估、最终绑定和后续 F 修复顺序。

## Acceptance commands

```bash
uv pip install --python repository/.venv/bin/python -e repository
repository/.venv/bin/drd-harness --help
test ! -d repository/src/drd_harness.egg-info
test -f current_capsule/REPAIR_AUDIT.md
rg -n "LOCAL_SEQUENCE_INVERSION|FUTURE_REPAIR_SEQUENCE|AUDIT_RECORDED_AND_BOUND" current_capsule/REPAIR_AUDIT.md
PYTHONPATH=repository/src python3 -m pytest repository/tests/p4/test_external_prd_source_preserving_drd.py repository/tests/p4/test_cli_contracts.py repository/tests/p4/test_program_driver.py repository/tests/p4/test_input_adapters.py repository/tests/kernel/test_import_boundaries.py repository/tests/compiler/test_final_drd_compilation.py
PYTHONPATH=repository/src python3 -m pytest repository/tests/p4/test_external_prd_staged_run.py
PYTHONPATH=repository/src python3 -m drd_harness.cli.main runtime-boundary-check repository/src
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```
