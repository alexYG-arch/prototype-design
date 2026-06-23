# Natural-language Layout Policy

## Authority

布局权威语义必须是 Markdown 自然语言。JSON 只能保存 ID、锚点、Hash、Review 状态与引用索引，不能替代布局正文。

## Required page description

每个页面必须自然语言描述：

1. 页面承载面和整体骨架；
2. 区域顺序、层级和包含关系；
3. 排列方向、对齐和空间关系；
4. 固定、滚动、伸缩、最小和最大尺寸行为；
5. 动态内容与边界值；
6. 各状态下显示、隐藏、替换和禁用关系；
7. Overlay 的锚点、遮罩、关闭和层级；
8. Figma 中可采用的 Frame、Auto Layout、组件实例和 Variant 还原建议。

## Prohibited compression

不得用一棵大型布局 JSON 作为唯一语义源，也不得只输出绝对坐标而缺少结构解释。

## Figma selection reconstruction

自然语言应足以确定：

```text
Page Frame
→ Region
→ Component
→ Element
```

并说明 parent、顺序、布局模式、尺寸行为和状态可见性。只有浮层、气泡、角标等确需锚定时才描述坐标或 anchor。
