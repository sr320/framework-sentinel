# Framework Sentinel — changelog

## 2026-08-05 — Initial build

- Wrote the scoring rubric (`RUBRIC.md`): the ten unresolved questions from
  the lab's conceptual framework, the five-verdict taxonomy (Confirms /
  Complicates / Closes / Extends / Irrelevant), in-scope literature
  definition, and staleness definition.
- Wrote `sweep_keywords.md`: the exact PubMed query, three Consensus semantic
  queries, bioRxiv category + keyword-filter list, and the Scite
  editorial-check procedure.
- Ran the first sweep, trailing window 2026-07-06 to 2026-08-05:
  - **47 papers screened** across PubMed, Consensus, and a partial bioRxiv
    pass (category browsing only reached ~2026-07-13 of the window before
    returns plateaued at 30 results/category — treat bioRxiv coverage this
    sweep as partial).
  - **8 papers scored** against the ten questions; **7 of 10 questions**
    touched (Q1, Q4, Q5 had no hits this sweep — expected for a first run,
    not an error).
  - **2 cross-domain flags** (C. elegans soma-to-germline mechanism paper;
    a locust phase-polyphenism systematic review) — both scored as
    methodologically relevant rather than as marine-invertebrate data, per
    RUBRIC.md.
  - **1 method-watch item** (human cancer/stem-cell lineage-tracing method,
    transferable to Q3/Q6).
  - **1 insufficient-info item** (a coral-restoration demography preprint
    surfaced with title only, no abstract — flagged for re-fetch next sweep).
  - Verdict split: 5 Confirms, 3 Complicates, 1 Extends.
  - Notable data-quality issue caught: Consensus resurfaced a 2024 bioRxiv
    preprint (Teichman et al.) as if newly published in 2026 — its date
    filter appears to key off revision date, not original posting date.
    Cross-checked via Scite (original post 2024-12-02, 8 existing citations)
    and flagged explicitly rather than reported as new. See the "Tuning
    notes" section of `sweep_keywords.md`.
- Built and verified `Framework_Sentinel_dashboard.html` (Playwright
  screenshot check, light + dark mode, no console errors).
- Persisted the dashboard as a Cowork artifact and moved the whole project
  (rubric, keywords, log, template, build script) into a Google Drive folder
  ("Framework Sentinel") so the weekly scheduled sweep — which starts a
  brand-new session each time — can rebuild its working copy and push
  updates back. See `README.md` for the persistence architecture.
- Set up the weekly scheduled sweep (Tuesdays).

## 2026-08-12 — Weekly sweep (window 2026-07-12 to 2026-08-11)

- **187 papers screened**, **7 newly scored**, plus **1 annotated update** to a prior
  entry. Sources: PubMed (split into 2 queries — see `sweep_keywords.md`), Consensus
  (3 semantic queries run sequentially), bioRxiv (partial category browse), Scite
  (editorial-notice checks).
- **9 of 10 questions now have at least one hit.** Q1 (persistence and decay of
  marks) and Q5 (ncRNA functional validation) received their **first hits ever**,
  each from two independent directions. **Q4 (F0–F1 methylation rebound) has now gone
  two consecutive sweeps with zero hits and has never been touched** — on the
  staleness logic in `RUBRIC.md`, this is the clearest signal yet that Q4 is a
  question the lab will have to move itself rather than wait on.
- **Most consequential hit: Durkin et al.** (bioRxiv), the first description of
  epi-miRNAs and ceRNA networks in any cnidarian, across three coral species. Scored
  `Confirms` on Q6 (channel integration): miRNAs target DNA methylation regulators
  (TET3, MBD, PRDM14) and histone-modifying machinery while lncRNA ceRNAs buffer
  those miRNAs — i.e. evidence for a **hierarchical** architecture with ncRNAs
  upstream of methylation, which the framework has held as plausible-but-untested.
  **Flagged in the log:** Kathleen Durkin is a Roberts Lab member, so this is the
  lab's own preprint and must not be read as independent external validation. Its
  **DOI could not be resolved** this sweep (Scite term search 502'd, bioRxiv has no
  keyword search) — resolve before citing.
- **A real tension opened on Q9.** Durkin finds regulatory architecture conserved
  across three corals *despite few orthologous miRNAs or lncRNAs*; Serdo & Németh
  (scored 2026-08-05) found "fundamental divergence rather than conservation" across
  locust species. Both scored `Confirms`/`Complicates` on Q9 and they do not agree.
  Likely reconciliation: conservation lives at the level of architecture, not
  components — which would be a substantive reframing of Q9.
- **A second candidate sixth channel.** Rosas-Anaya & Yépiz-Plascencia's crustacean
  review organises the field into four layers including RNA m6A, an epitranscriptomic
  channel the framework's five-channel model does not name. This is the second sweep
  running to point outside the five (Xue et al. made the same case for alternative
  splicing on 2026-08-05). Q6 may need "how many channels are there?" answered first.
