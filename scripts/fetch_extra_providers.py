#!/usr/bin/env python3
"""Search Crossref and DBLP and store the results the way `phd search` does.

Why this exists. The plan was arXiv + OpenAlex + Semantic Scholar. Semantic
Scholar's unauthenticated pool returns HTTP 429 to every request from this host,
including a bare three-result probe, so it is not a usable provider here.
Dropping it would have left two databases -- the exact coverage weakness that
makes a mapping study's breadth claim unsupportable.

Crossref and DBLP replace it. Both are key-free, both are stable under polite
serial use, and both index the IEEE, ACM and Springer venues that an arXiv +
OpenAlex pair is accused of missing. That takes the study to four digital
libraries.

Records are written to the same tables, with the same title|first-author|year
fingerprint that phd's Fingerprint() uses, so a record already retrieved by
arXiv or OpenAlex de-duplicates against these rather than double-counting.
"""
import argparse, hashlib, json, os, re, sqlite3, ssl, sys, time, urllib.parse, urllib.request

try:  # macOS python ships without a usable CA bundle; certifi is present here.
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")
NONALNUM = re.compile(r"[^a-z0-9]+")
UA = "loop-engineering-mapping-study/1.0 (mailto:chehir@clusterlab.com)"

def fingerprint(title, first_author, year):
    t = NONALNUM.sub("", (title or "").strip().lower())
    a = NONALNUM.sub("", (first_author or "").strip().lower())
    return hashlib.sha256(f"{t}|{a}|{year}".encode()).hexdigest()[:32]

def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                print(f"    ! {type(e).__name__}: {str(e)[:90]}", file=sys.stderr)
                return None
            time.sleep(4 * (i + 1))

# ----------------------------------------------------------------- providers
def crossref(query, rows, y0, y1):
    q = urllib.parse.urlencode({
        "query.bibliographic": query, "rows": min(rows, 100),
        "filter": f"from-pub-date:{y0}-01-01,until-pub-date:{y1}-12-31,type:journal-article,type:proceedings-article",
        "select": "DOI,title,author,issued,abstract,container-title,URL,type",
        "mailto": "chehir@clusterlab.com",
    })
    d = get("https://api.crossref.org/works?" + q)
    if not d:
        return [], 0
    items = d.get("message", {}).get("items", [])
    total = d.get("message", {}).get("total-results", 0)
    out = []
    for it in items:
        title = (it.get("title") or [""])[0]
        if not title:
            continue
        authors = [" ".join(filter(None, [a.get("given"), a.get("family")])).strip()
                   for a in it.get("author", [])]
        parts = (it.get("issued", {}).get("date-parts") or [[None]])[0]
        abstract = re.sub(r"<[^>]+>", " ", it.get("abstract") or "").strip()
        out.append({
            "external_id": it.get("DOI"), "doi": it.get("DOI"), "title": title.strip(),
            "authors": "; ".join(authors), "abstract": re.sub(r"\s+", " ", abstract),
            "year": parts[0] if parts and parts[0] else None,
            "venue": (it.get("container-title") or [""])[0],
            "url": it.get("URL"), "pdf_url": None, "source": "crossref",
        })
    return out, total

def dblp(query, rows, y0, y1):
    q = urllib.parse.urlencode({"q": query, "h": min(rows, 1000), "format": "json"})
    d = get("https://dblp.org/search/publ/api?" + q)
    if not d:
        return [], 0
    res = d.get("result", {}).get("hits", {})
    total = int(res.get("@total", 0))
    out = []
    for h in res.get("hit", []):
        i = h.get("info", {})
        title = (i.get("title") or "").strip()
        year = int(i["year"]) if str(i.get("year", "")).isdigit() else None
        if not title or year is None or not (y0 <= year <= y1):
            continue
        a = i.get("authors", {}).get("author", [])
        a = a if isinstance(a, list) else [a]
        authors = [x.get("text", "") if isinstance(x, dict) else str(x) for x in a]
        out.append({
            "external_id": i.get("key"), "doi": i.get("doi"), "title": title,
            "authors": "; ".join(authors), "abstract": "",  # DBLP carries no abstracts
            "year": year, "venue": i.get("venue") or "", "url": i.get("ee") or i.get("url"),
            "pdf_url": None, "source": "dblp",
        })
    return out, total

