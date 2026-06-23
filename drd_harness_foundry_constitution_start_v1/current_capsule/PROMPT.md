# Codex First Task — P1-SPEC-00

请严格执行当前 Capsule，不要扩大范围。

1. 读取根目录 `AGENTS.md`。
2. 读取 `current_capsule/TASK.md` 与 `current_capsule/context_manifest.json`。
3. 显式使用以下 Skills：
   - `$foundry-read-locks`
   - `$foundry-generate-spec-part`
   - `$foundry-validate-spec-part`
4. 运行：
   - `python tooling/verify_start_package.py`
   - `python tooling/validate_constitution.py`
   - `python tooling/validate_program.py`
   - `python tooling/validate_skills.py`
   - `python tooling/preflight_current_workpack.py`
5. 只在 `build_program/phases/P1/candidates/P1-SPEC-00/` 中生成 Candidate。
6. 生成 `TASK.md` 要求的全部文件，并运行当前 Capsule 的验收命令。
7. 不得修改：
   - `constitution/**`
   - `control/**`
   - `.agents/skills/**`
   - `build_program/program/**`
   - `repository/**`
   - `references/**`
   - `tooling/**`
8. 不得开始 P1-SPEC-01，不得 Seal，不得自我批准，不得开始 Harness 代码实现。
9. 若发现宪章冲突或缺失，生成 `SPEC_CHANGE_REQUEST.md` 后停止，不能自行补写锁定宪章。
10. 最终输出必须符合 `current_capsule/output_schema.json`。
