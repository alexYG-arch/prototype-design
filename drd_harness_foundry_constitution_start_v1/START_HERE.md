# DRD Harness Foundry Constitution Start v1

这是 DRD Harness 的宪章启动包，也是当前已经推进到 P4 完成态的本地 harness 包。

## 当前状态

- 宪章与 Foundry skills 已锁定；
- P1 至 P4 的 Spec / Build locks 已生成；
- `DRD_HARNESS_RELEASE_LOCK` 已存在；
- Program State 停在 `P4-PROGRAM-CLOSURE-STATUS-SYNC`；
- 当前用途是安装并运行 `drd-harness`，对输入 PRD 做隔离 run receipt、真实 staged-run 边界执行，以及 source-preserving DRD 文档编译。
- 外部 PRD run receipt 不包含执行包证据链 stage，不包含 lock/release/resume gate；lock/release 只属于执行包治理。外部 PRD `staged-run` 会单独产出 `run_state.json`，用于恢复校验当前停在的 Human Gate。

权威状态以这些文件为准：

```text
build_program/program/PROGRAM_STATE.json
build_program/program/PROGRAM_MANIFEST.json
control/locks/DRD_HARNESS_RELEASE_LOCK.json
current_capsule/context_manifest.json
```

## 包级检查

在本目录运行：

```bash
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```

`verify_start_package.py` 和 `validate_program.py` 会自动识别当前是完成态包。`--mode start` 只用于原始未推进启动包；当前完成态包的标准校验是默认 `auto` 或显式 `--mode complete`。

## 安装 harness

每次调整执行包约束后，先安装或确认本地 venv 已指向 `repository/`：

```bash
uv pip install --python repository/.venv/bin/python -e repository
```

安装元数据必须留在本地 venv 内，不得在源码树留下 `repository/src/drd_harness.egg-info/`。

确认 CLI：

```bash
repository/.venv/bin/drd-harness --help
```

## 标准外部 PRD run

外部 PRD run 只产出最小 receipt，不产出证据链 stage，不进入 resume/lock/release：

```bash
repository/.venv/bin/drd-harness run \
  --work-dir . \
  --adapter-id markdown_prd_adapter \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/run
```

标准 run 只写出：

```text
run_receipt.json
```

`run_receipt.json` 只记录输入源、适配器、源 hash、section 计数、DRD-00 到 DRD-06 文档生成 stage 顺序、输出边界和 no-lock/no-release 声明。

## 标准 DRD 生成

这是保守编译入口，不是完整 harness stage run：

```bash
repository/.venv/bin/drd-harness compile-source-preserving-drd \
  --work-dir . \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/drd
```

该命令产出 `SOURCE_PRESERVING_DRD.md`，只能使用 `DRD-00` 到 `DRD-06` 作为文档生成 stage。缺失页面、二三级页面、元素或业务能力不得自动补全；必须进入人工 review。不得调用 release，不得创建锁，不得发布 package。CLI payload 必须声明 `source_preserving_compile_only=true` 与 `staged_execution_complete=false`。旧命令 `generate-drd` 仅作为兼容 alias。

同一语义页面下的用户可见状态必须在 DRD-03 形成 `renderable_page_variants`：基础页使用原页面 ID，状态页使用稳定变体页 ID。DRD-04 的自然语言布局与 Figma 还原说明必须把这些变体当作独立可呈现页面/Frame 引用，例如页面 A、A1、A2、A3。该展开只呈现已采纳页面和状态，不得借机新增产品能力；如果必须新增页面、二三级页面、元素或能力才能补齐，进入人工 review。

`SOURCE_PRESERVING_DRD.md` 必须是面向读者的保源规格，不是证据包。hash、source path、review decision、gate 状态、run_state、完整 inventory dump 和候选过程标签必须留在 manifest/reference/hash/QA sidecar 中，不得混入正文。完整 staged execution 的 `DRD-05/FINAL_DRD.md` 命名保持不变。最终正文不得把 `DRD-01` 到 `DRD-04` 候选文档原文整段拼接，也不得出现多个一级标题。

完整 staged execution 中，`DRD-01` 到 `DRD-04/03B` 的输出必须区分双角色：candidate artifacts 只用于 review/gate，approved semantic artifacts 才能进入 `DRD-05` compiler bundle。approved semantic artifact 必须绑定 source candidate、review decision、semantic body hash 和过程证据 sidecar，正文不得包含“候选/CANDIDATE”、source/hash/review/gate/run_state 等过程信息。同一个文件不得同时作为候选和 approved semantic artifact；缺少 approved semantic artifact 时必须停住，不能用 candidate 顶替。

## 标准 staged run

这是外部 PRD 的真实 harness stage 边界入口：

```bash
repository/.venv/bin/drd-harness staged-run \
  --work-dir . \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/staged
```

无 Codex 运行时，或尚未存在已批准 DRD-01 候选输入时，标准 staged run 只会完成 `DRD-00` source freeze，然后停在 `DRD-01` 的 `CODEX_RUNTIME_GATE`。这不是失败；它表示体验事实提炼、后续用户任务、交互闭包、元素补全、共用模式和布局语义必须由 Codex 候选与人工 review/校验继续，不能由 Python CLI 静默推导。

标准 staged run 会写出 `stage_execution_plan.json`、`DRD-00/**`、`review_gates/DRD-01_EXPERIENCE_FACT_EXTRACTION_REQUEST.json`、`codex_prompts/DRD-01_EXPERIENCE_FACT_EXTRACTION_PROMPT.md` 和 `run_state.json`。它不得产出 `DRD-01/PRD_EXPERIENCE_BRIEF.md`、`DRD-01/experience_fact_index.json`、`SOURCE_PRESERVING_DRD.md` 或 `FINAL_DRD.md`，不得创建 lock/release，不得发布 package。

## 标准 Codex stage continuation

`staged-run` 停在 `CODEX_RUNTIME_GATE` 后，继续执行 Codex-owned stage 必须使用独立 continuation 入口：

```bash
repository/.venv/bin/drd-harness codex-stage \
  --work-dir . \
  --run-state-ref current_capsule/outputs/<run_dir>/staged/run_state.json \
  --stage-id DRD-01
```

该命令默认调用本机 `codex exec`。测试、离线或替代 runtime 环境可以显式传入 `--runtime-command`。`codex-stage` 只负责让 Codex runtime 产出 candidate、校验预期输出、记录 invocation/result sidecar 并更新 `run_state.json`；它不得 approval、promotion、编译 `FINAL_DRD.md`、创建 lock/release 或发布 package。

后续 `DRD-02`、`DRD-03`、`DRD-03B`、`DRD-04` 和 `DRD-06` 也通过 `codex-stage` 继续，但必须满足各自上游 approved semantic artifact 或 `DRD-05/FINAL_DRD.md` 输入要求。缺少上游批准时必须停住。

`DRD-01` 到 `DRD-04/03B` 的 candidate 通过人工 review 后，使用 `promote-stage` 生成 `APPROVED_SEMANTIC_ARTIFACT`。`DRD-05` 使用 `compile-stage` 做 Python deterministic compile，只消费 approved semantic artifacts。`DRD-06` 通过 `codex-stage` 生成 read-only QA 输出后，使用 `qa-complete-stage` 校验 QA PASS、DRD-05 hash 未漂移和只读边界，再标记 staged execution complete。
