# Codex Harness Run Task — External PRD Isolation

请严格执行当前运行态 capsule，不要扩大范围。

注意：`P4` 只表示执行包自身的治理来源标签，不表示用户提供的外部 PRD run 属于 P4。外部 PRD run 只能产出到 `current_capsule/outputs/**`，不得写入 `build_program/phases/P4/**` 或其他执行包治理目录。

1. 读取根目录 `AGENTS.md`。
2. 读取 `current_capsule/TASK.md` 与 `current_capsule/context_manifest.json`。
3. 先运行包级检查：
   - `python3 tooling/verify_start_package.py`
   - `python3 tooling/validate_constitution.py`
   - `python3 tooling/validate_program.py`
   - `python3 tooling/validate_skills.py`
   - `python3 tooling/preflight_current_workpack.py`
4. 对用户指定 PRD 使用 `drd-harness run`，输出目录必须位于 `current_capsule/outputs/**`。
5. 使用 run 生成的 `harness_run_result.json` 执行 `drd-harness resume --dry-run`。
6. 只有证据 clear 且 resume 返回 `BLOCK_LOCK_BOUNDARY` 时，才能说明已到锁边界。
7. 不得把外部 PRD run 产物写入 `build_program/**`；不得修改宪章、control locks、release lock、repository 源码或新增产品能力。
8. 不得创建锁、提交或推送，除非用户单独明确要求。
