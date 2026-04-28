---
type: root-cause
name: connection pool exhaustion
status: draft
owner: payments-team
incidents: [2026-03-14-checkout-latency]
services: [checkout-api, payments-db]
sources:
  - raw/postmortems/2026-03-14-checkout-latency.md
source_hashes:
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
tags: [database, capacity]
last_updated: 2026-04-27
---

## Definition

A pool of reusable database connections is exhausted: every
connection is checked out and in use, so new requests block waiting
for a free connection. Latency spikes upstream even though the
database itself may be healthy. Symptoms look like a slow database;
the actual constraint is the pool size on the client side.

## Why it recurs

Only one incident has been *attributed* to this root cause so far
([[2026-03-14-checkout-latency]]). A second incident with identical
symptoms ([[2026-04-02-checkout-latency]]) was *not* attributed
here — see the `CONTRADICTION:` block under `## Notes`. So it is
genuinely unclear whether this root cause is recurring under the
same name, or whether 03-14 itself should be re-attributed.

Pattern visible from 03-14:
- The pool size was a static value (50) set at launch and never
  revisited.
- Traffic grew ~3x against an unchanged pool, and saturation arrived
  silently — no leading alert.

The `recurring` tag has been removed pending RFC resolution.

## Detection

- Saturation metric on the connection pool (Datadog showed 100%
  utilization the whole window for [[2026-03-14-checkout-latency]]).
- Upstream p99 latency alert is a lagging signal — by the time it
  fires the pool is already saturated. A pool-utilization alert at
  ~80% was the action item proposed by Priya for 2026-03-21
  (shipped). It fired correctly on
  [[2026-04-02-checkout-latency]] but pointed the investigation at
  the database when the actual cause was upstream — useful symptom
  signal, misleading causal signal.

## Mitigations

- Short-term (used 2026-03-14): raise pool size and restart pods to
  reset connections. Effective but doesn't address the underlying
  capacity drift.
- Long-term: tie pool size to traffic forecasts; periodic capacity
  review (action item, [[payments-team]], due 2026-04-01).
- Systemic: audit other "set and forget" capacity configs across
  services (action item from postmortem, currently unowned).

## Related

- [[checkout-api]]
- [[payments-db]]
- [[2026-03-14-checkout-latency]]

## Notes

- Postmortem flags a broader pattern — capacity configs sized at
  launch and never revisited. Worth promoting to its own concept
  page if a second incident validates it.

CONTRADICTION: Root cause attribution differs between two incidents
with identical symptoms.

- [[2026-03-14-checkout-latency]] postmortem
  (raw/postmortems/2026-03-14-checkout-latency.md, Priya Shah,
  SRE on-call): blamed connection-pool exhaustion on
  `[[payments-db]]`. Fix: raised pool from 50 to 200.
- [[2026-04-02-checkout-latency]] postmortem
  (raw/postmortems/2026-04-02-checkout-latency.md, Marco Diaz,
  payments-team): same symptoms with the larger pool (already
  200; raised to 400 with no improvement). Blamed slow downstream
  call to `[[fraud-scoring]]` (regex with catastrophic
  backtracking), and explicitly argued the pool exhaustion was a
  downstream effect, not a root cause. Author further claims 03-14
  was a degenerate case of the same broader failure
  ([[downstream-slow-call-holds-upstream-resources]]) where the
  "downstream" was simply organic traffic against an undersized
  pool.

Both incidents are linked from this page; only 03-14 is in
`incidents:` because 03-14 is the only one *attributed* here. The
unifying explanation is open and explicitly disputed across teams.

Resolution mechanism: RFC action item on
[[2026-04-02-checkout-latency]], owner [[payments-team]], due
2026-04-15. **Overdue as of 2026-04-27.** Until that RFC concludes,
do not silently re-attribute 03-14.
