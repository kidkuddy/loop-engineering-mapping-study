#!/usr/bin/env python3
"""Flatten each coder's classification CSVs into the long form kappa.py expects,
and report coverage so a short batch cannot silently shrink the agreement base.

Writes coding/coder-A.csv and coding/coder-B.csv as paper_id,axis,value
(coder 1 -> A, coder 2 -> B).
"""
import csv, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXES = ["loop_mechanism", "contribution_type", "research_type",
        "evaluation_strategy", "human_role", "venue_type"]

for coder, out in (("1", "coder-A.csv"), ("2", "coder-B.csv")):
    d = os.path.join(ROOT, "coding", "classification", f"coder-{coder}", "labels")
    files = sorted(glob.glob(os.path.join(d, "*.csv")))
    rows, bad, papers = [], 0, set()
    for f in files:
        for r in csv.DictReader(open(f)):
            try:
                pid = int(r["paper_id"])
            except (KeyError, ValueError, TypeError):
                bad += 1; continue
            papers.add(pid)
            for a in AXES:
                v = (r.get(a) or "").strip()
                if v:
                    rows.append({"paper_id": pid, "axis": a, "value": v})
                else:
                    bad += 1
    with open(os.path.join(ROOT, "coding", out), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["paper_id", "axis", "value"])
        w.writeheader(); w.writerows(rows)
    print(f"coder-{coder}: {len(files)} files, {len(papers)} papers, "
          f"{len(rows)} labels, {bad} blank/malformed -> coding/{out}")
