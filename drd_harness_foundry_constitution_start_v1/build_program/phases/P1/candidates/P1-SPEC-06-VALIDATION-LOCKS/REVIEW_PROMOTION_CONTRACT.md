# P1-SPEC-06 Review Promotion Contract

## Purpose

This contract defines review states, promotion states, and the boundary between Codex output, Human Gate approval, and Python promotion.

## State Model

| State | Meaning |
|---|---|
| `CANDIDATE` | Generated output exists but has no approval authority. |
| `VALIDATED` | Required validators passed for the current subject hash. |
| `REVIEW_REQUIRED` | Human Gate review is required before authority can advance. |
| `REVISION_REQUIRED` | Human Gate or validator found blockers requiring repair. |
| `APPROVED_BY_HUMAN` | Human Gate approved the reviewed subject hash. |
| `PROMOTION_READY` | Validation and approval are present and lock prerequisites are satisfied. |
| `PROMOTED` | Python promotion has moved the approved subject into the next authorized state. |
| `LOCKED` | SPEC_LOCK or BUILD_LOCK binds the approved content hashes. |
| `INVALIDATED` | A dependency changed and the subject can no longer be trusted. |

## Review Decision Requirements

Review decisions must include:

- Stable `decision_id`.
- Reviewed `subject_hash`.
- Decision enum: `APPROVED`, `REVISION_REQUIRED`, or `REJECTED`.
- Reviewer identity.
- Open blockers.
- Approved sections when approved.

## Promotion Requirements

Promotion may happen only when:

- Candidate outputs are complete.
- Validators pass for the current subject hash.
- Review decision approves the same subject hash.
- Upstream review decisions or locks are present and hash-bound.
- No forbidden write paths changed.
- No downstream invalidation remains unresolved.

## Contract Clauses

### REVIEW-CONTRACT-001 Codex Cannot Approve Itself

Codex may prepare review material and repair Candidates, but cannot produce final approval of its own Candidate.

### REVIEW-CONTRACT-002 Approval Binds To Hash

Human approval applies only to the reviewed subject hash. Any change to approved output requires a new validation and review decision.

### REVIEW-CONTRACT-003 Promotion Is Python-Controlled

Promotion state is controlled by deterministic Python checks, not by Codex prose.

### REVIEW-CONTRACT-004 Rejection And Revision Block Promotion

`REJECTED` and `REVISION_REQUIRED` decisions block promotion and lock creation.

### REVIEW-CONTRACT-005 Approved Is Not Locked

`APPROVED_BY_HUMAN` does not equal `LOCKED`. Lock state requires separate lock artifact creation and hash binding.

### REVIEW-CONTRACT-006 Promotion Emits Audit Record

Promotion must emit an audit record naming input hashes, validators, review decision hash, output state, and invalidation effects.

