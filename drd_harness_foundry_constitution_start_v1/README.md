# DRD Harness Foundry Constitution Start

本目录包含 DRD harness 的宪章 start 包、执行包、源码、schema、fixture、测试和 tooling。

## 首次安装

在新设备上拉取仓库后，不能直接假设 `drd-harness` 命令已经存在。需要先创建本地 venv，并安装一次 harness：

```bash
cd drd_harness_foundry_constitution_start_v1

uv venv repository/.venv --python 3.13
uv pip install --python repository/.venv/bin/python -e repository
```

`repository/.venv` 是本地虚拟环境，不会提交到 GitHub。每台新设备第一次使用前都需要执行一次上面的安装步骤。

## 调用 harness

安装后使用本地 venv 中的入口：

```bash
repository/.venv/bin/drd-harness --help
```

常用命令：

```bash
repository/.venv/bin/drd-harness run --help
repository/.venv/bin/drd-harness compile-source-preserving-drd --help
repository/.venv/bin/drd-harness staged-run --help
```

## 校验

安装后建议运行：

```bash
python3 tooling/verify_start_package.py
python3 tooling/validate_constitution.py
python3 tooling/validate_program.py
python3 tooling/validate_skills.py
python3 tooling/preflight_current_workpack.py
```

当上述校验通过，并且 `repository/.venv/bin/drd-harness --help` 能显示命令列表时，说明本地 harness 已可用。
