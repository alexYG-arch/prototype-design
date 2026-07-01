# Current Capsule Rules

- 当前任务是 `P4-PROGRAM-CLOSURE-STATUS-SYNC` 的外部 PRD harness 安装约束修正。
- 只允许把外部 PRD run receipt 和 DRD 生成产物写入 `current_capsule/outputs/**`。
- 不得修改 `constitution/**`、`control/**`、`.agents/skills/**` 或已锁定 release 文件。
- 不得创建新的 Spec / Build / Release lock，除非用户单独明确授权。
- 对 PRD 的处理只能通过已安装的 `drd-harness` CLI；不得在 capsule 内新增产品能力。
- 外部 PRD run 不得包含证据链 stage、resume gate、lock gate 或 release/package 行为。
- lock/release 属于执行包治理，不属于外部 PRD run。
