# Validation Model

## Four assurance layers

1. Spec Validator：检查 Contract、Rule、Projection、Examples 与 MUST 覆盖；
2. Workpack Preflight：检查 Lock、Hash、读写范围和验收命令；
3. Postflight Validator：检查越界修改、锁定文件、测试篡改、输出与依赖；
4. Phase Gate Validator：检查全阶段覆盖、回归、lineage 与 Lock。

## Runtime validators

- Source and citation validator；
- PRD element adoption validator；
- Interaction closure validator；
- Cross-stage ID validator；
- Shared component consistency validator；
- Information presentation consistency validator；
- Natural-language layout completeness validator；
- Compiler conservation validator。

## Independence rule

当前 Implementation Workpack 不得修改锁定 Validator、Golden Test 或其验收规则。
