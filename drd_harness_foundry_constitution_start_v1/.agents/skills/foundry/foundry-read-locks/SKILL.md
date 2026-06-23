---
name: foundry-read-locks
description: Read and verify locked constitution, specs and upstream locks before any work.
---

# foundry-read-locks

## Instructions

Read `context_manifest.json`; verify every required file hash; stop on mismatch; do not substitute similarly named files.

## Global boundaries

- Read the active Workpack and Context Manifest first.
- Do not change locked Constitution or Specs.
- Do not expand write scope.
- Stop and report if required evidence is missing.
- Never self-approve or auto-advance.
