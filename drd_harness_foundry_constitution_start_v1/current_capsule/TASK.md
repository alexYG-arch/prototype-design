# Harness PRD-to-DRD Stage Repair

## Objective

修复 DRD Harness 中外部 PRD 转 DRD 的缺失 stage，使 `run/review/resume` 证据链与 `generate-drd` 编译链分离：

- `run/review/resume` 只负责输入适配、执行计划、review/lock gate 和 resume 判断；
- `generate-drd` 负责把已读取的 Markdown PRD 编译成 source-preserving `FINAL_DRD.md`；
- `release` 只保留发布治理用途，不得被 PRD 转 DRD 链路调用。

## Scope guardrail

`P4-PROGRAM-CLOSURE-STATUS-SYNC` 只表示执行包自身的治理来源标签，不表示外部 PRD run 属于 P4，也不得把外部 PRD 产物写入 `build_program/phases/P4/**`。

本任务可以修改 harness 代码、测试与当前 capsule 说明，但不得修改宪章、执行包治理目录、control locks、release lock，也不得把外部 PRD 业务内容写入执行包治理目录。

外部 PRD 运行产物只能写入 `current_capsule/outputs/**`。PRD 转 DRD 的生成过程不得新增 PRD 产品能力；若需要推导缺失页面、二三级页面、元素或业务能力，必须进入人工 review，而不能由 harness 自动补全。

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

## Required DRD generation outputs

`drd-harness generate-drd` 的输出目录由调用方指定，实际使用时必须位于：

```text
current_capsule/outputs/
```

每次标准 DRD 生成至少产出：

1. `external_prd_section_index.json`
2. `external_prd_review_decision.json`
3. `external_prd_source_snapshot_binding.json`
4. `external_prd_validation_report.json`
5. `external_prd_stage_order.json`
6. `compiler_input_bundle.json`
7. `FINAL_DRD.md`
8. `final_drd_manifest.json`
9. `final_drd_toc.json`
10. `final_drd_reference_index.json`
11. `final_drd_hash_index.json`
12. `compiler_conservation_report.json`
13. `compiler_semantic_unit_inventory.json`

## Required behavior

- `harness_run_result.json` 必须可直接作为 `drd-harness resume --run-state-ref` 的输入；
- `output_hashes` 必须绑定实际落盘的 4 个声明输出；
- `input_hashes` 必须绑定源 PRD 与 section refs；
- 到 lock gate 时必须停止在 `BLOCK_LOCK_BOUNDARY`；
- 如果声明输出丢失或 hash 漂移，必须先返回 `REPLAY`，不得直接请求锁授权；
- run / resume / review / gate 证据必须保持在 `current_capsule/outputs/**`，不得进入 `build_program/**`；
- run 不得新增 PRD 产品能力，只能做输入适配、计划、验证和边界判断。
- `generate-drd` 必须直接调用 DRD 编译器，不得调用 release；
- `generate-drd` 的 status payload 必须显式声明不会创建 release lock、不会发布 package；
- `generate-drd` 只能做 source-preserving 编译和原文行级 inventory，不得根据缺失内容推导新增产品能力；
- 外部 PRD 生成的 compiler bundle、section index、validation report、final DRD 均必须保持在 `current_capsule/outputs/**`。

## Acceptance commands

```bash
PYTHONPATH=repository/src python3 -m pytest repository/tests/p4/test_external_prd_generate_drd.py repository/tests/p4/test_cli_contracts.py repository/tests/compiler/test_final_drd_compilation.py
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```
