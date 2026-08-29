# Full-text eligibility instruction (issued verbatim to every assessor)

Every paper that survived title/abstract screening is assessed here, at full
text. There is no second route into the corpus: a paper is not admitted on the
strength of its abstract because its PDF was inconvenient to obtain.

## Your task, for ONE paper

1. Read `protocol/screening-guide.md` (the criteria) and the eligibility
   criteria F1-F3 recorded in the database.
2. Read the paper's text. Use `./bin/phd paper page -id <ID> -page <N>` to read
   pages. Read at minimum: the abstract, the introduction, the section that
   describes the method or system, and the evaluation section. If the paper is
   long, that is still the minimum -- skimming the abstract again is not a
   full-text assessment.
3. Decide `include` or `exclude`.

## What full text is for

Screening asked whether the abstract *claims* the loop is the object of the
contribution. This stage asks whether the paper *delivers* one. The specific
things to check, which an abstract routinely misrepresents:

- **F1.** Is the loop mechanism actually varied, measured or argued for? A system
  description that mentions a retry policy in passing and never returns to it is
  an `exclude / F1`, however agentic the abstract sounds.
- **F3.** Does the full text reveal an exclusion the abstract hid? The commonest
  case is a paper whose "agent" turns out to be a single generation call inside a
  fixed pipeline (`E2`), or a domain application that used a stock framework
  unmodified (`E3`).
- **F2.** If the text cannot be obtained or parsed, `exclude / F2`. Say so
  plainly. Do not substitute the abstract.

## Output

Append one row to the CSV path named in your task, with columns:

```
paper_id,decision,criteria,pages_read,reason
```

- `criteria` — `I1`/`I2` for an include; `F1`/`F2`/`F3`/`E1`-`E6` for an exclude.
- `pages_read` — the page numbers you actually read, e.g. `1;2;5;6`.
- `reason` — one sentence naming the evidence **and the page it is on**, e.g.
  "p.4 ablates the verifier and reports a 9-point drop, so the loop component is
  measured". An exclusion must cite the page where the disqualifying evidence
  appears. A reason with no page number is not acceptable.

Never guess a page number. If you did not read it, do not cite it.
