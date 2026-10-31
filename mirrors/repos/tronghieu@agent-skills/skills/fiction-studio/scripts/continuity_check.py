#!/usr/bin/env python3
"""Deterministic continuity checker for a Fiction Studio project.

Fiction *quality* can't be graded by a script — but a meaningful subset of
*consistency* errors can, and those are exactly the ones that slip through when a
team of agents drafts a long manuscript across many sessions. This tool reads a
structured canon (the machine-readable source of truth) and the manuscript, then
reports mechanical inconsistencies for a human or an LLM pass to resolve.

It is ADVISORY: everything it prints is "please review", not "this is wrong". The
goal is to surface candidates fast and cheaply, every session, with zero
dependencies (Python 3 standard library only).

What it checks
  1. Proper nouns in the manuscript not found in the canon
     (candidate invented-on-the-fly or misspelled names/places).
  2. Possible misspellings of canon names (fuzzy match: Mara vs Marah).
  3. Attribute conflicts for eyes/hair colour against the canon.
  4. Setup -> payoff ledger rows that are still unpaid.
  5. POV annotation coverage + per-file / total word counts.

Usage
  python3 continuity_check.py <project-dir>
  python3 continuity_check.py <project-dir> --canon path/to/canon.json \
      --manuscript path/to/manuscript --strict

  <project-dir> is expected to contain canon.json and a manuscript/ folder unless
  overridden. With --strict the script exits 1 when any issue is found (useful as
  a gate); by default it always exits 0.

Canon schema: see templates/canon.json.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

# Words that are commonly capitalised at the start of a sentence and are not
# proper nouns. Used to cut false positives. Proper nouns are still detected by
# their appearance mid-sentence, so this list only needs the obvious offenders.
STOPWORDS = {
    "The", "A", "An", "And", "But", "Or", "So", "Yet", "For", "Nor",
    "He", "She", "They", "It", "We", "You", "I", "His", "Her", "Their",
    "This", "That", "These", "Those", "There", "Here", "When", "Where",
    "While", "If", "Then", "Now", "As", "At", "In", "On", "Of", "To",
    "With", "By", "From", "Into", "Out", "Up", "Down", "Over", "Under",
    "Why", "How", "What", "Who", "Which", "Whose", "Whom", "Not", "No",
    "Yes", "Maybe", "Perhaps", "Once", "Still", "Even", "Just", "Only",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "Mr", "Mrs", "Ms", "Dr", "Sir", "Lady", "Lord",
}

COLOURS = {
    "amber", "auburn", "black", "blonde", "blond", "blue", "brown", "chestnut",
    "copper", "gold", "golden", "green", "grey", "gray", "hazel", "red",
    "silver", "violet", "white", "yellow",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")
PROPER_RE = re.compile(r"\b[A-Z][a-z][A-Za-z'’-]*\b")
POV_RE = re.compile(r"POV\s*[:=]\s*([A-Za-z][\w' ]*)", re.IGNORECASE)


def strip_markup(text):
    """Remove HTML comments, code fences, and leading markdown markers."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"^[#>*\-\s]+", " ", text, flags=re.MULTILINE)
    return text


def load_canon(path):
    if not path.exists():
        sys.exit(f"error: canon file not found: {path}\n"
                 f"create one from templates/canon.json")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"error: canon.json is not valid JSON: {exc}")


def canon_name_tokens(canon):
    """All capitalised tokens that the canon already knows about."""
    tokens = set()
    for group in ("characters", "places"):
        for entry in canon.get(group, []):
            names = [entry.get("name", "")] + entry.get("aliases", [])
            for name in names:
                for tok in PROPER_RE.findall(name):
                    tokens.add(tok)
    return tokens


def chapter_number(path):
    m = re.search(r"\d+", path.stem)
    return int(m.group()) if m else None


def load_manuscript(folder):
    files = sorted(p for p in folder.glob("*.md")) if folder.exists() else []
    chapters = []
    for i, path in enumerate(files):
        raw = path.read_text(encoding="utf-8")
        chapters.append({
            "path": path,
            "raw": raw,
            "text": strip_markup(raw),
            "number": chapter_number(path) if chapter_number(path) is not None else i + 1,
        })
    return chapters


def scan_proper_nouns(chapters):
    """Return {token: {'count': n, 'noninitial': n}} across the manuscript."""
    stats = {}
    for ch in chapters:
        # Split into rough sentences to detect sentence-initial position.
        sentences = re.split(r"(?<=[.!?])\s+|\n+", ch["text"])
        for sent in sentences:
            words = WORD_RE.findall(sent)
            for idx, word in enumerate(words):
                if PROPER_RE.fullmatch(word):
                    entry = stats.setdefault(word, {"count": 0, "noninitial": 0})
                    entry["count"] += 1
                    if idx > 0:
                        entry["noninitial"] += 1
    return stats


def check_unknown_names(stats, canon_tokens):
    """Proper nouns that appear mid-sentence and aren't in the canon."""
    unknown = []
    for token, s in sorted(stats.items()):
        if token in canon_tokens or token in STOPWORDS:
            continue
        # Mid-sentence capitalisation is the strong proper-noun signal.
        if s["noninitial"] >= 1:
            unknown.append((token, s["count"]))
    return unknown


def check_misspellings(stats, canon_tokens):
    """Manuscript tokens that are near-misses of a canon name."""
    hits = []
    seen = set()
    for token in stats:
        if token in canon_tokens or token in STOPWORDS:
            continue
        for name in canon_tokens:
            ratio = difflib.SequenceMatcher(None, token.lower(), name.lower()).ratio()
            if token != name and ratio >= 0.8:
                key = (token, name)
                if key not in seen:
                    seen.add(key)
                    hits.append((token, name, round(ratio, 2)))
    return hits


