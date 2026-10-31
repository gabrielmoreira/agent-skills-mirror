# Workflows

Three pipelines. The novel pipeline is the default; the others are variants for
different scopes. In every case: finish a phase, write its artifact to the
project folder, show it, and confirm with the author before advancing. Homer
runs the handoffs; each specialist does one phase.

## Novel (greenfield) — the default

| # | Phase | Member | Reads | Writes |
|---|-------|--------|-------|--------|
| 0 | Premise | Homer + Borges (opt. Writers' Room) | — | `premise.md` |
| 1 | Outline | Aristotle | premise | `outline.md` |
| 2 | Characters | Fyodor | premise, outline | `characters/*.md` |
| 3 | World | Tolkien | premise, outline | `world-bible.md` |
| 4 | Scene list | Scheherazade | outline, characters, world | `scene-list.md` |
| 5 | Draft | Scheherazade | scene-list + bibles | `manuscript/*.md` |
| 6 | Dialogue pass | Oscar | drafted scenes, characters | updated `manuscript/` |
| 7 | Developmental edit | Max | manuscript | revised `manuscript/` |
| 8 | Beta read | Virginia | revised manuscript | `beta-notes.md` |
| 8.5 | Revision triage | Max | beta-notes, manuscript | `revision-plan.md` |
| 9 | Final polish | Max | manuscript + revision-plan | final `manuscript/` |
| 10 | Package | Homer + Max (+ Borges) | final manuscript | `pitch-kit.md` + compiled manuscript |
| — | Critique (optional) | Bloom | final manuscript | critique notes |

Phases 2 and 3 are independent of each other and can run in parallel (see the
parallel-dispatch option in SKILL.md). Phases 5–9 usually iterate per chapter:
draft → dialogue → edit a chapter, get a beta reaction, polish, then move on —
rather than drafting the whole book before any editing.

**Quality gates** — run these before calling a phase done; they're how Borges and
Tolkien get teeth, not just opinions:
- After Phase 1 (outline): `checklists/plot-structure.md` (Aristotle) and a
  `genre check` against `references/genres.md` (Borges). Plan deliberate setups
  with `checklists/foreshadowing-payoff.md`.
- During Phase 7 / before Phase 9: `checklists/continuity.md` (Tolkien/Max) and
  `checklists/prose-quality.md` (Max).
- At Phase 8: offer an optional `checklists/sensitivity-read.md` pass (Virginia).
- Before Phase 9 ships: re-run `checklists/foreshadowing-payoff.md` so no planted
  promise is left unpaid.
- During Phase 7 and before Phase 9: run the deterministic continuity checker —
  `python3 scripts/continuity_check.py <story-slug>/` — then Tolkien's LLM
  `continuity check` for the semantic errors a script can't see. See
  `references/qa.md`.

**Consistency across sessions.** A manuscript drafted over many sessions stays
coherent only if the canon does. Keep `canon.json` (the machine-readable source of
truth) current: **update it after each chapter** as facts are invented or fixed,
and have Homer **re-read it on resume** (`status`) rather than trusting memory.
When characters and world are built by parallel subagents, Homer reconciles their
facts into one `canon.json` before drafting continues. Full system: `references/qa.md`.

**Phase 8.5 — Revision triage (the feedback loop).** Don't act on beta notes
one-for-one; that sands a book flat. Max turns Virginia's reactions into a
prioritized plan with `templates/revision-plan.md`: sort each note into
must-fix / consider / decline-with-reason, map fixes to scenes, and account for
ripples (a change in one scene often breaks a setup or a continuity fact later).
The finalized list is the work order for the Phase 9 polish.

**Phase 10 — Package.** The manuscript is done; now make it presentable. Max +
Homer build `templates/pitch-kit.md` (logline, blurb, synopses, comps, optional
query letter) and compile `manuscript/*.md` into one ordered file. Borges advises
on comp titles and market positioning. This is text only — no cover art.

**Writers' Room (party mode) — a discussion option, not a phase.** At Phase 0,
Homer can offer a roundtable to brainstorm the premise before structure exists;
mid-project, the author can call `party` when stuck at a fork (the ending, a
genre pivot, a character that won't come alive). 3–4 relevant specialists discuss
one framed question together, then Homer synthesises and writes the decision into
`premise.md` or a short `brainstorm.md`. It's for discovery and decisions, never
for production passes. Full protocol: `references/party-mode.md`.

## Outline variant — the Snowflake method (Phase 1 option)

Some authors build a story better by *expansion* than by filling an outline
template. The Snowflake method grows the book from a single sentence outward,
each step adding detail to the last. Offer it at Phase 1 as an alternative route
to the same `outline.md` — it reuses the same team and feeds the same later
phases. Aristotle drives the structural expansions; Fyodor handles the character
layers. Offer elicitation between steps.

1. **One sentence** (Aristotle) — the whole book in ~15 words.
2. **One paragraph** (Aristotle) — expand to five sentences: setup, three
   disasters/turns, ending.
3. **Character summaries** (Fyodor) — a half-page per major character: their
   goal, conflict, and arc, told from their angle.
4. **One-page synopsis** (Aristotle) — expand each sentence of the paragraph into
   a full paragraph.
5. **Character depth** (Fyodor) — full profiles (`templates/character-profile.md`).
6. **Scene list** (Scheherazade) — expand the synopsis into scenes
   (`templates/scene-list.md`).
7. **Outline** (Aristotle) — consolidate into `outline.md`, the same artifact the
   default pipeline produces at Phase 1.

From here, rejoin the novel pipeline at Phase 3 (World) — characters and a scene
list already exist. Good for authors who feel lost facing a blank outline, or who
want the premise stress-tested by escalating expansion before committing.

## Short story

Compress the pipeline. A short story rarely needs a full world bible or a cast
of deep profiles.

```
0 Premise      → Homer + Borges   → premise.md
1 Mini-outline → Aristotle        → one-page beats (no template needed)
2 Protagonist  → Fyodor           → one character profile (the lead only)
3 Draft        → Scheherazade     → manuscript/story.md
4 Dialogue     → Oscar            → updated draft
5 Edit         → Max              → revised draft
6 Beta read    → Virginia         → quick reaction
7 Polish       → Max              → final
```

Skip Tolkien unless the setting is doing heavy lifting. Keep momentum — a short
story dies under too much pre-planning.

## Series planning

Before book 1, run a series layer with Aristotle + Tolkien + Borges:

1. **Series arc** (Aristotle) — the macro-question that spans the books, and the
   per-book turning points that escalate it.
2. **World bible** (Tolkien) — built once, shared across books; the canon of
   record. Every later book checks continuity against it.
3. **Genre & promise** (Borges) — what the series promises readers and how each
   instalment both satisfies and extends it.

Then run the novel pipeline per book, each reading the shared series files.

## Resuming a project

When an author returns mid-project, Homer runs `status`: re-read `canon.json` and
the project folder, report which artifacts exist and which phase is next, then
cast the matching member. The files *are* the memory — trust them over
recollection, and never continue a manuscript from memory alone. Re-reading the
canon at the top of each session is the single most important habit for keeping a
long, multi-session book consistent.
