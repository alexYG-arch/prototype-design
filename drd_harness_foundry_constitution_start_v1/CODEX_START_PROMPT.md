# Codex Harness Run Prompt — P4 Program Closure

当前包已经完成 P1-P4 构建链，Program State 停在 `P4-PROGRAM-CLOSURE-STATUS-SYNC`。请不要按旧的 `P1-SPEC-00` 启动任务执行。

1. 读取根目录 `AGENTS.md`。
2. 读取 `START_HERE.md`。
3. 读取 `current_capsule/TASK.md` 与 `current_capsule/context_manifest.json`。
4. 运行：
   - `python3 tooling/verify_start_package.py`
   - `python3 tooling/validate_constitution.py`
   - `python3 tooling/validate_program.py`
   - `python3 tooling/validate_skills.py`
   - `python3 tooling/preflight_current_workpack.py`
5. 对用户指定 PRD 使用已安装的 `drd-harness` CLI 执行隔离 run。
6. run 输出只能写入 `current_capsule/outputs/**`。
7. 使用 `harness_run_result.json` 执行 resume dry-run，确认是否到达 `BLOCK_LOCK_BOUNDARY`。
8. 不得新增产品能力，不得修改锁，不得推进新 workpack，除非用户单独明确要求。
