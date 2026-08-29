#!/usr/bin/env python3
"""Summarise the full-text validation sample.

Two numbers the map needs and cannot get any other way:
  1. the false-inclusion rate of abstract-level screening, with a Wilson interval;
  2. per-axis agreement between the abstract-based adjudicated label and the
     label an assessor assigned from the full text.
"""
import csv, glob, json, math, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXES = ["loop_mechanism", "contribution_type", "research_type",
        "evaluation_strategy", "human_role", "venue_type"]
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite"))

adjudicated = {}
for pid, axis, val in con.execute(
        "SELECT paper_id, axis, value FROM facet_assignments WHERE topic_id=1 AND assigned_by='adjudicated'"):
    adjudicated.setdefault(pid, {})[axis] = val

rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "coding", "validation", "decisions", "*.csv"))):
    try:
        rows.extend(list(csv.DictReader(open(f))))
    except Exception:
        pass
rows = [r for r in rows if (r.get("paper_id") or "").strip().isdigit()]

drawn = json.load(open(os.path.join(ROOT, "coding", "validation", "sample.json")))["paper_ids"]
assessed = sorted({int(r["paper_id"]) for r in rows})
inc = [r for r in rows if (r.get("eligible") or "").strip().lower() == "include"]
exc = [r for r in rows if (r.get("eligible") or "").strip().lower() == "exclude"]
f2 = [r for r in exc if "F2" in (r.get("elig_criteria") or "")]

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

n_ass = len(assessed)
n_exc = len(exc)
lo, hi = wilson(n_exc, n_ass)

agree = {}
for a in AXES:
    pairs = [(adjudicated.get(int(r["paper_id"]), {}).get(a), (r.get(a) or "").strip())
             for r in rows]
    pairs = [(x, y) for x, y in pairs if x and y]
    agree[a] = {"n": len(pairs),
                "agreement": round(sum(x == y for x, y in pairs) / len(pairs), 3) if pairs else None}

out = {"drawn": len(drawn), "assessed": n_ass,
       "eligible_at_full_text": len(inc), "excluded_at_full_text": n_exc,
       "excluded_because_text_unobtainable": len(f2),
       "false_inclusion_rate": round(n_exc / n_ass, 3) if n_ass else None,
       "false_inclusion_ci95": [round(lo, 3), round(hi, 3)],
       "abstract_vs_fulltext_agreement": agree}
json.dump(out, open(os.path.join(ROOT, "coding", "validation", "summary.json"), "w"), indent=1)

print(f"drawn {len(drawn)}, assessed {n_ass}")
print(f"eligible at full text : {len(inc)}")
print(f"excluded at full text : {n_exc}  (of which text unobtainable: {len(f2)})")
if n_ass:
    print(f"false-inclusion rate  : {100*n_exc/n_ass:.1f}%  95% CI [{100*lo:.1f}, {100*hi:.1f}]")
print("\nabstract-based label vs full-text label:")
for a in AXES:
    v = agree[a]
    print(f"  {a:24s} n={v['n']:3d}  agreement={v['agreement']}")
