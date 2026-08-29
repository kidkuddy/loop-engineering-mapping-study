#!/usr/bin/env python3
"""Manual venue search (search strategy 3 of 3), over DBLP.

Petersen et al. (2015) count three study-identification strategies -- database
search, snowballing, manual venue search -- and treat using all three as the
full-marks case. This is the third.

A NOTE ON A DEFECT THIS SCRIPT FIXES. An earlier run recorded 'found=0' for
venue/term pairs that had in fact returned results minutes earlier, because DBLP
had begun refusing connections and the failure was being written as an empty
result. An empty venue is a finding; a throttled connection is not, and the two
must never be recorded the same way. Here a pair is written ONLY when the HTTP
call succeeds. Pairs whose call fails are retried, and any pair still failing at
the end is reported as not-attempted rather than as zero.

Venues: the ML, NLP and AI conferences where agent methods are published, plus
the software engineering venues, because the object of study is an engineering
practice and an SE audience is one of the two this map addresses.
"""
import json, os, sqlite3, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_extra_providers import store, SSL_CTX, UA

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")
OUT = os.path.join(ROOT, "coding", "venue-search")

VENUES = ["NeurIPS", "ICML", "ICLR", "ACL", "EMNLP", "AAAI",
          "ICSE", "FSE", "ASE", "TSE"]
TERMS = ["agentic", "self-refine", "self-correction", "iterative refinement",
         "autonomous agent", "multi-agent language model"]
PACE = 6.0

def fetch(q):
    """Return (ok, hits). ok=False means the call failed; the caller must not
    treat that as an empty result."""
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode(
        {"q": q, "h": 50, "format": "json"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as r:
            return True, json.load(r).get("result", {}).get("hits", {}) or {}
    except Exception as e:
        return False, str(e)[:80]

def main():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)
    pending = [(v, t) for v in VENUES for t in TERMS]
    log, total_new = [], 0

    for rnd in range(1, 6):
        if not pending:
            break
        print(f"--- pass {rnd}: {len(pending)} pairs pending")
        still = []
        for venue, term in pending:
            q = f"{term} venue:{venue}:"
            ok, hits = fetch(q)
            if not ok:
                still.append((venue, term))
                print(f"  {venue:8s} {term:28s} CALL FAILED ({hits}) -- will retry")
                time.sleep(PACE * 2)
                continue
            papers = []
            for h in hits.get("hit", []):
                i = h.get("info", {})
                year = int(i["year"]) if str(i.get("year", "")).isdigit() else None
                if not year or not (2018 <= year <= 2026) or not i.get("title"):
                    continue
                a = i.get("authors", {}).get("author", [])
                a = a if isinstance(a, list) else [a]
                papers.append({
                    "external_id": i.get("key"), "doi": i.get("doi"),
                    "title": i["title"].strip(),
                    "authors": "; ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in a),
                    "abstract": "", "year": year, "venue": i.get("venue") or venue,
                    "url": i.get("ee") or i.get("url"), "pdf_url": None,
                    "source": "dblp-venue"})
            new, _ = store(con, 1, "dblp-venue", q, papers,
                           int(hits.get("@total", 0)), 2018, 2026, 50)
            total_new += new
            log.append({"venue": venue, "term": term, "attempted": True,
                        "hits_in_range": len(papers),
                        "dblp_total": int(hits.get("@total", 0)), "new": new})
            print(f"  {venue:8s} {term:28s} hits={len(papers):3d} new={new}")
            time.sleep(PACE)
        pending = still
        if pending:
            print(f"    backing off 90s before retrying {len(pending)} failed pairs")
            time.sleep(90)

    for venue, term in pending:
        log.append({"venue": venue, "term": term, "attempted": False,
                    "hits_in_range": None, "dblp_total": None, "new": None})

    json.dump(log, open(os.path.join(OUT, "venue-log.json"), "w"), indent=1)
    done = [l for l in log if l["attempted"]]
    print(f"\npairs attempted successfully : {len(done)}/{len(log)}")
    print(f"pairs never completed        : {len(log)-len(done)} (reported as not-attempted, not as zero)")
    print(f"genuinely empty venue/term   : {sum(1 for l in done if l['hits_in_range']==0)}")
    print(f"new records                  : {total_new}")

if __name__ == "__main__":
    main()
