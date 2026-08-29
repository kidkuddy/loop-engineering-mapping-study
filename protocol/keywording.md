# Keywording — derivation of the topic facet

Petersen et al. (2008), step 4. The topic-facet scheme below was **derived from the
corpus**, not imported from an existing taxonomy.

## How it was derived

- **Input.** A random sample of **180 included papers** (title + abstract only),
  drawn with seed **20260829**, stored at `coding/keywording/sample.json`.
- **Pass 1 — keyword extraction.** Every abstract was read in full. From each, the
  keywords recorded are those naming *the part of the agent's control loop the paper
  contributes to* — the mechanism that governs whether and how the loop proceeds
  (what decides the next step, what checks it, what is remembered, what stops it,
  who talks to whom). Application domain, model names and benchmark names were
  deliberately not recorded. Per-paper keywords are in
  `coding/keywording/keywords.csv`.
- **Pass 2 — clustering.** The keyword strings were clustered into mutually
  exclusive categories. Two intermediate categories were merged because abstracts
  could not separate them reliably: *plan construction* and *explicit control-flow
  structure* (DAG/scheduler/stack/rollback engines) both answer "what determines the
  next step", and papers routinely present one as the other — they became
  `planning_and_control_flow`. One intermediate category was split, because a single
  "feedback and checking" bucket held ~32% of the sample: it divides cleanly into
  papers whose contribution is *the judgement* (`verification_and_gating`) and papers
  whose contribution is *the revision that follows a judgement*
  (`critique_and_revision`). A `human_in_the_loop` category was considered and
  dropped: the five to six candidate papers (clarification-seeking, ask-for-help,
  oversight escalation) all contribute a mechanism that decides whether the loop may
  proceed unaided, so they sit inside `verification_and_gating`.
- **Result.** 9 categories, all populated, no residual bucket needed. Largest
  category holds 30/180 (16.7%), so no further split is warranted.

Coding rule: assign **exactly one** category per paper — the primary one, i.e. the
mechanism the paper's own contribution claim is about. A paper that *uses* a
mechanism to study something else is coded by what it contributes, not by what it uses.

## Categories

| value | definition | keyword evidence | count in sample |
|---|---|---|---|
| `verification_and_gating` | The contribution is a **check** that decides whether a candidate output or a proposed action may stand or proceed: verifiers, self-verification, generated tests, formal proofs, confidence/uncertainty signals, judges used as acceptance criteria, pre-execution policy or safety gates, execution monitors, and deferral to a human. Code here whenever the mechanism *judges*, even if a revision follows. | self-verification; external verifier; pre-execution action verification; policy-bounded execution; runtime controller; verifier-gated action release; confidence calibration; execution-state monitoring; failure detection; theorem-prover check; LLM-as-judge as stopping criterion; escalation to human | 30 |
| `critique_and_revision` | The contribution is the **revise-on-feedback** step: how a critique is produced and fed back so an attempt is rewritten. Self-refine, self-correction, self-repair, critic agents, feedback format and granularity, how many revision rounds help, why intrinsic correction fails. Code here when the paper's object is the *correction*, not the *check*. | iterative refinement; self-correction; self-repair; critic feedback; structured repair feedback; reflection; multi-aspect critique; feedback-quality bottleneck; regenerate-on-diagnostic | 27 |
| `loop_evaluation_and_diagnosis` | The contribution is an **instrument for measuring loop behaviour** rather than a loop mechanism: benchmarks, harnesses for measurement, trace/trajectory studies, failure-mode taxonomies, diagnostic methodologies, structural criteria for what counts as long-horizon. | benchmark; diagnostic framework; failure modes; trajectory study; checkpoint instrumentation; root-cause analysis; progress metrics; failure lifecycle dataset | 24 |
| `multi_agent_coordination` | The contribution governs **how several agents are arranged and interact**: topology and its selection, role assignment, communication protocol and content, routing work to agents or models, peer trust/credibility, orchestration and workflow reallocation across agents. | orchestration topology; agent roles; writer-reviewer; debate/review pipeline; inter-agent communication; agent graph/DAG of agents; routing and model selection; credibility scoring; peer influence | 22 |
| `planning_and_control_flow` | The contribution determines **what the loop does next**: goal decomposition, plan and subgoal representation, replanning triggers, action selection and grounding, reason-act interleaving, and explicit control-flow machinery (execution DAGs, schedulers, procedure/decision graphs, stacks, rollback and branching) that fixes the order of steps. | plan decomposition; subgoal; replanning; action selection; grounded decoding; interleaved reasoning and acting; execution DAG; scheduler; decision graph / SOP; state commit and branch | 19 |
| `deliberative_search` | The contribution is **branching over multiple candidate continuations and selecting among them**: tree search, MCTS, beam search, best-of-N and tournament selection, pruning, backtracking within a search, parallel exploration of solution space. | tree search; MCTS; beam search; best-of-N; candidate sampling and selection; expansion and pruning; backtracking; exploration-exploitation | 16 |
| `self_evolution` | The contribution is an **outer loop that changes the agent itself between episodes**: training on its own trajectories, learned reflection/critique policies, prompt or skill rewriting from experience, recursive self-improvement, self-play improvement dynamics. | self-improvement; self-training on own trajectories; skill evolution; prompt policy gradient; recursive self-improvement; self-play; co-evolving world model | 15 |
| `memory_and_context_management` | The contribution governs **what state carries across steps or sessions and how**: context compaction, eviction and reconstruction, event logs, episodic and experience memory, memory write/retrieve/consolidate policies, explicit task- or situation-state kept outside the prompt. | context management; compression and eviction; memory store; experience retrieval; state tree; consolidation and forgetting; situation state; orientation cache | 14 |
| `budget_and_termination_control` | The contribution decides **how much the loop gets and when it stops**: adaptive compute and token budgets, halting, iteration caps, latency/SLO-aware allocation, escalating to a more expensive tier, cost-driven substitution of loop components, and whether an agentic loop is warranted at all. | compute budget; adaptive halting; test-time compute allocation; token and latency cost; budgeted replanning; tier escalation; suppression of unnecessary steps; agentic-versus-single-call decision | 13 |

