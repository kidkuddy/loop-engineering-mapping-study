#!/usr/bin/env bash
# Stage 1 -- database search (search strategy 1 of 3).
#
# Design notes that the manuscript reports rather than hides:
#
# 1. Queries target the MECHANISMS of the agent control loop, not the name
#    "loop engineering". The name was coined in June 2026 and the literature it
#    describes overwhelmingly predates it. Q23 searches the literal phrase so its
#    yield can be reported as evidence about the term rather than assumed.
# 2. Each query carries a QUOTED anchor phrase. Unquoted bag-of-words queries
#    were tried first and OpenAlex reported 8,115-54,520 loose matches per query,
#    i.e. every query was a top-100 sample of a very loose ranker. Quoting the
#    anchor cut one probe from 8,115 matches to 57.
# 3. -start-year 2018 is a TECHNICAL floor, not a scoping decision. With no lower
#    bound the CLI emits submittedDate:[00000101 TO ...] and the arXiv API answers
#    500 on every query. 2018 predates any language-model agent literature, so the
#    floor removes nothing; it is recorded here so the choice is not mistaken for
#    a substantive one.
# 4. One phd invocation per (query, provider) pair. Running all three providers in
#    one call meant a Semantic Scholar 429 discarded the arXiv and OpenAlex
#    results for that query too. Pairs are retried individually and paced, because
#    the Semantic Scholar free tier rate-limits an unauthenticated caller.
set -uo pipefail
T=1
CAP=200
SLEEP=8
OUT="coding/search-runs"
mkdir -p "$OUT"
: > "$OUT/queries.tsv"

run() { # run <id> <query>
  local id="$1" q="$2" pv
  printf '%s\t%s\n' "$id" "$q" >> "$OUT/queries.tsv"
  for pv in arxiv openalex; do
    local f="$OUT/${id}-${pv}.json"
    [ -s "$f" ] && { echo "skip $id/$pv"; continue; }
    local cap=$CAP; [ "$pv" = semantic ] && cap=100
    local ok=0 attempt
    for attempt in 1 2 3; do
      if phd search -query "$q" -providers "$pv" -max-results $cap \
           -start-year 2018 -end-year 2026 -topic-id $T > "$f" 2> "$f.err"; then
        if ! grep -q '"error"' "$f"; then ok=1; break; fi
      fi
      echo "   retry $id/$pv (attempt $attempt)"; sleep $((20 * attempt))
    done
    [ $ok -eq 1 ] || echo "   PERSISTENT FAIL $id/$pv"
    echo "  $id/$pv $(python3 -c "
import json,sys
try:
  d=json.load(open('$f'))
  p=d['providers'][0]
  print('found=%s matched=%s stored=%s trunc=%s' % (p.get('found'),p.get('matched'),d.get('stored'),p.get('truncated')))
except Exception as e: print('unreadable', e)
")"
    sleep $SLEEP
  done
}

run Q01 '"agentic loop" large language model agent'
run Q02 '"control loop" autonomous LLM agent architecture'
run Q03 'ReAct "reasoning and acting" language model agent'
run Q04 '"iterative refinement" large language model self-feedback'
run Q05 '"self-correction" large language model reasoning'
run Q06 '"self-verification" language model agent output'
run Q07 '"LLM-as-a-judge" evaluation language model'
run Q08 '"critic model" language model agent feedback'
run Q09 '"stopping criterion" iterative language model reasoning'
run Q10 '"test-time compute" adaptive budget reasoning language model'
run Q11 '"long-horizon" autonomous LLM agent task execution'
run Q12 '"agent memory" language model persistence episodes'
run Q13 '"context management" agent trajectory language model'
run Q14 '"multi-agent" LLM orchestration topology collaboration'
run Q15 '"agent framework" workflow orchestration large language model'
run Q16 '"task decomposition" planning replanning LLM agent'
run Q17 '"error recovery" retry failure autonomous LLM agent'
run Q18 '"failure modes" reliability LLM multi-agent systems'
run Q19 '"tool use" iterative language model agent environment feedback'
run Q20 '"self-improvement" reflection language model agent loop'
run Q21 '"tree search" language model reasoning agent'
run Q22 '"human-in-the-loop" LLM agent oversight autonomy'
run Q23 '"loop engineering"'
echo "ALL QUERIES DONE"
