#!/usr/bin/env python3
"""Draw the full-text validation sample, with a fixed seed, and commit the ids.

Per protocol/classification-design.md: a random sample of the screening
survivors is assessed at full text, to measure (a) the false-inclusion rate of
abstract-level screening and (b) how far abstract-based facet labels agree with
labels assigned from the full text.

The seed is fixed and the drawn ids are written before the assessment runs, so
the sample cannot be adjusted after its results are known.
"""
import argparse, csv, json, os, random, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=60)
ap.add_argument("--seed", type=int, default=20260829)
ap.add_argument("--topic-id", type=int, default=1)
a = ap.parse_args()

con = sqlite3.connect(DB)
survivors = sorted(r[0] for r in con.execute(
    """SELECT DISTINCT paper_id FROM screening_decisions
       WHERE topic_id=? AND stage='screening' AND decision='include'
         AND decided_by='screener-A'""", (a.topic_id,)))
if not survivors:
    raise SystemExit("no screening survivors -- load screener-A decisions first")

n = min(a.n, len(survivors))
sample = sorted(random.Random(a.seed).sample(survivors, n))

out = os.path.join(ROOT, "coding", "validation")
os.makedirs(out, exist_ok=True)
json.dump({"seed": a.seed, "n_requested": a.n, "n_drawn": n,
           "population_size": len(survivors), "paper_ids": sample},
          open(os.path.join(out, "sample.json"), "w"), indent=1)

rows = {r[0]: r for r in con.execute(
    "SELECT id,title,COALESCE(year,0),COALESCE(venue,''),COALESCE(pdf_url,'') FROM papers")}
with open(os.path.join(out, "sample.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["paper_id", "title", "year", "venue", "has_pdf_url"])
    for pid in sample:
        r = rows.get(pid)
        if r:
            w.writerow([r[0], r[1], r[2], r[3], bool(r[4])])

print(f"population (screening survivors): {len(survivors)}")
print(f"validation sample drawn         : {n}  (seed {a.seed})")
print(f"with a pdf url                  : {sum(1 for p in sample if rows.get(p) and rows[p][4])}")
print(f"wrote {out}/sample.json and sample.csv")
