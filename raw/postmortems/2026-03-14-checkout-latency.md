# Postmortem: Checkout latency spike — 2026-03-14

**Author:** Priya Shah (SRE on-call)
**Date filed:** 2026-03-15
**Severity:** SEV2
**Duration:** 47 minutes (14:23 – 15:10 UTC)
**Customer impact:** ~12% of checkout requests timed out.
Estimated $48k in dropped revenue.

## Summary

On 2026-03-14 at 14:23 UTC, p99 latency on `checkout-api` jumped from
180ms to over 8 seconds. The on-call was paged at 14:25 via PagerDuty.
After 47 minutes of investigation, mitigation came from increasing the
`payments-db` connection pool from 50 to 200 and restarting the
`checkout-api` pods. Latency returned to baseline at 15:10 UTC.

## Timeline (UTC)

- 14:23 — `checkout-api` p99 latency alert fires in PagerDuty.
- 14:25 — Priya (SRE) acknowledges the page.
- 14:31 — Initial hypothesis: bad deploy. Rolled back deploy
  `checkout-api@8a2f1c`. No improvement.
- 14:48 — Datadog dashboard shows `payments-db` connection pool at
  100% saturation for the entire window.
- 14:54 — New hypothesis: connection pool exhaustion. Increased pool
  size from 50 to 200 in config and restarted `checkout-api` pods.
- 15:10 — Latency back to under 250ms p99. Incident resolved.
- 15:30 — Priya posts incident summary in #incidents.

## Detection

Detected via existing PagerDuty alert on `checkout-api` p99 latency
threshold (>1s for 2 minutes). No customer reports came in before
detection.

## Root cause

`payments-db` connection pool exhaustion. The pool size of 50 had
been unchanged since 2024, while traffic to `checkout-api` had grown
roughly 3x in that period. Routine afternoon traffic crossed the pool
saturation threshold for the first time on 2026-03-14.

## Resolution

- Mitigation: raised connection pool from 50 to 200, restarted pods.
- Long-term fix: in flight (see action items).

## Action items

- [ ] Priya — Add pool-saturation alert at 80% utilization. Due 2026-03-21.
- [ ] payments-team — Capacity review for all DB pools. Due 2026-04-01.
- [ ] Priya — Document pool-tuning runbook. Due 2026-03-28.
- [ ] (unassigned) — Audit other "set and forget" capacity configs.
  No due date yet.

## Lessons learned

The pool size was a static value with no tie to traffic forecasts.
Capacity configs that were sized at launch and never revisited are a
hidden risk. We should periodically audit them against current traffic.

## Services involved

- `checkout-api` — owner: payments-team
- `payments-db` — owner: payments-team

## Related incidents

None known at time of writing.
