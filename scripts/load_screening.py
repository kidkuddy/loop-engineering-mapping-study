#!/usr/bin/env python3
"""Load screener decision CSVs into the database.

Coders write CSVs; this writes them to screening_decisions. The CSVs stay in the
repository as the per-coder raw record, because the database keeps one row per
(paper, reviewer) and the agreement analysis needs both reviewers' verdicts side
by side, in the form the reviewer actually produced them.

CSV columns: paper_id,decision,criteria,reason
"""
import argparse, csv, glob, os, sqlite3, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coder", required=True)
    ap.add_argument("--stage", default="screening")
    ap.add_argument("--topic-id", type=int, default=1)
    a = ap.parse_args()

    d = os.path.join(ROOT, "coding", a.stage, f"coder-{a.coder}", "decisions")
    files = sorted(glob.glob(os.path.join(d, "*.csv")))
    if not files:
        sys.exit(f"no decision files in {d}")
    con = sqlite3.connect(DB)
    cur = con.cursor()
    who = f"screener-{a.coder}" if a.stage == "screening" else f"assessor-{a.coder}"
    n, bad = 0, []
    seen = set()
    for f in files:
        for row in csv.DictReader(open(f)):
            try:
                pid = int(row["paper_id"])
            except (KeyError, ValueError, TypeError):
                bad.append((os.path.basename(f), str(row)[:70])); continue
            dec = (row.get("decision") or "").strip().lower()
            if dec not in ("include", "exclude"):
                bad.append((os.path.basename(f), f"{pid}: bad decision {dec!r}")); continue
            if (pid, who) in seen:
                continue
            seen.add((pid, who))
            cur.execute("""DELETE FROM screening_decisions
                           WHERE paper_id=? AND topic_id=? AND stage=? AND decided_by=?""",
                        (pid, a.topic_id, a.stage, who))
            cur.execute("""INSERT INTO screening_decisions
                           (paper_id,topic_id,stage,decision,reason,criteria_ids,decided_by)
                           VALUES (?,?,?,?,?,?,?)""",
                        (pid, a.topic_id, a.stage, dec, (row.get("reason") or "").strip()[:600],
                         (row.get("criteria") or "").strip(), who))
            n += 1
    con.commit()
    inc = cur.execute("""SELECT COUNT(*) FROM screening_decisions
                         WHERE topic_id=? AND stage=? AND decided_by=? AND decision='include'""",
                      (a.topic_id, a.stage, who)).fetchone()[0]
    print(f"{who}: loaded {n} decisions from {len(files)} files -- {inc} include, {n-inc} exclude")
    if bad:
        print(f"  {len(bad)} malformed rows skipped:")
        for f, r in bad[:10]:
            print(f"    {f}: {r}")

if __name__ == "__main__":
    main()
