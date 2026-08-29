#!/usr/bin/env python3
"""Manual venue search (search strategy 3 of 3).

Petersen et al. (2015) list three study-identification strategies -- database
search, snowballing, and manual search of relevant venues -- and treat using all
three as the full-marks case. This is the third.

Venues were chosen as the places this literature actually appears: the machine
learning and NLP conferences where agent methods are published, the AI
conferences, and the software engineering venues, since the object of study is
an engineering practice and an SE audience is one of the two this map is written
for. Every (venue, term) pair is queried and its yield recorded, including the
pairs that returned nothing -- an empty venue is a reportable observation, not a
failed query to be dropped.

DBLP is the index used: its venue scoping is exact and it searches titles, so
this pass is precision-oriented by construction and complements the recall-
oriented database search.
"""
import json, os, ssl, sys, time, urllib.parse, urllib.request, sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_extra_providers import store, SSL_CTX, UA  # same schema, same fingerprint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")

VENUES = ["NeurIPS", "ICML", "ICLR", "ACL", "EMNLP", "NAACL", "AAAI", "IJCAI",
          "ICSE", "FSE", "ASE", "TOSEM", "TSE", "EMSE", "CHI", "ISSTA"]
TERMS = ["agentic", "agent loop", "self-refine", "self-correction", "reflection agent",
         "iterative refinement", "verifier", "orchestration", "autonomous agent",
         "multi-agent language model", "tool use agent", "planning agent"]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45, context=SSL_CTX) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(3 * (i + 1))

def main():
    con = sqlite3.connect(DB)
    out = os.path.join(ROOT, "coding", "venue-search")
    os.makedirs(out, exist_ok=True)
    log, total_new = [], 0
    for venue in VENUES:
        vnew = 0
        for term in TERMS:
            q = f"{term} venue:{venue}:"
            d = get("https://dblp.org/search/publ/api?" +
                    urllib.parse.urlencode({"q": q, "h": 50, "format": "json"}))
            hits = ((d or {}).get("result", {}).get("hits", {}) or {})
            papers = []
            for h in hits.get("hit", []):
                i = h.get("info", {})
                year = int(i["year"]) if str(i.get("year", "")).isdigit() else None
                if not year or not (2018 <= year <= 2026) or not i.get("title"):
                    continue
                a = i.get("authors", {}).get("author", [])
                a = a if isinstance(a, list) else [a]
                papers.append({
                    "external_id": i.get("key"), "doi": i.get("doi"), "title": i["title"].strip(),
                    "authors": "; ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in a),
                    "abstract": "", "year": year, "venue": i.get("venue") or venue,
                    "url": i.get("ee") or i.get("url"), "pdf_url": None, "source": "dblp-venue",
                })
            new, _ = store(con, 1, "dblp-venue", q, papers, int(hits.get("@total", 0)),
                           2018, 2026, 50)
            log.append({"venue": venue, "term": term, "hits": len(papers), "new": new})
            vnew += new
            time.sleep(0.35)
        print(f"  {venue:8s} new={vnew}")
        total_new += vnew
    json.dump(log, open(os.path.join(out, "venue-log.json"), "w"), indent=1)
    print(f"\ntotal new records from manual venue search: {total_new}")
    print(f"pairs queried: {len(log)}  pairs with zero hits: {sum(1 for l in log if l['hits']==0)}")

if __name__ == "__main__":
    main()
