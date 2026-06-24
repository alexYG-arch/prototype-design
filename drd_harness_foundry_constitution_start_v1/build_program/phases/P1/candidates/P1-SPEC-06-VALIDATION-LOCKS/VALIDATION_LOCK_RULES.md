# P1-SPEC-06 Validation Lock Rules

## Candidate-Only Rules

### VLOCK-RULE-001 Candidate By Default

Codex outputs are Candidates by default. A Candidate label must remain visible in manifest, handoff, and result records until promotion.

### VLOCK-RULE-002 No Self Approval

The generating Codex run cannot approve, promote, or lock its own output.

### VLOCK-RULE-003 Approved Hash Only

Approval applies only to the exact Candidate subject hash reviewed by Human Gate.

## Validation Rules

### VLOCK-RULE-004 Independent Validator Required

Validation must be performed by Python validators or externally reviewable deterministic checks independent of the generation action.

Validator identity must include code hash, schema hash, runtime identity, and version. Validation evidence without validator identity cannot justify approval, promotion, lock, or unaffected claims.

### VLOCK-RULE-005 Validator Cannot Repair

Validators must not change semantic artifacts. They emit failures, findings, and repair requirements.

### VLOCK-RULE-006 Scope Postflight Required

Every Candidate must run postflight scope validation against allowed and forbidden paths.

### VLOCK-RULE-007 Required Output Coverage

Every required output in the Candidate manifest must exist, be non-empty, and pass syntax validation when applicable.

## Review And Promotion Rules

### VLOCK-RULE-008 Review Before Promotion

Promotion requires Human Gate approval bound to the current subject hash.

### VLOCK-RULE-009 Promotion Audit Required

Promotion must emit audit metadata for input hashes, validators, review decisions, output state, and invalidation effects.

### VLOCK-RULE-010 Approved Is Not Sealed

Human approval does not create SPEC_LOCK or BUILD_LOCK by itself.

## Lock Rules

### VLOCK-RULE-011 Python Creates Canonical Locks

Canonical SPEC_LOCK and BUILD_LOCK creation must be performed by Python-controlled lock tooling, not Codex prose.

### VLOCK-RULE-012 Lock Hash Canonicalization

Lock root hashes must be computed from deterministic ordered file path and sha256 records.

### VLOCK-RULE-013 Lock Inputs Are Closed

Lock inputs must list every file, review decision, validator result, source lock, and upstream lock needed to justify the lock.

Lock inputs must include validator identity hashes for every validator result used as evidence.

### VLOCK-RULE-014 Supersede Do Not Mutate

Existing lock artifacts must not be edited in place; new locks must supersede old locks explicitly.

### VLOCK-RULE-014A Supersession Graph Is Acyclic

Lock supersession records must form an acyclic graph. Direct or transitive self-supersession is invalid.

## Invalidation Rules

### VLOCK-RULE-015 Dependency Graph Required

Invalidation must use an explicit dependency graph mapping upstream hashes to downstream subjects.

Every dependency edge must declare an edge type: `SOURCE_DEPENDENCY`, `REVIEW_DEPENDENCY`, `SPEC_LOCK_DEPENDENCY`, `BUILD_LOCK_DEPENDENCY`, `VALIDATOR_DEPENDENCY`, `TEST_EVIDENCE_DEPENDENCY`, `WORKPACK_DEPENDENCY`, `SKILL_DEPENDENCY`, or `RELEASE_DEPENDENCY`.

### VLOCK-RULE-016 Transitive Propagation

When an upstream hash changes, invalidation must propagate to all downstream subjects that depend on it directly or transitively.

### VLOCK-RULE-017 Block Old Evidence

Invalidated tests, locks, Candidates, skills, workpacks, or artifacts cannot be used as evidence for current approval or release.

### VLOCK-RULE-018 Revalidate Or Repair

Every invalidated subject must record whether it requires revalidation, repair, review, relock, rebuild, retest, or discard.

It must also record recovery owner and required command or workflow. Unowned invalidation cannot be marked ready.

### VLOCK-RULE-019 Structured Partial Unaffected Claim

If only part of a subject is claimed unaffected, the claim must list affected paths, unaffected paths, reason, validator result reference, review requirement, and dependency expiry.
