#!/usr/bin/env python3
"""Attach the arXiv versions found for included records that had no open PDF.

Ninety-three included records arrived from Crossref, DBLP and OpenAlex without a
retrievable PDF. scripts/arxiv_recover.py found an arXiv version for a subset by
title. This writes those URLs onto the records so the package can fetch and parse
them like any other paper. The DOI and venue are untouched: the record is still
the peer-reviewed one, and venue_type is unaffected -- only the text source moves.
"""
import csv, os, sqlite3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "data", "phd.sqlite")); cur = con.cursor()
rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "coding", "no-fulltext.csv")))
        if r.get("arxiv_pdf") and not r["arxiv_pdf"].startswith("ERR")]
n = 0
for r in rows:
    url = r["arxiv_pdf"]
    if not url.endswith(".pdf"):
        url = url.rstrip("/") + ".pdf" if "/pdf/" in url else url
    cur.execute("UPDATE papers SET pdf_url=? WHERE id=? AND COALESCE(pdf_url,'')=''",
                (url, int(r["paper_id"])))
    n += cur.rowcount
con.commit()
print(f"attached arXiv PDF urls to {n} records")
still = con.execute("""SELECT COUNT(*) FROM papers WHERE COALESCE(pdf_url,'')='' AND id IN (
  SELECT paper_id FROM screening_decisions WHERE topic_id=1 AND stage='screening'
    AND decision='include' AND decided_by='adjudicated'
  UNION SELECT paper_id FROM screening_decisions s1 WHERE topic_id=1 AND stage='screening'
    AND decision='include' AND decided_by='screener-A' AND NOT EXISTS (
      SELECT 1 FROM screening_decisions s2 WHERE s2.paper_id=s1.paper_id AND s2.topic_id=1
        AND s2.stage='screening' AND s2.decided_by='adjudicated'))""").fetchone()[0]
print(f"included records still without a PDF url: {still}")
