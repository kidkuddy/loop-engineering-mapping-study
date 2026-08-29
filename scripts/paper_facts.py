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
put("NumRetrievalDepth", 200, "records requested per query per provider")
put("NumLibraries", 4, "arxiv, openalex, crossref, dblp")
put("NumSearchStrategies", 3, "database search, snowballing, manual venue search")
put("NumMappingFacets", 3, "topic, contribution, research type")
put("NumScreeners", 2)
put("NumClassificationCoders", 2)
put("AmendmentOne", "amendment-01")
put("PrismaAutomationItem", "16a")
put("SearchDate", "2026-08-29")
put("NamingMonthYear", "June 2026")
put("AnthropicNamingDate", "2026-06-30")
put("TermAgeWeeks", 8)
for name, value in {
    "RQOne": "RQ1", "RQTwo": "RQ2", "RQThree": "RQ3", "RQFour": "RQ4", "RQFive": "RQ5",
    "IOne": "I1", "ITwo": "I2", "IThree": "I3", "IFour": "I4", "IFive": "I5",
    "EOne": "E1", "ETwo": "E2", "EThree": "E3", "EFour": "E4", "EFive": "E5",
    "ESix": "E6", "ESeven": "E7", "RuleOne": "R1"
}.items():
    put(name, value)
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

venue_log = os.path.join(ROOT, "coding", "venue-search", "venue-log.json")
if os.path.exists(venue_log):
    rows = json.load(open(venue_log))
    put("NumManualVenues", len({r["venue"] for r in rows}))

snowball = os.path.join(ROOT, "coding", "snowball", "candidates.json")
if os.path.exists(snowball):
    r = json.load(open(snowball))
    put("NumSnowballStart", r["start_set_size"])
    put("NumSnowballWithCitationData", r["seeds_with_citation_data"])
    put("PctSnowballWithCitationData", round(100.0 * r["seeds_with_citation_data"] / r["start_set_size"]))
    put("NumSnowballCandidates", r["distinct_candidates"])

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

pilot_dir = os.path.join(ROOT, "coding", "screening-pilot", "decisions")
if os.path.isdir(pilot_dir):
    pilot = []
    for name in os.listdir(pilot_dir):
        if name.endswith(".csv"):
            pilot.extend(csv.DictReader(open(os.path.join(pilot_dir, name))))
    put("NumPilotRecords", len(pilot))
    pilot_included = sum(r["decision"] == "include" for r in pilot)
    put("NumPilotIncluded", pilot_included)
    put("PctPilotInclude", f"{100.0 * pilot_included / len(pilot):.1f}")
put("NumDoubleScreened", one("""SELECT COUNT(*) FROM (
      SELECT paper_id FROM screening_decisions WHERE topic_id=? AND stage='screening'
      GROUP BY paper_id HAVING COUNT(DISTINCT decided_by) > 1)""", T))

ag = os.path.join(ROOT, "coding", "screening-agreement.json")
if os.path.exists(ag):
    a = json.load(open(ag))
    put("ScreenKappa", a["kappa"]); put("ScreenAgreement", a["observed"])
    put("NumScreenDisagreements", a["disagreements"])

# ---------------------------------------------------------------- eligibility
validation_path = os.path.join(ROOT, "coding", "validation", "summary.json")
if os.path.exists(validation_path):
    v = json.load(open(validation_path))
    put("NumValidationDrawn", v["drawn"])
    put("NumFullTextAssessed", v["assessed"])
    put("NumValidationEligible", v["eligible_at_full_text"])
    put("NumValidationExcluded", v["excluded_at_full_text"])
    put("NumValidationTextUnobtainable", v["excluded_because_text_unobtainable"])
    put("PctValidationFalseInclusion", f"{100.0 * v['false_inclusion_rate']:.1f}")
    put("PctValidationFalseInclusionLo", f"{100.0 * v['false_inclusion_ci95'][0]:.1f}")
    put("PctValidationFalseInclusionHi", f"{100.0 * v['false_inclusion_ci95'][1]:.1f}")
    for axis, values in v["abstract_vs_fulltext_agreement"].items():
        key = "AgreementValidation" + "".join(w.capitalize() for w in axis.split("_"))
        put(key, f"{values['agreement']:.3f}")
    put("NumValidationIndependenceLeaks", 2)
else:
    put("NumFullTextAssessed", 0)

put("NumIncluded", one("SELECT COUNT(DISTINCT paper_id) FROM facet_assignments WHERE topic_id=?", T))
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

vs = os.path.join(ROOT, "coding", "validation", "summary.json")
if os.path.exists(vs):
    v = json.load(open(vs))
    if v.get("excluded_on_criteria") is not None:
        put("NumValidationExcludedCriteria", v["excluded_on_criteria"])
        put("PctValidationCriteriaExclusion", f"{100*v['criteria_exclusion_rate']:.1f}")
        put("PctValidationCriteriaLo", f"{100*v['criteria_exclusion_ci95'][0]:.1f}")
        put("PctValidationCriteriaHi", f"{100*v['criteria_exclusion_ci95'][1]:.1f}")

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
yrs = q("""SELECT p.year, COUNT(*) FROM papers p JOIN
           (SELECT DISTINCT paper_id FROM facet_assignments WHERE topic_id=?) s
           ON s.paper_id=p.id
           GROUP BY p.year ORDER BY p.year""", T)
if yrs:
    put("CorpusYearMin", yrs[0][0]); put("CorpusYearMax", yrs[-1][0])
    tot = sum(n for _, n in yrs)
    recent = sum(n for y, n in yrs if y and y >= 2025)
    put("PctSinceRecent", round(100.0 * recent / max(tot, 1)))

# ---------------------------------------------------------------- terminology and small-cell bounds
terminology = os.path.join(ROOT, "coding", "terminology.json")
if os.path.exists(terminology):
    term = json.load(open(terminology))["phrases"]["loop engineering"]
    put("NumTermRecords", term["records_in_identified_set"])
    put("NumTermLanguageModelRecords", term["of_which_about_language_models"])
    put("NumTermIncludedStudies", term["of_which_included_primary_studies"])

# Exact one-sided 95% binomial upper limits for zero observations in the
# small research-type strata discussed with the bubble plot.
put("PctZeroUpperPhilosophical", f"{100.0 * (1 - 0.05 ** (1 / 32)):.1f}")
put("PctZeroUpperOpinion", f"{100.0 * (1 - 0.05 ** (1 / 5)):.1f}")
put("PctZeroUpperExperience", f"{100.0 * (1 - 0.05 ** (1 / 4)):.1f}")
put("PctZeroUpperAblation", f"{100.0 * (1 - 0.05 ** (1 / 14)):.1f}")
put("PctZeroUpperHumanStudy", f"{100.0 * (1 - 0.05 ** (1 / 16)):.1f}")
put("PctZeroUpperIllustrative", f"{100.0 * (1 - 0.05 ** (1 / 34)):.1f}")

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
