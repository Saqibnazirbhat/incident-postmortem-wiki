# Incident & Postmortem Wiki

> A self-maintaining knowledge base for ops incidents — pre-processed,
> cross-referenced, and contradiction-aware. The wiki **is** the answer;
> raw sources are inputs to maintenance, not query.

The hard part of an ops knowledge base isn't insight — it's **bookkeeping**.
Cross-references go stale. Postmortems get filed and forgotten. The same
root cause shows up under three different names because nobody noticed the
pattern. Humans abandon wikis because the maintenance cost grows faster
than the value.

This repo flips that: an LLM agent (Claude Code, driven by a strict
[`CLAUDE.md`](./CLAUDE.md) operating manual) does the bookkeeping, the
human curates sources and asks questions. The maintenance cost is near
zero, so the wiki actually stays maintained.

---

## The 30-second pitch

You drop a postmortem into `raw/postmortems/`. The agent reads it,
talks through the takeaways with you, and then:

- writes a structured page for the incident,
- creates pages for any new services, root causes, owners it mentions,
- updates every other page that should know about it (incident history
  on the service, recent incidents on the owner, instance count on the
  root cause),
- refreshes the global index,
- appends a dated entry to a log,
- and runs two lint tools that catch broken cross-references, missing
  frontmatter, stub debt, source drift, and **contradictions across
  sources**.

Every page is just markdown with YAML frontmatter. The whole thing is
plain files you can grep, edit, and commit.

---

## Show, don't tell

This repo ships with a worked example: four real-shaped sources have
been ingested. Two are postmortems for checkout-latency incidents that
look superficially identical — same service, same symptoms, same alert
firing — but were attributed to **different root causes** by different
teams.

A typical RAG-over-postmortems setup will happily answer questions
about either incident in isolation. It won't tell you the two attributions
are in tension. This wiki does, on the page where it matters:

```
## Notes

CONTRADICTION: Root cause attribution differs between two incidents
with identical symptoms.

- 2026-03-14 postmortem (Priya Shah, SRE on-call): blamed connection-pool
  exhaustion on payments-db. Fix: raised pool from 50 to 200.
- 2026-04-02 postmortem (Marco Diaz, payments-team): same symptoms with
  the larger pool. Blamed slow downstream call to fraud-scoring; argued
  the pool exhaustion was a downstream effect, not a root cause.

Both incidents are linked from this page; only 03-14 is in `incidents:`
because 03-14 is the only one *attributed* here. The unifying
explanation is open and explicitly disputed across teams.
```

The lint tool reports it as a warning that stays visible until resolved.
The index has a top-level `## Open contradictions` section that surfaces
it from the front page. The log records when it was first detected and
why.

That is what "the LLM did the bookkeeping" looks like in practice.

---

## How it works — three operations and nothing else

The agent is allowed to do exactly three things without explicit user
approval. This narrowness is the whole point — wikis fail when the
maintainer scope-creeps.

### 1. Ingest

A new file lands in `raw/`. The agent:

- reads it and quotes 3–5 takeaways back to you,
- proposes which pages will be created, updated, stubbed,
- waits for your nod,
- writes the pages, updates the index, appends to the log,
- runs the lint tools and reports the result.

**One source per ingest run.** No chaining. The strict cadence is what
keeps the agent from going off the rails on a long-running session.

### 2. Query

You ask a question. The agent opens `wiki/index.md` first (always),
identifies the 1–3 most relevant pages, follows wiki-links only as
needed, and answers from the wiki — not from a fresh re-read of the
raw sources.

If the wiki has a gap, the answer is "the wiki doesn't cover that —
want me to ingest the relevant source?" rather than improvising from
`raw/`. The wiki is the system of record.

### 3. Lint

You ask for a health check. The agent runs:

```
python tools/lint.py
python tools/check-drift.py
```

and walks you through the findings. **It does not auto-fix.** Reports
only. You decide what to do.

---

## How is this different from RAG?

RAG (Retrieval-Augmented Generation) is the dominant pattern for
"answer questions from a corpus": embed every document, retrieve the
top-k relevant chunks at query time, stuff them into the prompt,
generate. It's great when the corpus is large, queries are unpredictable,
and you don't want to pre-process.

This pattern is the opposite shape:

| | RAG | This wiki |
|---|---|---|
| **When does the thinking happen?** | At query time | At ingest time |
| **Durable artifact** | Vector index (opaque) | Markdown pages (human-readable, greppable) |
| **Cross-document patterns** | Hidden in vector space; must be prompted to find them | Surfaced as first-class pages (root causes, contradictions, owners) |
| **Source drift detection** | Re-embed and hope | SHA-256 hash per source; lint reports mismatches |
| **Status of facts** | Implicit | Explicit: `stub` / `draft` / `reviewed` |
| **Audit trail** | None by default | `wiki/log.md` — every ingest dated and described |
| **Failure mode** | Hallucinate from incomplete chunks | Refuse, point at the gap, offer to ingest |
| **When sources contradict** | First chunk wins, silently | `CONTRADICTION:` block on the contested page; lint warning until resolved |
| **Human override** | Re-embed | Edit the markdown |
| **Stale data** | Sounds confident, is wrong | Frontmatter literally says `last_updated: 2026-04-15` |
| **Best for** | Large, frequently-changing corpora where pre-processing isn't worth it | Small, high-value corpora where cross-references and consistency matter — e.g. postmortems, RFCs, design docs |

The shorter version: **RAG retrieves. This synthesizes.** RAG asks the
model to answer a question by reading chunks. This wiki asks the model
to *write the answer in advance*, in a structured form, with
contradictions surfaced and owners attributed — and then humans (or the
model on a query turn) read the answer.

