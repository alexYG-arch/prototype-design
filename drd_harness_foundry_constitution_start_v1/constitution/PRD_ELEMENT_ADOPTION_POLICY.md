# PRD Element Adoption Policy

## Priority order

1. PRD 明确元素，经校验后采纳；
2. 为满足演绎义务而补充的必要元素；
3. 已经人工批准的归纳候选。

## Validation before adoption

PRD 中出现页面、按钮、Tab、弹层、卡片或状态时，必须执行：

```text
识别
→ 与任务、范围、平台和其他规则校验
→ 采纳 / 规范化 / 请求澄清 / 拒绝
```

## Possible outcomes

- `ADOPTED_EXPLICIT`：语义完整，直接采纳；
- `NORMALIZED_EXPLICIT`：名称或 ID 规范化，语义不变；
- `QUESTION_REQUIRED`：入口、结果、承载面或返回路径不明确；
- `REJECTED_CONFLICT`：与正式范围或锁定规则冲突。

所有拒绝或规范化必须保留理由和 PRD 引用。

## Completion obligations

只有现有元素无法满足任务完成、状态表达、信息呈现、错误恢复、导航退出或可访问性义务时，才允许演绎新增元素。

## Page detail conservation

页面元素采纳不得停留在页面或卡片名称级别。PRD 中明确出现的以下内容必须作为页面细节被保留并绑定源引用：

- 页面稿或 ASCII wireframe 中的可见文本、按钮、图标语义、示例值和顺序；
- 表格中描述的页面布局、业务逻辑、交互细节和状态文案；
- 卡片、弹层、列表、Tab、CTA、提示、空态、失败态和权限态的可见信息；
- 设计优先级、横滑/滚动/折叠等直接影响呈现的注释。

如果某条页面细节不进入最终 DRD，必须有可审查的 `drop_reason`。没有去向或理由的页面细节遗漏属于校验失败。

## Derivation origin

页面、状态页和 renderable variant 必须声明来源类型：`PRD_EXPLICIT`、`DEDUCTIVE_REQUIRED`、`HUMAN_APPROVED_INFERENCE` 或 `REVIEW_REQUIRED_INFERENCE`。任何非 PRD 明确项必须绑定推理依据或人工 Review 决策，并保持 `product_capability_addition = false`。
