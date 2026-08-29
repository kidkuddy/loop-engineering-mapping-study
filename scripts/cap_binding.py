#!/usr/bin/env python3
"""How much of the corpus is a top-k sample rather than a complete answer?

Petersen's guidance is silent on result caps, but a mapping study whose queries
all returned exactly the cap is reporting a property of the provider's ranker
before it reports a property of the field. This script measures that instead of
asserting it: for every (query, provider) pair it records how many records the
provider claimed to match, how many it returned, and whether the return was
truncated.

Reads coding/search-runs/*.json. Writes coding/cap-binding.csv and prints the
summary numbers the manuscript quotes.
"""
import json, csv, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "coding", "search-runs")

rows = []
for path in sorted(glob.glob(os.path.join(RUNS, "Q*-*.json"))):
    base = os.path.basename(path)[:-5]
    m = re.match(r"(Q\d+)-(\w+)$", base)
    if not m:
        continue
    qid, provider = m.groups()
    try:
        d = json.load(open(path))
    except Exception:
        continue
    p = (d.get("providers") or [{}])[0]
    rows.append({
        "query_id": qid,
        "provider": provider,
        "found": p.get("found", 0) or 0,
        "matched": p.get("matched", 0) or 0,
        "truncated": bool(p.get("truncated")),
        "stored": d.get("stored", 0) or 0,
        "error": (p.get("error") or "")[:80],
    })

if not rows:
    sys.exit("no search-run files found -- run protocol/10-search.sh first")

out = os.path.join(ROOT, "coding", "cap-binding.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

ok = [r for r in rows if not r["error"]]
trunc = [r for r in ok if r["truncated"]]
print(f"pairs attempted        : {len(rows)}")
print(f"pairs that returned    : {len(ok)}")
print(f"pairs that errored     : {len(rows) - len(ok)}")
print(f"pairs truncated at cap : {len(trunc)}  ({100.0*len(trunc)/max(len(ok),1):.0f}% of returning pairs)")
for prov in sorted({r["provider"] for r in ok}):
    sub = [r for r in ok if r["provider"] == prov]
    st = [r for r in sub if r["truncated"]]
    med = sorted(r["matched"] for r in sub)[len(sub)//2] if sub else 0
    print(f"  {prov:10s} pairs={len(sub):3d} truncated={len(st):3d} median_matched={med}")
print(f"records stored (pre-dedup sum): {sum(r['stored'] for r in ok)}")
print(f"\nwrote {out}")
