# Consistency & QA

A flat draft can be fixed; an *inconsistent* one quietly rots — a character's eyes
change colour, a dead man speaks, a planted gun never fires, chapter 20 forgets
what chapter 3 established. These errors multiply when a team of agents drafts a
long book across many sessions, because no single mind holds the whole thing and
context is repeatedly summarised and reloaded.

No script can judge whether prose is *good* — that's what Virginia, Bloom, and the
craft checklists are for. But a real subset of *consistency* errors is mechanical,
and those we can verify cheaply and deterministically. This file describes the
three-layer system that keeps a manuscript consistent.

## The core idea: a canon that is the source of truth

The prose bibles (`characters/*.md`, `world-bible.md`) are written for humans.
Alongside them, keep **`canon.json`** — the same facts in machine-readable form:
names + aliases, fixed attributes, places, timeline, established rules, and a
setup→payoff ledger. Schema by example: `templates/canon.json`.

`canon.json` is the *single source of truth*. Two disciplines keep it honest, and
both matter more than any tool:

- **Write back after every chapter.** When drafting invents or fixes a fact (a new
  place, a character's age, a rule clarified), update `canon.json` immediately.
  An out-of-date canon is worse than none — it verifies against the wrong truth.
- **Re-read on resume.** A new session does not remember the last one. Before
  writing, Homer's `status` re-reads `canon.json` and the project files; trust the
  files over recollection. Never continue a manuscript from memory alone.

## Layer 1 — Deterministic check (script, every session)

`scripts/continuity_check.py` reads `canon.json` + `manuscript/*.md` and reports,
with zero dependencies (Python 3 stdlib):

1. proper nouns not in the canon (invented-on-the-fly or misspelled names/places),
2. possible misspellings of canon names (Mara vs Marah),
3. eyes/hair colour conflicts against the canon,
4. unpaid setup→payoff ledger rows (with overdue flags),
5. POV-annotation coverage and word counts.

```bash
python3 scripts/continuity_check.py <story-slug>/
python3 scripts/continuity_check.py <story-slug>/ --strict   # exit 1 on findings
```

Everything it prints is **advisory** — a candidate to review, not a verdict. It is
fast and reliable for the mechanical layer, and is meant to run as a gate during
the dev edit (Phase 7) and before the final polish (Phase 9). Run it every session
so drift is caught while it's a one-line fix, not a chapter-20 rewrite.

To make POV checks work, annotate each scene/chapter file with a line the script
can find, e.g. `<!-- POV: Mara | tense: past -->` at the top.

## Layer 2 — LLM continuity audit (semantic)

The script can't catch what isn't mechanical: a character acting on knowledge they
shouldn't have, a voice drifting out of character, a world rule bent, a decision
that contradicts an established motivation. This is Tolkien's `continuity check`
as a *reading* pass: load `canon.json` + a chapter, and report contradictions in
meaning — the things only judgement catches. Run it on chapters the script flags,
and on any chapter drafted in a fresh session.

## Layer 3 — Process discipline (prevents the errors)

Tools catch errors; discipline prevents them:

- **Update `canon.json` after each chapter** (the write-back rule above).
- **Re-sync on resume** via Homer `status` (the re-read rule above).
- **Reconcile parallel work.** When characters and world are built by subagents in
  parallel, two specialists can invent conflicting facts. Homer merges their
  outputs into one `canon.json` and resolves clashes before drafting continues.
- **Keep the setup→payoff ledger live.** Add a row when you plant something; mark
  it `paid` when it pays off. Unpaid rows at Phase 9 are the fix list.

## What is NOT covered

Prose quality, pacing, emotional impact, theme, and whether the story is *good* —
none of these are tool-checkable. They are handled by the craft checklists
(`checklists/`), the beta read (Virginia), and the critique (Bloom). Don't mistake
a clean continuity report for a finished book.