def check_attributes(chapters, canon):
    """Heuristic eyes/hair colour conflicts against the canon."""
    findings = []
    for entry in canon.get("characters", []):
        name = entry.get("name", "")
        attrs = entry.get("attributes", {})
        for key in ("eyes", "hair"):
            canon_val = str(attrs.get(key, "")).lower()
            if canon_val not in COLOURS:
                continue
            for ch in chapters:
                for m in re.finditer(re.escape(name), ch["text"]):
                    window = ch["text"][max(0, m.start() - 60): m.end() + 60].lower()
                    if key not in window:
                        continue
                    for colour in COLOURS:
                        if colour == canon_val:
                            continue
                        if re.search(rf"\b{colour}\b", window) and re.search(rf"\b{key}\b", window):
                            snippet = " ".join(window.split())
                            findings.append((name, key, canon_val, colour,
                                             ch["path"].name, snippet[:90]))
                            break
    # De-duplicate (a window can match repeatedly).
    return sorted(set(findings))


def check_setups(canon, chapters):
    """Setup->payoff ledger rows that are not yet paid off."""
    max_ch = max((ch["number"] for ch in chapters), default=0)
    unpaid = []
    for s in canon.get("setups", []):
        status = str(s.get("status", "")).lower()
        if status != "paid":
            payoff_ch = s.get("payoff_chapter")
            overdue = (payoff_ch is not None and max_ch and payoff_ch <= max_ch)
            unpaid.append({
                "id": s.get("id", "?"),
                "setup": s.get("setup", ""),
                "chapter": s.get("chapter"),
                "payoff_chapter": payoff_ch,
                "overdue": overdue,
            })
    return unpaid, max_ch


def check_pov(chapters):
    missing = []
    found = []
    for ch in chapters:
        povs = POV_RE.findall(ch["raw"])
        if povs:
            found.append((ch["path"].name, [p.strip() for p in povs]))
        else:
            missing.append(ch["path"].name)
    return missing, found


def word_count(text):
    return len(WORD_RE.findall(text))


def main():
    ap = argparse.ArgumentParser(description="Deterministic continuity checker.")
    ap.add_argument("project", help="project directory (contains canon.json + manuscript/)")
    ap.add_argument("--canon", help="path to canon.json (default: <project>/canon.json)")
    ap.add_argument("--manuscript", help="path to manuscript dir (default: <project>/manuscript)")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any issue is found")
    args = ap.parse_args()

    project = Path(args.project)
    canon_path = Path(args.canon) if args.canon else project / "canon.json"
    manuscript_dir = Path(args.manuscript) if args.manuscript else project / "manuscript"

    canon = load_canon(canon_path)
    canon_tokens = canon_name_tokens(canon)
    chapters = load_manuscript(manuscript_dir)

    print(f"Continuity check — {canon.get('title', project.name)}")
    print(f"  canon: {canon_path}")
    print(f"  manuscript: {manuscript_dir}  ({len(chapters)} file(s))")
    print("=" * 64)

    issues = 0

    stats = scan_proper_nouns(chapters)

    unknown = check_unknown_names(stats, canon_tokens)
    print(f"\n[1] Proper nouns not in canon  (review: invented or misspelled?)")
    if unknown:
        issues += len(unknown)
        for token, count in unknown:
            print(f"    - {token}  (x{count})")
    else:
        print("    none")

    misspell = check_misspellings(stats, canon_tokens)
    print(f"\n[2] Possible misspellings of a canon name")
    if misspell:
        issues += len(misspell)
        for token, name, ratio in misspell:
            print(f"    - '{token}' looks like canon '{name}'  (similarity {ratio})")
    else:
        print("    none")

    attr = check_attributes(chapters, canon)
    print(f"\n[3] Attribute conflicts (eyes/hair colour vs canon)")
    if attr:
        issues += len(attr)
        for name, key, canon_val, found_val, fname, snippet in attr:
            print(f"    - {name}: canon {key}={canon_val}, found '{found_val}' in {fname}")
            print(f"        …{snippet}…")
    else:
        print("    none")

    unpaid, max_ch = check_setups(canon, chapters)
    print(f"\n[4] Unpaid setup -> payoff ledger  (latest chapter seen: {max_ch})")
    if unpaid:
        issues += len(unpaid)
        for s in unpaid:
            flag = "  <-- OVERDUE" if s["overdue"] else ""
            print(f"    - [{s['id']}] {s['setup']}  "
                  f"(set ch.{s['chapter']}, pays off ch.{s['payoff_chapter']}){flag}")
    else:
        print("    none unpaid")

    missing_pov, found_pov = check_pov(chapters)
    print(f"\n[5] POV annotation & word counts")
    if found_pov:
        for fname, povs in found_pov:
            print(f"    {fname}: POV {', '.join(sorted(set(povs)))}")
    if missing_pov:
        print(f"    no POV tag in: {', '.join(missing_pov)}")
    total_words = sum(word_count(ch["text"]) for ch in chapters)
    print(f"    total words: {total_words:,} across {len(chapters)} file(s)")

    print("\n" + "=" * 64)
    print(f"SUMMARY: {issues} item(s) to review"
          + (f"; {len(missing_pov)} file(s) without a POV tag" if missing_pov else ""))
    print("All findings are advisory — a human or an LLM continuity pass decides.")

    if args.strict and issues > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
