#!/usr/bin/env python3
"""For included papers with no retrievable PDF, look for an arXiv version by title.

Ninety-three of the included records came from Crossref, DBLP and OpenAlex with no
open PDF. Many peer-reviewed agent papers also exist as arXiv preprints, so this
asks arXiv for each title and reports which ones are recoverable that way.
"""
import csv, os, re, ssl, sys, time, urllib.parse, urllib.request
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError: CTX = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())

rows = list(csv.DictReader(open(os.path.join(ROOT, "coding", "no-fulltext.csv"))))
out, found = [], 0
for i, r in enumerate(rows, 1):
    t = re.sub(r"[^\w\s]", " ", r["title"])[:220]
    url = ("http://export.arxiv.org/api/query?search_query=ti:%22"
           + urllib.parse.quote(t) + "%22&max_results=3")
    hit = ""
    try:
        with urllib.request.urlopen(url, timeout=45, context=CTX) as fh:
            x = fh.read().decode("utf-8", "replace")
        for m in re.finditer(r"<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>", x, re.S):
            aid, at = m.group(1).strip(), " ".join(m.group(2).split())
            a, b = norm(at), norm(r["title"])
            if a and b and (a[:60] == b[:60] or a in b or b in a):
                hit = aid.replace("abs", "pdf"); break
    except Exception as e:
        hit = f"ERR:{type(e).__name__}"
    if hit and not hit.startswith("ERR"): found += 1
    out.append({**r, "arxiv_pdf": hit})
    print(f"[{i}/{len(rows)}] {'FOUND' if hit and not hit.startswith('ERR') else '  -  '}  {r['title'][:60]}", flush=True)
    time.sleep(3.2)

with open(os.path.join(ROOT, "coding", "no-fulltext.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(f"\nRECOVERABLE FROM ARXIV: {found} of {len(rows)}   still unobtainable: {len(rows)-found}")
