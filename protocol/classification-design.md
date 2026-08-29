# Classification and full-text validation design

**Written 2026-08-29, before any paper was classified and before any map existed.**

## The problem this design answers

Screening leaves roughly a thousand papers. Two designs were available and both
are defensible in isolation; the failure mode is mixing them.

- Assess every survivor at full text. Sound, but not achievable at this corpus
  size, and the alternative that presents itself under time pressure — full-text
  some papers and promote the rest on their abstracts — produces a corpus whose
  members were admitted by two different standards. That is precisely the defect
  this study is built to avoid.
- Classify every survivor from title and abstract. This is what Petersen et al.
  (2008) actually prescribe: the classification scheme in a mapping study is
  built by *keywording abstracts*, and the map is an abstract-level instrument.

This study takes the second, and then does the thing that makes it defensible:
it measures how wrong the abstract-level instrument is, on a random sample, by
re-doing the work at full text.

## The design

**Stage 4 — Classification.** All screening survivors are classified on all six
axes, from title and abstract, by **two independent coders** working from
`protocol/classification-guide.md` and blind to each other. Cohen's kappa is
computed **per axis** and reported. Disagreements go to a third adjudication pass
that sees both labels and the record; the adjudicated label is what enters the
map, and both original labels stay in the repository.

Every paper is coded the same way. There is no second route into the map.

**Stage 5 — Full-text validation.** A random sample of **n = 60** survivors is
drawn with a fixed seed and assessed at full text by an assessor who does not see
the abstract-based labels. That assessor does two things:

1. **Eligibility.** Applies criteria F1–F3 to the full text. This yields a
   directly measured estimate of the **false-inclusion rate** of abstract-level
   screening, with a binomial confidence interval, rather than an assumption
   that screening was right.
2. **Re-classification.** Re-codes all six axes from the full text. Agreement
   between the full-text label and the adjudicated abstract-based label is
   reported per axis.

## How the results must then be reported

- If full-text agreement on an axis is high, the abstract-based distribution for
  that axis is reported as the map, with the agreement figure beside it.
- If it is low, **the axis's findings are reported as unreliable and the claims
  on it are withdrawn**, not quietly retained. Mendes et al. found most papers
  self-designate their research type incorrectly; `research_type` is the axis
  most likely to fail this test, and it is better to discover that on 60 papers
  and say so than to publish a map that cannot survive being checked.
- The measured false-inclusion rate is applied to the headline corpus count as a
  stated caveat, not silently ignored.

## Why this beats assessing a convenient subset at full text

A study that full-texts some papers and not others cannot say what the untouched
papers would have looked like, because the ones it read were not chosen to
represent them. A random sample can, and the number it produces is the honest
version of the reassurance the other design only implies.

The sample is drawn with seed 20260829 by `scripts/draw_validation_sample.py`
and the drawn ids are committed **before** the assessment is run.
