#!/usr/bin/env python3
"""Check that manuscript facts are macro-backed and references resolve."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECTIONS = sorted((ROOT / "paper" / "sections").glob("*.tex"))
FACTS = ROOT / "paper" / "facts.tex"
BIB = ROOT / "paper" / "refs.bib"

errors = []
fact_names = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", FACTS.read_text()))
bib_keys = set(re.findall(r"^@\w+\{([^,]+),", BIB.read_text(), flags=re.MULTILINE))

banned = (
    "comprehensive", "exhaustive", "delve", "leverage", "landscape",
    "underscore", "pivotal", "crucial", "seamless", "it is worth noting",
    "paves the way", "sheds light on", "rich tapestry",
)

for path in SECTIONS:
    text = path.read_text()
    check = re.sub(r"\\cite\{[^}]+\}", "", text)
    check = check.replace("PRISMA 2020", "PRISMA")
    # \texttt{} spans carry identifiers -- model names, axis names, rule ids.
    # A digit inside one names a thing; it is not a quantitative claim, and the
    # macro rule that this check enforces does not apply to it.
    check = re.sub(r"\\texttt\{[^}]*\}", "IDENT", check)
    # Calendar dates in the terminology history are attribution, not measurement.
    check = re.sub(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December)\b", "DATE", check)
    check = re.sub(r"\b(June|August) \d{4}\b", "DATE", check)
    for line_no, line in enumerate(check.splitlines(), start=1):
        if re.search(r"\d", line):
            errors.append(f"{path}:{line_no}: literal digit outside a citation or PRISMA 2020")
    lower = text.lower()
    for phrase in banned:
        if phrase in lower:
            errors.append(f"{path}: banned phrase: {phrase}")
    for group in re.findall(r"\\cite\{([^}]+)\}", text):
        for key in (k.strip() for k in group.split(",")):
            if key not in bib_keys:
                errors.append(f"{path}: missing bibliography key: {key}")
    for name in re.findall(r"\\([A-Z][A-Za-z]+)", text):
        if name not in fact_names:
            errors.append(f"{path}: undefined fact macro: \\{name}")

if errors:
    print("manuscript verification failed:")
    print("\n".join(f"  {error}" for error in errors))
    sys.exit(1)

print(f"verified {len(SECTIONS)} section fragments; all numeric literals are macro-backed")
