#!/usr/bin/env python3
"""Cohen's kappa between the two independent coders, per facet axis.

Why this file exists rather than a column in the database: phd's
facet_assignments table is UNIQUE(paper_id, topic_id, axis, value), so two
coders who disagree on an axis produce two rows that are indistinguishable from
one coder assigning two labels. Inter-rater evidence therefore lives here, as
the coders' raw per-paper labels, and only the adjudicated label is written back
to the database.

Reads coding/coder-A.csv and coding/coder-B.csv, each: paper_id,axis,value
Writes coding/agreement.csv and coding/disagreements.csv, and prints the table
the manuscript quotes.
"""
import csv, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = lambda n: os.path.join(ROOT, "coding", n)

def load(path):
    d = {}
    with open(path) as fh:
        for row in csv.DictReader(fh):
            d[(int(row["paper_id"]), row["axis"])] = row["value"].strip()
    return d

try:
    A, B = load(C("coder-A.csv")), load(C("coder-B.csv"))
except FileNotFoundError as e:
    sys.exit(f"missing {e.filename} -- run the two classification passes first")

axes = sorted({a for _, a in A} | {a for _, a in B})
summary, disagreements = [], []

for axis in axes:
    keys = sorted(k for k in set(A) & set(B) if k[1] == axis)
    if not keys:
        continue
    a = [A[k] for k in keys]
    b = [B[k] for k in keys]
    n = len(keys)
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    expected = sum((ca[v]/n) * (cb[v]/n) for v in set(ca) | set(cb))
    kappa = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    summary.append({
        "axis": axis, "n": n,
        "observed_agreement": round(observed, 3),
        "expected_agreement": round(expected, 3),
        "cohens_kappa": round(kappa, 3),
        "interpretation": interp(kappa) if (interp := globals().get("interp")) else "",
    })
    for k in keys:
        if A[k] != B[k]:
            disagreements.append({"paper_id": k[0], "axis": axis,
                                  "coder_A": A[k], "coder_B": B[k]})

def label(k):
    return ("poor" if k < 0.0 else "slight" if k < .21 else "fair" if k < .41
            else "moderate" if k < .61 else "substantial" if k < .81 else "almost perfect")
for s in summary:
    s["interpretation"] = label(s["cohens_kappa"])

with open(C("agreement.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
with open(C("disagreements.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["paper_id","axis","coder_A","coder_B"])
    w.writeheader(); w.writerows(disagreements)

print(f"{'axis':24s} {'n':>4s} {'obs':>6s} {'kappa':>7s}  interpretation")
for s in summary:
    print(f"{s['axis']:24s} {s['n']:4d} {s['observed_agreement']:6.3f} "
          f"{s['cohens_kappa']:7.3f}  {s['interpretation']}")
tot = sum(s["n"] for s in summary)
print(f"\n{len(disagreements)} disagreements over {tot} double-coded assignments "
      f"({100.0*len(disagreements)/max(tot,1):.1f}%) -- all adjudicated, see coding/adjudication.csv")
