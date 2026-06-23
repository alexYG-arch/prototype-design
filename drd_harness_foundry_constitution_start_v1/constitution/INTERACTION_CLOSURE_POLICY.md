# Interaction Closure Policy

## Node and edge

```text
Node = page_id + state_id + overlay_stack + relevant_context
Edge = clickable_element_id + reaction + target_node_or_terminal
```

## Required clickable inventory

按钮、文本链接、可点击卡片、列表项、Tab、返回、关闭、取消、重试、复制、删除、展开、收起、清空、编辑、更多菜单、复选框、切换器、输入尾部图标与遮罩关闭等均属于可点击元素。

## Reaction types

- `NAVIGATE`
- `SAME_PAGE_STATE`
- `OPEN_OVERLAY`
- `SYSTEM_HANDOFF`
- `LOCAL_FEEDBACK`
- `DATA_MUTATION`
- `TERMINAL_SUCCESS`
- `TERMINAL_EXIT`
- `BLOCKED_WITH_REASON`

禁止使用无目标描述，如“进行操作”“处理数据”“显示提示”。

## Closure algorithm

从每个任务入口：

1. 枚举当前节点所有可点击元素；
2. 为每个元素定义成功、失败、取消和条件行为；
3. 解析目标节点；
4. 对新节点继续展开；
5. 直到返回已建模节点、到达终点、完成外部 handoff 返回定义，或没有未展开元素。

## Valid terminals

- 明确成功结果；
- 明确退出结果；
- 返回已建模节点；
- 外部 handoff 已定义成功、取消、失败的返回或退出。

普通错误状态不能是死路。

## Deterministic validation obligations

- 每个可见可点击元素有 Reaction；
- 每个 Reaction 有有效目标；
- 每个 Overlay 有关闭方式；
- 每个 Handoff 有返回或退出定义；
- 每个错误状态有恢复或退出；
- 每个非终止节点有出口；
- 每个任务可到达成功或退出终点；
- 不存在孤立页面、孤立状态或未展开元素；
- 合法循环有明确出口。
