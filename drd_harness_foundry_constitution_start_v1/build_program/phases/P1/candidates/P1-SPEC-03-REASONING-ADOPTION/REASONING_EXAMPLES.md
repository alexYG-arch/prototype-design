# P1-SPEC-03 Reasoning Examples

## Positive Example: Explicit Source Adoption

Inventory row:

```json
{
  "element_id": "EL-LOGIN-CTA",
  "element_type": "CTA",
  "source_refs": ["PRD:auth:login_button"],
  "source_text_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "stage_id": "DRD-03",
  "artifact_id": "PRD_EXPLICIT_ELEMENT_INVENTORY"
}
```

Adoption decision:

```json
{
  "element_id": "EL-LOGIN-CTA",
  "source_refs": ["PRD:auth:login_button"],
  "element_type": "CTA",
  "outcome": "ADOPT_AS_IS",
  "input_obligations": [],
  "inference_refs": ["INF-LOGIN-CTA-001"]
}
```

Why this passes:

- The CTA is explicit in source.
- The decision exists before downstream use.
- The decision joins to exactly one inventory element.
- No new product capability is introduced.

## Positive Example: Input Obligation

```json
{
  "inference_id": "INF-ADDR-001",
  "inference_class": "DEDUCTIVE_NECESSITY",
  "stage_id": "DRD-03",
  "artifact_id": "PAGE_ELEMENT_BLUEPRINT",
  "source_refs": ["PRD:checkout:shipping_required", "RD-RULE-001"],
  "premises": [
    "Checkout cannot complete without shipping address.",
    "RD-RULE-001 requires an actionable path for required input."
  ],
  "applied_rules": ["RD-RULE-001"],
  "necessity_basis": "The task cannot complete unless the required shipping address is obtained.",
  "unresolved_product_choices": [],
  "conclusion": "The checkout flow requires an address entry, selection, import, or acquisition path.",
  "canonical_eligibility": "ELIGIBLE",
  "downstream_use": ["PAGE_ELEMENT_BLUEPRINT", "USER_TASK_FLOW"]
}
```

Why this passes:

- The conclusion follows from task success and input obligation.
- It does not choose an unapproved external integration.

## Negative Example: Induction Promoted Too Early

```json
{
  "inference_id": "INF-SOCIAL-LOGIN-001",
  "inference_class": "INDUCTIVE_CANDIDATE",
  "source_refs": ["pattern:common_auth_flows"],
  "conclusion": "Add social login because most login pages include it.",
  "canonical_eligibility": "ELIGIBLE",
  "downstream_use": ["PAGE_ELEMENT_BLUEPRINT"]
}
```

Expected result: fail.

Reason:

- The source is a pattern, not PRD authority.
- The inference is inductive but marked canonical.
- Social login is a product capability expansion unless approved.

## Negative Example: Hidden Product Expansion In Normalization

```json
{
  "element_id": "EL-EXPORT",
  "source_refs": ["PRD:reports:view"],
  "element_type": "CTA",
  "outcome": "ADOPT_NORMALIZED",
  "normalized_label": "Export to Salesforce",
  "input_obligations": [],
  "inference_refs": ["INF-EXPORT-001"]
}
```

Expected result: fail.

Reason:

- Exporting to Salesforce is an integration and capability not proven by the source citation.
- The decision should be `ROUTE_PRODUCT_GAP` unless already approved.

## Negative Example: Missing Input Path

```json
{
  "derived_element_id": "DERIVE-QUOTE-001",
  "derivation_source": "task",
  "obligation_refs": ["RD-RULE-001"],
  "inference_refs": ["INF-QUOTE-001"],
  "canonical_eligibility": "ELIGIBLE"
}
```

Expected result: fail if the task depends on quote details and no path exists to enter, select, import, or acquire them.

## Positive Example: Product Gap Routing

```json
{
  "gap_id": "GAP-CRM-001",
  "gap_type": "UNAPPROVED_INTEGRATION",
  "source_refs": ["PRD:sales_notes"],
  "blocked_artifacts": ["PAGE_ELEMENT_BLUEPRINT"],
  "candidate_options": [
    "Manual CSV import",
    "Salesforce integration",
    "No CRM import in this version"
  ],
  "required_decision": "Select whether CRM import is in scope.",
  "status": "OPEN"
}
```

Why this passes:

- The candidate options are review material only.
- Dependent artifacts remain blocked until Human Gate resolves the gap.
