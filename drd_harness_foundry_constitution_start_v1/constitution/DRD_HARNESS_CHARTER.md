# DRD Harness Charter

## 1. Mission

DRD Harness 将已有 PRD 中与用户体验有关的事实、规则和约束，演绎为完整、可审阅、可追溯的文字版 Design Requirements Document。

运行链：

```text
PRD
→ 体验事实提炼
→ 用户任务与交互闭包
→ 页面元素校验、采纳与必要补全
→ 共用组件与一致信息呈现模式
→ 自然语言布局与 Figma 还原说明
→ 确定性编译
→ FINAL_DRD.md
```

## 2. Authority

- PRD 决定产品允许、要求和禁止什么。
- DRD Harness 决定如何把已批准产品语义展开为用户可经历的页面、状态、元素、交互和布局说明。
- DRD Harness 无权静默新增产品能力。
- 人工 Review 是高杠杆语义决策的最终权威。

## 3. Locked Invariants

### DRD-CHARTER-001 — Source permanence
每个语义推理 Stage 都必须重新读取不可变 Source PRD；任何派生简报不能替代源 PRD。

### DRD-CHARTER-002 — Ordered dependency
后置 Stage 必须消费已批准的前置结果，并绑定其 Hash。

### DRD-CHARTER-003 — Deduction first
体验补全以演绎推理为主，归纳推理只用于提出多个可行表现候选或识别模式。

### DRD-CHARTER-004 — PRD element validation
PRD 已明确的页面、状态、CTA 或元素，必须先经过一致性与可执行性校验，再采纳、规范化、请求澄清或拒绝。

### DRD-CHARTER-005 — Interaction closure
所有可点击元素必须有明确 Reaction；交互链必须继续展开，直到返回已有节点、到达明确终点或穷尽所有可点击元素。

### DRD-CHARTER-006 — Information presentation consistency
在相同语义意图、触发条件、作用范围和信息生命周期下，应采用一致且唯一的信息呈现方式。差异化呈现必须有明确场景依据并可追溯。

### DRD-CHARTER-007 — Element derivation
页面元素优先采纳经过校验的 PRD 明确内容；缺失元素只能从任务、状态、信息、反馈、恢复、导航、退出或可访问性义务中演绎补全，或由人工批准。

### DRD-CHARTER-008 — Natural-language layout
布局权威语义必须使用自然语言完整描述空间结构、层级、包含关系、排列、尺寸、滚动、状态变化和承载面约束。

### DRD-CHARTER-009 — Figma compatibility only
布局应足以支持设计师或 Agent 在 Figma 中还原页面、选框层级、Auto Layout、组件实例和 Variant；本 Harness 不实现 Figma API、Renderer 或写入器。

### DRD-CHARTER-010 — Candidate only
Codex 只产生 Candidate，不得直接更新 canonical DRD 或批准自己的结果。

### DRD-CHARTER-011 — Deterministic compilation
最终 DRD 由 Python 依据已批准章节确定性编译；编译阶段不得新增页面、状态、CTA、组件、交互或布局决策。

### DRD-CHARTER-012 — Explicit runtime
每个 Stage 必须声明主 Runtime、Python 控制职责、Codex 推理职责、Validator 和 Human Gate。

### DRD-CHARTER-013 — Spec before code
对应 Contract、Rule、Projection 和 Validator Spec 未形成 SPEC_LOCK 前，不得实现业务代码或业务 Skill。

### DRD-CHARTER-014 — Spec-to-code traceability
每条实现义务必须能追溯到 Contract Clause、Rule、Code Target、Validator、Test 和 Acceptance Command。

### DRD-CHARTER-015 — Invalidation
任何锁定上游内容发生变化，依赖旧 Hash 的 Skill、Workpack、Artifact、Test 结果和 Lock 必须失效。

### DRD-CHARTER-016 — No semantic YAML
人类语义使用 Markdown；运行控制和索引使用 JSON；不新增混合语义 YAML。

### DRD-CHARTER-017 — Shared pattern discipline
相同语义、数据、操作和状态模型应优先复用共用组件或表现模式；不同语义不得仅因外观相似而强行合并。

### DRD-CHARTER-018 — No silent product expansion
无法从 PRD、平台约束、批准决策或演绎义务推出的功能扩张，必须作为候选或 Gap 提交人工处理，不能进入正式 DRD。
