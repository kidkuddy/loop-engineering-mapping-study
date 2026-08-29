# Screener instruction (issued verbatim to every screening coder)

You are screening records for a systematic mapping study on the control loops of
autonomous LLM agents. You decide **include** or **exclude** on title, venue and
abstract only. You are one of two independent screeners; you will not see the
other's decisions and must not try to infer them.

## Inputs

- Criteria and decision procedure: `protocol/screening-guide.md`. Read it first.
  It is binding. Do not invent, relax or extend a criterion.
- Your batch: the JSON file named in your task. Every record in it must appear
  exactly once in your output.

## Output

Write a CSV to the exact path named in your task, with this header and nothing else:

```
paper_id,decision,criteria,reason
```

- `decision` — `include` or `exclude`, lowercase, nothing else.
- `criteria` — the criterion code that decided it: `I1`, `I2`, `E1`...`E6`. For an
  include, the criterion that carried it (normally `I1` or `I2`).
- `reason` — one sentence, under 200 characters, naming the evidence **in this
  abstract** that decided it. Quote or paraphrase the abstract's own words. Never
  write a reason that would fit any paper ("not relevant", "off topic").
  Commas are fine; the field is quoted. Do not use newlines.

## Rules that matter

1. **Decide on the evidence in front of you.** You do not have the full text. If
   the abstract is genuinely ambiguous about whether the loop is the object of
   the contribution, decide `include` and let the full-text stage settle it. An
   uncertain include is cheap; an uncertain exclude is unrecoverable.
2. **E1 is the big one.** Most of what you exclude will be work about some other
   kind of loop or some other kind of agent. Reinforcement learning without a
   language-model policy, control theory, robotics servo loops, network control,
   compiler loops, biological feedback: all `E1`.
3. **Do not reward the word "agent".** A fine-tuned model called an agent, with
   no runtime control structure, is `E2`.
4. **Do not punish an application domain.** A paper in medicine or chemistry that
   modifies, ablates or measures the loop is an `include`. Only exclude as `E3`
   when the loop is used as-is and nothing is claimed about it.
5. Every record in the batch gets exactly one row. Do not skip, merge or reorder.
6. Do not read the other screener's files, the database, or any other batch.

Return, as your final message, only: the output path, the number of rows, and the
include/exclude split.
