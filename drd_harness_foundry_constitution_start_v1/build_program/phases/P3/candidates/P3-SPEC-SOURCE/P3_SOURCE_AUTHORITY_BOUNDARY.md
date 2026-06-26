# P3 Source Authority And Boundary Rules

## Authority Model

Natural-language source content remains the primary semantic input when a PRD or brief is supplied. Structured source inventory rows are an index and verification skeleton; they do not replace the source wording.

For non-text files, the file hash and metadata are authoritative for identity, while extracted semantics are not authoritative until a separate extraction or distillation artifact records evidence and review status.

## Deduction And Adoption

Source intake may normalize filenames, MIME kinds, byte hashes, source roles, and obvious structural metadata. It may not infer product requirements, user journeys, UI elements, business rules, or layout instructions. Those deductions belong to downstream P3 modules and must cite the frozen source package.

## Human Review Required Conditions

A source item must be routed to human review when any of these conditions hold:

1. The source is mentioned but not locally available.
2. The source appears to contain credentials, private personal data, payment details, or unreleased third-party content.
3. The source authority conflicts with another accepted source.
4. The source would require adding product capability outside the locked phase scope.
5. The source file type is accepted for storage but lacks an extractor or schema needed for semantic adoption.
6. The source snapshot time, origin, or owner cannot be described well enough for downstream provenance.

## Mutation Boundary

After freeze, source bytes must not be modified in place. Redactions, conversions, OCR, parsing, and extracted text must be separate derivative artifacts that reference the immutable source item hash.

## Downstream Consumption Boundary

A downstream module may consume only source items whose `downstream_eligibility` is `eligible`, or may consume `review_required` items solely to preserve a blocker or open question. No downstream module may treat a rejected source as semantic authority.
