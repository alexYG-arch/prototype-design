# Reasoning Doctrine

## 1. Primary mode: deductive reasoning

DRD Harness 的主推理形式是：

```text
明确 PRD 事实
+ 平台与承载面约束
+ 已批准前置结果
+ 交互完整性义务
→ 必要结论
```

禁止以“常见产品一般如此”为唯一依据新增页面、状态或组件。

## 2. Deductive obligations

### RD-RULE-001 — Input obligation
若任务成功依赖输入 X，则必须存在获取、输入、选择或导入 X 的可操作路径。

### RD-RULE-002 — Async obligation
若操作不是即时完成，则必须存在处理中状态，并明确重复触发策略。

### RD-RULE-003 — Handoff obligation
若操作进入外部系统，则必须定义成功、取消、失败的返回或退出路径。

### RD-RULE-004 — Click obligation
若元素可点击，则必须具有明确 Reaction、目标和异常行为。

### RD-RULE-005 — Exit obligation
若状态不是终点，则必须存在继续、恢复、返回或退出路径。

### RD-RULE-006 — Failure obligation
若操作可能失败或被阻止，用户必须能理解原因，并具备恢复或退出方式。

### RD-RULE-007 — Content growth obligation
若内容长度或数量可变，布局必须解释换行、溢出、滚动、折叠、截断或扩展策略。

### RD-RULE-008 — Presentation obligation
若信息需要用户持续处理或决策，不能仅依赖短暂且不可恢复的信息呈现。

## 3. Secondary mode: inductive reasoning

归纳推理只用于：

- 在多个满足演绎义务的表现方案之间提出候选；
- 从既有设计系统或同类页面识别可复用模式；
- 提出布局、组件 Variant 或信息呈现候选；
- 发现可能遗漏的边界，再回到演绎规则验证。

归纳候选不能自动进入正式 DRD。

## 4. Inference classes

- `SOURCE_EXPLICIT`：PRD 明确表达并通过校验；
- `DEDUCTIVE_NECESSITY`：从明确前提必然推出；
- `INDUCTIVE_CANDIDATE`：基于模式提出，需进一步收敛或人工批准；
- `HUMAN_DECIDED`：人工审核确认；
- `REJECTED_INFERENCE`：已否决，不得继续使用。

## 5. Required inference record

推断必须使用自然语言记录：

```markdown
### INF-xxx · 结论名称

结论类型：DEDUCTIVE_NECESSITY

前提：
1. ...
2. ...

结论：
...

为何不是其他页面或状态：
...

来源：
REQ-xx、RULE-xx
```

不得暴露或依赖模型私有思维链；只记录可审计的前提、规则、结论和依据。
