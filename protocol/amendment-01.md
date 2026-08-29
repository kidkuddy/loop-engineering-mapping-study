# Protocol amendment 01 — tightening inclusion criterion I2

**Date:** 2026-08-29, after the screening pilot and before the full screening pass.
**Status:** applied. Both the pilot decisions and the full pass are in this repository.

## What triggered it

Criterion I2 as first written read:

> I2: The loop, or a named component of the loop, is the object of the contribution.

A pilot was screened before committing to the full pass: 14 batches, **623
records**, drawn from the start, middle and end of the retrieval order so that
the pilot spanned targeted and untargeted queries rather than only the queries
most likely to be on topic.

The pilot's include rate was **60.8%** (379 of 623), and it was between 49% and
80% in every batch, including the batches drawn from the least targeted queries.
A criterion that admits three fifths of a deliberately broad four-library harvest
is not selecting a corpus; it is restating the harvest.

Reading the pilot's own justifications showed why, and it is a defect in the
criterion rather than in the screeners. I2 was being satisfied by any paper with
an agentic architecture, because every such paper has a loop and every such paper
names a component of it. The screeners applied the criterion as written. The
criterion did not distinguish **a study of how a loop is controlled** from **a
system that happens to contain a loop** — and the second class is most of the
2025–2026 agent literature.

## The amendment

I2 is replaced, and a new exclusion E7 is added.

> **I2 (amended).** The paper's primary contribution is a mechanism that governs
> whether and how the agent's loop proceeds, and the paper offers evidence or an
> explicit reasoned argument **about that mechanism as such**. The mechanism must
> be one of: iteration policy; verification or evaluation of an intermediate
> result used to decide the next step; retry, repair or recovery; termination,
> stopping or budget; triggering or scheduling of a run; state carried between
> turns for the purpose of controlling the loop; or the topology of control
> among several agents where the topology is the studied variable.

> **E7 (new).** The paper contributes an agentic *system* — however well
> engineered — whose reported claims are about task outcomes rather than about
> the loop mechanism. A benchmark score for an agent is a claim about the agent,
> not about its loop. Retrieval-quality and memory papers whose claim is about
> what is retrieved, rather than about how retrieval changes what the loop does
> next, are excluded here.

## Why this is an amendment and not a result-driven change

The amendment changes which papers are in scope. It does not change any facet,
any research question, or any expected finding, and it was made before any
classification had been performed and before any map existed. The trigger was a
measured precision property of the corpus, not a look at what the answers would
be.

Piloting selection criteria on a sample and refining them before the full pass is
a recommended reliability action; Petersen et al. (2015) list "objective decision
criteria" and iterative refinement of the search and selection among the actions
their rubric scores. The alternative — noticing mid-study that the criterion is
under-specified and carrying on — is the defect this repository exists to make
visible.

## What is preserved

`coding/screening-pilot/` holds the pilot in full: the 14 batches exactly as the
screeners saw them, and all 623 decisions with their reasons under the original
I2. The pilot is reported in the manuscript with its include rate, because it is
the evidence for the amendment. Every record in the pilot was re-screened from
scratch under the amended criteria; no pilot decision was carried forward.
