# Prototype Design / DRD Harness

本仓库当前主要包含一套可溯源的 DRD Harness 工程，用于把外部 PRD 隔离处理为可审阅、可追溯、可校验的文字版 Design Requirements Document。

核心工程目录：

```text
drd_harness_foundry_constitution_start_v1/
```

## 当前工程能力

- 宪章约束：保留 `constitution/` 中的 DRD Harness Charter、stage dependency、runtime model 和锁定规则。
- 执行包链路：通过 `current_capsule/`、`build_program/`、`control/` 维护 workpack、review、lock、manifest 和完整性校验。
- Harness 源码：`repository/src/drd_harness/` 提供 CLI、compiler、orchestrator、validators 和 stage contracts。
- 外部 PRD 入口：
  - `run`：只做外部 PRD 输入适配和最小 run receipt。
  - `compile-source-preserving-drd`：source-preserving compile，不伪造完整 staged execution；`generate-drd` 仅作为兼容 alias。
  - `staged-run`：完整 harness stage 链路入口；无 Codex/Human Gate 输入时会停在对应 stage。
- DRD 编译：`DRD-05` 使用 Python 确定性编译，只消费已批准语义产物，不新增页面、状态、CTA、组件、交互或布局决策。
- Review/校验：包含 compiler conservation、reader-facing final DRD、approved semantic artifact、runtime boundary、start package、program 和 skill 校验。
- 可恢复性：staged run 会输出 `run_state.json`，用于后续 resume/gate 检查。

## 首次安装

新设备 clone 后，不能直接假设 `drd-harness` 命令可用。需要先创建本地 venv 并安装一次：

```bash
git clone https://github.com/alexYG-arch/prototype-design.git
cd prototype-design/drd_harness_foundry_constitution_start_v1

uv venv repository/.venv --python 3.13
uv pip install --python repository/.venv/bin/python -e repository
```

`repository/.venv` 是本地虚拟环境，不会提交到 GitHub。每台设备第一次使用前都需要执行一次安装。

## 调用方式

安装后使用本地 venv 中的入口：

```bash
repository/.venv/bin/drd-harness --help
```

常用命令：

```bash
repository/.venv/bin/drd-harness run --help
repository/.venv/bin/drd-harness compile-source-preserving-drd --help
repository/.venv/bin/drd-harness staged-run --help
repository/.venv/bin/drd-harness resume --help
```

## 安装后校验

建议在首次安装后运行：

```bash
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
PYTHONPATH=repository/src python3 -m drd_harness.cli.main runtime-boundary-check repository/src
```

当上述校验通过，并且 `repository/.venv/bin/drd-harness --help` 能显示命令列表时，说明本地 harness 已可用。

## 输出边界

外部 PRD run 产物应写入：

```text
drd_harness_foundry_constitution_start_v1/current_capsule/outputs/
```

该目录用于本地运行产物，默认不作为 GitHub 工程源码提交。
