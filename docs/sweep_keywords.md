# Sweep keyword sets

Used by both the initial build and every scheduled weekly run. Update this
file (not just the query typed inline in a given run) when a search proves
too noisy or too narrow, so the change persists.

## PubMed query (keyword search, `sort=relevance`, `date_from`=today-30d)

```
(oyster OR mussel OR clam OR scallop OR abalone OR coral OR "sea urchin" OR bivalve OR cnidaria OR gastropod)
AND (methylation OR epigenetic OR "gene body methylation" OR transgenerational OR "reaction norm"
     OR lncRNA OR ncRNA OR "non-coding RNA" OR "predictive phenotyp*" OR "environmental memory"
     OR frontloading OR preconditioning OR "transgenerational plasticity")
```

## Consensus query (semantic search, `year_min`/`month_min` set to the window start)

Run as 2-3 separate semantic queries rather than one long one — Consensus's
semantic search performs better on focused phrasing:

1. `"environmental memory" epigenetics marine invertebrate phenotype prediction`
2. `transgenerational plasticity marine invertebrate methylation mechanism`
3. `coral bivalve gene body methylation reaction norm stress`

## bioRxiv (category + date browse, then client-side keyword filter on title)

No keyword search exists in the bioRxiv MCP tool — `search_preprints` only
filters by date range and one category. Query these categories separately
with `date_from`/`date_to` set to the sweep window, `limit=100`:

- `genetics`
- `genomics`
- `molecular biology`
- `evolutionary biology`
- `ecology`
- `physiology`

Then keep only results whose title or abstract preview contains at least one
of: `oyster, mussel, clam, scallop, abalone, coral, Acropora, Pocillopora,
Porites, Crassostrea, Saccostrea, Mytilus, urchin, Strongylocentrotus,
bivalve, cnidarian, methylation, epigenet, transgenerational, lncRNA, ncRNA,
reaction norm, phenotypic plasticity, marine invertebrate`.

## Scite editorial-notice check

For every paper that will appear on the dashboard: `search_literature` with
`dois: [<doi>]` and no `term`, read `editorialNotices`. Record `None found`,
or the notice type, before the paper is added.

## Tuning notes (append here as the sweep runs over time)

- 2026-08-05 (initial build): all three query sets above run once against the
  2026-07-06 to 2026-08-05 window. See `CHANGELOG.md` for the first entry and
  hit counts.
- Known issue to fix in a future sweep: Consensus's date filter appears to key
  off a preprint's most recent revision date, not its original posting date —
  this resurfaced a 2024 bioRxiv preprint (Teichman et al.) as if new. Cross-
  check any Consensus hit's actual first-posted date via Scite before treating
  it as new in a lab-facing summary.
- 2026-08-12: three tool-level constraints hit, all worth knowing before next week.
  (a) **PubMed operator cap.** The query above contains 22 boolean operators and the
  tool caps at 20, so it must be run as two queries splitting the second clause;
  `"predictive phenotyp*"` was also dropped, because the tool rejects wildcards
  outright. Consider rewriting that term as `"predictive phenotype" OR "predictive
  phenotypes"` and folding it back in.
  (b) **bioRxiv pagination.** `search_preprints` returns 30 results per call
  regardless of `limit=100`; `cursor` advances by 30. A 30-day window needs roughly
  7 calls per category, so 6 categories is ~42 calls. Coverage this sweep was
  genomics 07-12..07-22 and ecology + molecular biology 07-12..07-16 only. Either
  budget for the full pagination or formally narrow to two categories and say so.
  (c) **Scite is bimodal.** `dois: [...]` lookups were reliable; `term` and `titles`
  searches returned intermittent 502s (retryable after ~60s, but not always). Use
  DOI lookups wherever a DOI is already in hand, and treat title-based DOI discovery
  as best-effort. This cost the Durkin et al. DOI this sweep.
