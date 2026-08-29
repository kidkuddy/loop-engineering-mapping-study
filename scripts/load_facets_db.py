#!/usr/bin/env python3
"""Write the adjudicated facet labels into the database.

Only adjudicated labels enter the map. Where the two coders agreed, the agreed
value is the adjudicated value; where they differed, the adjudicator's value is.
Both coders' raw labels stay in coding/coder-A.csv and coding/coder-B.csv, which
is where the agreement analysis reads from -- the database's
UNIQUE(paper_id, topic_id, axis, value) cannot represent two coders disagreeing.
"""
import csv, glob, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite")); cur = con.cursor()
T = 1

load = lambda p: {(int(r["paper_id"]), r["axis"]): r["value"] for r in csv.DictReader(open(p))}
A = load(os.path.join(ROOT, "coding", "coder-A.csv"))
B = load(os.path.join(ROOT, "coding", "coder-B.csv"))

resolved = {}
for f in glob.glob(os.path.join(ROOT, "coding", "facet-adjudication", "*-resolved.csv")):
    for r in csv.DictReader(open(f)):
        resolved[(int(r["paper_id"]), r["axis"])] = r["adjudicated"].strip()

allowed = {a: {v.strip() for v in s.split(",")} for a, s in
           con.execute("SELECT axis, allowed FROM facet_schemes WHERE topic_id=?", (T,))}

cur.execute("DELETE FROM facet_assignments WHERE topic_id=? AND assigned_by='adjudicated'", (T,))
n, agreed, adj, missing, bad = 0, 0, 0, [], []
for key in sorted(set(A) | set(B)):
    pid, axis = key
    if key in resolved:
        val, src = resolved[key], "adjudicated (disagreement resolved)"
        adj += 1
    elif A.get(key) and A.get(key) == B.get(key):
        val, src = A[key], "both coders agreed"
        agreed += 1
    else:
        missing.append(key); continue
    if axis not in allowed or val not in allowed[axis]:
        bad.append((pid, axis, val)); continue
    cur.execute("""INSERT INTO facet_assignments (paper_id,topic_id,axis,value,justification,assigned_by)
                   VALUES (?,?,?,?,?,'adjudicated')""", (pid, T, axis, val, src))
    n += 1
con.commit()
print(f"written : {n} adjudicated assignments ({agreed} by agreement, {adj} by adjudication)")
if missing:
    print(f"UNRESOLVED disagreements still pending adjudication: {len(missing)}")
    for k in missing[:8]:
        print(f"   paper {k[0]} axis {k[1]}: A={A.get(k)!r} B={B.get(k)!r}")
if bad:
    print(f"REJECTED values not in the declared whitelist: {len(bad)}")
    for p, a, v in bad[:8]:
        print(f"   paper {p} axis {a}: {v!r}")
