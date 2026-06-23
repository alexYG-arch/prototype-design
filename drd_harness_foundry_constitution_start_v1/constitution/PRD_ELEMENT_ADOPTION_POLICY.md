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
