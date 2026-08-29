# Reproduction targets for the mapping study.
#
# `make verify` is the one that matters: it recomputes every number the
# manuscript states, from the shipped database, and fails if the paper and the
# data disagree.

SHELL := /bin/bash
PY    := python3

.PHONY: all verify facts paper clean identification screening-batches agreement flow help

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-22s %s\n",$$1,$$2}'

all: facts ## regenerate every number the manuscript cites

facts: ## recompute every number AND figure the manuscript reports
	$(PY) scripts/validation_summary.py > /dev/null
	$(PY) scripts/build_map.py > /dev/null
	$(PY) scripts/flow.py > /dev/null
	$(PY) scripts/paper_facts.py

verify: ## check the manuscript against the data (needs the manuscript sources)
	@test -d paper/sections || { \
	  echo "paper/ is not in this repository -- it holds the pipeline, not the manuscript."; \
	  echo "Place the manuscript sources in paper/ to run this check, or use 'make facts'"; \
	  echo "to regenerate the numbers the manuscript cites."; exit 1; }
	$(PY) scripts/paper_facts.py > /dev/null
	$(PY) scripts/verify_manuscript.py

agreement: ## recompute inter-rater agreement from the raw coder files
	$(PY) scripts/kappa.py
	$(PY) scripts/screening_agreement.py

flow: ## regenerate the PRISMA flow counts
	./bin/phd export prisma -topic-id 1 -format markdown

paper: facts ## build paper/main.pdf (needs the manuscript sources; not shipped here)
	@test -d paper/sections || { echo "paper/ is not in this repository."; exit 1; }
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

identification: ## re-run the whole search from scratch (slow, hits four APIs)
	bash protocol/10-search.sh
	bash protocol/11-extra-sources.sh

clean:
	cd paper && latexmk -C || true
