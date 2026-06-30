# DRD Harness Foundry Constitution Start v1

这是 DRD Harness 的宪章启动包，也是当前已经推进到 P4 完成态的本地 harness 包。

## 当前状态

- 宪章与 Foundry skills 已锁定；
- P1 至 P4 的 Spec / Build locks 已生成；
- `DRD_HARNESS_RELEASE_LOCK` 已存在；
- Program State 停在 `P4-PROGRAM-CLOSURE-STATUS-SYNC`；
- 当前用途是运行已安装的 `drd-harness`，对输入 PRD 做隔离 run、review、resume 和锁边界检查。

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

## 标准 harness run

推荐先安装或确认本地 venv 已指向 `repository/`：

```bash
uv pip install --python ../.venv/bin/python -e repository
```

然后运行 PRD：

```bash
../.venv/bin/drd-harness run \
  --work-dir current_capsule/outputs/<run_dir> \
  --adapter-id markdown_prd_adapter \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/out \
  --target-workpack P4-IMPL-01
```

标准 run 会写出：

```text
adapter_result_manifest.json
source_intake_plan.json
stage_execution_plan.json
validation_report.json
harness_run_result.json
```

其中 `harness_run_result.json` 是 resume 的标准 run-state 引用；它不计入业务 `written_paths`，避免 run-state 自引用 hash。

继续到锁边界检查：

```bash
../.venv/bin/drd-harness resume \
  --run-state-ref current_capsule/outputs/<run_dir>/out/harness_run_result.json \
  --requested-resume-node <lock_gate_node_id> \
  --dry-run
```

如果证据未漂移，预期结果是 `BLOCK_LOCK_BOUNDARY`，下一步只能请求显式锁授权。
