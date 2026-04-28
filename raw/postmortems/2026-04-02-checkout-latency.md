# Postmortem: Checkout latency spike — 2026-04-02

**Author:** Marco Diaz (payments-team)
**Date filed:** 2026-04-03
**Severity:** SEV2
**Duration:** 38 minutes (16:40 – 17:18 UTC)
**Customer impact:** ~9% of checkout requests timed out.
Estimated $31k in dropped revenue.

## Summary

On 2026-04-02 at 16:40 UTC, `checkout-api` p99 latency spiked again —
the symptom profile looked nearly identical to the 2026-03-14
incident. After investigation, the actual root cause was traced to
the downstream `fraud-scoring` service, which had deployed a slow
regex-based rule at 16:35 UTC. `checkout-api` calls to
`fraud-scoring` queued for ~11 seconds each, holding `payments-db`
connections open while waiting for the response.

## Timeline (UTC)

- 16:35 — `fraud-scoring` deploys new rule (regex with catastrophic
  backtracking on long inputs).
- 16:40 — `checkout-api` p99 latency alert fires.
- 16:42 — Marco (payments-team) acks the page. Pool-saturation alert
  (added after the 03-14 incident) also firing.
- 16:48 — Connection pool at 100%. Initial assumption: same problem
  as 03-14, raise the pool. Pool was already at 200 from the
  previous fix; raised it to 400. **No improvement.**
- 17:01 — Distributed traces show `checkout-api` → `fraud-scoring`
  calls averaging 11 seconds. Cross-checked deploy log; fraud-scoring
  deployed at 16:35.
- 17:08 — Reverted fraud-scoring deploy.
- 17:18 — `fraud-scoring` p99 back to 80ms; `checkout-api` recovered.

## Detection

Two alerts fired: the original p99 latency alert and the new
pool-saturation alert added after the 2026-03-14 postmortem. Marco
notes the pool-saturation alert was misleading — it pointed the
investigation at the database, not the upstream cause.

## Root cause

`fraud-scoring` deployed a new regex rule at 16:35 with catastrophic
backtracking on long inputs. Calls from `checkout-api` to
`fraud-scoring` blocked for ~11 seconds, holding `payments-db`
connections open and saturating the pool.

**Important:** this is NOT the same root cause as the 2026-03-14
incident, even though the symptoms (pool saturation + checkout
latency) were identical. On 03-14, the pool was the bottleneck
because it was undersized for organic traffic. On 04-02, the pool
would have saturated at any size — the upstream `fraud-scoring`
latency was holding connections open. A bigger pool only delays the
saturation; it doesn't prevent it.

The 03-14 fix (raising pool size) was necessary but not sufficient.
The real failure mode is "downstream slow call holds upstream
resources," which a bigger pool never solves.

## Resolution

- Reverted fraud-scoring deploy.
- Action items below to prevent recurrence on both ends.

## Action items

- [ ] fraud-scoring team — Add ReDoS lint on regex rules in CI.
  Due 2026-04-09.
- [ ] payments-team — Add 3-second timeout on `checkout-api` calls
  to `fraud-scoring`. Due 2026-04-12.
- [ ] payments-team — Open RFC: revisit the 2026-03-14 postmortem.
  Same symptom, different root cause — we need a shared name and
  detection strategy for this whole class of failure. Due 2026-04-15.
- [ ] Marco — Update the pool-saturation runbook to include
  "check downstream call latency" as the first step.

## Lessons learned

Symptom-matching is dangerous when two unrelated root causes produce
the same pattern. The pool-saturation alert added after 2026-03-14
fired correctly but pointed the investigation in the wrong direction
for ~20 minutes.

The deeper lesson: "downstream slow call holds upstream resources"
is the *real* failure mode, and the 03-14 incident was actually a
special case of it (where there was no slow downstream — the pool
was just too small for normal traffic). We currently have no name
for this class of failure, no shared dashboard, and no shared
runbook.

## Services involved

- `checkout-api` — owner: payments-team
- `payments-db` — owner: payments-team
- `fraud-scoring` — owner: trust-and-safety-team

## Related incidents

- 2026-03-14 checkout latency spike — same symptom, different root
  cause. See contradiction discussion above.
