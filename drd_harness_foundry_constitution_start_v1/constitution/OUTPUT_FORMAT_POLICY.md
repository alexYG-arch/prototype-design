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
