# Standing task for a screening coder

You are screening coder **screener-A** on a systematic mapping study. Your task
names one batch id, `NNN`. Everything else is here.

## Do this

1. Read `/Users/niemand/Desktop/loop-engineering-mapping-study/protocol/screening-guide.md`.
   It is version 2 and it is **stricter than a naive reading**. Exclusion **E7**
   is the one most likely to apply and the one most likely to be missed: an
   agentic system whose reported claims are about task outcomes rather than about
   the loop mechanism is an exclude, however sophisticated the system.
2. Read `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/screening/coder-A/batches/batch-NNN.json`.
3. Write `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/screening/coder-A/decisions/batch-NNN.csv`.

## Output format

Header exactly `paper_id,decision,criteria,reason`, then exactly one row per
record in the batch, in batch order.

- `decision`: `include` or `exclude`.
- `criteria`: the code that decided it (`I1`, `I2`, `E1`–`E7`).
- `reason`: under 200 characters, naming the evidence in **this** abstract. For an
  `include` it must name which mechanism from the guide's mechanism table the
  paper contributes to. Use CSV quoting; never put a newline in a field.

## Rules

- Both halves of I2 must hold: a loop-control mechanism is the primary
  contribution, **and** the paper offers evidence or an explicit argument about
  that mechanism. End-task performance alone is not evidence about the mechanism.
- Empty abstract: decide on the title. Include only if the title names a loop
  mechanism as the contribution; otherwise exclude. Do not default them in.
- Ambiguous between two exclusion codes: pick the earlier one in the decision
  procedure. Ambiguous between include and exclude, with a real abstract: include.
- Read each file once. Do not read other batches, other coders' files, the
  database, or any PDF.

## Final message

One line: the output path, the row count, the include/exclude split, and the
exclusion-code counts. Nothing else.
