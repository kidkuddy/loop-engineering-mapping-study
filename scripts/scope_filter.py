#!/usr/bin/env python3
"""Automated scope exclusion at identification, before title/abstract screening.

PRISMA 2020 provides for records removed by automation tools prior to screening
(item 16a), and this is that step. It exists because the database search is
deliberately broad -- four libraries, 23 queries, generous caps -- and the
resulting record set contains a large, mechanically identifiable class of false
positives: work about loops that are not the control loop of a language-model
agent (control theory, RL environment stepping, speech and language corpora,
compiler loop transformation).

The rule automates exactly ONE screening criterion, E1, and only in its
unambiguous direction. It never decides inclusion. Anything that passes goes to
a screener, who applies the full criteria.

RULE R1. A record is retained iff its title or abstract contains
  (A) at least one TECHNOLOGY term -- the record is about language models or
      language-model agents at all; and
  (B) at least one CONTROL-STRUCTURE term -- the record mentions something that
      returns, checks, repeats, remembers or halts.
Both lists are given in full below and are the published rule.

VALIDATION. The rule is checked against the quasi-gold standard declared in
protocol/quasi-gold-standard.md before any record is removed. If the rule drops
a known-relevant paper it is a bad rule; the script exits non-zero and removes
nothing. The check and its result are reported in the manuscript.
"""
import csv, json, os, sqlite3, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

TECHNOLOGY = [
    'llm', 'large language model', 'language model', 'foundation model', 'gpt-3', 'gpt-4', 'gpt4',
    'chatgpt', 'agentic', 'ai agent', 'autonomous agent', 'llm-based', 'language-model',
    'generative ai', 'claude', 'gemini', 'llama', 'vision-language model', 'multimodal model',
    'instruction-tuned',
]
CONTROL = [
    'loop', 'iterat', 'refine', 'refinement', 'self-correct', 'self-verif', 'self-improv',
    'self-refl', 'critic', 'verifier', 'verification', 'reflexion', 'reflection', 'retry',
    're-attempt', 'replan', 're-plan', 'multi-turn', 'multi-step', 'trajector', 'orchestrat',
    'stopping criteri', 'termination', 'feedback', 'revise', 'revision', 'react',
    'plan-and-execute', 'scaffold', 'controller', 'agentic workflow', 'tool-use loop',
    'closed-loop', 'human-in-the-loop', 'episodic memory', 'long-horizon', 'autonomous agent',
    'error recovery', 'failure recovery', 'rollback', 'backtrack',
]
# Title fragments of the pre-declared test set, used only to validate the rule.
QGS = {
    'react: synergizing': 'ReAct', 'reflexion: language agents': 'Reflexion',
    'self-refine: iterative': 'Self-Refine', 'tree of thoughts': 'Tree of Thoughts',
    'language agent tree search': 'LATS', 'voyager: an open-ended': 'Voyager',
    'autogen: enabling': 'AutoGen', 'critic: large language models can self-correct': 'CRITIC',
    'generative agents: interactive': 'Generative Agents',
    'cannot self-correct reasoning yet': 'Cannot Self-Correct',
}

def passes(text):
    return (any(t in text for t in TECHNOLOGY), any(c in text for c in CONTROL))

def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT id, title, COALESCE(abstract,'') FROM papers").fetchall()
    keep, drop = [], []
    for pid, title, abstract in rows:
        text = f"{title} {abstract}".lower()
        a, b = passes(text)
        (keep if (a and b) else drop).append(
            {"paper_id": pid, "title": title, "technology_term": a, "control_term": b,
             "retained": a and b})

    kept_ids = {r["paper_id"] for r in keep}
    report = {"identified": len(rows), "retained": len(keep), "removed": len(drop),
              "rule": {"technology_terms": TECHNOLOGY, "control_terms": CONTROL},
              "validation": []}
    failed = []
    for frag, name in QGS.items():
        hit = next((r for r in rows if frag in r[1].lower()), None)
        status = ("not_retrieved" if not hit
                  else "retained" if hit[0] in kept_ids else "REMOVED")
        report["validation"].append({"paper": name, "status": status})
        if status == "REMOVED":
            failed.append(name)

    with open(os.path.join(ROOT, "coding", "scope-filter.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["paper_id", "title", "technology_term",
                                           "control_term", "retained"])
        w.writeheader(); w.writerows(keep + drop)
    json.dump(report, open(os.path.join(ROOT, "coding", "scope-filter-report.json"), "w"), indent=1)

    print(f"identified : {len(rows)}")
    print(f"retained   : {len(keep)} ({100*len(keep)/max(len(rows),1):.0f}%)")
    print(f"removed    : {len(drop)} ({100*len(drop)/max(len(rows),1):.0f}%)")
    print("\nvalidation against the quasi-gold standard:")
    for v in report["validation"]:
        print(f"  {v['paper']:22s} {v['status']}")
    if failed:
        sys.exit(f"\nRULE REJECTED -- it removes known-relevant papers: {failed}")
    print("\nrule retains every retrieved test-set paper; safe to apply.")

if __name__ == "__main__":
    main()
