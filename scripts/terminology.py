#!/usr/bin/env python3
"""How much of the retrieved literature actually uses the phrase this study is named after?

'Loop engineering' was surfaced by practitioners in June 2026. The study is a map
of the mechanisms the phrase denotes, not of the phrase. This script measures the
gap directly, so the paper can report a number instead of an impression.
"""
import json, os, re, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite"))
T = 1

rows = con.execute("SELECT id, title, COALESCE(abstract,''), year FROM papers").fetchall()
included = {r[0] for r in con.execute(
    """SELECT paper_id FROM screening_decisions WHERE topic_id=? AND stage='screening'
       AND decision='include' AND decided_by IN ('screener-A','adjudicated')""", (T,))}

PHRASES = {
    "loop engineering": re.compile(r"\bloop[- ]engineering\b", re.I),
    "agentic loop": re.compile(r"\bagentic loop", re.I),
    "agent loop": re.compile(r"\bagent(?:'s)? loop", re.I),
    "control loop": re.compile(r"\bcontrol loop", re.I),
    "context engineering": re.compile(r"\bcontext engineering\b", re.I),
    "prompt engineering": re.compile(r"\bprompt engineering\b", re.I),
}

# A phrase can be a homonym. "Loop engineering" has a long prior life in control
# and hardware engineering, so a raw hit count would overstate the agentic usage
# enormously. Records are therefore split by whether they are about language
# models at all, using the same technology terms as the scope filter.
TECH = re.compile(r"\b(llm|large language model|language model|foundation model|"
                  r"gpt-?[34]|chatgpt|agentic|ai agent|autonomous agent|generative ai|"
                  r"claude|gemini|llama)\b", re.I)

out = {}
for name, rx in PHRASES.items():
    hits = [r for r in rows if rx.search(r[1] or "") or rx.search(r[2] or "")]
    agentic = [r for r in hits if TECH.search((r[1] or "") + " " + (r[2] or ""))]
    inc = [r for r in hits if r[0] in included]
    out[name] = {
        "records_in_identified_set": len(hits),
        "of_which_about_language_models": len(agentic),
        "of_which_included_primary_studies": len(inc),
        "earliest_year_any_sense": min([r[3] for r in hits if r[3]], default=None),
        "earliest_year_language_model_sense": min([r[3] for r in agentic if r[3]], default=None),
        "examples": [r[1][:110] for r in inc[:5]],
    }

json.dump({"identified_total": len(rows), "included_total": len(included), "phrases": out},
          open(os.path.join(ROOT, "coding", "terminology.json"), "w"), indent=1)

print(f"identified records: {len(rows)}   included primary studies: {len(included)}\n")
print(f"{'phrase':22s} {'identified':>10s} {'LM-sense':>9s} {'in corpus':>10s} "
      f"{'1st any':>8s} {'1st LM':>7s}")
for k, v in out.items():
    print(f"{k:22s} {v['records_in_identified_set']:10d} "
          f"{v['of_which_about_language_models']:9d} "
          f"{v['of_which_included_primary_studies']:10d} "
          f"{str(v['earliest_year_any_sense']):>8s} "
          f"{str(v['earliest_year_language_model_sense']):>7s}")
