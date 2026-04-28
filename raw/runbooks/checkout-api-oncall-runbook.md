# checkout-api on-call runbook

**Owner:** payments-team
**Last reviewed:** 2026-04-15 (post 04-02 incident updates)
**Page audience:** SRE on-call, payments-team on-call

---

## What this service does

`checkout-api` is the public-facing checkout endpoint. It accepts
a cart and a payment method, validates inventory, runs fraud
scoring, charges the payment method, and returns an order ID. It's
tier-1, customer-facing, and a SEV2-or-worse outage means active
revenue loss.

## Dependencies

**Upstream calls (services checkout-api depends on):**
- `user-service` — for user identity + billing address
- `inventory-api` — to verify stock
- `fraud-scoring` — for fraud check (added 2025-Q3)
- `payments-db` — primary database for the service

**Downstream consumers (services that read checkout-api's output):**
- `orders-mart` — daily aggregate for analytics
- `fulfillment-service` — for shipping + warehouse routing

## Common failure modes

These are the failure modes the team has actually seen, not a
theoretical exhaustive list. Each links to a known incident.

### 1. payments-db connection pool saturation

**Symptom:** p99 latency spikes from ~180ms to multi-second.
Datadog dashboard shows pool utilization at or near 100%.
PagerDuty pool-saturation alert (added 2026-03-21) usually fires.

**First diagnostic step (post 2026-04-02 update):** Do NOT assume
the pool is the root cause. Check `checkout-api` →
`fraud-scoring` p99 *first*. If fraud-scoring is slow, the pool
saturation is a *symptom* of upstream blocking, and raising the
pool will not help. See 2026-04-02 incident for the failure mode.

If fraud-scoring is healthy (<200ms p99): treat as genuine
capacity exhaustion. Consider raising the pool size, but also
check whether traffic is actually anomalous vs. organic growth.
The 2026-03-14 incident was organic growth crossing a pool
threshold last tuned in 2024.

**Mitigation:** Pool resize requires config change + pod restart.
~5 minute deploy.

### 2. Slow fraud-scoring calls

**Symptom:** Same as above — p99 latency spike, pool saturation.
Distinguishable from #1 only by checking `checkout-api` →
`fraud-scoring` traces. This is *the* lesson from 2026-04-02:
identical-looking symptoms, different root cause.

**Mitigation:** Outbound timeout on `checkout-api` → `fraud-scoring`
calls is the long-term fix (action item open as of 2026-04-12,
overdue). Short-term: revert any recent `fraud-scoring` deploy
and page their on-call.

### 3. Bad checkout-api deploy

**Symptom:** Latency or error rate spike correlated with a deploy
timestamp. Bisects cleanly to a single commit.

**Mitigation:** Roll back via `kubectl rollout undo`. Standard
deploy-rollback runbook applies.

This was the *initial* hypothesis on both 2026-03-14 and 2026-04-02
and was ruled out in both. Don't anchor on it just because it's
the easiest to mitigate.

### 4. inventory-api unavailability

**Symptom:** Checkout requests return 503 with "inventory check
failed" in the response body. Distinct from latency-style
incidents — error rate spike, not latency spike.

Last seen: 2025-09-08 (not yet documented in this wiki).

**Mitigation:** inventory-api has its own runbook. Page their
on-call. checkout-api can run in degraded mode (skip inventory
check) for short periods — feature flag `checkout.skip-inventory`,
default false, see config docs.

## On-call decision tree (latency incident)

```
1. checkout-api p99 latency alert fires
   ↓
2. Check checkout-api → fraud-scoring p99 in Datadog FIRST
   ↓
   ├── fraud-scoring slow (>1s p99)
   │   → Failure mode #2. Page fraud-scoring on-call.
   │     Check for recent fraud-scoring deploys; revert if any.
   │
   └── fraud-scoring healthy
       ↓
       3. Check payments-db pool utilization
          ↓
          ├── Pool >80%
          │   → Failure mode #1. Check traffic levels first —
          │     anomalous spike vs. organic? If organic, raise pool.
          │
          └── Pool healthy
              ↓
              4. Check for recent checkout-api deploys
                 ↓
                 ├── Deploy in last 30min
                 │   → Failure mode #3. Roll back.
                 │
                 └── No recent deploy
                     → Page payments-team lead. Unknown failure mode.
                       Capture diagnostics; do not guess.
```

## Useful dashboards

- `dashboards.internal/checkout-api-overview` — top-level p99,
  error rate, request rate
- `dashboards.internal/payments-db-pool` — connection pool state,
  query latency
- `dashboards.internal/checkout-fraud-scoring` — outbound call
  latency to fraud-scoring (added post 2026-04-02)

## Escalation

- First on-call: payments-team rotation in PagerDuty
- Backup: SRE on-call
- Lead: Janelle Okonkwo (EM)

## Notes

This runbook was rewritten on 2026-04-15 to incorporate lessons
from the 2026-04-02 incident. Prior to that revision, failure
mode #1 was listed as the *primary* failure mode and the decision
tree started at "check the pool." That ordering caused ~20
minutes of misdirected investigation on 2026-04-02 because the
pool-saturation alert fired but pointed at the wrong cause.

If you find yourself updating this runbook after an incident,
preserve the old version in a Notes block — future on-call
engineers want to know *why* the runbook says what it says.
