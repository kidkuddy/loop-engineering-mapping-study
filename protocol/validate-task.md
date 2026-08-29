# Standing task for a full-text validation assessor

Your task names ONE `paper_id`. You assess that paper **from its full text** and
you have not seen, and must not look for, the abstract-based labels already
assigned to it. `coding/classification/` is off limits.

## Get the text

```
cd /Users/niemand/Desktop/loop-engineering-mapping-study
./bin/phd paper download -id <PAPER_ID>          # fetches and parses the PDF
./bin/phd paper page -id <PAPER_ID> -page 1 -page-end 4
```

Read at minimum the abstract, introduction, the section describing the method or
system, and the evaluation. If `paper download` fails or returns no pages, the
full text is unobtainable: record `eligible=F2` and stop.

## Decide two things

**1. Eligibility at full text.** Apply `protocol/screening-guide.md` (v2) plus:
- `F1` the loop mechanism is incidental -- described but neither varied, measured
  nor argued for;
- `F2` full text unobtainable or unparseable;
- `F3` the full text reveals an exclusion the abstract concealed (E1--E7).
Record `include`, or the code that excludes it.

**2. Re-classify all six axes from the full text**, using
`protocol/classification-guide.md` and `protocol/keywording.md`. Same closed
value lists. If you excluded the paper, still classify it if you can; leave the
axes blank only when the text was unobtainable.

## Output

Append ONE row to `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/validation/decisions/<PAPER_ID>.csv`
with this header and one data row:

```
paper_id,eligible,elig_criteria,pages_read,loop_mechanism,contribution_type,research_type,evaluation_strategy,human_role,venue_type,note
```

- `eligible`: `include` or `exclude`
- `elig_criteria`: `I2` for an include; `F1`/`F2`/`F3`/`E1`-`E7` for an exclude
- `pages_read`: e.g. `1;2;3;7`
- `note`: under 200 chars, citing the page that decided eligibility, e.g.
  "p.6 ablates the verifier, 9-point drop". No page number, no credit.

## Rules

- Never cite a page you did not read.
- Do not consult the abstract-based labels. The whole point of this pass is that
  it is independent of them.
- **Do NOT run `phd paper get`.** It prints the stored screening decision inline
  with the metadata, which destroys the independence this pass exists to provide.
  Two assessors hit this before the rule was written and disclosed it; their rows
  are flagged in the results. Take `venue` from the PDF's own front matter, or
  from `coding/validation/sample.csv`, which carries title, year and venue and
  no decisions.
- If `paper download` fails because the DOI resolves to a landing page rather
  than a PDF, you may fetch the real PDF URL and retry. Say so in `note`.

Final message: one line -- paper id, eligibility, and the six labels.
