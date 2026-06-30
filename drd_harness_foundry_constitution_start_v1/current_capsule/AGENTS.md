# Current Capsule Rules

- 当前任务是 `P4-PROGRAM-CLOSURE-STATUS-SYNC` 的运行态校验。
- 只允许把 harness run 证据写入 `current_capsule/outputs/**`。
- 不得修改 `constitution/**`、`control/**`、`.agents/skills/**` 或已锁定 release 文件。
- 不得创建新的 Spec / Build / Release lock，除非用户单独明确授权。
- 对 PRD 的处理只能通过已安装的 `drd-harness` CLI；不得在 capsule 内新增产品能力。
- 如果 run 证据漂移，先修复或重放声明输出，再进入 review 或 lock gate。
