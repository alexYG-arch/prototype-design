# P4 Packaging and Release Model

## Model Summary

The P4 packaging and release model defines how a release candidate becomes eligible for lock review. It is intentionally conservative: package build, example project smoke, and release readiness can produce evidence, but they cannot publish or create locks without a later explicit action.

## Package Manifest

Every package readiness check must emit a package manifest with:

- `package_name`
- `package_version`
- `source_git_commit`
- `source_dirty_state`
- `included_files`
- `excluded_files`
- `entrypoints`
- `dependency_lock_hash`
- `build_command`
- `package_artifact_hash`
- `dry_run_report_hash`

The manifest must fail if it includes generated review decisions, local credentials, machine-specific temporary files, or untracked release inputs.

## Example Project Manifest

Every example project readiness check must emit:

- `example_id`
- `example_path`
- `source_input_refs`
- `expected_commands`
- `expected_outputs`
- `smoke_command`
- `smoke_status`
- `smoke_report_hash`
- `cleanup_policy`

The example project must demonstrate a minimal governed run without creating product semantics outside source evidence.

## Release Readiness Packet

The release readiness packet is the single reviewable summary for release lock eligibility.

Required fields:

- `release_candidate_id`
- `p4_spec_lock_ref`
- `p4_build_lock_ref`
- `test_suite_reports`
- `migration_coverage_report`
- `package_manifest`
- `example_project_manifest`
- `missing_gate_list`
- `dirty_state_policy`
- `dirty_state_records`
- `release_lock_input_bundle_preview`
- `human_authorization_required`
- `readiness_packet_hash`

The packet must report missing gates as structured fields. It cannot hide missing evidence in prose.

`readiness_packet_hash` is the canonical JSON sha256 of the readiness packet with `readiness_packet_hash` itself excluded. The packet may include a `release_lock_input_bundle_preview`, but not the full release lock input bundle. The final release lock input bundle is a separate artifact that references `release_readiness_packet_hash`.

## Dirty State Policy

Release readiness must classify the repository state:

- `CLEAN`: all release inputs are committed at the referenced git commit.
- `DOCUMENTED_DIRTY`: uncommitted files exist but are excluded from release inputs and listed in the readiness packet.
- `BLOCKED_DIRTY`: uncommitted files affect release inputs or cannot be classified.

Each dirty state record must include `path`, `git_status`, `is_release_input`, `classification`, `reason`, and `required_action`. `DOCUMENTED_DIRTY` is allowed only when every dirty state record is classified as `EXCLUDED_FROM_RELEASE_INPUTS`.

Release lock creation eligibility requires `CLEAN` unless a later human-approved lock creation workpack explicitly accepts `DOCUMENTED_DIRTY`.

## Release Lock Eligibility

`DRD_HARNESS_RELEASE_LOCK` is eligible only when:

1. P4 spec lock exists and includes approved P4-SPEC-01, P4-SPEC-02, and P4-SPEC-03.
2. P4 build lock exists and binds the implementation outputs used by the release suite.
3. Golden, integration, and release suite reports pass.
4. v3.1 migration coverage has no unreviewed blocker.
5. Package dry-run and example project smoke pass.
6. Release readiness packet has no missing gate.
7. A separate explicit human lock creation authorization exists.

Eligibility is not lock creation. The lock file is written only by a later lock creation step.
