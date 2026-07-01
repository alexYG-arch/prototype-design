# Codex Harness Install Prompt — External PRD Isolation

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
5. 先按 `START_HERE.md` 安装或确认 editable harness 指向 `repository/`。
6. 对用户指定 PRD 使用已安装的 `drd-harness` CLI 执行隔离 run receipt。
7. run 输出只能写入 `current_capsule/outputs/**`，且只保留最小 `run_receipt.json`。
8. 文档生成只能使用 `DRD-00` 到 `DRD-06`；不得新增产品能力。
9. 外部 PRD run 不得包含证据链 stage、resume gate、lock gate 或 release/package 行为。
10. 不得修改锁，不得推进新 workpack，除非用户单独明确要求。
