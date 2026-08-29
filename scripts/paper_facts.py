#!/usr/bin/env python3
"""Regenerate every number the manuscript states, from the database.

The manuscript does not contain a typed number. It contains \\newcommand macros
that this script writes into paper/facts.tex, and the LaTeX source uses the
macros. A number in the paper that this script cannot produce is a number the
study cannot support, and the build breaks rather than printing a stale one.

Run: python3 scripts/paper_facts.py
Out: paper/facts.tex, and a human-readable dump on stdout.
"""
import collections, csv, json, os, sqlite3, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")
T = 1
con = sqlite3.connect(DB)
q = lambda s, *a: con.execute(s, a).fetchall()
one = lambda s, *a: (con.execute(s, a).fetchone() or [0])[0]

facts, notes = {}, []

def put(name, value, note=""):
    facts[name] = value
    if note:
        notes.append((name, value, note))

# ---------------------------------------------------------------- identification
put("NumProviders", 5, "arxiv, openalex, crossref, dblp, dblp-venue")
put("NumQueries", len(open(os.path.join(ROOT, "coding", "search-runs", "queries.tsv")).read().strip().splitlines()))
put("NumIdentified", one("SELECT COUNT(*) FROM papers"))
for src in ("arxiv", "openalex", "crossref", "dblp", "dblp-venue"):
    put(f"Num{src.replace('-','').capitalize()}", one("SELECT COUNT(*) FROM papers WHERE source=?", src))

cb = os.path.join(ROOT, "coding", "cap-binding.csv")
if os.path.exists(cb):
    rows = [r for r in csv.DictReader(open(cb)) if not r["error"]]
    tr = [r for r in rows if r["truncated"] == "True"]
    put("NumPairsQueried", len(rows))
    put("PctCapBound", round(100.0 * len(tr) / max(len(rows), 1)))

sf = os.path.join(ROOT, "coding", "scope-filter-report.json")
if os.path.exists(sf):
    r = json.load(open(sf))
    put("NumScopeRemoved", r["removed"])
    put("NumScreened", r["retained"])
    put("NumQgsRetained", sum(1 for v in r["validation"] if v["status"] == "retained"))
    put("NumQgsRetrieved", sum(1 for v in r["validation"] if v["status"] != "not_retrieved"))
    put("NumQgsTotal", len(r["validation"]))

# ---------------------------------------------------------------- screening
def dec(stage, who, d):
    return one("""SELECT COUNT(*) FROM screening_decisions
                  WHERE topic_id=? AND stage=? AND decided_by=? AND decision=?""", T, stage, who, d)

put("NumScreenIncludeA", dec("screening", "screener-A", "include"))
put("NumScreenExcludeA", dec("screening", "screener-A", "exclude"))
put("NumDoubleScreened", one("""SELECT COUNT(*) FROM (
      SELECT paper_id FROM screening_decisions WHERE topic_id=? AND stage='screening'
      GROUP BY paper_id HAVING COUNT(DISTINCT decided_by) > 1)""", T))

ag = os.path.join(ROOT, "coding", "screening-agreement.json")
if os.path.exists(ag):
    a = json.load(open(ag))
    put("ScreenKappa", a["kappa"]); put("ScreenAgreement", a["observed"])
    put("NumScreenDisagreements", a["disagreements"])

# ---------------------------------------------------------------- eligibility
put("NumFullTextAssessed", one("""SELECT COUNT(DISTINCT paper_id) FROM screening_decisions
                                  WHERE topic_id=? AND stage='eligibility'""", T))
put("NumIncluded", one("""SELECT COUNT(DISTINCT paper_id) FROM screening_decisions
                          WHERE topic_id=? AND stage='eligibility' AND decision='include'""", T))
put("NumEligExcluded", one("""SELECT COUNT(DISTINCT paper_id) FROM screening_decisions
                              WHERE topic_id=? AND stage='eligibility' AND decision='exclude'""", T))

# ---------------------------------------------------------------- classification
axes = [r[0] for r in q("SELECT DISTINCT axis FROM facet_schemes WHERE topic_id=?", T)]
put("NumAxes", len(axes))
put("NumAssignments", one("SELECT COUNT(*) FROM facet_assignments WHERE topic_id=?", T))
for ax in axes:
    for val, n in q("""SELECT value, COUNT(*) FROM facet_assignments
                       WHERE topic_id=? AND axis=? GROUP BY value""", T, ax):
        key = "N" + "".join(w.capitalize() for w in ax.split("_")) + \
              "".join(w.capitalize() for w in val.replace("-", "_").split("_"))
        put(key, n)

kp = os.path.join(ROOT, "coding", "agreement.csv")
if os.path.exists(kp):
    ks = list(csv.DictReader(open(kp)))
    for r in ks:
        key = "Kappa" + "".join(w.capitalize() for w in r["axis"].split("_"))
        put(key, r["cohens_kappa"])
    vals = [float(r["cohens_kappa"]) for r in ks]
    if vals:
        put("KappaMin", f"{min(vals):.2f}"); put("KappaMax", f"{max(vals):.2f}")
        put("KappaMean", f"{sum(vals)/len(vals):.2f}")
    dis = os.path.join(ROOT, "coding", "disagreements.csv")
    if os.path.exists(dis):
        put("NumFacetDisagreements", sum(1 for _ in csv.DictReader(open(dis))))

# ---------------------------------------------------------------- corpus profile
yrs = q("""SELECT p.year, COUNT(*) FROM papers p JOIN screening_decisions s
           ON s.paper_id=p.id AND s.topic_id=? AND s.stage='eligibility' AND s.decision='include'
           GROUP BY p.year ORDER BY p.year""", T)
if yrs:
    put("CorpusYearMin", yrs[0][0]); put("CorpusYearMax", yrs[-1][0])
    tot = sum(n for _, n in yrs)
    recent = sum(n for y, n in yrs if y and y >= 2025)
    put("PctSince2025", round(100.0 * recent / max(tot, 1)))

# ---------------------------------------------------------------- write
os.makedirs(os.path.join(ROOT, "paper"), exist_ok=True)
out = os.path.join(ROOT, "paper", "facts.tex")
with open(out, "w") as fh:
    fh.write("% Generated by scripts/paper_facts.py -- do not edit.\n")
    fh.write("% Every number in the manuscript is a macro defined here.\n")
    for k in sorted(facts):
        fh.write("\\newcommand{\\%s}{%s}\n" % (k, facts[k]))
for k in sorted(facts):
    print(f"  {k:34s} {facts[k]}")
print(f"\n{len(facts)} facts -> {out}")
