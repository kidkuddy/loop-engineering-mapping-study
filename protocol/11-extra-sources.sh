#!/usr/bin/env bash
# Stage 1b -- the remaining two digital libraries, then the manual venue search.
set -uo pipefail
cd "$(dirname "$0")/.."
while ! grep -q "ALL QUERIES DONE" coding/search-runs/driver.log 2>/dev/null; do sleep 20; done
echo "=== database search finished; adding Crossref + DBLP ==="
python3 scripts/fetch_extra_providers.py --queries coding/search-runs/queries.tsv --max-results 100
echo "=== manual venue search (strategy 3) ==="
python3 scripts/venue_search.py
echo "IDENTIFICATION COMPLETE"
