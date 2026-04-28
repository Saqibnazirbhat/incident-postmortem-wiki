---
type: root-cause
name: downstream slow call holds upstream resources
status: draft
owner: payments-team
incidents: [2026-04-02-checkout-latency]
services: [checkout-api, payments-db, fraud-scoring]
sources:
  - raw/postmortems/2026-04-02-checkout-latency.md
source_hashes:
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
tags: [latency, capacity, recurring, deploy-induced]
last_updated: 2026-04-27
---

## Definition

An upstream service holds a finite local resource (a connection
from a pool, a worker thread, a request slot) for the duration of a
synchronous downstream call. When the downstream call slows down,
the upstream resource is held longer per request, and resource
exhaustion follows even though the upstream's own capacity is
unchanged.

The visible failure looks like the upstream's local resource is
undersized — pool saturation, thread starvation, queue backlog —
but raising that resource only buys time. The bottleneck is the
downstream's latency, multiplied by upstream concurrency.

## Why it recurs

Captured once so far ([[2026-04-02-checkout-latency]]). Author of
that postmortem explicitly proposes this as a *class* of failure
that subsumes [[2026-03-14-checkout-latency]] as a degenerate case
("no slow downstream — the pool was just too small for normal
traffic"). That broader claim is contested; see the
`CONTRADICTION:` block on [[connection-pool-exhaustion]].

Pattern visible from one incident:
- Symptoms (pool saturation, upstream latency) point at the
  upstream's own resource, not the downstream call.
- A naive symptom-matching alert (pool saturation) fires
  correctly but causally misleads — the 04-02 investigation lost
  ~20 minutes to this.
- The shape recurs with any deploy or change that slows a
  downstream call: bad regex, missing index, cache miss storm,
  retry storms, etc.

The `recurring` tag is a watch-flag pending a second incident.

## Detection

- Distributed traces with per-hop latency are the diagnostic that
  worked on 04-02 (17:01). Without traces, this failure mode is
  hard to distinguish from local pool exhaustion.
- A useful leading signal would be downstream-call p99 latency
  alerts paired with upstream resource utilization. As of 04-02
  this signal does not exist for `[[checkout-api]] →
  [[fraud-scoring]]`.
- Pool/thread/queue saturation alone is insufficient — see notes on
  [[2026-04-02-checkout-latency]].

## Mitigations

- Short-term (used 2026-04-02): revert the offending downstream
  deploy.
- Per-call: timeouts on outbound calls bound the upstream resource
  hold time. Action item on
  [[2026-04-02-checkout-latency]]: 3-second timeout on
  `[[checkout-api]] → [[fraud-scoring]]` (overdue, due 2026-04-12).
- Source-side: ReDoS lint and similar pre-deploy checks on the
  downstream service. Action item on
  [[2026-04-02-checkout-latency]]: ReDoS lint in CI for
  `[[fraud-scoring]]` (overdue, due 2026-04-09).
- Architectural: bulkheads, per-downstream connection budgets, or
  asynchronous decoupling. Not yet proposed.

## Related

- [[connection-pool-exhaustion]] — overlapping symptoms; see
  contradiction discussion there.
- [[checkout-api]]
- [[payments-db]]
- [[fraud-scoring]]
- [[2026-04-02-checkout-latency]]

## Notes

- The unifying claim that [[connection-pool-exhaustion]] is a
  degenerate case of this failure mode is the 04-02 author's
  framing alone; the 03-14 postmortem's SRE attribution stands
  unless and until the cross-team RFC concludes otherwise. RFC
  action item (due 2026-04-15) is overdue as of 2026-04-27.