# ----------------------------------------------------------------- storage
def store(con, topic_id, provider, query, papers, found, y0, y1, cap):
    cur = con.cursor()
    cur.execute("""INSERT INTO searches (topic_id, provider, query, start_year, end_year,
                   max_results, papers_found, papers_new) VALUES (?,?,?,?,?,?,?,0)""",
                (topic_id, provider, query, y0, y1, cap, len(papers)))
    sid = cur.lastrowid
    new = 0
    for p in papers:
        first = (p["authors"].split(";")[0] if p["authors"] else "")
        fp = fingerprint(p["title"], first, p["year"] or 0)
        cur.execute("SELECT id FROM papers WHERE fingerprint = ?", (fp,))
        row = cur.fetchone()
        if row:
            pid = row[0]
            # A record already held from another library: keep it, but fill an
            # abstract or venue if this provider supplies one we lack.
            if p["abstract"]:
                cur.execute("UPDATE papers SET abstract = ? WHERE id = ? AND COALESCE(abstract,'') = ''",
                            (p["abstract"], pid))
            if p["venue"]:
                cur.execute("UPDATE papers SET venue = ? WHERE id = ? AND COALESCE(venue,'') = ''",
                            (p["venue"], pid))
            if p["doi"]:
                cur.execute("UPDATE papers SET doi = ? WHERE id = ? AND COALESCE(doi,'') = ''",
                            (p["doi"], pid))
        else:
            cur.execute("""INSERT INTO papers (external_id, doi, title, authors, abstract, year,
                           venue, source, url, pdf_url, fingerprint)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (p["external_id"], p["doi"], p["title"], p["authors"], p["abstract"],
                         p["year"], p["venue"], p["source"], p["url"], p["pdf_url"], fp))
            pid = cur.lastrowid
            new += 1
        cur.execute("INSERT OR IGNORE INTO paper_topics (paper_id, topic_id) VALUES (?,?)", (pid, topic_id))
        cur.execute("INSERT OR IGNORE INTO search_papers (search_id, paper_id, provider) VALUES (?,?,?)",
                    (sid, pid, provider))
    cur.execute("UPDATE searches SET papers_new = ? WHERE id = ?", (new, sid))
    con.commit()
    return new, found

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True, help="TSV: id<TAB>query")
    ap.add_argument("--topic-id", type=int, default=1)
    ap.add_argument("--start-year", type=int, default=2018)
    ap.add_argument("--end-year", type=int, default=2026)
    ap.add_argument("--max-results", type=int, default=100)
    ap.add_argument("--out", default=os.path.join(ROOT, "coding", "search-runs"))
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    for line in open(a.queries):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        qid, query = line.split("\t", 1)
        for name, fn in (("crossref", crossref), ("dblp", dblp)):
            path = os.path.join(a.out, f"{qid}-{name}.json")
            if os.path.exists(path) and os.path.getsize(path) > 2:
                print(f"skip {qid}/{name}"); continue
            papers, found = fn(query, a.max_results, a.start_year, a.end_year)
            new, _ = store(con, a.topic_id, name, query, papers, found, a.start_year, a.end_year, a.max_results)
            rec = {"query": query, "stored": new,
                   "providers": [{"provider": name, "found": len(papers), "matched": found,
                                  "truncated": found > len(papers), "stored": new}]}
            json.dump(rec, open(path, "w"), indent=1)
            print(f"  {qid}/{name} found={len(papers)} matched={found} new={new}")
            time.sleep(2)
    con.close()

if __name__ == "__main__":
    main()
