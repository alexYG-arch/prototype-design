# Engineering Directory Rules

```text
project-root/
├── constitution/          # 锁定宪章，只读
├── control/               # Catalog、Schema 与 Lock
├── build_program/         # P1–P4 施工系统
├── current_capsule/       # 当前唯一激活 Workpack
├── .agents/skills/        # Foundry Skills
├── references/            # 旧版本只读参照
├── tooling/               # 独立确定性工具
└── repository/            # Codex 逐步编码的 DRD Harness 本体
```

`build_program/` 不得被最终运行时 import。

`references/v3_1/` 不得被 `repository/src/` 直接 import。

CLI 必须保持薄层，业务规则不得隐藏在 CLI 或脚本中。
