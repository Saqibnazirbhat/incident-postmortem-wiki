---
type: service
name: fraud-scoring
status: stub
owner: trust-and-safety-team
sources:
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: []
last_updated: 2026-04-28
---

Stub. Referenced by [[2026-04-02-checkout-latency]],
[[checkout-api]], and
[[downstream-slow-call-holds-upstream-resources]]. Owned by
[[trust-and-safety-team]] per the 2026-04-02 postmortem. Not yet
documented. Known facts:

- Added as a `[[checkout-api]]` upstream dependency in 2025-Q3
  (per `[[checkout-api]]`'s runbook).
- A regex rule deployed at 16:35 UTC on 2026-04-02 had
  catastrophic backtracking and made the service's p99 spike to
  ~11s until reverted.
- ReDoS lint in CI is the open follow-up action item from
  [[2026-04-02-checkout-latency]] — overdue, due 2026-04-09.
