#!/usr/bin/env python3
"""
Schema and self-consistency check for data/sentinel_log.json.

Run standalone, or let build_dashboard.py call it — the build refuses to write
index.html if this fails, so a malformed log can never reach the published page.

    python3 scripts/validate_log.py

Checks:
  * every entry carries the fields build_dashboard.py indexes into, so a typo
    surfaces here with an entry id instead of as a bare KeyError in the build
  * ids are unique, and every `supersedes` points at an id that exists, in the
    same section, without cycles
  * verdicts are one of the four the dashboard has a colour for (an unknown one
    would otherwise render as a silent grey pill)
  * each sweep's declared papers_scored / papers_annotated_updates matches the
    entries actually carrying that sweep_date
  * editorial_status is one of the three known values and agrees with the prose
    in editorial_notice
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "data", "sentinel_log.json")

VERDICTS = {"Confirms", "Complicates", "Closes", "Extends"}
QUESTIONS = {f"Q{i}" for i in range(1, 11)}
STATUSES = {"checked", "unavailable", "not_applicable"}

ENTRY_FIELDS = ["id", "doi", "title", "authors", "journal", "year", "pub_date",
                "species", "questions", "sweep_date", "editorial_status"]
SWEEP_FIELDS = ["sweep_date", "window_start", "window_end", "sources_queried",
                "papers_screened", "papers_scored"]


def check_supersedes(items, section, err):
    """Every supersedes must name a real id in the same section, and the chains
    it forms must terminate — a cycle would hang the lineage walk in the build."""
    by_id = {i["id"]: i for i in items}
    for item in items:
        target = item.get("supersedes")
        if target is None:
            continue
        if target not in by_id:
            err(f"{section}/{item['id']}: supersedes unknown id {target!r}")
            continue
        seen, cur = {item["id"]}, target
        while cur is not None:
            if cur in seen:
                err(f"{section}/{item['id']}: supersedes chain is cyclic")
                break
            seen.add(cur)
            cur = by_id.get(cur, {}).get("supersedes")


def validate(log):
    problems = []
    err = problems.append

    entries = log.get("entries", [])
    seen_ids = set()
    for e in entries:
        eid = e.get("id", "<no id>")
        if eid in seen_ids:
            err(f"entries/{eid}: duplicate id")
        seen_ids.add(eid)
        for f in ENTRY_FIELDS:
            if f not in e:
                err(f"entries/{eid}: missing required field {f!r}")

        status = e.get("editorial_status")
        if status is not None and status not in STATUSES:
            err(f"entries/{eid}: editorial_status {status!r} not in {sorted(STATUSES)}")
        notice = str(e.get("editorial_notice", ""))
        if status == "checked" and not notice.startswith("None found"):
            err(f"entries/{eid}: editorial_status 'checked' but notice reads {notice[:40]!r}")
        if status == "unavailable" and notice.startswith("None found"):
            err(f"entries/{eid}: editorial_status 'unavailable' contradicts notice {notice[:40]!r}")

        for hit in e.get("questions", []):
            if hit.get("q") not in QUESTIONS:
                err(f"entries/{eid}: question id {hit.get('q')!r} is not Q1-Q10")
            if hit.get("verdict") not in VERDICTS:
                err(f"entries/{eid}: verdict {hit.get('verdict')!r} not in {sorted(VERDICTS)}")
            if not str(hit.get("rationale", "")).strip():
                err(f"entries/{eid}: empty rationale on {hit.get('q')}")

    check_supersedes(entries, "entries", err)
    check_supersedes(log.get("insufficient_info", []), "insufficient_info", err)

    # A sweep's header must agree with the records that carry its date, or the
    # history table prints a number the log itself contradicts.
    for s in log.get("sweeps", []):
        date = s.get("sweep_date")
        for f in SWEEP_FIELDS:
            if f not in s:
                err(f"sweeps/{date}: missing required field {f!r}")
        mine = [e for e in entries if e.get("sweep_date") == date]
        new = sum(1 for e in mine if not e.get("supersedes"))
        updates = len(mine) - new
        if s.get("papers_scored") != new:
            err(f"sweeps/{date}: papers_scored={s.get('papers_scored')} but "
                f"{new} non-superseding entries carry that sweep_date")
        if int(s.get("papers_annotated_updates") or 0) != updates:
            err(f"sweeps/{date}: papers_annotated_updates="
                f"{s.get('papers_annotated_updates') or 0} but {updates} "
                f"superseding entries carry that sweep_date")

    return problems


def main():
    with open(LOG) as fh:
        log = json.load(fh)
    problems = validate(log)
    if problems:
        print(f"sentinel_log.json: {len(problems)} problem(s)", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"sentinel_log.json OK "
          f"({len(log.get('entries', []))} entries, {len(log.get('sweeps', []))} sweeps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
