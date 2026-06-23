---
name: foundry-invalidate-downstream
description: Mark downstream artifacts and workpacks invalid when an upstream hash changes.
---

# foundry-invalidate-downstream

## Instructions

Traverse declared dependency graph; record reasons; never silently reuse stale artifacts.

## Global boundaries

- Read the active Workpack and Context Manifest first.
- Do not change locked Constitution or Specs.
- Do not expand write scope.
- Stop and report if required evidence is missing.
- Never self-approve or auto-advance.
