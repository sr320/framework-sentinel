# Framework Sentinel

**A living scorecard of incoming literature in marine invertebrate environmental epigenetics, scored against ten unresolved questions.**

📊 **[View the dashboard →](https://sr320.github.io/framework-sentinel/)**

---

## What this is

Most literature alerts answer "what came out this week?" This one answers a harder
question: **does this paper move us?**

A scheduled pipeline sweeps a trailing 30-day window each week, screens the hits for
scope, and scores each in-scope paper against the ten unresolved questions in Section 5
of the Roberts Lab conceptual framework — not summarizing the paper, but recording what
it does to a specific open question, and why.

Each question carries a **staleness indicator**: days since any paper was last scored
against it. A question nobody has touched in months isn't necessarily solved — it may
just be hard to address with current methods. Either way, that is a signal about where
the lab's own next experiment would buy the most.

## How to read it

Every paper matched to a question gets exactly one verdict **per question it touches**
(a paper can be `Confirms` on Q9 and `Complicates` on Q1 in the same entry):

| Verdict | Meaning |
|---|---|
| **Confirms** | Supports the framework's current position, or supplies the first direct empirical evidence for a claim it holds as plausible-but-untested. |
| **Complicates** | Introduces a nuance, boundary condition, exception, or conflicting result. Not a negative label — these are the hits the dashboard exists to surface. |
| **Closes** | Substantially resolves the question, such that its "unresolved" framing should be revisited. Expected to be rare. |
| **Extends** | Applies an already-answered mechanism to a new taxon, stressor, or context without changing the answer. |
| **Irrelevant** | Doesn't bear on any of the ten questions. Screened out, but counted in the sweep log so the screening is auditable. |

Full criteria, scope definition, and the staleness rule: **[docs/RUBRIC.md](docs/RUBRIC.md)**.

## Honest limitations

This is a **screening and triage tool, not a citation-ready literature review.**

- **Verdicts are judgments from abstracts**, usually without the full text.
- **Preprints are included** and are not peer reviewed.
- **bioRxiv coverage is approximate.** Its API has no keyword search, so the sweep
  browses by date + category and filters client-side, and the per-page result cap means
  coverage skews toward the start of each window. Treat bioRxiv hits as a bonus signal,
  not a completeness guarantee.
- **The retraction/correction check is not always available.** Scored papers are checked
  against Scite for retractions, corrections, and expressions of concern before being
  added, but when that lookup fails the record says so on its own card and in the JSON.
  Every entry carries a categorical **`editorial_status`** — `checked`, `unavailable`, or
  `not_applicable` (a bioRxiv preprint, where no editorial notice can exist) — alongside
  the prose `editorial_notice`. The dashboard counts and flags off the categorical field,
  so the "unverified" figure can't drift as the prose is reworded.
- **Papers authored by this lab are flagged as such.** They are scored normally, but
  in-house work cannot count as independent corroboration of the lab's own framework.

Verify any finding against the full text before using it in a manuscript or grant.

## Repository layout

```
.
├── index.html                     # the dashboard — GENERATED, do not hand-edit
├── data/
│   └── sentinel_log.json          # append-only log: every sweep, every scored paper
├── docs/
│   ├── RUBRIC.md                  # the ten questions, verdict taxonomy, scope, staleness
│   └── sweep_keywords.md          # exact queries per source + accumulated tuning notes
├── scripts/
│   ├── build_dashboard.py         # sentinel_log.json + template -> index.html
│   ├── validate_log.py            # schema + self-consistency check on the log
│   ├── dashboard_template.html    # layout/styling/JS — edit this, not index.html
│   └── verify.js                  # optional Playwright render check
├── CHANGELOG.md                   # narrative history of what each sweep found
└── .github/workflows/pages.yml    # rebuilds and deploys the dashboard on push
```

## Rebuilding the dashboard

```bash
python3 scripts/build_dashboard.py
```

No dependencies beyond the Python standard library. The script validates
`data/sentinel_log.json`, aggregates entries per question, computes staleness as of
today, and writes `index.html`. A log that fails validation **aborts the build** rather
than publishing a broken page; run the check on its own with:

```bash
python3 scripts/validate_log.py
```

It enforces the fields the build indexes into, unique ids, `supersedes` targets that
exist and don't form cycles, verdicts drawn from the four the dashboard has a colour
for, `editorial_status` agreeing with its prose, and each sweep's declared
`papers_scored` / `papers_annotated_updates` matching the records that actually carry
that sweep date.

GitHub Actions runs the same command on every push to `main` and deploys the result to
GitHub Pages, so **updating `data/sentinel_log.json` is enough to refresh the site** —
the committed `index.html` is a convenience copy and a fallback. Because staleness is
computed at build time, the workflow also rebuilds on a weekly schedule, so the "days
since" figures can't quietly go stale in a week with no pushes.

One-time repo setup: **Settings → Pages → Source = "GitHub Actions"**.

Optional render check (needs Playwright):

```bash
NODE_PATH=$(npm root -g) node scripts/verify.js
```

Set `PW_CHROMIUM` to a Chromium binary if Playwright's own download isn't present.

## The append-only rule

`data/sentinel_log.json` is append-only. A prior sweep's records are never deleted or
silently edited. When a paper needs a correction — a deferred retraction check comes
back, a DOI finally resolves — the fix is added as a new annotated entry beside the
original, not written over it.

The new record carries **`supersedes`**, naming the id of the record it updates:

```json
{ "id": "Thyrring_2026_update", "supersedes": "Thyrring_2026", ... }
```

That one field is what keeps append-only from turning into double-counting. A
supersedes-chain describes **one paper**, so the build collapses it for every number on
the page: papers scored, verdict split, cross-domain flags, and the editorial-check gap
each count the chain once, and the editorial status is read off the newest record (a
deferred check that a later sweep completed is resolved, not outstanding).

Staleness is the case that matters most. It answers "when did the literature last say
anything about this question?", so each paper contributes **the sweep that first scored
it** against that question. Without that rule a sweep containing nothing but re-checks
of old papers would flip every question it touched back to a green "Active" badge, with
no new science behind it.

The cost is still visible on the dashboard: a re-checked paper shows two cards under the
same question. That's deliberate — but the second card is now marked *re-check · not a
new finding* and doesn't move any count. A scorecard that quietly rewrites its own
history isn't worth trusting, and the duplicate is a cheap price for an auditable record.

`insufficient_info` items use the same `supersedes` convention, but the dashboard shows
only the latest state of each item, annotated with how many sweeps have carried it.

## Data sources

| Source | Role |
|---|---|
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/) | Keyword search over the trailing window |
| [Consensus](https://consensus.app/) | Semantic search, catches papers the keyword query misses |
| [bioRxiv](https://www.biorxiv.org/) | Date + category browse, keyword-filtered client-side |
| [Scite](https://scite.ai/) | Retraction / correction / expression-of-concern checks |

Known source quirks (Consensus surfacing old preprints under a recent revision date,
PubMed print-issue reassignment putting months-old papers in a current window) are
documented with examples in [docs/sweep_keywords.md](docs/sweep_keywords.md), which
doubles as the pipeline's accumulated tuning notes.

## License

Code (`scripts/`) is MIT — see [LICENSE](LICENSE).

The sweep log, rubric, and scoring commentary (`data/`, `docs/`, `CHANGELOG.md`) are
released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): reuse freely
with attribution. Paper titles, abstracts, and DOIs belong to their respective
publishers and are referenced here under normal academic citation practice.

---

Maintained by the [Roberts Lab](https://robertslab.github.io/), School of Aquatic and
Fishery Sciences, University of Washington.
