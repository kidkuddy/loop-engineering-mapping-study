# Standing task for screening coder B

Identical to `protocol/screen-task.md` in every respect except the paths. You are
**screener-B**, the independent second screener on a random 20% sample drawn with
seed 20260829. You have not seen screener-A's decisions and must not look for
them: `coding/screening/coder-A/` is off limits.

1. Read `/Users/niemand/Desktop/loop-engineering-mapping-study/protocol/screening-guide.md`.
   It is version 2. Exclusion **E7** — an agentic system whose reported claims are
   about task outcomes rather than the loop mechanism — is the one most often
   missed.
2. Read `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/screening/coder-B/batches/batch-NNN.json`.
3. Write `/Users/niemand/Desktop/loop-engineering-mapping-study/coding/screening/coder-B/decisions/batch-NNN.csv`.

Header exactly `paper_id,decision,criteria,reason`, one row per record, batch
order, CSV quoting, no newlines in fields, reasons under 200 characters naming
the evidence in that abstract and, for an include, the mechanism.

Both halves of I2 must hold. Empty abstract: decide on the title, include only if
the title names a loop mechanism as the contribution.

Final message: path, row count, include/exclude split, exclusion-code counts.
