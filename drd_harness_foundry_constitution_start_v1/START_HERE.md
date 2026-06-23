# DRD Harness Foundry Constitution Start v1

这是交给 Codex 的**完整宪章启动包**。它用于从锁定宪章开始，依次生成 P1–P4 的规范执行包和实施 Workpack，并在同一 `repository/` 中逐步编码出独立 DRD Harness。

## 包内已冻结的内容

- DRD Harness 的目标、边界、推理原则与所有权；
- 演绎推理为主、归纳推理为辅；
- PRD 已有元素先校验后采纳；
- 用户任务与所有可点击元素的交互闭包；
- 共用组件和信息呈现模式一致性；
- 以自然语言描述布局并兼容 Figma 手工或 Agent 还原；
- DRD-00 至 DRD-06 的 Stage 与 Runtime 分工；
- P1-SPEC/P1-IMPLEMENT 至 P4-SPEC/P4-IMPLEMENT 的建设链；
- Spec→Code 映射、Validator、Review、Promotion、Invalidation 与 Lock；
- Foundry 通用 Skills；
- 当前激活 Workpack：`P1-SPEC-00`。

## 第一次使用

在 Codex 中打开**解压后的本目录**，先运行：

```bash
python tooling/verify_start_package.py
python tooling/validate_constitution.py
python tooling/validate_program.py
python tooling/validate_skills.py
python tooling/preflight_current_workpack.py
```

全部通过后，把 `CODEX_START_PROMPT.md` 的完整内容提交给 Codex。

也可以使用：

```bash
bash tooling/run_codex_current.sh
```

该脚本使用 `codex exec`，只执行当前 Capsule。

## 当前执行范围

当前只允许生成 P1 的首个规范规划 Candidate：

```text
P1-SPEC-00
```

它会建立 P1 的 Clause ownership、Spec 分片计划、Implementation Workpack 地图和验收矩阵。它**不会直接修改锁定宪章，也不会开始 Harness 业务代码实现**。

后续由 Program Driver 根据 Gate、SPEC_LOCK 与 BUILD_LOCK 推进：

```text
P1-SPEC → P1-IMPLEMENT
→ P2-SPEC → P2-IMPLEMENT
→ P3-SPEC → P3-IMPLEMENT
→ P4-SPEC → P4-IMPLEMENT
→ RELEASE_LOCK
```

## v3.1 参照

本包不重复携带 2MB 以上的旧源码，以避免下载超时。`references/v3_1/` 已锁定预期 ZIP 的 SHA-256，并提供安全安装脚本。P1 盘点或后续迁移 Workpack 需要旧代码时执行：

```bash
python tooling/install_v31_baseline.py --archive "/path/to/prd_subharness_v3_1(1).zip"
```

旧源码只作为只读参照，不得被 V4 代码 import。
