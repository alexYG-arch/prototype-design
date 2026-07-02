# Output Format Policy

## Human semantic artifacts — Markdown

```text
PRD_EXPERIENCE_BRIEF.md
USER_TASK_FLOW.md
INTERACTION_CLOSURE_REPORT.md
PAGE_ELEMENT_BLUEPRINT.md
SHARED_COMPONENT_REGISTRY.md
INFORMATION_PRESENTATION_REGISTRY.md
LAYOUT_COMPOSITION_SPEC.md
FIGMA_RECONSTRUCTION_GUIDANCE.md
FINAL_DRD.md
```

## Operational artifacts — JSON

```text
run_state.json
artifact_manifest.json
reference_graph.json
interaction_graph.json
review_decision.json
validation_report.json
SPEC_LOCK.json
BUILD_LOCK.json
```

JSON 不得成为完整页面布局或产品语义的唯一事实源。

## Candidate patch rule

Codex 输出 Section Patch Candidate；Python 验证和 Promotion 后写入 Working 文档。Codex 不直接更新 `FINAL_DRD.md`。

## Final DRD identity

`FINAL_DRD.md` 是读者版最终 DRD 的保留名称。Review 候选、Stage Evidence、中间汇编、Prompt、Receipt 和 QA 证据不得使用该名称，除非它们位于 DRD-05 canonical 输出路径且已通过最终读者版校验。

读者版 `FINAL_DRD.md` 不得包含候选状态、Review Gate、运行状态、Hash dump、源文件索引 dump 或其他过程证据标记。过程证据必须进入 JSON 索引、receipt 或 QA 报告。
