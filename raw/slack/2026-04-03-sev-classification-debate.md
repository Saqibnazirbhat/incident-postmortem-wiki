# #incidents Slack thread — SEV classification debate

**Channel:** #incidents
**Date:** 2026-04-03 (day after the 04-02 checkout incident)
**Participants:** Marco Diaz (payments-team), Priya Shah (SRE),
Janelle Okonkwo (engineering manager, payments), Devon Park (SRE lead)

---

**Marco Diaz** — 09:14
Filing yesterday's checkout incident as SEV2. 38 minutes,
~9% of checkouts timed out, ~$31k impact. Postmortem coming today.

**Priya Shah** — 09:18
Honest question — should this have been a SEV1? We had real
revenue impact and the symptom was identical to 03-14, which we
also called SEV2. I'm starting to think we're under-classifying.

**Marco Diaz** — 09:21
Our SEV1 threshold is "majority of users affected." 9% isn't
majority. And we recovered in under an hour. Textbook SEV2.

**Priya Shah** — 09:24
Right but our docs also say "SEV1 = critical revenue impact." $31k
in 38 minutes is a $48k/hr burn rate. If it had taken us 3 hours
to find the fraud-scoring deploy, we'd be at six figures. The fact
that we got lucky on detection time shouldn't determine the SEV.

**Devon Park** — 09:32
Jumping in — Priya has a point. The classification doc was written
in 2023 when we had a smaller revenue base. "Majority of users" was
the only operative criterion at the time. The "critical revenue
impact" line was added later and we never defined the dollar figure.

**Janelle Okonkwo** — 09:40
Two separate issues here. (1) Was 04-02 correctly classified per
current docs? Yes — Marco called it right per the letter of the
policy. (2) Is the policy itself broken? Probably yes.

For now: 04-02 stays SEV2. Don't retcon. But I'm opening an RFC
this week to revise the SEV definitions, specifically:
- Add a dollar threshold for SEV1 ($50k revenue impact, or
  $25k/hr burn rate sustained for 15+ min)
- Clarify "majority of users" — does that mean simultaneously
  affected, or affected at any point during the incident?
- Add a "blast radius" criterion separate from user count

**Marco Diaz** — 09:43
Agree with all that. Want me to add a note on the postmortem that
the SEV classification was per-policy correct but the policy is
under review?

**Janelle Okonkwo** — 09:44
Yes please.

**Priya Shah** — 09:46
One more thing — the 03-14 incident is also worth re-examining
under whatever new definitions we land on. Same revenue burn rate
roughly ($48k in 47 min ≈ $61k/hr), arguably worse impact than
04-02. If $50k/hr is the SEV1 line, both were SEV1 by the proposed
definition.

**Devon Park** — 09:51
Let's not retcon old SEVs even after the policy lands. It muddies
historical reporting. New policy applies forward only.

**Janelle Okonkwo** — 09:52
+1, agreed. Forward-only.

**Marco Diaz** — 09:53
👍 Will note this thread in the 04-02 postmortem and link the RFC
once it's open.

---

## Decision summary (Janelle, end of thread)

- 04-02 stays SEV2. Classification was per-policy correct.
- 03-14 stays SEV2. Same reason.
- RFC opening this week to revise SEV criteria. Owner: Janelle.
- New criteria, when adopted, apply forward only — no retroactive
  reclassification.
- 04-02 postmortem to note the policy-under-review caveat.

## Open questions

- What's the right dollar threshold for SEV1?
- Is burn-rate-per-hour or absolute-impact the better criterion?
- How do we handle "blast radius" (e.g., did the outage block
  signups too?) as a separate dimension from user count?
