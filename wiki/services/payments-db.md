---
type: service
name: payments-db
status: draft
owner: payments-team
upstream: []
downstream: [checkout-api]
incidents: [2026-03-14-checkout-latency, 2026-04-02-checkout-latency]
sources:
  - raw/postmortems/2026-03-14-checkout-latency.md
  - raw/postmortems/2026-04-02-checkout-latency.md
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: [database, tier-1]
last_updated: 2026-04-28
---

## Purpose

Primary database for `[[checkout-api]]`. The connection pool on
the client side has been the visible failure surface in two SEV2
incidents.

## Dependencies

- Downstream consumers: `[[checkout-api]]` is the only consumer
  documented in sources to date.
- Upstream calls: not yet documented.

## Known failure modes

- `[[connection-pool-exhaustion]]` — the pool can saturate on
  organic traffic when sized too small. The historical pool size
  (50) was unchanged since 2024 and was crossed for the first time
  on 2026-03-14. See [[2026-03-14-checkout-latency]].
- Indirect saturation via
  [[downstream-slow-call-holds-upstream-resources]]. On
  [[2026-04-02-checkout-latency]] the pool saturated as a *symptom*
  of slow upstream calls from `[[checkout-api]]` to
  `[[fraud-scoring]]`; raising the pool size did not help.

## Pool history

- Pre-2024: pool size 50 (static, set at launch).
- 2026-03-14: raised 50 → 200 as mitigation for
  [[2026-03-14-checkout-latency]].
- 2026-04-02: raised 200 → 400 as initial response to
  [[2026-04-02-checkout-latency]]; had no effect because the
  cause was upstream.

## Incident history

Newest first.

- [[2026-04-02-checkout-latency]] — SEV2, 38 min. Pool saturated
  as a symptom; root cause attributed elsewhere.
- [[2026-03-14-checkout-latency]] — SEV2, 47 min. Pool
  saturation attributed as root cause.

## Owners

`[[payments-team]]`.

## Notes

- Useful dashboard (per `[[checkout-api]]`'s runbook):
  `dashboards.internal/payments-db-pool` — pool state and query
  latency.
- The pool-saturation alert (added 2026-03-21 as an action item
  from [[2026-03-14-checkout-latency]]) fires on this database's
  utilization. It is a useful symptom signal but, per the
  04-02 lesson, not a sufficient causal signal — see the
  `CONTRADICTION:` block on [[connection-pool-exhaustion]].
- This page was promoted from stub to draft on 2026-04-28 with
  the runbook ingest. Schema beyond pool sizing (replication,
  query patterns, retention, capacity beyond connections) is
  still undocumented.