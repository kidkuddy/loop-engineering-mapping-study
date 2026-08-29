# Standing task for a facet adjudicator

Two coders classified every included paper on six axes, independently and blind
to each other. You settle the cases where they differ **on one axis**, named in
your task.

## Read

1. `protocol/classification-guide.md` — the borrowed axes and their coding rules.
2. `protocol/keywording.md` — the `loop_mechanism` values, definitions and
   boundary cases. Read the boundary section even if your axis is not
   `loop_mechanism`; it says how the scheme is meant to cut.
3. Your file: `coding/facet-adjudication/<AXIS>.json` — every disagreement on
   your axis, with both coders' values, the title, venue, source and abstract.

## Decide

For each row, apply the guide and choose the value the guide supports. You are
settling on the criteria, not splitting the difference and not defaulting to
either coder. If the guide supports a **third** value that neither coder chose,
choose it and say so.

Watch for the two systematic traps:
- **Self-designation.** Classify by what the paper does, not what it calls
  itself. A "case study" section heading does not make it a case study.
- **The foregrounded contribution.** Where two values genuinely fit, take the one
  the paper's own contribution claim leads with.

## Output

Write `coding/facet-adjudication/<AXIS>-resolved.csv`, header exactly:

```
paper_id,axis,coder_1,coder_2,adjudicated,rationale
```

One row per input row, same order. `adjudicated` must be a declared value for the
axis. `rationale` under 200 characters, naming the evidence in the abstract that
decides it. CSV quoting, no newlines in fields.

## Final message

One line: axis, rows resolved, how many went to coder 1, how many to coder 2, how
many to a third value, and the single most common cause of the disagreement.
