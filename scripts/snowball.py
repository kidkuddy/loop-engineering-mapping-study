#!/usr/bin/env python3
"""Backward and forward snowballing (search strategy 2 of 3).

Wohlin's procedure over a declared start set.

PROVIDER NOTE, reported in the manuscript rather than hidden. The citation graph
here is OpenCitations COCI, with Crossref for the metadata of discovered works.
Semantic Scholar, the usual choice, refuses unauthenticated callers from this
host with HTTP 429 on every request. OpenAlex served the database search but
began returning 429 to sustained citation-graph traversal and did not recover
within the study window. OpenCitations is keyed on DOIs, so the start set is
necessarily the DOI-bearing part of the included corpus; that restriction is a
real limitation of the snowballing pass and is stated as one.

Backward: works cited by a seed. Forward: works citing a seed.
Candidates already in the corpus are dropped. The rest are ranked by how many
seeds touch them and written out for screening.
"""
import argparse, collections, json, os, random, re, sqlite3, ssl, sys, time
import urllib.parse, urllib.request

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "phd.sqlite")
UA = "loop-engineering-mapping-study/1.0 (mailto:chehir@clusterlab.com)"
COCI = "https://w3id.org/oc/index/coci/api/v1"
PACE = 0.5

def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45, context=SSL_CTX) as r:
                return json.load(r)
        except Exception as e:
            msg = str(e)
            if i == tries - 1:
                return None
            time.sleep((10 * (i + 1)) if "429" in msg else (3 * (i + 1)))

def crossref(doi):
    d = get("https://api.crossref.org/works/" + urllib.parse.quote(doi) +
            "?mailto=chehir@clusterlab.com")
    if not d:
        return None
    it = d.get("message", {})
    title = (it.get("title") or [""])[0]
    if not title:
        return None
    parts = (it.get("issued", {}).get("date-parts") or [[None]])[0]
    abstract = re.sub(r"<[^>]+>", " ", it.get("abstract") or "").strip()
    return {"doi": doi, "title": title.strip(),
            "authors": "; ".join(" ".join(filter(None, [a.get("given"), a.get("family")])).strip()
                                 for a in it.get("author", [])[:12]),
            "abstract": re.sub(r"\s+", " ", abstract),
            "year": parts[0] if parts and parts[0] else None,
            "venue": (it.get("container-title") or [""])[0],
            "type": it.get("type", ""), "url": it.get("URL")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic-id", type=int, default=1)
    ap.add_argument("--start-set-size", type=int, default=100)
    ap.add_argument("--seed", type=int, default=20260829)
    ap.add_argument("--out", default=os.path.join(ROOT, "coding", "snowball"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    con = sqlite3.connect(DB)

    pool = con.execute("""
        SELECT p.id, p.doi, p.title FROM papers p
        WHERE COALESCE(p.doi,'') <> '' AND p.id IN (
          SELECT paper_id FROM screening_decisions
          WHERE topic_id=? AND stage='screening' AND decision='include'
            AND decided_by IN ('screener-A','adjudicated'))""", (a.topic_id,)).fetchall()
    pool = sorted({r[0]: r for r in pool}.values())
    n = min(a.start_set_size, len(pool))
    seeds = sorted(random.Random(a.seed).sample(pool, n))
    print(f"DOI-bearing included papers: {len(pool)}")
    print(f"start set (seed {a.seed})   : {n}")

    have = {re.sub(r"[^a-z0-9]", "", (t or "").lower())
            for (t,) in con.execute("SELECT title FROM papers")}
    have_doi = {(d or "").lower() for (d,) in con.execute("SELECT doi FROM papers") if d}

    back, fwd, ok = collections.Counter(), collections.Counter(), 0
    for i, (pid, doi, title) in enumerate(seeds, 1):
        d = doi.strip().lower()
        refs = get(f"{COCI}/references/{urllib.parse.quote(d)}") or []
        cits = get(f"{COCI}/citations/{urllib.parse.quote(d)}") or []
        if refs or cits:
            ok += 1
        for r in refs:
            c = (r.get("cited") or "").lower()
            if c and c not in have_doi:
                back[c] += 1
        for c_ in cits:
            c = (c_.get("citing") or "").lower()
            if c and c not in have_doi:
                fwd[c] += 1
        print(f"  [{i}/{n}] refs={len(refs):3d} cites={len(cits):3d}  {title[:52]}")
        time.sleep(PACE)

    touched = back + fwd
    ranked = [d for d, _ in touched.most_common() if touched[d] >= 2]
    print(f"\nseeds with citation data : {ok}/{n}")
    print(f"distinct candidate DOIs  : {len(touched)}")
    print(f"touched by >= 2 seeds    : {len(ranked)}  (these are hydrated)")

    cands = []
    for i, d in enumerate(ranked[:400], 1):
        m = crossref(d)
        time.sleep(0.4)
        if not m or not m["year"] or not (2018 <= m["year"] <= 2026):
            continue
        if re.sub(r"[^a-z0-9]", "", m["title"].lower()) in have:
            continue
        cands.append({**m, "backward_hits": back.get(d, 0), "forward_hits": fwd.get(d, 0),
                      "total_hits": touched[d]})
        if i % 25 == 0:
            print(f"    hydrated {i}/{min(len(ranked),400)}")
    cands.sort(key=lambda c: -c["total_hits"])

    json.dump({"start_set_size": n, "seeds_with_citation_data": ok,
               "distinct_candidates": len(touched), "hydrated": len(ranked[:400]),
               "candidates": cands},
              open(os.path.join(a.out, "candidates.json"), "w"), indent=1)
    print(f"\nnew candidate papers not already in the corpus: {len(cands)}")
    print(f"wrote {a.out}/candidates.json")

if __name__ == "__main__":
    main()
