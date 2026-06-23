# P1-SPEC-01 Foundation: Output Format Contract

## Format Split

The Harness must use:

- Markdown for human semantic artifacts.
- JSON for operational control, indexes, manifests, locks, schemas, and machine validation results.

Semantic YAML is prohibited. Mixed human semantic and operational YAML is prohibited. JSON must not become the only source of page layout or product semantics.

## Human Semantic Markdown

Markdown is required for artifacts that contain meaning intended for human review or design reconstruction, including:

- Experience briefs.
- User task flows.
- Interaction closure reports.
- Page element blueprints.
- Shared component registries.
- Information presentation registries.
- Natural-language layout specifications.
- Figma reconstruction guidance.
- Final DRD text.
- Human-readable contracts and rules.

Markdown artifacts must expose enough natural language for review without requiring private model reasoning.

## Operational JSON

JSON is required for:

- Run state.
- Artifact manifests.
- Reference graphs.
- Interaction graph indexes.
- Review decisions.
- Validation reports.
- SPEC_LOCK and BUILD_LOCK artifacts.
- Code target maps.
- Test obligation matrices.
- Workpack indexes.
- Machine-readable schemas.

JSON artifacts must use stable IDs and must be parseable by deterministic validators.

## Layout Authority

Natural-language layout meaning must live in Markdown. JSON may index layout sections, IDs, anchors, hashes, review status, and references, but may not replace the layout explanation.

## Candidate Patch Rule

Codex produces Section Patch Candidates and spec Candidates. Python validators and promotion decide whether the Candidate enters a canonical artifact. Codex does not directly update `FINAL_DRD.md`.
