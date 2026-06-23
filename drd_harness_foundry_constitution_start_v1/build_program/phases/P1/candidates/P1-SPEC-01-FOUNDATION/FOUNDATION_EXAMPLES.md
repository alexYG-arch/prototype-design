# P1-SPEC-01 Foundation Examples

## Positive Example: Runtime Declaration

```json
{
  "unit_id": "DRD-02",
  "primary_runtime": "CODEX_PYTHON_LOOP",
  "python_duties": [
    "Build interaction graph index",
    "Validate reachability and terminal closure"
  ],
  "codex_duties": [
    "Derive candidate tasks, states, overlays, handoffs, and reactions"
  ],
  "validator": "interaction_closure_validator",
  "human_gate": "Review A",
  "authority_inputs": [
    "Source PRD snapshot",
    "approved DRD-01 artifacts",
    "locked interaction closure contract"
  ],
  "write_scope": [
    "candidate interaction artifacts"
  ],
  "forbidden_scope": [
    "Source PRD",
    "locked contracts"
  ]
}
```

This passes because runtime duties and authority boundaries are explicit.

## Negative Example: Codex Promotion Authority

```json
{
  "unit_id": "PROMOTE-DRD-02",
  "primary_runtime": "CODEX",
  "codex_duties": [
    "Approve and promote its own interaction candidate"
  ]
}
```

This fails with `FND003` because Codex cannot approve or promote its own Candidate.

## Positive Example: Format Split

```json
{
  "artifact_id": "LAYOUT-COMPOSITION-SPEC",
  "path": "LAYOUT_COMPOSITION_SPEC.md",
  "format": "markdown",
  "authority_role": "human_semantic"
}
```

This passes because natural-language layout authority is Markdown.

## Negative Example: Semantic YAML

```text
PAGE_LAYOUT.yaml
```

This fails with `FND005` if it contains adopted Harness semantic layout or product meaning.

## Boundary Example: JSON Layout Index

```json
{
  "artifact_id": "layout_index",
  "path": "layout_index.json",
  "anchors": [
    {
      "page_id": "PAGE-001",
      "markdown_anchor": "LAYOUT_COMPOSITION_SPEC.md#page-001"
    }
  ]
}
```

This passes only when the referenced Markdown contains the full natural-language layout authority.

## Negative Example: Runtime Import From Foundry

```python
from build_program.program.run_program import status
```

This fails with `FND007` inside `repository/src/drd_harness/` because final runtime code cannot import construction tooling.

## Negative Example: Runtime Reads Construction Authority

```python
Path("constitution/DRD_HARNESS_CHARTER.md").read_text()
Path("control/CONSTITUTION_LOCK.json").read_text()
```

This fails with `FND010` inside runtime code because runtime must read promoted repository-local contracts and schemas, not construction authority files.

## Negative Example: CLI Embeds Domain Logic

```python
def validate_interaction_graph(graph):
    for node in graph.nodes:
        ...
```

This fails with `FND008` when placed in `repository/src/drd_harness/cli/` because graph validation belongs in validators or rules, not CLI.

## Positive Example: CLI Delegates

```python
def main(argv):
    args = parse_args(argv)
    return validators.run_named_validator(args.validator, args.path)
```

This passes the CLI thinness rule when `parse_args` only parses command options and `validators.run_named_validator` owns validation behavior.
