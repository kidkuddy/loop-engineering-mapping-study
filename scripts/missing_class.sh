#!/usr/bin/env bash
R=/Users/niemand/Desktop/loop-engineering-mapping-study
C=${1:-1}
miss=()
for b in "$R"/coding/classification/coder-$C/batches/batch-*.json; do
  n=$(basename "$b" .json); n=${n#batch-}
  d="$R/coding/classification/coder-$C/labels/batch-$n.csv"
  want=$(python3 -c "import json;print(len(json.load(open('$b'))))")
  if [ ! -s "$d" ]; then miss+=("$n"); continue; fi
  got=$(python3 -c "
import csv
try: print(len(list(csv.DictReader(open('$d')))))
except Exception: print(-1)")
  [ "$got" != "$want" ] && miss+=("$n($got/$want)")
done
echo "coder-$C missing/short: ${#miss[@]}"
printf '%s\n' "${miss[@]}" | paste -sd' ' -
