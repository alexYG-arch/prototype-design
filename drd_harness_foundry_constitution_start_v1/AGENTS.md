# Agent Instructions — DRD Harness Foundry

## 当前目标

在锁定宪章约束下，用 P1–P4 的 Spec / Implement Workpack 逐步编码独立 DRD Harness。

## 永久纪律

- 每次只执行 `current_capsule` 指定的一个 Workpack。
- `constitution/` 与 `control/CONSTITUTION_LOCK.json` 是只读权威。
- Contract、Rule、Projection、Validator Spec 未锁定前，不得实现对应业务 Skill 或业务代码。
- Codex 只能产出 Candidate；不得自我批准、Promotion、Seal 或进入下一 Workpack。
- Validator 失败必须停止；不得修改 Validator 或 Golden Test 来迎合实现。
- Workpack 未允许的路径不得修改。
- 遇到规范缺口，输出 `SPEC_CHANGE_REQUEST.md`，不要在代码或 Prompt 中隐式补规则。
- 人类语义使用 Markdown；运行控制与索引使用 JSON；不得新增混合语义 YAML。
- 布局权威语义必须是自然语言；结构化索引不能替代布局正文。
- Figma 仅作为还原兼容目标；本 Harness 不实现 Figma Renderer 或写入器。

## 推理纪律

- 以演绎推理为主，以归纳推理为辅。
- PRD 明确内容先校验后采纳，不能直接照抄，也不能无理由忽略。
- 新增页面、状态、元素或信息呈现方式必须有明确前提、必要性或人工批准。
- 所有可点击元素必须具有有效 Reaction，交互链必须闭包。
- 在相同语义意图、触发条件、作用范围和信息生命周期下，应采用一致且唯一的信息呈现方式；差异必须有明确依据。

## 完成定义

Workpack 只有在以下条件全部满足时才算 Candidate 完成：

1. 必需输出齐全；
2. Required IDs 全部覆盖；
3. Allowed write scope 未被突破；
4. Acceptance commands 全部通过；
5. 无 `TBD`、`TODO`、空实现或“后续补充”；
6. 输出 Handoff 与结构化结果；
7. 未自动进入下一 Workpack。
