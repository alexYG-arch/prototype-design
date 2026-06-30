# DRD Harness

This directory contains the DRD Harness runtime produced by the governed P1-P4 workpacks.

## Standard PRD Run

From the package root:

```bash
uv pip install --python ../.venv/bin/python -e repository

../.venv/bin/drd-harness run \
  --work-dir current_capsule/outputs/<run_dir> \
  --adapter-id markdown_prd_adapter \
  --source-ref /path/to/input_prd.md \
  --output-dir current_capsule/outputs/<run_dir>/out \
  --target-workpack P4-IMPL-01
```

The run writes four governed evidence artifacts plus a resume state sidecar:

```text
adapter_result_manifest.json
source_intake_plan.json
stage_execution_plan.json
validation_report.json
harness_run_result.json
```

Use the sidecar for recovery checks:

```bash
../.venv/bin/drd-harness resume \
  --run-state-ref current_capsule/outputs/<run_dir>/out/harness_run_result.json \
  --requested-resume-node <lock_gate_node_id> \
  --dry-run
```

`harness_run_result.json` is not included in `written_paths`; the governed output hashes bind only the declared evidence artifacts.
