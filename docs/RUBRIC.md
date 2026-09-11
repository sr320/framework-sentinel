# Framework Sentinel — scoring rubric

Framework Sentinel scores incoming literature against the Roberts Lab's
conceptual framework (`02_lab_conceptual_framework.md`), specifically the ten
unresolved questions in its Section 5. The point is not to summarize papers —
it's to answer, for each one, **"does this move us?"**

## The ten questions (verbatim from the framework, Section 5)

| ID | Question | One-line gloss |
|----|----------|-----------------|
| Q1 | Persistence and decay of marks | What governs whether an induced epigenetic state washes out, persists, or assimilates, and on what timescale? |
| Q2 | Soma-to-germline transmission | How is parental experience translated into the gamete in marine invertebrates? |
| Q3 | Causal direction | When methylation, transcription, and phenotype co-vary, which causes which? |
| Q4 | F0–F1 methylation rebound | Why do parental and offspring methylation responses sometimes invert? |
| Q5 | ncRNA functional validation | Are inferred cis-regulatory effects of lncRNAs on neighboring genes real, and at what magnitude? |
| Q6 | Channel integration | Are methylation- and ncRNA-mediated memory independent, redundant, or hierarchical? |
| Q7 | Energetic cost of plasticity | What is the metabolic burden of maintaining high-turnover methylation states? |
| Q8 | Mismatch threshold | At what rate of environmental change does anticipatory memory tip from adaptive to maladaptive? |
| Q9 | Cross-taxa generality | Does the plasticity-frontloading trade-off generalize across taxa (corals, bivalves, etc.)? |
| Q10 | Held-out predictive performance | Can molecular signatures trained on one cohort forecast performance in an independent cohort under novel conditions? |

A paper can touch more than one question. A paper that touches none of them
is screened out as **Irrelevant** and does not appear on the dashboard (but is
logged, so the screening is auditable).

## Verdict taxonomy

Every paper matched to at least one question gets exactly one verdict **per
question it touches** (a paper can be `Confirms` on Q9 and `Complicates` on Q1
in the same entry):

- **Confirms** — supports the framework's existing position on this question,
  or provides the first/additional direct empirical evidence for a claim the
  framework currently holds as plausible-but-untested (most valuable on Q10,
  where the framework explicitly says no held-out test yet exists).
- **Complicates** — introduces a nuance, boundary condition, exception, or
  a result that conflicts with the framework's current framing. This is not a
  negative label — a paper that shows the framework's assumption fails in a
  new context is exactly the kind of hit this dashboard exists to surface.
- **Closes** — substantially resolves the question, such that the framework's
  "unresolved" framing should be revisited. Expect this to be rare; flag it
  prominently when it happens.
- **Extends** — applies an existing, already-answered mechanism to a new
  taxon, stressor, or context without changing the answer to the question
  itself (e.g., a ninth bivalve species showing the already-established
  gbM-noise-suppression pattern). Useful for Q9 (cross-taxa generality)
  specifically; elsewhere, mostly a lower-priority note.
- **Irrelevant** — doesn't bear on any of the ten questions. Screened out,
  not shown on the dashboard body, but kept in the sweep log.

## What counts as in-scope literature

Same taxonomic and conceptual scope as the framework itself: marine or
estuarine invertebrates (bivalves, corals/cnidarians, echinoderms, gastropods,
crustaceans, polychaetes), and the five mechanistic channels in Section 2
(gene body methylation, regulatory ncRNAs, gene expression baselines/reaction
norms, chromatin/histone modification, genome-methylation reciprocal
coupling). Vertebrate or plant epigenetic-memory papers are in scope ONLY if
they report a method, mechanism, or finding directly transferable to a
framework question (e.g., a new causal-perturbation method for testing Q3) —
tag these `cross-domain relevance` in notes rather than scoring them as if
they were marine-invertebrate data.

## Staleness

Each question on the dashboard carries a **staleness indicator**: days since
the last paper was **first** scored against it (any verdict). "First" is load-
bearing: because the log is append-only, a paper re-checked in a later sweep
appears again as a record carrying `supersedes`, and that record must not reset
the clock — otherwise a sweep that found no new literature at all could turn
every question it re-touched green. Staleness measures what the literature has
said, not what the bookkeeping has done. A question with no hit in
90+ days is not itself bad news — it may mean the question is simply hard to
address with current methods — but it is a signal for whether the lab's own
next experiment might be the fastest way to move that question, rather than
waiting on the literature.

## Source coverage and known gaps

Each weekly sweep queries:
- **PubMed** — keyword search, trailing window, sorted by relevance then date.
- **Consensus** — semantic search, trailing window via year/month filters.
- **bioRxiv** — date + category browse (the API has no keyword search), then
  client-side title/abstract filtering against a marine-invertebrate keyword
  list. This means bioRxiv coverage is necessarily approximate — a paper whose
  title doesn't surface an obvious keyword can be missed. Treat bioRxiv hits
  as a bonus signal, not a completeness guarantee.
- **Scite** — every paper that scores against a question is checked for
  retractions/corrections/expressions of concern before being added to the
  dashboard.

Elicit was evaluated as a fifth source (its systematic-review pipeline would
suit this task well) but requires a Pro-tier API plan not available at build
time — worth revisiting if that changes.

## Dashboard update procedure (what the weekly run actually does)

1. Sweep PubMed + Consensus + bioRxiv for the trailing window (default 30
   days) using the keyword sets in `sweep_keywords.md`.
2. Screen each hit against the inclusion scope above.
3. Score each in-scope hit against the ten questions using this rubric.
4. Check Scite for editorial notices on each paper that will appear on the
   dashboard.
5. Merge new hits into `sentinel_log.json` (append-only — never delete a
   prior week's entries; a paper can be re-scored if a correction is issued,
   but the record of the original scoring stays, annotated). A record that
   updates an earlier one MUST carry `supersedes: "<earlier id>"`, and every
   entry MUST carry `editorial_status` (`checked` / `unavailable` /
   `not_applicable`) alongside its prose `editorial_notice`. The sweep header's
   `papers_scored` counts only new papers; re-checks go in
   `papers_annotated_updates`. `scripts/validate_log.py` enforces all of this,
   and the dashboard build refuses to run if it fails.
6. Regenerate the dashboard HTML from `sentinel_log.json` (which validates the
   log first) and update the persisted Cowork artifact.
7. Append one line to `CHANGELOG.md`: date, papers found, papers scored,
   questions touched, anything notable (a `Closes` verdict, a retraction
   found, zero hits on a previously-active question).
