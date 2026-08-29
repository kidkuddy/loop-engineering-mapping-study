# Screening guide (title + abstract) — v2, after protocol amendment 01

Binding on both screeners. A screener may not invent, relax or extend a
criterion. See `protocol/amendment-01.md` for why v1 was replaced.

## The object of study

A **control loop** here is the structure that decides what an autonomous LLM or
foundation-model agent does next, and whether it goes again.

## The question this stage actually asks

Not "does this paper have an agent loop in it?" — nearly every agent paper does,
and asking that admits three fifths of the harvest. Ask instead:

> **Is the paper's primary contribution a mechanism that governs whether and how
> the loop proceeds, and does the paper offer evidence or an explicit argument
> about that mechanism as such?**

Both halves must hold. A paper that proposes a clever verifier and then reports
only end-task accuracy on a benchmark has not made a claim about the verifier; it
has made a claim about the system. That is `E7`.

## Decision procedure

Apply in order. The first rule that fires decides.

1. **E1 (homonym).** Is the loop a language-model agent's loop? Control theory,
   PID, RL environment stepping with no language-model policy, hardware, process
   or network control, compiler loop transformation, biological or economic
   feedback loops: `exclude / E1`. This remains the largest false-positive class.
2. **E4 (not a research contribution).** Blog post, vendor doc, tutorial, news,
   patent, letter, book, leaderboard or dataset record with no method: `exclude / E4`.
3. **E5 (secondary study).** Survey, review, SLR, mapping study, taxonomy-only
   overview: `exclude / E5`. These are retained as snowballing seeds.
4. **E2 (no loop).** Single-pass prompting, prompt or context engineering with no
   iterative control, fine-tuning or distillation whose "agent" has no runtime
   loop, one-shot generation quality: `exclude / E2`.
5. **E7 (system, not mechanism).** The contribution is an agentic system, pipeline
   or application, and the reported claims are about task outcomes — accuracy,
   success rate, domain metrics — rather than about the loop mechanism.
   `exclude / E7`. **This is now the most common exclusion after E1.**
6. **E3 (loop used, not studied).** A domain application wiring up an off-the-shelf
   loop and reporting domain results: `exclude / E3`. (Where E3 and E7 both fit,
   use E3 if the loop is unmodified off-the-shelf, E7 if the authors built it.)
7. Otherwise **I1 and I2** hold: `include`.

## The mechanism list (I2)

The contribution must govern one of these. If you cannot name which, it is not an
include.

| Mechanism | What a contribution to it looks like |
|---|---|
| iteration policy | how the next step is chosen, whether to go again, search over steps |
| verification | checking an intermediate result to decide what happens next |
| retry / repair | what happens after a step fails |
| termination | stopping rules, budgets, when the agent decides it is done |
| triggering / scheduling | what starts a run, background or recurring execution |
| loop state | what is carried between turns **in order to control** the loop |
| control topology | the arrangement of several agents, **where the arrangement is the studied variable** |

## The evidence half of I2

The paper must do at least one of: measure the mechanism; ablate or remove it and
report the effect; compare it against an alternative mechanism; or argue for it
explicitly as a design position. End-task performance alone is not evidence about
the mechanism.

**A position or philosophical paper that argues explicitly about loop control is
an include** — the map must be able to see conceptual work. What it may not be is
a system paper that never discusses its own loop.

## Calls that are easy to get wrong

| Case | Decision | Why |
|---|---|---|
| Chain-of-thought prompting, no feedback | E2 | Control never returns. |
| Self-consistency (sample *k*, vote) | E2 | Parallel sampling, not iteration. |
| Self-Refine, Reflexion, CRITIC | include | The refinement cycle is the contribution and is measured. |
| Tree/graph search over reasoning states | include | Search is the iteration policy. |
| A multi-agent system that beats a baseline on a domain task | **E7** | The claim is about the system. |
| A multi-agent paper comparing topologies against each other | include | The topology is the studied variable. |
| Agentic RAG that re-queries on a failed check, effect measured | include | Control returns on a signal, and the signal is studied. |
| A memory architecture evaluated by retrieval quality | **E7** | The claim is about retrieval, not about loop control. |
| A memory mechanism ablated for its effect on task continuation | include | The claim is about what the loop does next. |
| Benchmark or leaderboard for agents | include **only** if it measures a loop property (stuck loops, termination, retries) | Otherwise E4/E5. |
| Negative results on self-correction | include | A claim about a loop component. |
| An LLM-based system in medicine that reports only clinical accuracy | E7 | Task outcome. |
| Empty or missing abstract | decide on the title; if the title names a loop mechanism as the contribution, include; otherwise exclude | Do not default everything with no abstract into the corpus. |

## Recording

One row per record. `criteria` is the code that fired. `reason` names the evidence
**in this abstract**, in under 200 characters, and must say which mechanism the
paper contributes to when the decision is `include`. Screeners do not read each
other's files.
