# Stage Dependency and Runtime Model

## Canonical runtime chain

| Stage | Purpose | Primary runtime | Python duties | Codex duties | Gate |
|---|---|---|---|---|---|
| DRD-00 | Source freeze | Python | Snapshot、Hash、索引 | 无 | 无 |
| DRD-01 | PRD 体验事实提炼 | Codex | Context、引用与分类完整性校验 | 分类、解释体验影响 | 条件 |
| DRD-02 | 用户任务与交互闭包 | Codex + Python loop | 图构建、闭包、死路、循环检查 | 演绎任务、页面、状态、Reaction | Review A |
| DRD-03 | PRD 元素校验、采纳与补全 | Codex | ID、来源、覆盖和重复校验 | 校验显式元素并演绎必要元素 | 条件 |
| DRD-03B | 共用组件与信息表现模式 | Codex + Python | 重复语义、Registry 与引用检查 | 识别共用模式和合理 Variant | Review B 一部分 |
| DRD-04 | 自然语言布局与 Figma 兼容 | Codex | 完整性、来源、承载面约束校验 | 编写自然语言布局和还原说明 | Review B |
| DRD-05 | DRD 编译 | Python | 确定性拼装、目录、引用、Hash | 默认不重写正文 | Final Review |
| DRD-06 | 只读一致性 QA | Codex read-only | 冻结输入、收集报告 | 检查遗漏、冲突、压扁与越权 | Final Review 输入 |

## Stage input rule

每个 DRD-01 至 DRD-04 Stage 的输入必须包含：

```text
Source PRD snapshot
+ approved upstream artifacts
+ applicable human decisions
+ locked contracts/rules
```

DRD-05 只消费已批准章节和控制索引。

## Standard execution lifecycle

```text
Python Prepare
→ Codex Candidate
→ Python Validate
→ optional targeted repair
→ Human Review when required
→ Python Promotion
```
