---
name: foundry-run-program
description: Inspect and advance the P1-P4 program only through declared gates.
---

# foundry-run-program

## Instructions

Run one active Workpack at a time; stop at human gates; never activate a phase without required locks.

## Global boundaries

- Read the active Workpack and Context Manifest first.
- Do not change locked Constitution or Specs.
- Do not expand write scope.
- Stop and report if required evidence is missing.
- Never self-approve or auto-advance.
