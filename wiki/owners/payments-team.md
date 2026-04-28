---
type: owner
name: payments-team
status: draft
owner: payments-team
services: [checkout-api, payments-db]
incidents: [2026-03-14-checkout-latency, 2026-04-02-checkout-latency]
sources:
  - raw/postmortems/2026-03-14-checkout-latency.md
  - raw/postmortems/2026-04-02-checkout-latency.md
  - raw/slack/2026-04-03-sev-classification-debate.md
  - raw/runbooks/checkout-api-oncall-runbook.md
source_hashes:
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
  raw/postmortems/2026-04-02-checkout-latency.md: 66774015e1e78f2ade75b1ad8780470238e71b119280df9c3269b3510e9132e7
  raw/slack/2026-04-03-sev-classification-debate.md: 2855fe19d7e17c6a99fedb72502d231fc0cb96b317eb4d562f860547d431b279
  raw/runbooks/checkout-api-oncall-runbook.md: 92e02ff339d8cd9dc92d54daf6ee787048abda1eae43513d51547cc787a61319
tags: [team]
last_updated: 2026-04-28
---

## Members

Members on file from sources so far:

- Janelle Okonkwo — engineering manager. Owns the
  [[sev-classification]] RFC.
- Marco Diaz — engineer. Held the page and wrote the postmortem
  for [[2026-04-02-checkout-latency]].

Priya Shah, who held the page for
[[2026-03-14-checkout-latency]], is **not** on this team — see
[[sre-team]]. SRE provides on-call coverage horizontally; that
relationship was previously flagged here as unknown and is now
resolved by raw/slack/2026-04-03-sev-classification-debate.md.

Rotation membership beyond the named individuals is otherwise
undocumented.

## Services owned

- [[checkout-api]]
- [[payments-db]]

## Recent incidents

Newest first.

- [[2026-04-02-checkout-latency]] — SEV2, 38 min, 2026-04-02.
- [[2026-03-14-checkout-latency]] — SEV2, 47 min, 2026-03-14.

## Notes

- Owner of the unassigned action item ("Audit other set-and-forget
  capacity configs") in [[2026-03-14-checkout-latency]] is not
  established. Default-assign to `[[payments-team]]` only after
  confirmation.
- The team owns three open action items from
  [[2026-04-02-checkout-latency]] that are all overdue as of
  2026-04-28: 3-second timeout (due 2026-04-12), RFC on the
  contradiction (due 2026-04-15), and runbook update (no due
  date). The RFC slip is what is keeping the
  [[connection-pool-exhaustion]] vs
  [[downstream-slow-call-holds-upstream-resources]] attribution
  open across teams.
- Janelle additionally owns the open RFC on
  [[sev-classification]] (committed to "this week" of
  2026-04-03). Status not yet confirmed in any later source.
