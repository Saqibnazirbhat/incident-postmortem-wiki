---
type: owner
name: sre-team
status: draft
owner: sre-team
services: []
incidents: [2026-03-14-checkout-latency]
sources:
  - raw/slack/2026-04-03-sev-classification-debate.md
  - raw/postmortems/2026-03-14-checkout-latency.md
source_hashes:
  raw/slack/2026-04-03-sev-classification-debate.md: 2855fe19d7e17c6a99fedb72502d231fc0cb96b317eb4d562f860547d431b279
  raw/postmortems/2026-03-14-checkout-latency.md: 036f5decf3f9cb06d5a58223927fd9b5f1a9f2ab618b0d32f2e53a62585aa4d6
tags: [team]
last_updated: 2026-04-28
---

## Members

Horizontal team — distinct from the product teams that own
services. Known members from sources so far:

- Devon Park — SRE lead (per the 2026-04-03 #incidents thread).
- Priya Shah — SRE on-call (held the page for
  [[2026-03-14-checkout-latency]]).

Rotation membership is otherwise undocumented.

## Services owned

None directly. SRE provides on-call coverage and operational
support across product-team services rather than owning services
itself.

## Recent incidents

- [[2026-03-14-checkout-latency]] — SEV2, 47 min. Priya held the
  page on behalf of SRE.

## Notes

- This page resolves an open question previously flagged on
  [[payments-team]] ("whether SRE rotates separately from the
  payments team or sits within it"). Per the 2026-04-03 thread,
  SRE is its own team with its own lead.
- Devon Park has been the strongest voice on
  [[sev-classification]] — both that "majority of users" alone is
  insufficient and that historical SEVs should not be re-graded
  even after the policy lands. Worth tracking SRE's stance on
  classification disputes as more sources land.
- SRE was not on the 2026-04-02 incident response (Marco of
  [[payments-team]] held the page) but engaged afterward in the
  04-03 SEV thread. Whether SRE was paged on 04-02 and declined,
  or simply not paged, is not in the source.
