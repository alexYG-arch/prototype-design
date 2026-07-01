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
6. 对用户指定 PRD 使用已安装的 `drd-harness run` 执行隔离 run receipt。
7. run 输出只能写入 `current_capsule/outputs/**`，且只保留最小 `run_receipt.json`。
8. 对用户指定 PRD 做完整 stage 边界执行时使用 `drd-harness staged-run`；它必须落盘 DRD-00、stage receipt、DRD-01 Codex runtime gate request、Codex prompt 和 run_state，并在缺少 Codex runtime/approved candidate 输入时停住。
9. `drd-harness generate-drd` 只是 source-preserving 保守编译，不是完整 staged execution；payload 必须声明 `staged_execution_complete=false`。
10. 文档生成只能使用 `DRD-00` 到 `DRD-06`；不得新增产品能力。
11. 外部 PRD run 不得包含证据链 stage、resume gate、lock gate 或 release/package 行为。
12. 同一语义页面下的用户可见状态必须在 DRD-03 形成可呈现页面变体，并在 DRD-04/Figma 指引中作为独立页面/Frame 呈现；这只是状态呈现展开，不是新增产品能力。
13. `DRD-05/FINAL_DRD.md` 必须是最终规格正文，不得拼接候选文档、不得包含 hash/source/review/gate/run_state 过程证据、不得 dump 完整 inventory；这些证据只能进入 manifest/reference/hash/QA sidecar。
14. DRD-01 到 DRD-04/03B 必须先产出 candidate artifacts 供 review；gate 通过后再 promotion 为 `APPROVED_SEMANTIC_ARTIFACT`。DRD-05 只能消费 approved semantic artifact，不能把 candidate 文档当作最终正文来源。
15. 不得修改锁，不得推进新 workpack，除非用户单独明确要求。
