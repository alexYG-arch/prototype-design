# Harness Run Standard — External PRD Isolation

## Objective

使用已完成的 DRD Harness，对输入 PRD 执行隔离 run，并产出可 review、可 resume、可锁边界检查的证据包。

## Scope guardrail

`P4-PROGRAM-CLOSURE-STATUS-SYNC` 只表示执行包自身的治理来源标签，不表示外部 PRD run 属于 P4，也不得把外部 PRD 产物写入 `build_program/phases/P4/**`。

外部 PRD run 的产物只能写入 `current_capsule/outputs/**`。本任务不得修改宪章、执行包治理目录、control locks、release lock、repository 源码，也不得新增 PRD 产品能力。

## Required run outputs

运行目录由调用方指定，必须位于：

```text
current_capsule/outputs/
```

每次标准 run 至少产出：

1. `adapter_result_manifest.json`
2. `source_intake_plan.json`
3. `stage_execution_plan.json`
4. `validation_report.json`
5. `harness_run_result.json`

## Required behavior

- `harness_run_result.json` 必须可直接作为 `drd-harness resume --run-state-ref` 的输入；
- `output_hashes` 必须绑定实际落盘的 4 个声明输出；
- `input_hashes` 必须绑定源 PRD 与 section refs；
- 到 lock gate 时必须停止在 `BLOCK_LOCK_BOUNDARY`；
- 如果声明输出丢失或 hash 漂移，必须先返回 `REPLAY`，不得直接请求锁授权；
- run / resume / review / gate 证据必须保持在 `current_capsule/outputs/**`，不得进入 `build_program/**`；
- run 不得新增 PRD 产品能力，只能做输入适配、计划、验证和边界判断。

## Acceptance commands

```bash
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```