## Boundary cases

**`verification_and_gating` vs `critique_and_revision`.** Almost every check is
followed by a rewrite, so nearly every paper touches both. Ask what the paper claims
to improve. If the novelty is *how the judgement is produced or enforced* — a solver,
a test suite, a confidence estimate, a policy the action must pass — code
`verification_and_gating` (e.g. *Chain-of-Verification*, *Semantic Self-Verification*,
*TrustBench*, unit-test generation for debugging). If the novelty is *what happens
after a judgement exists* — feedback wording, refinement schedule, whether refining
helps at all — code `critique_and_revision` (e.g. *Structured Feedback Improves
Repair*, *MAgICoRe*, *Is Self-Repair a Silver Bullet?*). Actor-critic frameworks whose
critic is an off-the-shelf checker but whose claim is the refinement loop go to
`critique_and_revision`.

**`deliberative_search` vs `budget_and_termination_control`.** Both are common in
test-time-compute papers. If the contribution changes *the shape of the exploration* —
how candidates are generated, expanded, pruned, or selected — code
`deliberative_search`. If it changes *how much* is spent or *when to stop* while
leaving the search shape intact — per-query allocation, halting, token/latency budgets,
tier escalation — code `budget_and_termination_control`. A paper doing both is coded
by whichever its own ablation credits (e.g. *THROW* credits the easy/hard gate, so
budget; *PAC-MCTS* credits the pruning rule, so search).

**`loop_evaluation_and_diagnosis` vs the mechanism categories.** A benchmark or an
empirical study will always exercise some mechanism. Code
`loop_evaluation_and_diagnosis` only when the headline artefact is the *instrument* —
a benchmark, dataset of failures, diagnostic methodology, or trace-analysis framework
that generalises past the one mechanism under test. Code the mechanism category when
the paper is an empirical audit of *one named mechanism* (e.g. *On the Brittle
Foundations of ReAct Prompting* → `planning_and_control_flow`; *Fight Fire With Fire*,
on ChatGPT's self-verification → `verification_and_gating`).

**`memory_and_context_management` vs `planning_and_control_flow`.** Papers that keep
task state outside the prompt sit on this line. If the stored state exists to *fit the
history into the window and be read back* (compaction, eviction, retrieval), code
memory. If the stored state exists to *determine the next step or allow the loop to
return to an earlier one* (phase plans, rollback and branching), code
`planning_and_control_flow`.

**`multi_agent_coordination` vs everything else.** Many mechanisms are implemented as
a second agent. Having a critic agent, a verifier agent or a planner agent is not
sufficient for this category. Code `multi_agent_coordination` only when the
contribution is about the *arrangement itself* — which topology, which role gets which
model, what agents send each other, how many agents — rather than about what one of
those roles does.

## Papers that could not be placed cleanly

None required a residual category; all 180 are assigned. Two qualifications:

1. **Title-only records.** Nine sample entries carry an empty or citation-only
   abstract (`2228`, `7834`, `9117`, `9484`, `10432`, `10547`, `10761`, `10769`,
   `10785`). They were keyworded and coded from the title alone and should be
   re-coded once full metadata is retrieved; they are the lowest-confidence rows in
   `keywords.csv`.
2. **Duplicate content.** `236` and `1456` are two records of the same paper
   (MAgICoRe, preprint and camera-ready). Both are coded `critique_and_revision`;
   deduplication belongs to the screening stage, not here.

Three further papers were genuinely two-mechanism and were resolved by the rules
above rather than by a residual bucket: `4598` (memory poisoning — coded
`verification_and_gating`, because the mechanism is a write-time authority check, not
a memory representation), `4360` (coded `deliberative_search` on the uncertainty-guided
MCTS, though its adaptive planning-mode selection would support
`planning_and_control_flow`), and `3318` (coded `verification_and_gating` because its
ablation credits iterative verification, though its framing is a three-role
multi-agent system).
