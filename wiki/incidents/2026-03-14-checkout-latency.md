---
type: incident
name: 2026-03-14 checkout latency spike
date: 2026-03-14
severity: SEV2
duration_minutes: 47
status: draft
owner: payments-team
services: [checkout-api, payments-db]
root_causes: [connection-pool-exhaustion]
sources:
  - raw/postmortems/2026-03-14-checkout-latency.md
  - raw/slack/2026-04-03-sev-classification-debate.md
source_hashes:
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
  raw/slack/2026-04-03-sev-classification-debate.md: 2855fe19d7e17c6a99fedb72502d231fc0cb96b317eb4d562f860547d431b279
tags: [latency, database, capacity, customer-facing]
last_updated: 2026-04-28
---

## Summary

On 2026-03-14 at 14:23 UTC, p99 latency on `[[checkout-api]]` jumped
from 180ms to over 8 seconds. Roughly 12% of checkout requests timed
out over a 47-minute window, with an estimated $48k revenue impact.
Mitigation came from raising the `[[payments-db]]` connection pool
from 50 to 200 and restarting `[[checkout-api]]` pods. Latency
returned to baseline at 15:10 UTC.

## Timeline

- 14:23 — `[[checkout-api]]` p99 latency alert fires in PagerDuty.
- 14:25 — Priya (SRE on-call) acknowledges the page.
- 14:31 — Initial hypothesis: bad deploy. Rolled back deploy
  `checkout-api@8a2f1c`. No improvement.
- 14:48 — Datadog dashboard shows `[[payments-db]]` connection pool
  at 100% saturation for the entire window.
- 14:54 — New hypothesis: connection pool exhaustion. Increased pool
  size from 50 to 200 and restarted `[[checkout-api]]` pods.
- 15:10 — Latency back under 250ms p99. Incident resolved.
- 15:30 — Incident summary posted in #incidents.

## Detection

Detected by an existing PagerDuty alert on `[[checkout-api]]` p99
latency (>1s for 2 minutes). No customer reports came in before
detection.

## Root cause

`[[connection-pool-exhaustion]]` on `[[payments-db]]`. The pool size
of 50 had been unchanged since 2024 while traffic to
`[[checkout-api]]` had grown roughly 3x in that period. Routine
afternoon traffic crossed the saturation threshold for the first
time on 2026-03-14.

## Resolution

- Mitigation: raised `[[payments-db]]` connection pool from 50 to
  200; restarted `[[checkout-api]]` pods.
- Long-term fix: in flight — see action items.

## Action items

- [ ] Priya — Add pool-saturation alert at 80% utilization. Due 2026-03-21.
- [ ] [[payments-team]] — Capacity review for all DB pools. Due 2026-04-01.
- [ ] Priya — Document pool-tuning runbook. Due 2026-03-28.
- [ ] (unassigned) — Audit other "set and forget" capacity configs.
  No due date yet.

## Notes

- Action item #4 (audit set-and-forget capacity configs) has no
  owner and no due date. Source explicitly notes it as systemic, so
  it should not be allowed to drift.
- The first 25 minutes of investigation chased a deploy-rollback
  hypothesis that produced no improvement. Worth comparing against
  future incidents to see whether deploy-rollback is over-favored as
  a first response on this service.
- Source claims "Related incidents: None known at time of writing."
  Re-evaluate as more sources are ingested.

CORRECTION (added 2026-04-27 during ingest of
[[2026-04-02-checkout-latency]]):

- [[2026-04-02-checkout-latency]] reproduced the symptom profile of
  this incident with the larger pool already in place, and traced
  the cause to a slow downstream call to `[[fraud-scoring]]` rather
  than pool sizing. The 03-14 mitigation (pool 50 → 200) was
  necessary but not sufficient against this broader class of
  failure ([[downstream-slow-call-holds-upstream-resources]]).
- The pool-saturation alert that came out of this postmortem (Priya,
  due 2026-03-21, shipped) fired correctly on 04-02 but pointed
  the investigation in the wrong direction for ~20 minutes —
  useful symptom signal, misleading causal signal. Recorded as
  feedback on the scope of this incident's detection action item.
- The 03-14 root-cause attribution stands as written above. The
  04-02 author proposes 03-14 was a degenerate case of a broader
  failure mode; that reframing is contested and tracked as a
  `CONTRADICTION:` block on [[connection-pool-exhaustion]]. Do not
  silently re-attribute 03-14 here pending the RFC (overdue,
  2026-04-15).

SEV CLASSIFICATION (added 2026-04-28 from
raw/slack/2026-04-03-sev-classification-debate.md):

- SEV2 stays. Per the 2026-04-03 #incidents thread, the
  forward-only rule (Janelle Okonkwo + Devon Park) means existing
  SEVs are not retroactively reclassified, even when policy
  changes.
- For reference: this incident's burn rate (~$48k in 47 min ≈
  $61k/hr) would clear the *proposed* (not adopted) SEV1
  threshold of $25k/hr sustained 15+ min. Priya Shah raised this
  in the thread; the answer was forward-only.
- See [[sev-classification]] for the full policy state and open
  RFC.
