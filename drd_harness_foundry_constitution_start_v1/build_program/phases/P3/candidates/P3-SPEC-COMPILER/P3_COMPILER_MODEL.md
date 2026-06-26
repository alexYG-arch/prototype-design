# P3 Compiler Model

## Model Overview

The P3 compiler model has two rails:

- authority rail: approved natural-language sections from P3 source, distillation, closure, element, pattern, and layout candidates
- verification rail: structured records that index semantic units, section order, source hashes, review decisions, schema hashes, and conservation results

The authority rail decides meaning. The verification rail proves that the final DRD preserved that meaning.

## Core Records

### Closed Input Record

A closed input record identifies one approved input. It carries the input type, path, sha256, approval reference, semantic role, and invalidation state. It is rejected if it lacks a hash, lacks approval linkage, has an unknown input type, or points to invalidated evidence.

### Compiler Input Bundle

The input bundle is the complete closed set for compilation. It includes approved semantic artifacts, operational indexes, review decisions, lock references, validator results, control indexes, schema identities, stage order, section order, and a closed input hash.

If an input is not in the bundle, the compiler must behave as if it does not exist.

### Approved Section

An approved section is a source-attributed natural-language section selected for final DRD assembly. It must include stage id, section id, order indexes, heading text, source path, source hash, approval reference, body, and semantic unit ids.

The compiler may not edit the body except for exact preservation of approved text and mechanical placement in the final document.

### Atomic Semantic Unit

An atomic semantic unit is the smallest verifiable semantic claim used for conservation. Each unit binds a unit id, unit type, unit class, source path, source section, source span, source hash, approval reference, parent relation, canonical value, unit hash, and inventory version.

Atomic units are not a replacement for prose. They are the checkable skeleton used to prove that compiled prose did not lose or gain meaning.

### Conservation Report

The conservation report compares approved input semantic units with compiled output semantic units. A passing report has no added units, no omitted units, no hash drift, no unapproved inputs, no non-atomic unit findings, no ordering findings, no nondeterminism findings, and no read-only QA mutation.

### Final Manifest And Indexes

The final manifest names the output files, counts compiled inputs and units, records semantic and mechanical hashes, and reports conservation status.

The table of contents records deterministic section order. The reference index records source and approval lineage. The hash index records input, semantic, mechanical, output, reference, table-of-contents, conservation, schema, and compiler-code hashes.

## Stage Mapping

The compiler consumes P3 modules into the existing DRD stage order:

| DRD stage | P3 source modules |
| --- | --- |
| `DRD-01` | `source_intake` |
| `DRD-02` | `prd_experience_distillation` |
| `DRD-03` | `interaction_closure` |
| `DRD-03B` | `page_element_model`, `shared_component_and_information_patterns` |
| `DRD-04` | `natural_language_layout`, compiler assembly metadata |

Compiler assembly metadata is mechanical. It does not add product semantics to `DRD-04`.

## Failure Routing

The compiler stops when input closure, deterministic order, hash freshness, section references, atomic inventory, conservation, final manifest, or read-only QA boundary checks fail.

Manual review may classify the failed upstream input, but the compiler cannot resolve the failure by adding product content or weakening the conservation rules.
