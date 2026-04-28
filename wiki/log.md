# Ingest Log

## 2026-04-28 — ingested raw/runbooks/checkout-api-oncall-runbook.md

Source: on-call runbook for `checkout-api`, last reviewed
2026-04-15 (post 04-02 incident updates). First high-authority
operational source ingested. Owner: payments-team.

Pages created:
- wiki/services/user-service.md (stub)
- wiki/services/inventory-api.md (stub) — flagged: 2025-09-08
  unavailability incident referenced in runbook is not ingested.
- wiki/services/orders-mart.md (stub)
- wiki/services/fulfillment-service.md (stub)

Pages promoted:
- wiki/services/checkout-api.md — `draft` → `reviewed`. First
  reviewed page in the wiki. Full rewrite: complete dependency
  graph, four failure modes (two new from runbook: bad-deploy
  anti-pattern and inventory-api unavailability), dashboards,
  escalation chain, decision-tree summary in prose.
  Now sourced for the `tier-1` tag.
- wiki/services/payments-db.md — `stub` → `draft`. Full Purpose,
  pool history (50 → 200 → 400), incident history, dashboard
  reference.

Pages updated:
- wiki/services/fraud-scoring.md — stays stub but enriched with
  the 2025-Q3 onboarding date and a clearer link to the open
  ReDoS-lint action item.
- wiki/incidents/2026-04-02-checkout-latency.md — Marco's
  runbook action item (the only undated one) marked closed,
  struck through; runbook added to sources; date arithmetic on
  overdue items rolled forward to 2026-04-28.
- wiki/owners/payments-team.md — runbook added to sources.
- wiki/index.md — Services 3 → 7; Stubs to flesh out 2 → 5
  (payments-db left the stub list, four new stubs joined).

