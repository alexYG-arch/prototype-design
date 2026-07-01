# Codex Harness Repair Task — External PRD to DRD

请严格执行当前运行态 capsule，不要扩大范围。

注意：`P4` 只表示执行包自身的治理来源标签，不表示用户提供的外部 PRD run 属于 P4。外部 PRD run 只能产出到 `current_capsule/outputs/**`，不得写入 `build_program/phases/P4/**` 或其他执行包治理目录。

1. 读取根目录 `AGENTS.md`。
2. 读取 `current_capsule/TASK.md` 与 `current_capsule/context_manifest.json`。
3. 修复 harness 时只允许修改 repository 代码、repository 测试和当前 capsule 说明；不得修改宪章、control locks、release lock 或执行包治理目录。
4. 先运行包级检查：
   - `python3 tooling/verify_start_package.py`
   - `python3 tooling/validate_constitution.py`
   - `python3 tooling/validate_program.py`
   - `python3 tooling/validate_skills.py`
   - `python3 tooling/preflight_current_workpack.py`
5. 对用户指定 PRD 的隔离 run 仍使用 `drd-harness run`，输出目录必须位于 `current_capsule/outputs/**`。
6. 将用户指定 PRD 转成 DRD 时使用 `drd-harness generate-drd`，输出目录必须位于 `current_capsule/outputs/**`。
7. `generate-drd` 不得调用 release，不得创建 release lock，不得发布 package，不得把外部 PRD 业务内容写入 `build_program/**` 或 `control/**`。
8. `generate-drd` 只能做 source-preserving 编译和原文行级 inventory；缺失页面、二三级页面、元素或业务能力的推导必须进入人工 review。
9. 不得创建锁、提交或推送，除非用户单独明确要求。
