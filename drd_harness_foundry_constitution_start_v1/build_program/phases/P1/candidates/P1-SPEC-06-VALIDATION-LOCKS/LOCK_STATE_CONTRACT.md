# P1-SPEC-06 Lock State Contract

## Purpose

This contract defines SPEC_LOCK and BUILD_LOCK semantics for approved and validated artifacts.

## Lock Types

| Lock Type | Purpose |
|---|---|
| `SPEC_LOCK` | Binds approved spec artifacts, review decision hashes, source locks, and required validation results. |
| `BUILD_LOCK` | Binds implementation output, git commit, SPEC_LOCK hash, test results, and build validation state. |
| `REVIEW_LOCK` | Optional record binding review decision to subject hash and approved sections. |
| `INVALIDATION_RECORD` | Records downstream subjects invalidated by upstream hash change. |

## SPEC_LOCK Required Fields

| Field | Requirement |
|---|---|
| `lock_id` | Stable lock ID. |
| `phase` | Phase ID. |
| `spec_part_ids` | Spec parts included in the lock. |
| `files` | File paths and hashes included in the lock. |
| `root_sha256` | Hash over ordered file hash records. |
| `review_decision_hashes` | Hashes of approval records. |
| `source_lock_refs` | Source or constitution locks used. |
| `validator_results` | Validator command, version or hash, exit code, and result hash. |
| `validator_identity_hashes` | Validator code, schema, runtime, and version hashes used for lock readiness. |
| `created_by_runtime` | Must be Python for lock creation. |

## BUILD_LOCK Required Fields

| Field | Requirement |
|---|---|
| `lock_id` | Stable lock ID. |
| `phase` | Phase ID. |
| `git_commit` | Commit containing build outputs. |
| `spec_lock_hash` | SPEC_LOCK hash used by implementation. |
| `files` | Build output file paths and hashes. |
| `test_results` | Test command, exit code, and result hash. |
| `validator_identity_hashes` | Validators and schemas used to accept build evidence. |
| `root_sha256` | Hash over build lock content. |
| `invalidates_on` | Upstream hashes that invalidate this lock if changed. |

## Contract Clauses

### LOCK-CONTRACT-001 Locks Are Immutable

Once created, a lock artifact must not be edited in place. Changes require a new lock ID or superseding lock record.

### LOCK-CONTRACT-002 Locks Bind Review

SPEC_LOCK must bind to approved review decisions and the exact files approved by those decisions.

### LOCK-CONTRACT-003 Locks Bind Validators

Locks must record which validators ran and the result hashes that justified lock readiness.

Locks must also record validator code hash, schema hash, and runtime identity. A lock cannot rely on a validation result whose validator identity is unknown.

### LOCK-CONTRACT-004 Locks Bind Upstream

Locks must include upstream hashes required for invalidation checks.

### LOCK-CONTRACT-005 No Codex Lock Creation

Codex may draft lock readiness Candidates but cannot create canonical SPEC_LOCK or BUILD_LOCK authority.

### LOCK-CONTRACT-006 Supersession Is Explicit

When a new lock supersedes an old lock, the new record must identify superseded lock IDs and invalidation impact.

### LOCK-CONTRACT-007 Supersession Is Acyclic

The lock supersession graph must be acyclic. A lock must not directly or indirectly supersede itself.
