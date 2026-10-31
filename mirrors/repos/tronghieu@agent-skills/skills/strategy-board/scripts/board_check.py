#!/usr/bin/env python3
"""Advisory hygiene checker for a strategy-board engagement folder.

Usage:
    python3 board_check.py <engagement-dir>

Checks the mechanical half of the board's non-negotiables:
  - artifacts present for the phases that appear to have run
  - numbers in analyses/options/recommendation carry [S#]/[A#] citations
  - options.md contains at least three options
  - recommendation.md contains the required honesty sections
  - decision-log.md exists and has dated entries
  - unresolved placeholders (TODO / TBD / [brackets]) in "final" artifacts

All findings are advisory. Exit code 0 always (this is a linter for judgment,
not a gate); output is human-readable to stdout.
"""

import re
import sys
from pathlib import Path

# Accept [S#] sources, [A#] assumptions, [F#] fact-base rows (each row carries
# its own source), combined refs like [S6/F12], and artifact refs like
# [graham-tco] pointing at an analysis file.
CITATION = re.compile(
    r"\[(?:[SAF]\d+(?:-\d+)?)(?:\s*[/,]\s*[SAF]?\d+(?:-\d+)?)*\]"
    r"|\[[a-z][a-z0-9]*(?:-[a-z0-9]+)+\]"
)
# figures worth citing: currency, %, or large plain numbers (>= 3 digits, allowing separators)
NUMBERISH = re.compile(
    r"(?:\$|€|£|₫|VND|USD)\s?[\d.,]+|[\d.,]+\s?(?:%|billion|million|bn|mn|tri[eệ]u|t[ỷy])|\b\d{1,3}(?:[.,]\d{3}){2,}\b"
)
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b", re.IGNORECASE)

findings = []


def flag(level, path, msg):
    findings.append((level, str(path), msg))


def check_citations(path: Path, text: str):
    """Numeric claims should sit on a line that also carries a citation or an
    explicit (assumption) label. Line-level granularity keeps false positives
    tolerable — tables cite once per row."""
    uncited = 0
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("#", "```", "|--", "<!--")):
            continue
        if NUMBERISH.search(line) and not CITATION.search(line) \
                and "(assumption)" not in line.lower():
            uncited += 1
            if uncited <= 3:
                flag("WARN", path, f"line {i}: figure without [S#]/[A#] or (assumption): {stripped[:80]}")
    if uncited > 3:
        flag("WARN", path, f"...and {uncited - 3} more uncited figures")


def check_options(path: Path, text: str):
    n = len(re.findall(r"^###\s+Option\b", text, re.MULTILINE))
    if n < 3:
        flag("FAIL", path, f"only {n} option narrative(s) found — the board requires three genuine options (### Option ...)")


def check_recommendation(path: Path, text: str):
    lower = text.lower()
    required = {
        "what we will not do": "the 'What we will NOT do' section (strategy is choice)",
        "risks we accept": "the 'Risks we accept' section (pre-mortem survivors)",
    }
    for needle, desc in required.items():
        if needle not in lower:
            flag("FAIL", path, f"missing {desc}")
    if "situation" not in lower or "complication" not in lower:
        flag("WARN", path, "no SCQA opening detected (Situation/Complication)")


def check_decision_log(root: Path):
    log = root / "decision-log.md"
    if not log.exists():
        flag("WARN", root, "decision-log.md missing — gates should be logged as they are passed")
        return
    text = log.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text):
        flag("WARN", log, "no dated entries found — every gate decision gets a date")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(0)
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Not a directory: {root}")
        sys.exit(0)

    seen = {}
    for name in ("brief.md", "fact-base.md", "options.md", "recommendation.md", "roadmap.md"):
        p = root / name
        seen[name] = p if p.exists() else None

    # phase-order sanity: a later artifact without its predecessors
    order = ["brief.md", "fact-base.md", "options.md", "recommendation.md", "roadmap.md"]
    have = [n for n in order if seen[n]]
    if have:
        latest = order.index(have[-1])
        for n in order[:latest]:
            if not seen[n]:
                flag("WARN", root, f"{have[-1]} exists but {n} is missing — a phase may have been skipped")

    for name, p in seen.items():
        if not p:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        # brief.md holds the executive's own words; fact-base.md IS the source
        # registry (its rows carry a Source column) — neither needs inline tags
        if name not in ("brief.md", "fact-base.md"):
            check_citations(p, text)
        if name == "options.md":
            check_options(p, text)
        if name == "recommendation.md":
            check_recommendation(p, text)
            if PLACEHOLDER.search(text):
                flag("WARN", p, "unresolved TODO/TBD placeholder in a shipping document")
        if name == "roadmap.md" and PLACEHOLDER.search(text):
            flag("WARN", p, "unresolved TODO/TBD placeholder in a shipping document")

    analysis = root / "analysis"
    if analysis.is_dir():
        for p in sorted(analysis.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="replace")
            check_citations(p, text)
            if "so what" not in text.lower():
                flag("WARN", p, "no 'So what' section — analysis that doesn't move the decision is noise")

    check_decision_log(root)

    if not findings:
        print("board_check: clean — no mechanical issues found. Judgment checks (checklists/) still apply.")
        return
    fails = sum(1 for lvl, *_ in findings if lvl == "FAIL")
    print(f"board_check: {len(findings)} finding(s), {fails} serious. All advisory.\n")
    for lvl, path, msg in findings:
        print(f"  [{lvl}] {path}: {msg}")


if __name__ == "__main__":
    main()
