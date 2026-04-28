---
type: service
name: checkout-api
status: reviewed
owner: payments-team
upstream: [user-service, inventory-api, fraud-scoring, payments-db]
downstream: [orders-mart, fulfillment-service]
incidents: [2026-03-14-checkout-latency, 2026-04-02-checkout-latency]
sources:
  - raw/postmortems/2026-03-14-checkout-latency.md
  - raw/postmortems/2026-04-02-checkout-latency.md
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: [tier-1, customer-facing]
last_updated: 2026-04-28
---

## Purpose

Public-facing checkout endpoint. Accepts a cart and a payment
method; validates inventory, runs fraud scoring, charges the
payment method, returns an order ID. Tier-1, customer-facing — a
SEV2-or-worse outage means active revenue loss (see
[[2026-03-14-checkout-latency]] at ~$48k impact and
[[2026-04-02-checkout-latency]] at ~$31k).

## Dependencies

**Upstream — services `checkout-api` calls:**
- `[[user-service]]` — user identity and billing address.
- `[[inventory-api]]` — stock verification.
- `[[fraud-scoring]]` — fraud check (added 2025-Q3).
- `[[payments-db]]` — primary database.

**Downstream — consumers of `checkout-api` output:**
- `[[orders-mart]]` — daily aggregate for analytics.
- `[[fulfillment-service]]` — shipping and warehouse routing.

## Known failure modes

These are failure modes the team has actually seen, not a
theoretical exhaustive list. The on-call decision tree lives in
`raw/runbooks/checkout-api-oncall-runbook.md`; the canonical
first-check post-2026-04-02 is **traces to `[[fraud-scoring]]`,
not pool utilization on `[[payments-db]]`** — symptoms are
indistinguishable until you check the upstream call.

### 1. payments-db connection-pool saturation

`[[connection-pool-exhaustion]]`. Surfaced by
[[2026-03-14-checkout-latency]]: pool size 50 (static since 2024)
was crossed by routine traffic after ~3x organic growth.
Symptoms: p99 multi-second, pool utilization at 100%, the
post-03-14 pool-saturation alert fires. Mitigation requires
config change + pod restart (~5 min deploy). Note: under failure
mode #2 below, the same symptoms appear, and raising the pool
will not help — check fraud-scoring traces first.

### 2. Slow fraud-scoring calls

[[downstream-slow-call-holds-upstream-resources]]. Surfaced by
[[2026-04-02-checkout-latency]] when a regex deploy on
`[[fraud-scoring]]` blocked outbound calls ~11s and saturated
`[[payments-db]]`'s pool indirectly. Symptom-identical to #1; the
distinguishing diagnostic is `checkout-api → fraud-scoring` p99
in Datadog. As of 2026-04-28 there is **no outbound timeout** on
`checkout-api → fraud-scoring` — the 3-second timeout action
item is open and overdue (due 2026-04-12).

### 3. Bad checkout-api deploy

Latency or error-rate spike correlated to a deploy timestamp;
bisects to a single commit. Mitigation: `kubectl rollout undo`.

This was the **wrong** initial hypothesis on both
[[2026-03-14-checkout-latency]] and
[[2026-04-02-checkout-latency]] and was ruled out in both. The
runbook explicitly warns: don't anchor on it just because it's
the easiest mitigation. No incident yet attributed to this mode.

### 4. inventory-api unavailability

Distinct from the latency-style modes above — error rate spike,
not latency spike. Requests return 503 with "inventory check
failed" in the body. `[[inventory-api]]` carries its own runbook;
escalate to that team's on-call.

`checkout-api` can run in degraded mode (skip the inventory
check) for short periods via the feature flag
`checkout.skip-inventory` (default false). The runbook references
config docs for full feature-flag detail.

Last seen 2025-09-08 per the runbook. **That incident is not
ingested in this wiki yet.** Flagged as a documentation gap on
[[inventory-api]] and in the log.

## Incident history

Newest first.

- [[2026-04-02-checkout-latency]] — SEV2, 38 min,
  `[[fraud-scoring]]` regex deploy. Same symptoms as 03-14,
  different root cause.
- [[2026-03-14-checkout-latency]] — SEV2, 47 min, pool
  exhaustion on `[[payments-db]]`.

The runbook also references a 2025-09-08 inventory-api
unavailability incident that is not yet documented here.

## Owners

`[[payments-team]]`. Escalation per the runbook:

- First on-call: `[[payments-team]]` rotation in PagerDuty.
- Backup: `[[sre-team]]` on-call.
- Lead: Janelle Okonkwo (EM).

## Notes

- Two failure modes (#1 and #2) share symptom profile but have
  different mechanisms — see the `CONTRADICTION:` block on
  [[connection-pool-exhaustion]]. Investigators must not
  symptom-match between them; the runbook's decision tree is the
  authoritative response.
- Useful dashboards (per runbook):
  - `dashboards.internal/checkout-api-overview` — top-level
    p99, error rate, request rate.
  - `dashboards.internal/payments-db-pool` — pool state and
    query latency.
  - `dashboards.internal/checkout-fraud-scoring` — outbound
    call latency, added post 2026-04-02.
- Runbook last reviewed 2026-04-15 (post 04-02). Prior to that
  rewrite, the decision tree started at "check the pool" — that
  ordering is what cost ~20 minutes on 04-02.
- Page promoted from `draft` to `reviewed` on 2026-04-28 on the
  back of the runbook source — first reviewed service in this
  wiki.