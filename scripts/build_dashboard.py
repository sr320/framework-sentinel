#!/usr/bin/env python3
"""
Build index.html (the public dashboard) from data/sentinel_log.json +
scripts/dashboard_template.html.

scripts/dashboard_template.html is the real source for layout, styling, and JS.
This script:
  1. Loads data/sentinel_log.json and validates it (see validate_log.py) — a log
     that fails validation aborts the build rather than publishing a broken page.
  2. Aggregates entries per question (Q1-Q10) and computes a staleness value.
     The log is append-only, so a re-checked paper appears as a second record
     carrying `supersedes`. Those records are shown (the audit trail is the
     point) but are NOT counted as new science: totals, verdict counts and
     staleness all collapse a supersedes-chain to the one paper it describes,
     and staleness uses the date the question was FIRST scored in that chain, so
     a sweep that only re-checks old papers cannot make a question look active.
  3. Counts records whose editorial (retraction/correction) check could not be
     run, from the categorical `editorial_status` field, so the page can say so
     honestly rather than implying every paper was checked.
  4. Injects the resulting data model + a footer string + the repo URL into the
     template's __DATA__ / __FOOT__ / __REPO__ placeholders and writes index.html.

Never hand-edit index.html — it is generated and will be overwritten the next time
this script (or the GitHub Actions workflow) runs. Edit the template or the log.

Usage:
    python3 scripts/build_dashboard.py
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import validate_log  # noqa: E402  (needs HERE on sys.path first)

REPO_URL = os.environ.get(
    "FRAMEWORK_SENTINEL_REPO", "https://github.com/sr320/framework-sentinel"
)

# Keep this list in sync with docs/RUBRIC.md's table if the questions ever change.
QUESTIONS = [
    {"id": "Q1", "title": "Persistence and decay of marks",
     "gloss": "What governs whether an induced epigenetic state washes out, persists, or assimilates, and on what timescale?"},
    {"id": "Q2", "title": "Soma-to-germline transmission",
     "gloss": "How is parental experience translated into the gamete in marine invertebrates?"},
    {"id": "Q3", "title": "Causal direction",
     "gloss": "When methylation, transcription, and phenotype co-vary, which causes which?"},
    {"id": "Q4", "title": "F0-F1 methylation rebound",
     "gloss": "Why do parental and offspring methylation responses sometimes invert?"},
    {"id": "Q5", "title": "ncRNA functional validation",
     "gloss": "Are inferred cis-regulatory effects of lncRNAs on neighboring genes real, and at what magnitude?"},
    {"id": "Q6", "title": "Channel integration",
     "gloss": "Are methylation- and ncRNA-mediated memory independent, redundant, or hierarchical?"},
    {"id": "Q7", "title": "Energetic cost of plasticity",
     "gloss": "What is the metabolic burden of maintaining high-turnover methylation states?"},
    {"id": "Q8", "title": "Mismatch threshold",
     "gloss": "At what rate of environmental change does anticipatory memory tip from adaptive to maladaptive?"},
    {"id": "Q9", "title": "Cross-taxa generality",
     "gloss": "Does the plasticity-frontloading trade-off generalize across taxa (corals, bivalves, etc.)?"},
    {"id": "Q10", "title": "Held-out predictive performance",
     "gloss": "Can molecular signatures trained on one cohort forecast performance in an independent cohort under novel conditions?"},
]

FOOTER = (
    "Framework Sentinel scores incoming literature against ten unresolved questions from the Roberts Lab "
    "conceptual framework in marine invertebrate environmental epigenetics. A scheduled pipeline sweeps a "
    "trailing 30-day window each week across <b>PubMed</b> (keyword search), <b>Consensus</b> (semantic search), and "
    "<b>bioRxiv</b> (date + category browse, keyword-filtered client-side — the API has no native keyword search, so "
    "bioRxiv coverage is necessarily approximate and skews toward the start of each window). Papers are then screened "
    "for scope and scored against the rubric. "
    "<br><br>"
    "Scored papers are checked against <b>Scite</b> for retractions, corrections, and expressions of concern before "
    "being added — but that check is not always available, and any record where it could not be run says so on its own "
    "card. Treat those as unverified. "
    "<br><br>"
    "This is a <b>screening and triage tool, not a citation-ready literature review</b>. Verdicts are one reader's "
    "judgment from abstracts, most often without the full text; preprints are included and are not peer reviewed; "
    "and papers authored by the lab itself are flagged as such, because they cannot count as independent corroboration "
    "of the lab's own framework. Verify any finding against the full text before using it in a manuscript or grant. "
    "<br><br>"
    'The underlying log is append-only — prior scoring is never deleted or silently rewritten. See the '
    '<a href="__REPOURL__/blob/main/CHANGELOG.md">changelog</a> for what each sweep found, '
    '<a href="__REPOURL__/blob/main/docs/RUBRIC.md">RUBRIC.md</a> for the scoring criteria, and '
    '<a href="__REPOURL__/blob/main/data/sentinel_log.json">sentinel_log.json</a> for the raw data behind this page.'
)


def load_log():
    path = os.path.join(ROOT, "data", "sentinel_log.json")
    with open(path) as fh:
        log = json.load(fh)
    problems = validate_log.validate(log)
    if problems:
        print(f"REFUSING TO BUILD: sentinel_log.json has {len(problems)} problem(s):",
              file=sys.stderr)
        for prob in problems:
            print(f"  - {prob}", file=sys.stderr)
        sys.exit(1)
    return log


def lineage_roots(items):
    """Map each record id to the id at the head of its supersedes-chain.

    The log is append-only: a re-checked paper is a NEW record pointing at the
    one it updates. All of those records describe a single paper, so every
    count on the dashboard has to collapse them to their root or it reports
    bookkeeping as if it were literature. validate_log guarantees the chains
    terminate, so this walk cannot spin.
    """
    by_id = {i["id"]: i for i in items}
    roots = {}
    for item in items:
        cur = item["id"]
        while by_id.get(cur, {}).get("supersedes"):
            cur = by_id[cur]["supersedes"]
        roots[item["id"]] = cur
    return roots


def collapse_lineages(items):
    """Return [(root_id, [records oldest-first])], one group per real paper."""
    roots = lineage_roots(items)
    groups = {}
    for item in items:
        groups.setdefault(roots[item["id"]], []).append(item)
    for recs in groups.values():
        recs.sort(key=lambda r: r.get("sweep_date") or "")
    return groups


def days_between(today, iso_date):
    try:
        return (today - datetime.date.fromisoformat(iso_date)).days
    except (ValueError, TypeError):
        return None


def build_model(log):
    today = datetime.date.today()
    entries = log.get("entries", [])
    roots = lineage_roots(entries)
    groups = collapse_lineages(entries)

    by_q = {q["id"]: [] for q in QUESTIONS}
    for e in entries:
        for hit in e.get("questions", []):
            qid = hit["q"]
            by_q.setdefault(qid, []).append({
                "entry_id": e["id"], "root_id": roots[e["id"]],
                "supersedes": e.get("supersedes"),
                "doi": e["doi"], "title": e["title"],
                "authors": e["authors"], "journal": e["journal"], "year": e["year"],
                "pub_date": e["pub_date"], "species": e["species"],
                "cross_domain": e.get("cross_domain", False),
                "verdict": hit["verdict"], "rationale": hit["rationale"],
                "caveat": e.get("caveat", ""),
                "editorial_notice": e.get("editorial_notice", "Not checked"),
                "editorial_status": e.get("editorial_status", "unavailable"),
                "evidence_source": e.get("evidence_source", ""),
                "sweep_date": e.get("sweep_date"),
            })

    questions_out = []
    for q in QUESTIONS:
        hits = by_q.get(q["id"], [])
        hits_sorted = sorted(hits, key=lambda h: h["sweep_date"] or "", reverse=True)

        # Staleness answers "when did the literature last say anything here?",
        # so each paper contributes the sweep that FIRST scored it against this
        # question. A later re-check of that same paper adds no new information
        # and must not reset the clock.
        first_scored = {}
        for h in hits:
            prev = first_scored.get(h["root_id"])
            if prev is None or (h["sweep_date"] or "") < prev:
                first_scored[h["root_id"]] = h["sweep_date"] or ""
        last_date = max(first_scored.values()) if first_scored else None
        questions_out.append({
            **q,
            "hits": hits_sorted,
            "hit_count": len(first_scored),
            "record_count": len(hits_sorted),
            "last_sweep_date": last_date,
            "days_since_last_hit": days_between(today, last_date) if last_date else None,
        })

    sweeps = log.get("sweeps", [])
    last_sweep = sweeps[-1] if sweeps else None

    # One verdict per paper per question — taken from the most recent record in
    # the chain, so a correction that changes a verdict is what gets counted.
    verdict_counts = {}
    for recs in groups.values():
        latest_verdict = {}
        for rec in recs:
            for hit in rec.get("questions", []):
                latest_verdict[hit["q"]] = hit["verdict"]
        for verdict in latest_verdict.values():
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    cross_domain_count = sum(
        1 for recs in groups.values() if any(r.get("cross_domain") for r in recs)
    )
    # The editorial check is judged on the newest record: a deferred check that
    # a later sweep completed is resolved, not outstanding.
    unchecked = sum(
        1 for recs in groups.values()
        if recs[-1].get("editorial_status", "unavailable") == "unavailable"
    )

    insufficient_groups = collapse_lineages(log.get("insufficient_info", []))
    insufficient = []
    for recs in sorted(insufficient_groups.values(),
                       key=lambda r: r[-1].get("sweep_date") or ""):
        latest = dict(recs[-1])
        latest["recheck_count"] = len(recs) - 1
        latest["first_seen"] = recs[0].get("sweep_date")
        insufficient.append(latest)

    return {
        "questions": questions_out,
        "sweeps": sweeps,
        "last_sweep": last_sweep,
        "entries_count": len(groups),
        "records_count": len(entries),
        "update_records_count": len(entries) - len(groups),
        "cross_domain_count": cross_domain_count,
        "verdict_counts": verdict_counts,
        "unchecked_count": unchecked,
        "method_watch": log.get("method_watch", []),
        "insufficient_info": insufficient,
        "insufficient_records_count": len(log.get("insufficient_info", [])),
        "built": today.isoformat(),
    }


def main():
    log = load_log()
    model = build_model(log)
    # The model is injected into a <script> block, so no string in it may close
    # that block. json.dumps already escapes U+2028/U+2029 via \uXXXX.
    data_json = json.dumps(model, separators=(",", ":")).replace("</", "<\\/")

    tpl_path = os.path.join(ROOT, "scripts", "dashboard_template.html")
    with open(tpl_path) as fh:
        tpl = fh.read()

    foot = FOOTER.replace("__REPOURL__", REPO_URL)

    html = (tpl
            .replace("__DATA__", data_json)
            .replace("__FOOT__", json.dumps(foot))
            .replace("__REPO__", json.dumps(REPO_URL)))

    out_path = os.path.join(ROOT, "index.html")
    with open(out_path, "w") as fh:
        fh.write(html)

    print(f"Wrote {out_path} ({len(html) / 1024:.1f} KB)")
    print(f"Questions with hits: "
          f"{sum(1 for q in model['questions'] if q['hit_count'] > 0)} / {len(model['questions'])}")
    print(f"Papers scored: {model['entries_count']} "
          f"({model['records_count']} records, of which "
          f"{model['update_records_count']} are annotated re-checks)")
    print(f"Editorial check unavailable on: {model['unchecked_count']} papers")
    print(f"Sweeps in log: {len(model['sweeps'])}")


if __name__ == "__main__":
    main()
