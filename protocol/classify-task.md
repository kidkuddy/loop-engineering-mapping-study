# Standing task for a classification coder

Your task names a coder number (1 or 2) and a batch id `NNN`. You classify papers
into a **declared, closed** facet scheme. You may not invent a value.

## Read first, in this order

1. `/Users/niemand/Desktop/loop-engineering-mapping-study/protocol/classification-guide.md`
   — the five borrowed axes and their coding rules.
2. `/Users/niemand/Desktop/loop-engineering-mapping-study/protocol/keywording.md`
   — the `loop_mechanism` axis: its nine values, their definitions, and the
   boundary-case rules. Read the boundary cases; they exist because those pairs
   are genuinely confusable.
3. Your batch:
   `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/classification/coder-C/batches/batch-NNN.json`
   (replace `C` with your coder number).

## What to produce

Write `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/classification/coder-C/labels/batch-NNN.csv`

Header exactly:

```
paper_id,loop_mechanism,contribution_type,research_type,evaluation_strategy,human_role,venue_type,justification
```

One row per paper in the batch, in batch order. **Six labels per paper, every
paper, no blanks.** Every value must be spelled exactly as declared:

- `loop_mechanism`: verification_and_gating | critique_and_revision | loop_evaluation_and_diagnosis | multi_agent_coordination | planning_and_control_flow | deliberative_search | self_evolution | memory_and_context_management | budget_and_termination_control
- `contribution_type`: metric | tool | model | method | process
- `research_type`: validation_research | evaluation_research | solution_proposal | philosophical_paper | opinion_paper | experience_paper
- `evaluation_strategy`: benchmark | controlled_experiment | ablation | case_study | human_study | illustrative_example | none
- `human_role`: fully_autonomous | human_on_the_loop | human_in_the_loop | not_specified
- `venue_type`: preprint | workshop | conference | journal

`justification` is one sentence under 240 characters naming the evidence in the
abstract for the `loop_mechanism` and `research_type` choices specifically —
those two carry the map. Use CSV quoting; no newlines inside a field.

## Rules that decide the hard cases

- **One value per axis.** Where two fit, choose the one the paper's own
  contribution claim foregrounds.
- **Classify by what the paper does, not what it calls itself.** Most papers
  self-designate their research type incorrectly. A benchmark run in a lab is
  `validation_research`, however large; `evaluation_research` needs the loop
  running in a real setting with real users or real production work.
- **`venue_type`**: use the `venue` and `source` fields. `arxiv` source, or a
  venue that is an arXiv identifier, is `preprint`. `CoRR` is `preprint`.
- **`not_specified` is a real answer** for `human_role`. Use it rather than
  guessing; how often it is needed is itself a result.
- **`none` is a real answer** for `evaluation_strategy`.
- Do not read the other coder's directory, any other batch, or the database.

## Final message

One line: output path, row count, and the `loop_mechanism` distribution. Nothing else.
