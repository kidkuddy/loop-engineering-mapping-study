#!/usr/bin/env python3
"""Cut the included corpus into classification batches, one set per coder.

Both coders receive identical batches. They work independently and never see
each other's labels; the agreement analysis depends on that being true, so the
two coders' outputs live in separate directories and each coder's task forbids
reading the other's.
"""
import argparse, csv, json, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

ap = argparse.ArgumentParser()
ap.add_argument("--size", type=int, default=25)
ap.add_argument("--topic-id", type=int, default=1)
a = ap.parse_args()

con = sqlite3.connect(DB)
included = sorted(r[0] for r in con.execute(
    """SELECT DISTINCT paper_id FROM screening_decisions
       WHERE topic_id=? AND stage='screening' AND decision='include'
         AND decided_by='adjudicated'
       UNION
       SELECT DISTINCT paper_id FROM screening_decisions s1
       WHERE topic_id=? AND stage='screening' AND decision='include'
         AND decided_by='screener-A'
         AND NOT EXISTS (SELECT 1 FROM screening_decisions s2
                         WHERE s2.paper_id=s1.paper_id AND s2.topic_id=s1.topic_id
                           AND s2.stage='screening' AND s2.decided_by='adjudicated')""",
    (a.topic_id, a.topic_id)))

rows = {r[0]: r for r in con.execute(
    "SELECT id,title,COALESCE(year,0),COALESCE(venue,''),COALESCE(abstract,''),COALESCE(source,'') FROM papers")}

json.dump(included, open(os.path.join(ROOT, "coding", "included-ids.json"), "w"))
with open(os.path.join(ROOT, "coding", "included.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["paper_id", "title", "year", "venue", "source"])
    for p in included:
        if p in rows:
            w.writerow([p, rows[p][1], rows[p][2], rows[p][3], rows[p][5]])

n = 0
for coder in ("1", "2"):
    outdir = os.path.join(ROOT, "coding", "classification", f"coder-{coder}", "batches")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "coding", "classification", f"coder-{coder}", "labels"), exist_ok=True)
    n = 0
    for i in range(0, len(included), a.size):
        chunk = [rows[p] for p in included[i:i + a.size] if p in rows]
        json.dump([{"paper_id": r[0], "title": r[1], "year": r[2], "venue": r[3],
                    "source": r[5], "abstract": r[4][:2400]} for r in chunk],
                  open(os.path.join(outdir, f"batch-{n:03d}.json"), "w"), indent=1)
        n += 1
print(f"included corpus: {len(included)} papers -> {n} batches of <= {a.size}, for each of 2 coders")
