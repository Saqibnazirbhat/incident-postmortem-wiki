---
type: owner
name: trust-and-safety-team
status: draft
owner: trust-and-safety-team
services: [fraud-scoring]
incidents: [2026-04-02-checkout-latency]
sources:
  - raw/postmortems/2026-04-02-checkout-latency.md
source_hashes:
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
tags: [team]
last_updated: 2026-04-27
---

## Members

Not yet documented. The 2026-04-02 postmortem names the team as
owner of `[[fraud-scoring]]` but does not list members or rotation.

## Services owned

- [[fraud-scoring]]

## Recent incidents

- [[2026-04-02-checkout-latency]] — SEV2, 38 min, fraud-scoring
  regex deploy. The team owned the deploy that triggered the
  incident; they did not hold the page (Marco of [[payments-team]]
  did).

## Notes

- The 2026-04-02 action item "Add ReDoS lint on regex rules in CI"
  is attributed to "fraud-scoring team" in the postmortem and
  presumed to fall to this team. Owner is overdue as of 2026-04-27
  (due 2026-04-09) — flag to confirm before re-attributing.
