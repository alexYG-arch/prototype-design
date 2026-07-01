# DRD Harness Foundry Constitution Start v1

这是 DRD Harness 的宪章启动包，也是当前已经推进到 P4 完成态的本地 harness 包。

## 当前状态

- 宪章与 Foundry skills 已锁定；
- P1 至 P4 的 Spec / Build locks 已生成；
- `DRD_HARNESS_RELEASE_LOCK` 已存在；
- Program State 停在 `P4-PROGRAM-CLOSURE-STATUS-SYNC`；
- 当前用途是安装并运行 `drd-harness`，对输入 PRD 做隔离 run receipt 和 DRD-00 到 DRD-06 文档生成。
- 外部 PRD run 不包含执行包证据链 stage，不包含 lock/release/resume gate；lock/release 只属于执行包治理。

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

```bash
repository/.venv/bin/drd-harness generate-drd \
  --work-dir . \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/drd
```

DRD 生成只能使用 `DRD-00` 到 `DRD-06` 作为文档生成 stage。缺失页面、二三级页面、元素或业务能力不得自动补全；必须进入人工 review。不得调用 release，不得创建锁，不得发布 package。
