#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/current_capsule/outputs"
python "$ROOT/tooling/preflight_current_workpack.py"
codex exec \
  -C "$ROOT" \
  --sandbox workspace-write \
  --ask-for-approval never \
  --ephemeral \
  --json \
  --output-last-message "$ROOT/current_capsule/outputs/codex_result.json" \
  --output-schema "$ROOT/current_capsule/output_schema.json" \
  - < "$ROOT/current_capsule/PROMPT.md" \
  > "$ROOT/current_capsule/outputs/events.ndjson"
