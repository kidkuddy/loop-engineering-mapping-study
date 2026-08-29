#!/usr/bin/env python3
"""Backward and forward snowballing over the included set (search strategy 2 of 3).

Wohlin's procedure, run against OpenAlex because its citation graph is open and
unmetered -- Semantic Scholar, the usual choice, returns 429 to unauthenticated
callers from this host.

Backward: the works each included paper cites.
Forward:  the works that cite each included paper.

A candidate is proposed for screening when it is not already in the corpus.
Candidates are ranked by how many included papers touch them, because a work
cited by six included papers is a likelier miss than one cited by a single
paper, and the ranking is reported rather than used to silently truncate.
"""
import argparse, collections, json, os, re, sqlite3, ssl, sys, time, urllib.parse, urllib.request

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")
UA = "loop-engineering-mapping-study/1.0 (mailto:chehir@clusterlab.com)"
API = "https://api.openalex.org/works"

def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                print(f"    ! {str(e)[:80]}", file=sys.stderr); return None
            time.sleep(3 * (i + 1))

def resolve(title, doi):
    """Find a paper's OpenAlex id from its DOI, else its title."""
    if doi:
        d = get(f"{API}/https://doi.org/{urllib.parse.quote(doi.strip())}?mailto=chehir@clusterlab.com")
        if d and d.get("id"):
            return d
    t = re.sub(r"[^\w\s]", " ", title or "")[:250]
    d = get(f"{API}?filter=title.search:{urllib.parse.quote(t)}&per-page=1&mailto=chehir@clusterlab.com")
    if d and d.get("results"):
        return d["results"][0]
    return None

def brief(w):
    inv = w.get("abstract_inverted_index") or {}
    words = [None] * (max((p for ps in inv.values() for p in ps), default=-1) + 1)
    for term, ps in inv.items():
        for p in ps:
            words[p] = term
    loc = (w.get("primary_location") or {}) or {}
    src = (loc.get("source") or {}) or {}
    return {
        "openalex_id": w.get("id"), "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": w.get("title") or "", "year": w.get("publication_year"),
        "venue": src.get("display_name") or "", "type": w.get("type") or "",
        "cited_by_count": w.get("cited_by_count", 0),
        "authors": "; ".join(a.get("author", {}).get("display_name", "")
                             for a in (w.get("authorships") or [])[:12]),
        "abstract": " ".join(x for x in words if x),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help="CSV of seed paper ids, one per line, or 'included'")
    ap.add_argument("--topic-id", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(ROOT, "coding", "snowball"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    con = sqlite3.connect(DB)

    if a.seeds == "included":
        q = """SELECT p.id, p.title, COALESCE(p.doi,'') FROM papers p
               JOIN screening_decisions s ON s.paper_id = p.id AND s.topic_id = ?
               WHERE s.stage='screening' AND s.decision='include' GROUP BY p.id"""
        seeds = con.execute(q, (a.topic_id,)).fetchall()
    else:
        ids = [int(x) for x in open(a.seeds).read().split() if x.strip().isdigit()]
        seeds = con.execute(
            f"SELECT id,title,COALESCE(doi,'') FROM papers WHERE id IN ({','.join('?'*len(ids))})", ids
        ).fetchall()
    print(f"{len(seeds)} seed papers")

    have_titles = {re.sub(r"[^a-z0-9]", "", (t or "").lower())
                   for (t,) in con.execute("SELECT title FROM papers")}
    back, fwd = collections.Counter(), collections.Counter()
    meta, resolved, unresolved = {}, 0, []

    for i, (pid, title, doi) in enumerate(seeds, 1):
        w = resolve(title, doi)
        if not w:
            unresolved.append({"paper_id": pid, "title": title}); continue
        resolved += 1
        oid = w["id"]
        for ref in (w.get("referenced_works") or [])[:80]:
            back[ref] += 1
        d = get(f"{API}?filter=cites:{oid.rsplit('/',1)[-1]}&per-page=60&mailto=chehir@clusterlab.com")
        for cw in (d or {}).get("results", []):
            fwd[cw["id"]] += 1
            meta[cw["id"]] = brief(cw)
        print(f"  [{i}/{len(seeds)}] {title[:58]:58s} refs={len(w.get('referenced_works') or [])} cites={len((d or {}).get('results',[]))}")
        time.sleep(0.3)

    # Backward candidates need one more fetch each; only those touched by >=2
    # included papers are hydrated, which is the reported cut.
    need = [k for k, v in back.items() if v >= 2 and k not in meta]
    print(f"\nhydrating {len(need)} backward candidates cited by >=2 included papers")
    for i in range(0, len(need), 50):
        chunk = need[i:i+50]
        ids = "|".join(x.rsplit("/", 1)[-1] for x in chunk)
        d = get(f"{API}?filter=openalex_id:{ids}&per-page=50&mailto=chehir@clusterlab.com")
        for w in (d or {}).get("results", []):
            meta[w["id"]] = brief(w)
        time.sleep(0.3)

    cands = []
    for oid, m in meta.items():
        norm = re.sub(r"[^a-z0-9]", "", m["title"].lower())
        if not norm or norm in have_titles:
            continue
        if not m["year"] or not (2018 <= m["year"] <= 2026):
            continue
        cands.append({**m, "backward_hits": back.get(oid, 0), "forward_hits": fwd.get(oid, 0),
                      "total_hits": back.get(oid, 0) + fwd.get(oid, 0)})
    cands.sort(key=lambda c: (-c["total_hits"], -c["cited_by_count"]))

    json.dump({"seeds": len(seeds), "resolved": resolved, "unresolved": unresolved,
               "candidates": cands}, open(os.path.join(a.out, "candidates.json"), "w"), indent=1)
    print(f"\nseeds resolved on OpenAlex : {resolved}/{len(seeds)}")
    print(f"new candidates not in corpus: {len(cands)}")
    print(f"wrote {a.out}/candidates.json")

if __name__ == "__main__":
    main()
