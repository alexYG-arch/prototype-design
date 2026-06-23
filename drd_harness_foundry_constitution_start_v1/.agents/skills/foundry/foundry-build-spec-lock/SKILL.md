---
name: foundry-build-spec-lock
description: Build a phase SPEC_LOCK from approved assembled specs.
---

# foundry-build-spec-lock

## Instructions

Record file hashes, root hash, review decision hash and catalogs; fail if any required part or validation is missing.

## Global boundaries

- Read the active Workpack and Context Manifest first.
- Do not change locked Constitution or Specs.
- Do not expand write scope.
- Stop and report if required evidence is missing.
- Never self-approve or auto-advance.
