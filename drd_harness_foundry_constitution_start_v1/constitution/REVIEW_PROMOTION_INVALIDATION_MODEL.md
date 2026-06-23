# Review, Promotion and Invalidation Model

## Review A

位于 DRD-02 后，批准：任务、页面、状态、Overlay、Handoff、主要可点击元素和交互边。

## Review B

位于 DRD-04 后，批准：页面元素、共用组件、信息表现模式、自然语言布局和 Figma 还原兼容性。

## Final Review

批准最终编译文档、追溯、未决事项和下游可用性。

## Decision states

```text
APPROVED
REVISION_REQUIRED
REJECTED
```

批准必须绑定审核对象 Hash。

## Promotion

只有 Python Promotion Engine 可以把已批准 Candidate 写入 canonical artifact。

## Invalidation

Source、Constitution、Contract、Rule、Projection、批准 Artifact 或 Human Decision 的 Hash 变化时，所有依赖旧 Hash 的下游 Artifact、Skill、Workpack、测试结果和 Lock 必须标记 `INVALIDATED`。
