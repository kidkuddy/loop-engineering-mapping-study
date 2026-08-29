# Classification guide (facets)

Binding on both coders. Every included paper is classified on every axis, from
the **full text**, by two coders working independently. Coders do not see each
other's labels. Disagreements are resolved after both passes are complete, by a
third adjudication pass that sees both labels and the paper, and every
adjudicated cell is recorded with the two original labels beside it.

**One value per axis per paper.** Where a paper could plausibly take two values,
assign the one the paper's own contribution section foregrounds, and say in the
justification what the runner-up was. Single-labelling is what makes Cohen's
kappa computable and the map's cells countable.

**Justification is mandatory and must be specific.** Name the section or the
claim in the paper that puts it in that cell. A justification that would fit any
paper is a defect, and adjudication treats it as one.

---

## Axis: `research_type` (Wieringa et al. 2006, as used by Petersen et al. 2008)

Adopted unchanged. Classify by what the paper *does*, never by what it calls
itself: Mendes et al. found most papers self-designate their research type
incorrectly, so the abstract's own word for itself is not evidence.

| Value | Test |
|---|---|
| `validation_research` | A novel technique, investigated in the lab -- experiments, simulation, prototypes -- but **not yet used in practice**. |
| `evaluation_research` | The technique is **implemented in practice** and the evaluation studies its consequences in that setting. Field study, industrial deployment, real users. |
| `solution_proposal` | A solution is proposed and argued for, with a small example or an argument, but no full-blown validation. |
| `philosophical_paper` | Structures the field as a taxonomy, conceptual framework or new way of looking. |
| `opinion_paper` | The authors' position on what is right or wrong, no research method. |
| `experience_paper` | What was done in practice and what was learned, personal experience of the authors. |

**The decisive line for this corpus** is `validation_research` vs
`evaluation_research`. A benchmark run on SWE-bench or WebArena is a lab
evaluation -- `validation_research` -- however large. `evaluation_research`
requires the loop to be running in a real setting with real users or real
production work, and the paper to study what happened there.

## Axis: `contribution_type` (Petersen et al. 2008)

What the paper leaves behind.

| Value | Test |
|---|---|
| `metric` | The contribution is a way of measuring -- a score, an indicator, a measurement procedure. |
| `tool` | A runnable artefact: framework, library, system, harness. |
| `model` | A representation of something -- an architecture, a formalism, a conceptual or mathematical model. |
| `method` | A way of doing the thing: an algorithm, a technique, a procedure applied within a loop. |
| `process` | A prescription for how work is organised across stages or roles. |

`tool` vs `method`: if the paper's claim survives the code being deleted, it is a
`method`; if the artefact *is* the claim, it is a `tool`.

## Axis: `evaluation_strategy` (research method)

The strongest form of evidence the paper offers **for its loop claim**. If a
paper runs a benchmark and also shows one worked example, it is `benchmark`.

| Value | Test |
|---|---|
| `benchmark` | Performance reported on a named, pre-existing benchmark or dataset. |
| `controlled_experiment` | Conditions deliberately varied and compared, with a stated design. |
| `ablation` | The loop's own components are removed or varied to attribute the effect. **Use this only when the ablation is the primary evidence for the loop claim**; if it supports a benchmark result, code `benchmark`. |
| `case_study` | One or a few real systems or settings studied in depth. |
| `human_study` | Human participants or human judges are the measuring instrument. |
| `illustrative_example` | A worked example or walkthrough, no measurement. |
| `none` | No evaluation of the claim is offered. |

## Axis: `human_role`

Where the paper puts the human **relative to the loop it studies**, as the paper
itself describes its operating mode -- not what a deployment might do.

| Value | Test |
|---|---|
| `fully_autonomous` | The loop runs to its own termination with no human step. |
| `human_on_the_loop` | A human supervises and may interrupt, approve or halt, but does not act each turn. |
| `human_in_the_loop` | A human acts within the cycle -- provides feedback, answers, or a decision the loop waits on. |
| `not_specified` | The paper does not say. Use this rather than guessing; the size of this cell is itself a finding. |

## Axis: `venue_type`

From the record's publication venue, not its perceived quality.

| Value | Test |
|---|---|
| `preprint` | arXiv or another preprint server, with no indexed peer-reviewed version found. |
| `workshop` | A workshop proceedings. |
| `conference` | Conference or symposium proceedings. |
| `journal` | A journal. |

Where a preprint and a proceedings version both exist, criterion E6 keeps one
record and it is coded at the peer-reviewed venue.

## Axis: `loop_mechanism`

Derived from keywording the corpus, not borrowed. Its values are declared in
`protocol/keywording.md` **after** screening and before classification begins,
and are fixed for the whole classification pass. See that file for the value
definitions and their keyword evidence.
