# Package Scope

本包是 **DRD Harness 的 Foundry Constitution Start**，包含建设宪章、通用 Skills、P1–P4 Program Driver、目标仓库骨架、旧版参照描述和当前 Capsule。

它不是：

- 已完成的 DRD Harness；
- 已完成的 P1–P4 执行包集合；
- DRD 运行时的业务输入包；
- Figma Renderer。

它启动的建设过程是：

```text
锁定宪章
→ Codex 生成并冻结 Spec 执行包
→ Codex 依据 SPEC_LOCK 生成 Implementation Workpack
→ Codex 编码 repository/
→ 独立 Validator 与 Human Gate
→ BUILD_LOCK
→ 激活下一阶段
```
