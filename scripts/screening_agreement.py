#!/usr/bin/env python3
"""Cohen's kappa between the two screeners, over the double-screened sample.

Screening reliability and classification reliability are separate claims about
separate stages, and a kappa on one says nothing about the other. This computes
the screening one; scripts/kappa.py computes the classification one.

Reads screening_decisions for papers carrying decisions from both screeners,
writes coding/screening-agreement.json, and lists the disagreements so that the
adjudication pass has an explicit worklist.
"""
import collections, json, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite"))

rows = con.execute("""
    SELECT paper_id, decided_by, decision FROM screening_decisions
    WHERE topic_id = 1 AND stage = 'screening'
      AND decided_by IN ('screener-A','screener-B')""").fetchall()

by = collections.defaultdict(dict)
for pid, who, dec in rows:
    by[pid][who] = dec
both = {p: d for p, d in by.items() if len(d) == 2}
if not both:
    raise SystemExit("no papers carry decisions from both screeners yet")

a = [both[p]["screener-A"] for p in sorted(both)]
b = [both[p]["screener-B"] for p in sorted(both)]
n = len(a)
obs = sum(x == y for x, y in zip(a, b)) / n
ca, cb = collections.Counter(a), collections.Counter(b)
exp = sum((ca[v] / n) * (cb[v] / n) for v in set(ca) | set(cb))
kappa = (obs - exp) / (1 - exp) if exp < 1 else 1.0
label = ("poor" if kappa < 0 else "slight" if kappa < .21 else "fair" if kappa < .41
         else "moderate" if kappa < .61 else "substantial" if kappa < .81 else "almost perfect")

dis = [{"paper_id": p, "screener_A": both[p]["screener-A"], "screener_B": both[p]["screener-B"]}
       for p in sorted(both) if both[p]["screener-A"] != both[p]["screener-B"]]

out = {"double_screened": n, "observed": round(obs, 3), "expected": round(exp, 3),
       "kappa": round(kappa, 3), "interpretation": label,
       "disagreements": len(dis), "disagreement_list": dis,
       "screened_total_A": sum(1 for _, w, _ in rows if w == "screener-A")}
json.dump(out, open(os.path.join(ROOT, "coding", "screening-agreement.json"), "w"), indent=1)
print(f"double-screened papers : {n}")
print(f"observed agreement     : {obs:.3f}")
print(f"Cohen's kappa          : {kappa:.3f} ({label})")
print(f"disagreements          : {len(dis)}")