Contradictions surfaced: none. The runbook reinforces the 04-02
framing and explicitly preserves the historical reasoning ("if
you find yourself updating this runbook after an incident,
preserve the old version"). Existing
[[connection-pool-exhaustion]] vs
[[downstream-slow-call-holds-upstream-resources]] contradiction
unaffected.

Action items closed:
- Marco — Update the pool-saturation runbook to include "check
  downstream call latency" as the first step. Closed 2026-04-15
  per the runbook's own Notes section. The rewrite reordered the
  decision tree to put `checkout-api → fraud-scoring` p99 ahead
  of the pool check.

Open questions:
- The 2025-09-08 inventory-api unavailability incident is
  referenced in the runbook but not ingested. Need the
  postmortem from inventory-api's team. Tracked on
  [[inventory-api]].
- Owners of `[[user-service]]`, `[[inventory-api]]`,
  `[[orders-mart]]`, and `[[fulfillment-service]]` are
  undocumented in any source so far.
- `checkout.skip-inventory` feature flag is referenced from the
  runbook; config docs are not ingested. Capture on next
  config-doc ingest.
- Three 04-02 action items remain open and overdue (ReDoS lint,
  3-second timeout, RFC). The 3-second timeout being open is
  what keeps failure mode #2 latent on `[[checkout-api]]`.

## 2026-04-28 — ingested raw/slack/2026-04-03-sev-classification-debate.md

Source: #incidents Slack thread (2026-04-03), four participants —
Marco Diaz (payments-team), Priya Shah (sre-team), Janelle Okonkwo
(payments engineering manager), Devon Park (sre-team lead). Meta
discussion, not an incident report.

Pages created:
- wiki/concepts/sev-classification.md (draft) — first concept page.
  Captures current policy, the dispute, the proposed thresholds
  (clearly marked as proposed not adopted), and the forward-only
  rule.
- wiki/owners/sre-team.md (draft) — establishes SRE as a separate
  horizontal team with Devon Park (lead) and Priya Shah (on-call).

Pages updated:
- wiki/incidents/2026-04-02-checkout-latency.md — appended SEV
  CLASSIFICATION block. SEV2 stays; policy under review per
  [[sev-classification]]; would clear proposed SEV1 line; forward-
  only rule prevents reclassification. Slack source added to
  sources list.
- wiki/incidents/2026-03-14-checkout-latency.md — appended same
  block. SEV2 stays for the same forward-only reason. Burn-rate
  arithmetic (~$61k/hr) noted for reference.
- wiki/owners/payments-team.md — added Janelle Okonkwo as
  engineering manager and RFC owner. Resolved a previously open
  flag: SRE is its own team ([[sre-team]]), not nested in
  payments. Slack source added.
- wiki/index.md — counts to 2/3/2/1/3/2/1; added concepts and SRE
  owner sections.

Contradictions surfaced: none new. The existing
[[connection-pool-exhaustion]] vs
[[downstream-slow-call-holds-upstream-resources]] contradiction is
unaffected by this ingest (different question — root cause vs.
classification).

Open questions:
- Janelle's RFC was committed to "this week" of 2026-04-03; no
  later source confirms it has opened, was discussed, or is
  blocked. Status check on next ingest.
- Three open questions from the 04-03 thread are unanswered: the
  right dollar threshold for SEV1, burn-rate vs. absolute-impact,
  and how to operationalise blast radius. Tracked on
  [[sev-classification]].
- Whether SRE was paged on 2026-04-02 (and declined, or simply
  was not paged) is not in the source. They engaged afterward in
  the SEV thread but were absent from the response itself.
- Devon Park's stance — "majority of users" alone is insufficient,
  but historical SEVs should not be re-graded — is the SRE
  position so far. Worth tracking against future classification
  disputes.

## 2026-04-27 — ingested raw/postmortems/2026-04-02-checkout-latency.md

Source: 2026-04-02 checkout latency postmortem (SEV2, 38 min, by
Marco Diaz of payments-team).

Pages created:
- wiki/incidents/2026-04-02-checkout-latency.md (draft)
- wiki/root-causes/downstream-slow-call-holds-upstream-resources.md (draft)
- wiki/services/fraud-scoring.md (stub)
- wiki/owners/trust-and-safety-team.md (draft)

Pages updated:
- wiki/root-causes/connection-pool-exhaustion.md — added
  CONTRADICTION block; removed `recurring` tag pending RFC; updated
  Detection section to reflect that the pool-saturation alert
  misled the 04-02 investigation.
- wiki/incidents/2026-03-14-checkout-latency.md — appended
  CORRECTION block. The 03-14 attribution stands; the 04-02 author
  proposes 03-14 was a degenerate case of a broader failure mode,
  recorded but not adopted.
- wiki/services/checkout-api.md — added 04-02 to incidents and
  fraud-scoring as upstream; second known failure mode added.
- wiki/services/payments-db.md — stub updated with the 04-02 pool
  raise (200 → 400, no effect).
- wiki/owners/payments-team.md — added 04-02; flagged three overdue
  action items.
- wiki/index.md — counts and listings.

**Contradictions surfaced: 1** (the central event of this ingest).
The 03-14 postmortem (SRE) attributes the failure to connection-pool
exhaustion. The 04-02 postmortem (payments-team) attributes the same
symptoms to a different mechanism — slow downstream call to
fraud-scoring — and explicitly argues 03-14 was a special case of
the same broader failure
([[downstream-slow-call-holds-upstream-resources]]). Recorded as a
CONTRADICTION block on [[connection-pool-exhaustion]]. Both
incidents are linked from that page; only 03-14 is in its
`incidents:` list, because only 03-14 is *attributed* to it. The
04-02 author's unifying claim is contested across teams and the RFC
that was supposed to resolve it (action item due 2026-04-15) is
overdue as of 2026-04-27.

Open questions:
- Three action items on [[2026-04-02-checkout-latency]] are overdue
  by 12–18 days: ReDoS lint (fraud-scoring team, due 2026-04-09),
  3-second timeout on checkout-api → fraud-scoring (payments-team,
  due 2026-04-12), and the cross-team RFC (payments-team, due
  2026-04-15). The runbook-update item (Marco) has no due date.
- The pool-saturation alert added by the 03-14 postmortem fired
  correctly on 04-02 but pointed investigation in the wrong
  direction for ~20 minutes. Recorded as feedback on the scope of
  03-14's detection action item; no auto-fix.
- "fraud-scoring team" on the ReDoS-lint action item is presumed to
  be [[trust-and-safety-team]] but the postmortem doesn't spell it
  out. Confirm before re-attributing.
- [[trust-and-safety-team]] members and rotation are still
  undocumented.

## 2026-04-27 — ingested raw/postmortems/2026-03-14-checkout-latency.md

Source: 2026-03-14 checkout latency postmortem (SEV2, 47 min, by Priya Shah).

Pages created:
- wiki/incidents/2026-03-14-checkout-latency.md (draft)
- wiki/services/checkout-api.md (draft)
- wiki/services/payments-db.md (stub)
- wiki/root-causes/connection-pool-exhaustion.md (draft)
- wiki/owners/payments-team.md (draft)

Pages updated: wiki/index.md.

Contradictions surfaced: none.

Open questions:
- Action item #4 in the postmortem ("audit other set-and-forget
  capacity configs") has no owner and no due date — flagged on the
  incident page and on [[payments-team]].
- Source claims "no related incidents known"; revisit once more
  postmortems are ingested.
- payments-team membership and SRE rotation relationship are
  undocumented; flagged for the next oncall-rotation source.
- The systemic "set-and-forget capacity" lesson may deserve its own
  concept page if a second incident validates the pattern; for now
  it lives in the [[connection-pool-exhaustion]] notes.
