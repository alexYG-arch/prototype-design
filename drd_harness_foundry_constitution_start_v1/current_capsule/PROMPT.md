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
9. 将用户指定 PRD 做完整 stage 边界执行时使用 `drd-harness staged-run`，输出目录必须位于 `current_capsule/outputs/**`。
10. 将用户指定 PRD 做 source-preserving 保守 DRD 编译时才使用 `drd-harness compile-source-preserving-drd`；该命令不是完整 staged execution，payload 必须声明 `staged_execution_complete=false`。`generate-drd` 只能作为兼容 alias。
11. 外部 PRD run 不得包含证据链 stage、resume gate、lock gate、release lock 或 package publish。
12. 文档生成只能使用 `DRD-00` 到 `DRD-06`；缺失页面、二三级页面、元素或业务能力的推导必须进入人工 review。
13. `staged-run` 必须真实落盘 stage plan、DRD-00 产物、stage receipt、DRD-01 Codex runtime gate request、Codex prompt 和 run_state；不得用 Python 或 source-preserving compile 冒充 DRD-01 到 DRD-04。
14. `SOURCE_PRESERVING_DRD.md` 必须是 reader-facing source-preserving spec；完整 staged execution 的 `DRD-05/FINAL_DRD.md` 仍保留最终规格命名。hash、source path、review decision、gate 状态、run_state、候选标签和完整 inventory dump 必须保存在 sidecar，不得进入正文。
15. DRD-01 到 DRD-04/03B 的 candidate artifacts 只能用于 review/gate；通过 gate 后必须 promotion 为 `APPROVED_SEMANTIC_ARTIFACT`，该产物才允许进入 DRD-05 compiler bundle。
16. 同一个 stage 文件不得同时承担 candidate 与 approved semantic artifact 双角色；缺少 approved semantic artifact 时必须停住，不能用 candidate 代替。
17. F 修复必须先更新执行包或当前 capsule 约束，再修改 `repository/**`；若发生局部倒序，必须写入并绑定 `current_capsule/REPAIR_AUDIT.md`。
18. 新增 Codex runtime continuation 必须走 `drd-harness codex-stage`；该命令只能调用 Codex runtime 生成 candidate、校验输出并更新 `run_state.json`，不得 review、approval、promotion、compile、release 或 package publish。
19. `DRD-05` 必须通过 `drd-harness compile-stage` 从 promoted approved semantic artifacts 做 deterministic compile；`DRD-06` 必须通过 `codex-stage` 生成 read-only QA，再由 `qa-complete-stage` 在 QA PASS 且无 DRD-05 hash 漂移时完成 staged execution。
20. 不得创建锁、提交或推送，除非用户单独明确要求。
