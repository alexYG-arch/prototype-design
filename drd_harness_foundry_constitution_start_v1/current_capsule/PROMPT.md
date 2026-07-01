# Codex Harness Install Task — External PRD Isolation

请严格执行当前运行态 capsule，不要扩大范围。

注意：`P4` 只表示执行包自身的治理来源标签，不表示用户提供的外部 PRD run 属于 P4。外部 PRD run 只能产出到 `current_capsule/outputs/**`，不得写入 `build_program/phases/P4/**` 或其他执行包治理目录。

1. 读取根目录 `AGENTS.md`。
2. 读取 `START_HERE.md`。
3. 读取 `current_capsule/TASK.md` 与 `current_capsule/context_manifest.json`。
4. 先修改执行包入口说明和当前 capsule 约束，再安装/更新 harness；不得绕过执行包直接改 harness 行为。
5. 允许修改 repository 代码、repository 测试、根启动说明和当前 capsule 说明；不得修改宪章、control locks、release lock 或执行包治理目录。
6. 运行包级检查：
   - `python3 tooling/verify_start_package.py`
   - `python3 tooling/validate_constitution.py`
   - `python3 tooling/validate_program.py`
   - `python3 tooling/validate_skills.py`
   - `python3 tooling/preflight_current_workpack.py`
7. 安装或确认 editable harness：`uv pip install --python repository/.venv/bin/python -e repository`。
8. 对用户指定 PRD 的隔离 run 只能产出最小 `run_receipt.json`，输出目录必须位于 `current_capsule/outputs/**`。
9. 将用户指定 PRD 转成 DRD 时使用 `drd-harness generate-drd`，输出目录必须位于 `current_capsule/outputs/**`。
10. 外部 PRD run 不得包含证据链 stage、resume gate、lock gate、release lock 或 package publish。
11. 文档生成只能使用 `DRD-00` 到 `DRD-06`；缺失页面、二三级页面、元素或业务能力的推导必须进入人工 review。
12. F 修复必须先更新执行包或当前 capsule 约束，再修改 `repository/**`；若发生局部倒序，必须写入并绑定 `current_capsule/REPAIR_AUDIT.md`。
13. 不得创建锁、提交或推送，除非用户单独明确要求。
