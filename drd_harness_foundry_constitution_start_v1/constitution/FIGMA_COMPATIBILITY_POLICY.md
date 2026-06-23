# Figma Compatibility Policy

DRD Harness 输出 Figma 还原兼容说明，但不实现 Figma Renderer。

## Supported downstream use

- 人工设计师依据 DRD 还原；
- Figma Agent 依据自然语言和稳定 ID 还原；
- 外部工具将 DRD 投射为 Figma 节点。

## Not owned by this Harness

- Figma API 鉴权；
- Frame 或组件节点写入；
- Prototype reaction 写入；
- Figma 文件同步；
- 节点 readback 与 diff。

## Required compatibility information

- 页面/承载面；
- 选框层级；
- Region 与组件包含关系；
- Auto Layout 建议；
- 固定、Hug、Fill、滚动等行为；
- 组件实例和 Variant；
- Overlay 与锚点；
- 状态差异和显示隐藏关系。
