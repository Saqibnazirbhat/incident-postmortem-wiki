---
type: incident
name: 2026-04-02 checkout latency spike
date: 2026-04-02
severity: SEV2
duration_minutes: 38
status: draft
owner: payments-team
services: [checkout-api, payments-db, fraud-scoring]
root_causes: [downstream-slow-call-holds-upstream-resources]
sources:
  - raw/postmortems/2026-04-02-checkout-latency.md
  - raw/slack/2026-04-03-sev-classification-debate.md
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
  raw/slack/2026-04-03-sev-classification-debate.md: 2855fe19d7e17c6a99fedb72502d231fc0cb96b317eb4d562f860547d431b279
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: [latency, regex, deploy-induced, customer-facing]
last_updated: 2026-04-28
---

## Summary

On 2026-04-02 at 16:40 UTC, `[[checkout-api]]` p99 latency spiked
with a symptom profile nearly identical to
[[2026-03-14-checkout-latency]]. The actual cause was upstream: the
`[[fraud-scoring]]` service had deployed a regex rule at 16:35 UTC
with catastrophic backtracking. `[[checkout-api]]` calls to
`[[fraud-scoring]]` blocked ~11s each, holding `[[payments-db]]`
connections open and saturating the pool. ~9% of checkouts timed
out over 38 minutes; ~$31k revenue impact.

## Timeline

- 16:35 — `[[fraud-scoring]]` deploys new regex rule (catastrophic
  backtracking on long inputs).
- 16:40 — `[[checkout-api]]` p99 latency alert fires.
- 16:42 — Marco ([[payments-team]]) acks. Pool-saturation alert
  (action item from [[2026-03-14-checkout-latency]]) also firing.
- 16:48 — Pool at 100%. Initial assumption mirrored 03-14: raise the
  pool. Pool was already at 200; raised to 400. No improvement.
- 17:01 — Distributed traces show `[[checkout-api]] →
  [[fraud-scoring]]` calls averaging 11s. Deploy log shows
  fraud-scoring deployed at 16:35.
- 17:08 — Reverted fraud-scoring deploy.
- 17:18 — `[[fraud-scoring]]` p99 back to 80ms; `[[checkout-api]]`
  recovered.

## Detection

Two alerts fired: the existing p99 latency alert on
`[[checkout-api]]` and the new pool-saturation alert added after
[[2026-03-14-checkout-latency]]. The pool-saturation alert pointed
investigation at `[[payments-db]]` for ~20 minutes when the real
problem was upstream — useful symptom signal, misleading causal
signal.

## Root cause

[[downstream-slow-call-holds-upstream-resources]]. A regex with
catastrophic backtracking deployed to `[[fraud-scoring]]` made
upstream calls block ~11s, holding `[[payments-db]]` connections
open and saturating the pool.

The author explicitly contrasts this with
[[2026-03-14-checkout-latency]]: same symptoms (pool saturation +
checkout latency), different mechanism. On 03-14 the pool was
undersized for organic traffic; on 04-02 the pool would have
saturated at any size. See the `CONTRADICTION:` block on
[[connection-pool-exhaustion]].

## Resolution

- Reverted the `[[fraud-scoring]]` deploy.
- Long-term fixes in flight (see action items).

## Action items

- [ ] fraud-scoring team — Add ReDoS lint on regex rules in CI.
  Due 2026-04-09. **Overdue as of 2026-04-27.**
- [ ] [[payments-team]] — Add 3-second timeout on `[[checkout-api]]`
  calls to `[[fraud-scoring]]`. Due 2026-04-12. **Overdue.**
- [ ] [[payments-team]] — Open RFC: revisit
  [[2026-03-14-checkout-latency]]. Same symptom, different root
  cause — we need a shared name and detection strategy for this
  whole class of failure. Due 2026-04-15. **Overdue.**
- [x] ~~Marco — Update the pool-saturation runbook to include
  "check downstream call latency" as the first step. No due
  date.~~ Closed 2026-04-15: see
  `raw/runbooks/checkout-api-oncall-runbook.md`. The runbook was
  rewritten to put "check `checkout-api → fraud-scoring` p99
  first" as step 2 of the decision tree, before any pool check.

## Notes

- All three dated action items are overdue as of 2026-04-28
  (13–19 days past). The RFC item (2026-04-15) is the very
  mechanism the postmortem proposed for resolving the 03-14 vs
  04-02 attribution conflict; its slip is what keeps the
  contradiction open. Flagged on [[connection-pool-exhaustion]]
  and in `wiki/log.md`. Marco's runbook item — the only
  undated one — is closed; see action items above.
- The pool-saturation alert (a 03-14 follow-up that was completed
  and shipped) actively misled this investigation. Worth recording
  as feedback on how 03-14's detection action items were scoped —
  see corrective Notes on [[2026-03-14-checkout-latency]].
- "fraud-scoring team" on the ReDoS-lint action item is presumed to
  be [[trust-and-safety-team]] (the only known owner of
  `[[fraud-scoring]]`), but the postmortem doesn't spell it out.
  Confirm before reassigning.

SEV CLASSIFICATION (added 2026-04-28 from
raw/slack/2026-04-03-sev-classification-debate.md):

- SEV2 was per-policy correct at filing — Marco called it right
  per the letter of the current `[[sev-classification]]` policy.
- The policy itself is under review. Janelle Okonkwo opened the
  question in the 04-03 #incidents thread and committed to an
  RFC. ~$48k/hr burn rate during this incident clears the
  *proposed* (not adopted) SEV1 threshold of $25k/hr sustained
  15+ min.
- The forward-only rule (Janelle + Devon Park, 2026-04-03)
  applies: even if the proposed thresholds are adopted, this
  incident stays SEV2. Do not retcon.
