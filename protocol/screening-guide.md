# Screening guide (title + abstract)

Binding on both screeners. Written before any record was screened. A screener
may not invent a criterion; if a record cannot be decided under the rules below,
it is marked `include` and pushed to full text, where the evidence is complete.

## The object of study, in one sentence

A **control loop** here is the structure that decides what an autonomous LLM or
foundation-model agent does next, and whether it goes again: action selection,
verification of the last step, retry or repair, what is carried between turns,
what triggers a turn, and what ends the run.

## Decision procedure

Apply in order. The first rule that fires decides.

1. **E1 (homonym).** Is the loop a language-model agent's loop? Control theory,
   PID, RL environment stepping with no language-model policy, hardware or
   process control, compiler loop transformation, network control loops, and
   biological feedback loops are all `exclude / E1`. This is the single largest
   false-positive class in the retrieved set -- expect it, and do not agonise.
2. **E4 (not a research contribution).** Blog post, vendor doc, tutorial, news,
   patent, leaderboard or dataset record with no method: `exclude / E4`.
3. **E5 (secondary study).** Survey, review, SLR, mapping study, benchmark
   *survey*: `exclude / E5`. Record it -- these are snowballing seeds.
4. **E2 (no loop).** Single-pass prompting, prompt/context engineering, one-shot
   generation quality, fine-tuning with no iterative control at inference:
   `exclude / E2`.
5. **E3 (loop used, not studied).** A domain application -- medicine, law,
   robotics, chemistry -- that wires up an off-the-shelf ReAct or CrewAI loop and
   reports domain results. The loop is scaffolding, not the object: `exclude / E3`.
   **Boundary:** if the paper modifies the loop, ablates a loop component, or
   makes a claim about loop behaviour, it is `include` even in a domain setting.
6. Otherwise **I1 and I2** are satisfied: `include`.

## Calls that are easy to get wrong

| Case | Decision | Why |
|---|---|---|
| Chain-of-thought prompting, no feedback | exclude / E2 | Control never returns. |
| Self-consistency (sample *k*, vote) | exclude / E2 | Parallel sampling, not iteration. |
| Self-Refine, Reflexion, CRITIC | include | The refinement cycle is the contribution. |
| Tree/graph search over reasoning states | include | Search *is* the iteration policy. |
| RAG pipeline, retrieve-then-generate | exclude / E2 | One pass unless retrieval is re-entered on a verification signal. |
| Agentic RAG that re-queries on a failed check | include | Control returns on a signal. |
| Tool-learning / API-calling, single call | exclude / E2 | No loop. |
| Multi-agent debate or role assignment | include | Topology is a loop-control choice. |
| Benchmark paper for agents | include only if it measures a loop property | A leaderboard alone is E4/E5. |
| "Agent" that is a fine-tuned model, no runtime loop | exclude / E2 | The loop is the object, not the policy weights. |
| Negative results on self-correction | include | A claim about a loop component is a claim about the loop. |
| Survey of agent architectures | exclude / E5, log as seed | Secondary. |

## Recording

Every decision is written with `phd screen`, carries the criterion id that fired,
and a reason that names the evidence in the abstract. `--decided-by` is the
screener's own id, never the other's. Screeners do not read each other's rows.
