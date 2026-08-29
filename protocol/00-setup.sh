#!/usr/bin/env bash
# Stage 0 — protocol registration.
#
# Everything here is written BEFORE any paper is retrieved, which is the point:
# the criteria and the borrowed classification axes are fixed in advance so that
# "we decided this after seeing the corpus" is never an available excuse.
#
# The one axis that is NOT declared here is loop_mechanism. Petersen's method
# derives the topic facet from keywording the abstracts of the retrieved corpus,
# so declaring it now would be the defect the method exists to avoid. It is
# declared in 40-keywording.sh, after screening, and that ordering is logged.
set -euo pipefail
P=1; T=1

# ---------------------------------------------------------------- research questions
phd rq add -topic-id $T -label RQ1 \
  -text "Which mechanisms of the autonomous agent control loop does the retrieved corpus address, and which are sparsely covered?" \
  -answered-by "facet:loop_mechanism"
phd rq add -topic-id $T -label RQ2 \
  -text "What types of contribution does the retrieved corpus produce, and under which Wieringa research types are they reported?" \
  -answered-by "facet:contribution_type"
phd rq add -topic-id $T -label RQ3 \
  -text "What evidence is offered for claims about loop behaviour, and is the loop itself the unit of evaluation?" \
  -answered-by "facet:evaluation_strategy"
phd rq add -topic-id $T -label RQ4 \
  -text "What role does the corpus assign to the human relative to the loop?" \
  -answered-by "facet:human_role"
phd rq add -topic-id $T -label RQ5 \
  -text "What is the publication-venue profile of the retrieved corpus, and how does it constrain what the map can claim?" \
  -answered-by "facet:venue_type"

# ---------------------------------------------------------------- screening criteria
ic() { phd criterion add -topic-id $T -stage screening -kind inclusion -text "$1" -rationale "$2" -proposed-by user -accept; }
ec() { phd criterion add -topic-id $T -stage screening -kind exclusion -text "$1" -rationale "$2" -proposed-by user -accept; }

ic "I1: The record presents, analyses or evaluates a mechanism that governs the iterative control loop of an autonomous LLM or foundation-model agent -- how the next action is selected, checked, retried, remembered, scheduled or stopped." \
   "This is the object of the map. It is stated in mechanism terms rather than by the name 'loop engineering' because that name was coined in June 2026 and almost none of the literature it describes uses it."
ic "I2: The loop, or a named component of the loop, is the object of the contribution." \
   "Separates studies of the loop from the far larger set of studies that merely run inside one."
ic "I3: Written in English." "Coding is done against the text; no translation step is in the protocol."
ic "I4: Retrievable in full text by the search date (2026-08-29)." \
   "Full-text assessment is applied to every screening survivor, so a record we cannot read cannot enter the corpus."
ic "I5: Preprints are eligible, on equal terms with peer-reviewed records." \
   "The practice was named in June 2026 and the mechanism literature is recent; a peer-review filter would remove the object of study rather than clean it. Venue status is instead recorded on the venue_type axis so that maturity is visible in the map, and no finding in this study is conditioned on peer-review status."

ec "E1: The control loop studied is not that of an LLM or foundation-model agent -- classical control theory, reinforcement-learning environment loops with no language-model policy, hardware or process control, or compiler loop optimisation." \
   "'Loop' is a homonym across several fields and is the dominant source of false positives in the retrieved set."
ec "E2: Single-pass prompting, prompt or context engineering with no iterative control structure." \
   "The distinguishing feature of the object of study is that control returns."
ec "E3: An application or domain paper that uses an off-the-shelf agent loop without studying or modifying it." \
   "Satisfies I1 superficially and I2 not at all."
ec "E4: Not a research contribution -- blog post, vendor documentation, tutorial, news item, patent, or a dataset or leaderboard record with no method." \
   "The practitioner literature is the reason this topic has a name; it is analysed separately as terminology evidence and is not a primary study."
ec "E5: Secondary study -- survey, systematic review or mapping study." \
   "A map classifies primary studies. Secondary studies are retained outside the corpus and mined as snowballing seeds, which is recorded."
ec "E6: Duplicate or superseded version of a record already in the corpus." \
   "Preprint-plus-proceedings pairs would otherwise double-count a single contribution; the most complete version is kept."

# ---------------------------------------------------------------- eligibility criteria
phd criterion add -topic-id $T -stage eligibility -kind exclusion -proposed-by user -accept \
  -text "F1: Full text shows the loop mechanism is incidental -- described but neither varied, measured, nor argued for." \
  -rationale "Abstracts overstate. Petersen (2008) warns abstracts are misleading, and Mendes et al. found most papers self-designate their research type incorrectly; this criterion exists so that the abstract is not the last word."
phd criterion add -topic-id $T -stage eligibility -kind exclusion -proposed-by user -accept \
  -text "F2: Full text unobtainable, truncated, or not machine-readable." \
  -rationale "Every survivor is read at full text. A record that cannot be read is excluded and counted, never silently promoted on its abstract."
phd criterion add -topic-id $T -stage eligibility -kind exclusion -proposed-by user -accept \
  -text "F3: Full text reveals an exclusion that the title and abstract concealed (any of E1-E6)." \
  -rationale "Screening decisions on partial evidence must be revisable at the stage where the evidence is complete."

# ---------------------------------------------------------------- borrowed facet axes
phd facet scheme add -topic-id $T -axis contribution_type \
  -values "metric,tool,model,method,process" \
  -rationale "Petersen et al. (2008) contribution facet, adopted unchanged. Borrowed rather than derived, so it is declared before any paper is read."
phd facet scheme add -topic-id $T -axis research_type \
  -values "validation_research,evaluation_research,solution_proposal,philosophical_paper,opinion_paper,experience_paper" \
  -rationale "Wieringa et al. (2006) research-type facet as adopted by Petersen et al. (2008), unchanged."
phd facet scheme add -topic-id $T -axis evaluation_strategy \
  -values "benchmark,controlled_experiment,ablation,case_study,human_study,illustrative_example,none" \
  -rationale "Research-method axis required by Petersen's rubric action 'research method classified'. Values cover the evidence forms the agent literature actually uses; 'none' is a declared value so that its cells are readable rather than missing."
phd facet scheme add -topic-id $T -axis human_role \
  -values "fully_autonomous,human_on_the_loop,human_in_the_loop,not_specified" \
  -rationale "RQ4. The practitioner framing of loop engineering is explicitly about removing the human from the per-turn position, so where the corpus places the human is a first-order question rather than a demographic one."
phd facet scheme add -topic-id $T -axis venue_type \
  -values "preprint,workshop,conference,journal" \
  -rationale "Venue-type axis required by Petersen's rubric. Carries criterion I5: preprints are included, and this axis is how their weight in the corpus is disclosed rather than argued about."
