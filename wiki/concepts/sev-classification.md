---
type: concept
name: sev-classification
status: draft
owner: payments-team
incidents: [2026-03-14-checkout-latency, 2026-04-02-checkout-latency]
sources:
  - raw/slack/2026-04-03-sev-classification-debate.md
source_hashes:
  raw/slack/2026-04-03-sev-classification-debate.md: 2855fe19d7e17c6a99fedb72502d231fc0cb96b317eb4d562f860547d431b279
tags: [severity, policy]
last_updated: 2026-04-28
---

## Definition

The framework used to grade an incident's severity. Drives paging,
who joins the call, and how the postmortem is written. Two
criteria are operative in the current policy:

1. **User reach** — "majority of users affected" qualifies as
   SEV1.
2. **Critical revenue impact** — added to the doc after the
   original 2023 version. The dollar figure was never specified.

Anything below SEV1 thresholds defaults to SEV2 (or lower).

## Why it recurs

The classification keeps being contested because the policy hasn't
kept pace with revenue scale. The "majority of users" criterion
was the only operative test in 2023; "critical revenue impact" was
later bolted on without a number. As of
[[2026-04-02-checkout-latency]], a 9% user impact with a $48k/hr
burn rate cleanly clears the per-policy SEV2 line — but that same
revenue burn would, by the proposed thresholds (below), be SEV1.
The dispute on 04-03 is the second time in three weeks that
"identical-looking checkout incident" forced the question.

## Detection

Today: filers apply the user-reach test (objective) and the
revenue-impact test (subjective) in parallel. The revenue test is
unenforceable because no dollar figure is defined.

**Proposed (RFC open, owner [[payments-team]] / Janelle Okonkwo,
not yet adopted):**

- SEV1 if **either** ≥$50k absolute revenue impact during the
  incident, **or** ≥$25k/hr burn rate sustained for 15+ minutes.
- Disambiguate "majority of users": simultaneously affected, vs.
  affected at any point during the incident.
- Add a separate **blast radius** dimension (e.g., outage that
  blocks signups too), independent of user count.

These are proposals, not policy. Do not file by them.

## Mitigations

- Open RFC to revise the SEV definitions. Owner: Janelle Okonkwo.
  Status as of 2026-04-28: RFC was promised "this week" of
  2026-04-03; not yet linked from this page. Confirm whether it
  has opened on next ingest.
- 04-02 postmortem to carry a "policy-under-review" note (Marco's
  commitment in the 04-03 thread) — captured on
  [[2026-04-02-checkout-latency]].

## Related

- [[2026-03-14-checkout-latency]] — SEV2; ~$61k/hr burn, would
  clear the proposed SEV1 line.
- [[2026-04-02-checkout-latency]] — SEV2; ~$48k/hr burn, would
  clear the proposed SEV1 line.
- [[payments-team]] — RFC owner.
- [[sre-team]] — pushed back on the under-classification pattern
  in the 04-03 thread.

## Notes

**Forward-only decision (Janelle, 2026-04-03, +1 from Devon Park):**
when the new criteria are adopted, they apply to incidents filed
after that date. Existing SEVs are not retroactively reclassified.
Both [[2026-03-14-checkout-latency]] and
[[2026-04-02-checkout-latency]] stay SEV2 even though both would
qualify as SEV1 under the proposed thresholds. Reason given:
"muddies historical reporting." Recorded so a future reader does
not try to retcon either incident.

Open questions from the 04-03 thread, not yet answered:

- What is the right dollar threshold for SEV1?
- Burn-rate-per-hour vs. absolute-impact — which is the better
  primary criterion?
- How to operationalise "blast radius" as a dimension separate
  from user count?
