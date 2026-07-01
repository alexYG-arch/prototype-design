# Harness Install Contract — External PRD Isolation

## Objective

按“先修改执行包，再安装 harness”的正规流程，修正外部 PRD harness 合约：

- 删除外部 PRD run 中的证据链 stage；
- 外部 PRD run 只保留最小 `run_receipt.json`；
- 文档生成只允许使用 `DRD-00` 到 `DRD-06` 作为 stage；
- lock/release 保留给执行包治理，不放进外部 PRD run。

## Scope guardrail

`P4-PROGRAM-CLOSURE-STATUS-SYNC` 只表示执行包自身的治理来源标签，不表示外部 PRD run 属于 P4，也不得把外部 PRD 产物写入 `build_program/phases/P4/**`。

本任务必须先修改执行包入口说明、当前 capsule 说明和 context manifest，再安装/更新 harness。不得绕过执行包直接把旧证据链模型留在 harness 中。

本任务可以修改 harness 代码、测试、当前 capsule 说明、根启动说明和安装入口提示，但不得修改宪章、control locks、release lock，也不得把外部 PRD 业务内容写入执行包治理目录。

外部 PRD 运行产物只能写入 `current_capsule/outputs/**`。PRD 转 DRD 的生成过程不得新增 PRD 产品能力；若需要推导缺失页面、二三级页面、元素或业务能力，必须进入人工 review，而不能由 harness 自动补全。

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

`drd-harness generate-drd` 的输出目录由调用方指定，实际使用时必须位于：

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
7. `FINAL_DRD.md`
8. `final_drd_manifest.json`
9. `final_drd_toc.json`
10. `final_drd_reference_index.json`
11. `final_drd_hash_index.json`
12. `compiler_conservation_report.json`
13. `compiler_semantic_unit_inventory.json`

## Required behavior

- `run` 不得产出 `stage_execution_plan.json`、`harness_run_result.json`、`validation_report.json` 或 lock/review gate 证据；
- `run` status payload 不得包含 `program_dag_snapshot`、`stage_execution_plan`、`upstream_lock_refs`、`gate_states` 或 release/package 字段；
- `output_hashes` 必须绑定实际落盘的 `run_receipt.json`；
- `input_hashes` 必须绑定源 PRD 与 section refs；
- run 不得新增 PRD 产品能力，只能做输入适配和最小 receipt。
- `generate-drd` 必须直接调用 DRD 编译器，不得调用 release；
- `generate-drd` 的 status payload 必须显式声明不会创建 release lock、不会发布 package；
- `generate-drd` 只能做 source-preserving 编译和原文行级 inventory，不得根据缺失内容推导新增产品能力；
- `generate-drd` 必须输出 DRD-00 到 DRD-06 的文档生成 stage plan；
- 外部 PRD 生成的 compiler bundle、section index、validation report、final DRD 均必须保持在 `current_capsule/outputs/**`。
- 安装 harness 后不得在源码树留下 `repository/src/drd_harness.egg-info/`。
- 当前 repair audit 必须记录局部倒序、影响评估、最终绑定和后续 F 修复顺序。

## Acceptance commands

```bash
uv pip install --python repository/.venv/bin/python -e repository
repository/.venv/bin/drd-harness --help
test ! -d repository/src/drd_harness.egg-info
test -f current_capsule/REPAIR_AUDIT.md
rg -n "LOCAL_SEQUENCE_INVERSION|FUTURE_REPAIR_SEQUENCE|AUDIT_RECORDED_AND_BOUND" current_capsule/REPAIR_AUDIT.md
PYTHONPATH=repository/src python3 -m pytest repository/tests/p4/test_external_prd_generate_drd.py repository/tests/p4/test_cli_contracts.py repository/tests/p4/test_program_driver.py repository/tests/p4/test_input_adapters.py repository/tests/kernel/test_import_boundaries.py repository/tests/compiler/test_final_drd_compilation.py
PYTHONPATH=repository/src python3 -m drd_harness.cli.main runtime-boundary-check repository/src
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```
