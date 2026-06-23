# Skill Policy

## Skill roles

- Foundry Skills：规范分片、校验、Review、Seal、Assembly、Lock 和 Workpack 执行；
- Domain Build Skills：依据锁定 Spec 建设 DRD Stage；
- Runtime Domain Skills：最终 Harness 调用 Codex 执行语义 Stage。

## Dependency rule

业务 Skill 只能在相关 Contract、Rule、Projection 和 Validator Spec 形成 SPEC_LOCK 后生成。

## No second authority

Skill 引用 Contract，不复制 Contract；执行 Rule，不拥有 Rule；使用 Projection，不重新定义 Projection。

## Version binding

Skill Manifest 必须绑定所需规范的 Version 与 Hash。上游 Hash 改变时 Skill 失效。
