#!/usr/bin/env python3
"""Cut the records that survived the scope filter into screening batches.

Each batch file is exactly the evidence its screener saw -- id, title, year,
venue, abstract -- and is kept in the repository. Petersen's repeatability
category asks for the process to be reported in enough detail to redo; a package
of decisions without the text those decisions were made from documents the
conclusion rather than the inference, so the inputs ship alongside the outputs.
"""
import argparse, csv, json, os, random, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coder", default="A")
    ap.add_argument("--size", type=int, default=40)
    ap.add_argument("--sample", type=float, default=1.0,
                    help="fraction of retained records to draw (coder B draws a sample)")
    ap.add_argument("--seed", type=int, default=20260829)
    ap.add_argument("--also-include-ids", default="",
                    help="file of paper ids that must be in the draw regardless of sampling")
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    with open(os.path.join(ROOT, "coding", "scope-filter.csv"), newline="") as fh:
        retained = sorted({int(r["paper_id"]) for r in csv.DictReader(fh)
                           if r["retained"] == "True"})

    if a.sample < 1.0:
        rng = random.Random(a.seed)
        n = int(round(len(retained) * a.sample))
        pick = set(rng.sample(retained, n))
        if a.also_include_ids and os.path.exists(a.also_include_ids):
            pick |= {int(x) for x in open(a.also_include_ids).read().split() if x.strip().isdigit()}
        retained = sorted(pick)

    outdir = os.path.join(ROOT, "coding", "screening", f"coder-{a.coder}", "batches")
    os.makedirs(outdir, exist_ok=True)
    rows = {r[0]: r for r in con.execute(
        "SELECT id,title,COALESCE(year,0),COALESCE(venue,''),COALESCE(abstract,''),COALESCE(source,'') FROM papers")}

    n = 0
    for i in range(0, len(retained), a.size):
        chunk = [rows[p] for p in retained[i:i + a.size] if p in rows]
        batch = [{"paper_id": r[0], "title": r[1], "year": r[2], "venue": r[3],
                  "source": r[5], "abstract": r[4][:2200]} for r in chunk]
        path = os.path.join(outdir, f"batch-{n:03d}.json")
        json.dump(batch, open(path, "w"), indent=1)
        n += 1
    print(f"coder {a.coder}: {len(retained)} records -> {n} batches of <= {a.size} in {outdir}")

if __name__ == "__main__":
    main()