- 2026-08-12: the Consensus revision-date artifact recurred, as predicted above —
  CpGPT (a methylation foundation model carrying 35 citations, so obviously not new)
  surfaced under a 2026 month filter. The citation count is the cheapest tell:
  anything with a non-trivial citation count inside a 30-day window is almost
  certainly a resurfaced revision. Screen on that before spending a Scite call.
- 2026-08-12: three genuinely-in-window hits (Janssens, Rosas-Anaya, Nobre) carry
  publication dates of 2026-07-01, ~11 days before the window start, because the
  Consensus filter is month-granular. This is now the second sweep running with the
  same border case and no rule. Proposed rule for next week: keep any hit whose
  publication date falls within 14 days before the window start, note it, and do not
  re-score it if it resurfaces in a later window.
- 2026-11-19: PubMed operator cap resolved for good. Run these two queries
  (16 operators each), which also fold the dropped wildcard back in:
  (A) `(<taxa>) AND (methylation OR epigenetic OR "gene body methylation" OR
  transgenerational OR "reaction norm" OR lncRNA OR ncRNA)`.
  (B) `(<taxa>) AND ("non-coding RNA" OR "predictive phenotype" OR
  "predictive phenotypes" OR "environmental memory" OR frontloading OR
  preconditioning OR "transgenerational plasticity")`.
  `<taxa>` is the 10-term taxon clause above. This week (B) returned only
  duplicates of (A), so it is cheap insurance.
  The taxon terms also catch "coral" outside biology: coral-like nanoplates,
  the CORAL spatial-omics model, a coral-inspired aerogel. Expect 4-5 such
  off-topic hits a month. Screening by title is enough.
- 2026-11-19: **bioRxiv full coverage is feasible.** The cursor does advance in
  steps of 30, even though every response echoes `"cursor":0, "total":0`.
  Page each category until a page returns fewer than 30 records. A 30-day
  window took 53 calls across 7 categories (genomics 11, molecular biology
  10, evolutionary biology 10, ecology 10, genetics 6, physiology 5, zoology
  1). Delegating that paging to a subagent keeps the main context small.
  - `zoology` added almost nothing (25 records a month, no keyword hits).
    Optional.
  - A new version of an older preprint shows up as a fresh listing, so check
    the DOI date stem. 7 of this week's keyword hits were revised versions.
  - `get_preprint` returns v1 metadata and sometimes the v1 title.
  - Keyword misses worth adding to the filter list: `cnidaria, porifera,
    barnacle, chiton, cockle, snail, crab, nudibranch, octopus, tubeworm,
    shellfish, epimutation`. Note that "cnidarian" does not match "Cnidaria".
- 2026-11-19: **Scite `verify_papers` with `references` resolves missing
  DOIs.** Pass the reference as written (authors, year, title, venue). It
  resolved 5 of 6 DOIs in one call: Durkin, Yuan, Gonzalez-Rajal, Madin, and
  a Consensus-only shrimp paper. Title-based `search_literature` had failed
  on all of these for weeks. Use it first for any Consensus-only hit, since
  Consensus cards carry no DOI. For the one it missed (a Chinese-language
  journal title), a short PubMed keyword search found the DOI.
  - `search_literature` with `dois` and `verify_papers` with `dois` agree on
    editorial notices.
  - `search_literature` also surfaces a "new version" record (seen on a PLoS
    Biology paper). `verify_papers` does not count that as an editorial
    notice. Record it in the prose, not as a correction.
- 2026-11-19: **14-day border rule ADOPTED.** Keep any hit dated up to 14
  days before the window start, note it in the record, and never re-score it
  in a later window.
  - It does not rescue papers lost to a skipped week. This sweep followed a
    ten-week gap, and items from 15+ days before the window were left out
    and named in the sweep notes.
  - If a run is skipped, run a catch-up sweep over the missed window. Do not
    stretch the border.
- 2026-11-19: Render check: Playwright's bundled Chromium is now at
  `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`, not `chrome-linux`.
  `verify.js` also ran fine with `PW_CHROMIUM` unset.
