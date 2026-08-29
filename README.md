# Loop Engineering: A Systematic Mapping Study of Autonomous LLM Agent Control Loops

Replication package. Everything the manuscript states is produced from what is in
this repository, by the scripts in this repository.

> **`make verify` recomputes every number in the paper from `data/phd.sqlite`.**
> If the paper and the data disagree, the build fails.

## What the study is

"Loop engineering" is a name coined by practitioners in June 2026, and adopted in
Anthropic's Claude blog on 2026-06-30, for designing the system that prompts,
verifies, retries and stops an agent rather than prompting it turn by turn. This
study is **not** a map of the phrase. It is a systematic mapping study, following
Petersen et al. (2008, rev. 2015), of the research literature the phrase denotes:
the mechanisms that govern whether and how an autonomous language-model agent's
loop proceeds.

**This study is standalone.** It is not a stratum, extract, companion or
continuation of any other study, and it shares no data with any other
publication. Search date 2026-08-29.

## The numbers, and where they come from

| | |
|---|---|
| Digital libraries | arXiv, OpenAlex, Crossref, DBLP |
| Search strategies | database search, backward+forward snowballing, manual venue search |
| Records identified | 7,757 |
| Removed by automated scope rule R1 | 4,354 |
| Screened on title and abstract | 3,403 |
| Included in the map | 973 |
| Facet axes | 6 (5 borrowed, 1 derived by keywording) |
| Adjudicated classifications | 5,838 |
| Screening $\kappa$ (n=681 double-screened) | 0.802 |
| Classification $\kappa$ per axis | 0.783 – 0.940 |
| Full-text validation sample | 60 drawn with seed 20260829 |

## Layout

```
protocol/     every decision rule, written before the stage it governs
  00-setup.sh              RQs, criteria and borrowed facet axes, registered first
  quasi-gold-standard.md   10 test papers, declared before the first search
  screening-guide.md       v2 -- the binding criteria and decision procedure
  amendment-01.md          why v1 was replaced, and the pilot that triggered it
  keywording.md            how loop_mechanism was derived from the corpus
  classification-guide.md  the six axes and their coding rules
  classification-design.md why the map is abstract-based and how that is validated
  *-task.md                the instructions each coder actually received

coding/       every decision, and the evidence each coder saw
  search-runs/             raw provider responses per query
  screening-pilot/         the 623-record pilot, under the superseded criterion
  screening/coder-A|B/     batches (the inputs) and decisions (the outputs)
  screening/adjudication.csv
  classification/coder-1|2/  both coders' independent labels
  facet-adjudication/      disagreements and how each was settled
  validation/              the full-text sample and its assessments
  coder-A.csv, coder-B.csv raw labels, long form -- the agreement base
  map-*.csv, crosstab-*.csv the map itself

scripts/      everything that turns data into numbers
data/         phd.sqlite -- the whole study
paper/        main.tex, sections/, facts.tex (generated), OUTLINE.md
figures/      flow.pdf, bubble.pdf, evidence.pdf (generated)
```

## Reproducing

```bash
make facts        # recompute every manuscript number from the database
make agreement    # recompute both inter-rater analyses from the raw coder files
make paper        # rebuild the PDF
make identification   # re-run the search itself (slow; hits four live APIs)
```

`bin/phd` wraps the `phd` CLI so it always resolves this repository's local
SQLite database. `phd.env` is deliberately empty; it shadows any user-level
config so nothing here depends on a private remote.

## Things this package discloses that a reader should know

- **The search is cap-bound.** 90% of query/provider pairs returned exactly the
  requested cap. For those pairs the corpus is a top-*k* relevance sample, which
  bounds recall.
- **The search missed three of its own ten test papers.** Named in the manuscript.
- **The criteria were amended once, after a pilot.** Both the pilot and the full
  pass are here. See `protocol/amendment-01.md`.
- **The coders were independent LLM agent instances** working from the written
  guides, with disagreements adjudicated by the author. This is stated in the
  manuscript's Method and again in its Threats section.
- **Two validation assessors self-disclosed** that `phd paper get` prints the
  stored screening decision, so their rows are not fully independent of the
  abstract-based pass. `protocol/keywording.md` also names three paper ids with
  their labels. Both leaks are recorded in the affected rows.
- **Quality assessment of primary studies was deliberately not performed**, per
  Petersen et al. (2015). Stated in the manuscript rather than omitted silently.
- **Snowballing found citation data for a minority of its start set.** Citation
  indexes cover a literature this recent poorly, and the yield reflects that.

## License

Data and code released for review and replication.