If your corpus is a million pages and a user might ask anything, use
RAG. If your corpus is fifty postmortems and the questions are "do these
incidents have the same root cause?", "what's still open from the last
SEV2?", "is this service still owned by the team listed in the
runbook?" — then a maintained wiki gives you better answers than any
RAG pipeline, because the cross-cutting work has already been done.

You can also combine them: the wiki is a fantastic *retrieval target*
for a downstream RAG layer, because the pages are denser and more
internally consistent than the raw sources.

---

## Project layout

```
raw/                     # Sources. READ-ONLY. Never edited by the agent.
├── postmortems/         # Markdown postmortems, RCA docs
├── alerts/              # Exported PagerDuty/Datadog/Opsgenie alerts
├── slack/               # Exported #incidents threads
└── runbooks/            # Existing runbooks, oncall docs

wiki/                    # Owned by the agent.
├── index.md             # Catalog of every page. Refreshed every ingest.
├── log.md               # Dated diary of every ingest run. Append-only.
├── incidents/           # One page per incident.        {YYYY-MM-DD-slug}.md
├── services/            # One page per service.         {service-name}.md
├── root-causes/         # One page per recurring cause. {cause-slug}.md
├── concepts/            # One page per term/idea.       {concept-slug}.md
└── owners/              # One page per team/person.     {owner-slug}.md

tools/                   # Stdlib-only Python.
├── lint.py              # Broken links, frontmatter, stub debt, orphans, contradictions
└── check-drift.py       # SHA-256 every source; report or --update on drift

CLAUDE.md                # The agent's operating manual. The actual config.
```

Every page has YAML frontmatter (`type`, `name`, `status`, `owner`,
`sources`, `source_hashes`, `tags`, `last_updated`) plus body sections
defined per page type. Cross-links use Obsidian wiki-link syntax
(`[[page-name]]`) so the whole tree opens cleanly in
[Obsidian](https://obsidian.md) or any wiki viewer.

---

## The tools

Both tools are stdlib-only Python. No `pip install`. They run from the
repo root.

### `tools/lint.py`

Checks:

- broken `[[wiki-links]]` (target page does not exist)
- missing required frontmatter fields
- basename collisions across the whole `wiki/` tree (because wiki-links
  resolve by basename)
- stub debt — pages marked `status: stub` older than `--stub-days`
  (default 30)
- orphans — pages not referenced from `wiki/index.md`
- unresolved `CONTRADICTION:` blocks (warnings, not errors — they
  should stay visible)

Exit code 1 on errors, 0 on warnings-only. CI-friendly.

### `tools/check-drift.py`

For every page that lists `source_hashes:` in its frontmatter:

- compute the SHA-256 of each referenced source file in `raw/`,
- report missing files, hash mismatches, and "recorded but no longer
  referenced" entries.

`--update` rewrites the `source_hashes:` block in place with the
current hashes. Use after every ingest.

---

## Quickstart

You need Python 3.8+ and [Claude Code](https://github.com/anthropics/claude-code).

```bash
# 1. Clone and open in Claude Code
git clone <this repo>
cd incident-postmortem-wiki
claude

# 2. Drop a source into raw/
cp ~/some-postmortem.md raw/postmortems/

# 3. Ask Claude to ingest it
> Ingest raw/postmortems/some-postmortem.md

# 4. Ask Claude a question
> What do we know about checkout latency incidents?

# 5. Run the lint tools
python tools/lint.py
python tools/check-drift.py
```

The agent reads `CLAUDE.md` automatically — that's the file that
defines what "ingest", "query", and "lint" mean in this repo.

---

## What's already in this demo

Four sources are pre-ingested so the wiki has a worked example to
explore:

- `raw/postmortems/2026-03-14-checkout-latency.md` — SEV2 incident,
  attributed to connection-pool exhaustion.
- `raw/postmortems/2026-04-02-checkout-latency.md` — SEV2 incident
  with **identical symptoms** but a different root cause. The agent
  surfaces this as a `CONTRADICTION:`.
- `raw/slack/2026-04-03-sev-classification-debate.md` — meta-source.
  The agent recognises this is policy debate, not an incident, and
  lands it as a concept page.
- `raw/runbooks/checkout-api-oncall-runbook.md` — high-authority
  operational source. Triggers the first `reviewed` page in the wiki,
  promotes a stub, surfaces four new service stubs (because the
  runbook lists dependencies the wiki didn't know about), and closes
  an open action item.

Open `wiki/index.md` and follow the wiki-links to see how it all hangs
together. Open `wiki/log.md` to see the agent's working diary.

---

## Why this works

The pattern this repo implements is essentially:

> Give an LLM agent a strict, file-based operating manual. Constrain its
> scope to a few well-defined operations. Let it do the boring,
> high-leverage maintenance work humans skip.

That's it. The interesting bits aren't in any of the Python — they're
in [`CLAUDE.md`](./CLAUDE.md):

- exact step-by-step workflows for ingest / query / lint,
- exact page templates with required frontmatter,
- explicit rules about what the agent does **not** do
  (`raw/` is read-only; no auto-fix; one source per run; never
  silently overwrite contradictions),
- the tone for how the agent behaves on judgment calls.

The Python tools just enforce mechanical invariants the agent might
otherwise skip. The agent does the writing; the tools verify the
writing is consistent.

If you're building anything LLM-driven that needs to maintain state
across long-running work — a runbook, a research notebook, a project
journal, a code review queue — the pattern transfers cleanly. Replace
the section headers in `CLAUDE.md` and you have a different application
of the same shape.

---

## License

MIT

---

Built as a worked example of using [Claude Code](https://github.com/anthropics/claude-code)
to maintain durable, structured knowledge from streaming inputs.
