---
type: service
name: inventory-api
status: stub
owner: unknown
sources:
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: []
last_updated: 2026-04-28
---

Stub. Referenced by [[checkout-api]] as an upstream dependency
("stock verification") per the on-call runbook. Owner not named
in any ingested source.

**Documentation gap:** the runbook references a 2025-09-08
`inventory-api` unavailability incident — error rate spike with
503 "inventory check failed" — that is not yet ingested in this
wiki. Postmortem source not present in `raw/`. Surface to the
inventory-api team on the next opportunity.

`checkout-api` carries a degraded-mode feature flag
`checkout.skip-inventory` (default false) that allows it to run
short windows without this service. Mentioned in the runbook,
config docs not yet ingested.