- **A measurement-validity warning worth acting on.** Grau-Bové et al. show coral cell
  types moving in *opposite* directions under the same heat stress (epidermal cells
  activating renewal, calicoblasts repressing calcification), so bulk-tissue
  covariation of methylation, transcription, and phenotype may reflect shifting cell
  composition rather than within-cell coupling — scored `Complicates` on Q3. Edgar et
  al. separately show a sea anemone respires ~2× faster expanded than closed at the
  same temperature, confounding behaviour with physiology in any whole-organism
  energetic-cost estimate — scored `Complicates` on Q7, that question's first hit.
- **Deferred check closed:** Thyrring et al. (flagged 2026-08-05 as "not yet indexed
  in Scite") is now indexed and carries **no** retraction, correction, or expression
  of concern. Recorded as an annotated update entry rather than an edit, per the
  append-only rule; Q8 will therefore show two cards for that paper.
- **No retractions, corrections, or expressions of concern** were found on any paper
  added to the dashboard this sweep.
- Still unresolved after two sweeps: the Madin et al. coral-restoration preprint,
  which Consensus has now surfaced twice with a title and no abstract or DOI. Logged
  again with a changed action — stop waiting on Consensus, resolve the DOI directly.
- Fixed a small template bug: `method_watch` cards emitted a dead `https://doi.org/`
  link when an item had no DOI; they now render the title as plain text instead.
  `dashboard_template.html` re-uploaded.
- Dashboard rebuilt from `sentinel_log.json` and verified with Playwright (10 question
  cards, 23 hit cards, light + dark, no console or page errors).
- The persisted Cowork artifact could **not** be refreshed this run: scheduled runs
  have no device bridge, so `update_artifact` was unavailable. The dashboard was
  delivered as a file instead.

## 2026-09-01 — Weekly sweep (window 2026-08-02 to 2026-09-01)

- **219 papers screened**, **4 newly scored**, **3 new cross-domain method-watch items**,
  **1 insufficient-info carryover** (third sweep in a row). Sources: PubMed (2 split
  queries), Consensus (3 semantic queries, run sequentially), bioRxiv (6 categories,
  partial coverage as in prior sweeps — genetics/genomics/evolutionary biology each
  needed 1-2 retries after 30s timeouts).
- **Scite was unavailable all sweep**: the Scite MCP server needs re-authorization
  (OAuth token expired), and this is a non-interactive scheduled run, so the
  mandatory pre-dashboard retraction/correction check could not be performed on
  *any* paper added this week. Every new entry and method-watch item is flagged
  `editorial_notice: "Not checked — Scite unavailable..."` and needs a retroactive
  check next sweep. **Action needed from Steven:** re-authorize the Scite connector
  (via Claude Code Remote MCP settings) so next week's run can check for retractions.
- **9 of 10 questions now have at least one hit.** Q4 (F0-F1 methylation rebound)
  has gone three consecutive sweeps with zero hits and remains untouched since the
  log began — the clearest signal yet that this question needs a lab experiment
  rather than more literature sweeps.
- **Best hit: Vaidya et al.** (bioRxiv, *Tigriopus californicus* splash-pool copepod)
  is the first crustacean system to show the plasticity-frontloading trade-off
  (Q9) previously only demonstrated in corals and bivalves: populations with
  higher fixed heat tolerance show lower plasticity, and vice versa, across a
  12°-latitude cline.
- **Three strong cross-domain method-watch items**, all directly portable to a
  marine-invertebrate experiment: Pichon et al. (*Biomphalaria glabrata*, freshwater
  snail) directly demonstrates that an induced epigenetic/metabolic state persists
  stably and causally primes a later phenotypic response — the exact Q1/Q3
  persistence-then-causation sequence the framework needs tested, via a WGBS +
  chromatin-accessibility + transcriptomics + metabolomics design on the same
  samples. Zicola et al. (*Arabidopsis*) CRISPR-validates specific genes driving
  methylome change after novel-habitat colonization — the causal-perturbation
  standard Q3 rarely gets in marine systems, in a mismatch/novel-habitat scenario
  structurally similar to Q8. Gralak et al. (meSMiLE-seq) is a scalable in-vitro
  assay for whether methylation directly gates transcription-factor binding, one
  concrete causal link within Q3 (note: the underlying preprint is from Nov 2024;
  this is the formal 2026-08-05 journal publication, not new unpublished work).
- **The append-only log paid for itself**: a PubMed hit this week (Thyrring et al.,
  *Mytilus edulis* lead/thermal cross-tolerance, DOI 10.1016/j.ecoenv.2026.120601)
  was recognized as an exact-DOI duplicate of the paper already scored on Q8 in the
  2026-08-05 sweep, despite carrying a fresh-looking PubMed record this week, and
  was correctly **not** re-added.
- **New tool-quirk discovered and logged in `sweep_keywords.md`**: two Elsevier
  *Comparative Biochemistry and Physiology Part D* papers (Zhou_2026_Tudor,
  print-dated 2026-03-30; Zhao_2026_lncRNA_growth, print-dated 2026-05-11) matched
  a `pdat`-filtered PubMed search for the 2026-08-02..2026-09-01 window despite
  print/epub dates months earlier — a likely print-issue-reassignment artifact,
  analogous to the known Consensus revision-date issue. Both are genuinely new to
  this log, so were scored, with the date mismatch flagged in their entries.
- **Fixed a real bug in `dashboard_template.html`**: the "Needs another look"
  (insufficient-info) section was silently never rendering — the JS set
  `.sinnerHTML` instead of `.innerHTML` on that list element. No error was thrown
  (JS doesn't error on setting an arbitrary property), so this had likely been
  silently broken since the initial 2026-08-05 build; prior Playwright checks
  apparently didn't specifically assert that section's card count. Fixed and
  reverified — the section now correctly renders all 3 insufficient-info cards.
  `dashboard_template.html` re-uploaded.
- Dashboard rebuilt from `sentinel_log.json` and verified with Playwright (10
  question cards, 27 hit cards, 6 method-watch cards, 3 insufficient-info cards,
  light + dark, no console or page errors).
- No retractions, corrections, or expressions of concern could be checked this
  sweep (see Scite outage above).
- The persisted Cowork artifact could **not** be refreshed this run: this
  scheduled run has no desktop bridge connected, so `update_artifact` was
  unavailable (same limitation as the 2026-08-12 run). Delivered as a file
  instead.

## 2026-09-08 — Weekly sweep (window 2026-08-09 to 2026-09-08)

- **~215 papers screened** (approximate, deduplicated across sources — bioRxiv's
  per-category 30-result cap means this is a partial count, same limitation as
  every prior sweep), **7 newly scored**, **1 annotated update** (no new score),
  **4 new cross-domain method-watch items**, **0 insufficient-info carryovers**
  added (see below). Sources: PubMed (2 split queries), Consensus (3 semantic
  queries, run sequentially), bioRxiv (6 categories, partial coverage as usual).
- **Scite has now been unreachable for two consecutive sweeps.** Unlike the
  2026-09-01 outage (a reachable server reporting an expired token), this sweep
  the Scite tool was not listed or reachable in the session at all — a broader
  connectivity gap. **No retraction/correction/expression-of-concern checks
  could be performed on anything added this sweep or last sweep** (12 entries +
  7 method-watch items across both sweeps are still uncertified). **Action
  needed from Steven:** check why the Scite MCP connector isn't showing up at
  all, not just re-authorize it.
- **9 of 10 questions have at least one hit.** Q4 (F0–F1 methylation rebound)
  had zero hits again — now zero hits across **all four sweeps** since the log
  began. This is the strongest signal yet that Q4 needs a lab experiment rather
  than more literature sweeps.
- **Best hit: Baird et al.** (bioRxiv) — the lab's own (Roberts Lab) Pacific
  oyster parental-immune-priming preprint. Directly quantifies the Q8
  mismatch/tipping-point phenomenon: priming benefit at 40°C (35% lower
  offspring mortality) inverts to a cost at 42°C (17% higher mortality).
  Also scored `Confirms` on Q2 (parent-to-offspring transmission of an
  immune-stress-induced phenotype). **Flagged as in-house work, not
  independent validation** — same caveat as Durkin_2026. Also note: this
  preprint was actually first posted 2025-12-13, ~9 months before this
  window; it resurfaced via bioRxiv's date+category browse (a
  version/reindex artifact, not a genuinely new preprint).
- **Buso et al.** (coral, cross-confirmed via bioRxiv AND all three Consensus
  queries) disentangles genotype-associated from genotype-independent DNA
  methylation variation in two coral species across the South Pacific —
  `Confirms` on Q3 (causal direction), `Extends` on Q9.
- **Two more Roberts Lab items surfaced.** Ashey et al. (Environmental
  Epigenetics, published) characterizes ncRNA machinery across three coral
  genera from the same Mo'orea system as the still-unresolved Durkin_2026
  (2026-08-12) — logged as a separate, related-but-not-confirmed-identical
  entry. Durkin_2026's own DOI remains unresolved after a second recheck
  (annotated update added, no re-score).
- **Two strong hits couldn't get a DOI resolved this sweep:** Yuan et al.
  (sponge, light-entrained chromatin priming — `Confirms` Q1, `Extends` Q8)
  and González-Rajal et al. (siphonophore, methylation vs. chromatin
  decoupling — `Complicates` Q6). Both surfaced only via Consensus, which
  doesn't return DOIs in its result cards; PubMed/bioRxiv title lookups found
  no match. Flagged for DOI resolution before citing either in a manuscript.
- **Cross-validation worked as designed:** three PubMed hits this week were
  recognized as exact-DOI duplicates of papers already scored 2026-09-01
  (Zhou_2026_Tudor, Zhao_2026_lncRNA_growth, Ai_2026_Turritopsis) and
  correctly not re-added.
- **Four new cross-domain method-watch items** (all outside taxonomic scope,
  tagged rather than scored): a zebra-mussel small-RNA/RNAi toolkit
  (freshwater bivalve, transferable to Q5); a prospective human
  epigenetic-age-acceleration cohort study (transferable design for Q1/Q10);
  a 14-year Norway spruce common-garden study showing stable,
  partially embryo-to-adult-transmitted methylation differences (one of the
  longest persistence datasets found in any taxon so far — relevant to
  Q1/Q2/Q4); and a plant-epigenome bioenergetics review proposing a metabolic
  "yield penalty" framework for stress memory (relevant to Q7, explicitly
  unvalidated even in plants).
- Per the 2026-09-01 sweep's own recommendation, the Madin et al.
  coral-restoration insufficient-info item was **not** re-attempted a fourth
  time via automated search this sweep; it still needs manual resolution.
- Dashboard rebuilt from `sentinel_log.json` and verified with Playwright
  (10 question cards, 42 hit cards, 10 method-watch cards, 3
  insufficient-info cards, light + dark, no console or page errors).
- The persisted Cowork artifact could **not** be refreshed this run either:
  this is a cloud-scheduled run with no desktop bridge connected, so
  `update_artifact` was unavailable. Delivered as a file instead.

## 2026-09-11 — Codebase audit and pipeline fixes

No sweep this entry — a review of the repository itself, and the fixes it turned up.

- **`supersedes` added to the log schema.** The append-only rule was producing
  re-check records (`Thyrring_2026_update`, `Durkin_2026_update_20260908`, two
  `Madin_2026` re-checks) that nothing distinguished from newly scored papers, so
  every aggregate counted bookkeeping as literature: 28 "records scored" where
  there were 26 papers, 4 double-counted verdicts, and three "needs another look"
  cards for one unresolved item. A re-check now names the record it updates, and
  the build collapses each chain to the one paper it describes.
- **Staleness no longer resets on a re-check.** Each paper contributes the sweep
  that *first* scored it against a question. The old behaviour hadn't yet produced
  a wrong badge — the 2026-09-08 re-checks happened to land in a sweep with real
  Q5/Q6/Q9 hits — but a re-check-only sweep would have turned questions green with
  no new science behind them.
- **`editorial_status` added** (`checked` / `unavailable` / `not_applicable`). The
  unverified count was matching on the prose prefix `"Not checked"`, which missed a
  paper too recent to be indexed and a preprint whose DOI never resolved. The
  honest figure was 14 records, not 12; after collapsing re-checks (one of which
  resolved Thyrring's deferred check) it is **12 of 26 papers**.
- **`scripts/validate_log.py` added**, and the build now aborts rather than
  publishing a page built from a malformed log. It immediately caught a real drift:
  the 2026-08-12 sweep declared `papers_scored: 7` while 8 entries carried that
  date — its annotated update was never recorded in the header.
- **`.github/workflows/pages.yml` added.** The README had described it and the
  layout listed it, but no workflow existed and the repo had no commits at all —
  nothing rebuilt or deployed anything. It also rebuilds weekly on a schedule,
  since staleness is computed at build time and a page that is never rebuilt
  slowly starts lying.
- Template: DOIs are URI-encoded before going into an `href` (the method-watch
  cards already escaped theirs), the injected JSON is guarded against a `</script>`
  sequence, and re-check cards are labelled *re-check · not a new finding*.
- `scripts/verify.js` no longer hardcodes a container-only Chromium path; set
  `PW_CHROMIUM` to override. Playwright was installed and the check run in full:
  10 question cards, 42 hit cards (4 tagged as re-checks), 10 method-watch cards,
  1 insufficient-info card, light + dark, no console or page errors, and no
  horizontal overflow at desktop or at a 390px mobile viewport.
- Deployed: GitHub Pages enabled (source: GitHub Actions) and the live site at
  https://sr320.github.io/framework-sentinel/ verified to serve the corrected
  figures — 26 papers / 28 records, editorial gap 12 of 26, one
  insufficient-info card.
- Unchanged: no scoring verdict, rationale, or caveat was edited, and no record was
  removed. All schema changes are additive.
