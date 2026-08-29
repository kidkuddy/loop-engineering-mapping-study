#!/usr/bin/env python3
"""PRISMA-style flow figure, drawn from the database rather than typed.

PRISMA 2020 item 16a asks for the number of reports assessed for eligibility,
not only the number excluded, and provides for records removed by automation
tools before screening. Both appear here.
"""
import json, os, sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite"))
one = lambda q, *a: (con.execute(q, a).fetchone() or [0])[0]

identified = one("SELECT COUNT(*) FROM papers")
by_src = dict(con.execute("SELECT source, COUNT(*) FROM papers GROUP BY 1"))
sf = json.load(open(os.path.join(ROOT, "coding", "scope-filter-report.json")))
removed, screened = sf["removed"], sf["retained"]
inc = one("""SELECT COUNT(*) FROM (
  SELECT paper_id FROM screening_decisions WHERE topic_id=1 AND stage='screening'
    AND decision='include' AND decided_by='adjudicated'
  UNION
  SELECT paper_id FROM screening_decisions s1 WHERE topic_id=1 AND stage='screening'
    AND decision='include' AND decided_by='screener-A'
    AND NOT EXISTS (SELECT 1 FROM screening_decisions s2 WHERE s2.paper_id=s1.paper_id
      AND s2.topic_id=1 AND s2.stage='screening' AND s2.decided_by='adjudicated'))""")
excluded = screened - inc
try:
    v = json.load(open(os.path.join(ROOT, "coding", "validation", "summary.json")))
    vline = f"full-text validation sample: {v['assessed']} assessed,\n{v['excluded_at_full_text']} ineligible at full text"
except Exception:
    vline = "full-text validation sample"

db = sum(by_src.get(k, 0) for k in ("arxiv", "openalex", "crossref", "dblp"))
vs = by_src.get("dblp-venue", 0)

boxes = [
    (f"Records identified ($n={identified}$)\n"
     f"database search {db}, manual venue search {vs}", "#e8eef7"),
    (f"Removed by automated scope rule R1\n($n={removed}$)", "#f6ecec"),
    (f"Records screened on title and abstract\n($n={screened}$)", "#e8eef7"),
    (f"Excluded at screening ($n={excluded}$)", "#f6ecec"),
    (f"Included in the map ($n={inc}$)", "#e6f0e8"),
    (vline, "#f2f0e6"),
]
fig, ax = plt.subplots(figsize=(3.4, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 26); ax.axis("off")
ys = [23.0, 19.2, 15.6, 11.8, 8.2, 4.0]
main = [0, 2, 4, 5]
for i, ((txt, col), y) in enumerate(zip(boxes, ys)):
    x, w = (0.3, 6.4) if i in main else (3.4, 6.3)
    h = 2.3 if "\n" in txt else 1.7
    ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h, boxstyle="round,pad=0.12",
                                fc=col, ec="#6b7a90", lw=.8))
    ax.text(x + w / 2, y, txt, ha="center", va="center", fontsize=6.2)
arrow = lambda a, b, **k: ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>",
                                                       mutation_scale=8, lw=.8, color="#6b7a90", **k))
for a, b in ((0, 2), (2, 4), (4, 5)):
    arrow((3.5, ys[a] - 1.15), (3.5, ys[b] + 1.15))
for a, b in ((0, 1), (2, 3)):
    arrow((3.5, ys[a] - 1.6), (3.4, ys[b]))
fig.savefig(os.path.join(ROOT, "figures", "flow.pdf"), bbox_inches="tight")
print(f"identified {identified} -> removed {removed} -> screened {screened} -> included {inc}")
print(f"wrote {ROOT}/figures/flow.pdf")
