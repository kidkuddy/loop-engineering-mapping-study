#!/usr/bin/env bash
# Which screening batches have no decision file yet, and are they well-formed?
R=/Users/niemand/Desktop/loop-engineering-mapping-study
C=${1:-A}
miss=()
for b in "$R"/coding/screening/coder-$C/batches/batch-*.json; do
  n=$(basename "$b" .json); n=${n#batch-}
  d="$R/coding/screening/coder-$C/decisions/batch-$n.csv"
  want=$(python3 -c "import json;print(len(json.load(open('$b'))))")
  if [ ! -s "$d" ]; then miss+=("$n"); continue; fi
  got=$(python3 -c "
import csv
try: print(len(list(csv.DictReader(open('$d')))))
except Exception: print(-1)")
  [ "$got" != "$want" ] && miss+=("$n(rows $got/$want)")
done
echo "missing/short: ${#miss[@]}"
printf '%s\n' "${miss[@]}" | paste -sd' ' -
