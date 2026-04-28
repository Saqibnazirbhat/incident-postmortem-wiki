# Wiki Index

Last refreshed: 2026-04-28

## Incidents (2)

Newest first.

- [[2026-04-02-checkout-latency]] — SEV2, 38min, fraud-scoring regex deploy
- [[2026-03-14-checkout-latency]] — SEV2, 47min, payments-db pool exhaustion

## Services (7)

- [[checkout-api]] — payments-team (reviewed)
- [[fraud-scoring]] — trust-and-safety-team (stub)
- [[fulfillment-service]] — unknown (stub)
- [[inventory-api]] — unknown (stub)
- [[orders-mart]] — unknown (stub)
- [[payments-db]] — payments-team
- [[user-service]] — unknown (stub)

## Root causes (2)

- [[connection-pool-exhaustion]] — 1 incident; contested attribution
- [[downstream-slow-call-holds-upstream-resources]] — 1 incident

## Concepts (1)

- [[sev-classification]] — current policy, dispute, open RFC

## Owners (3)

- [[payments-team]]
- [[sre-team]]
- [[trust-and-safety-team]]

## Stubs to flesh out (5)

- [[fraud-scoring]] — referenced by [[2026-04-02-checkout-latency]], [[checkout-api]], [[downstream-slow-call-holds-upstream-resources]]
- [[fulfillment-service]] — referenced by [[checkout-api]] (downstream)
- [[inventory-api]] — referenced by [[checkout-api]] (upstream); 2025-09-08 incident in runbook is unfiled
- [[orders-mart]] — referenced by [[checkout-api]] (downstream)
- [[user-service]] — referenced by [[checkout-api]] (upstream)

## Open contradictions (1)

- [[connection-pool-exhaustion]] — 03-14 (SRE) attributes pool exhaustion as root cause; 04-02 (payments-team) attributes the same symptoms to [[downstream-slow-call-holds-upstream-resources]] and argues 03-14 was a degenerate case. RFC due 2026-04-15 is overdue.
