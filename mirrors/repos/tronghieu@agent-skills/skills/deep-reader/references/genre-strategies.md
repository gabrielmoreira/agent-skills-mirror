# Genre strategies

Adler's *How to Read a Book* Part III argues that different kinds of books
demand different reading rules on top of the general method. SKILL.md Step 2
points here once `map.md`'s classification field is filled in. Each section
below states only what changes relative to the default study pipeline
(SKILL.md Steps 3–5) — if a genre isn't mentioned here, assume the default
pipeline applies unchanged.

## Practical books

Practical books argue for action: how to do something, or how to live. The
whole-book question in `map.md` should be phrased as a problem to be solved,
not a fact to be known.

- **Central question shifts** from "is this true?" to "does it work, and
  should I act on it?" A practical book can be internally consistent and
  still fail this test if its prescriptions don't fit the reader's situation.
- **Critical judgment** (Step 5 / Critical judgment in SKILL.md) must weigh
  both the ends the author proposes and the means offered to reach them —
  agreeing with the goal doesn't oblige you to agree the method gets there.
- **Watch for persuasion devices** — practical books sell as much as they
  argue. When a chapter note's "evidence offered" field is thin but the
  language is confident, flag that gap explicitly rather than letting the
  author's rhetoric stand in for evidence.

## Imaginative literature

Novels, plays, poetry. The analytical machinery built for expository prose
does not transfer directly — do not force it.

- **Do not apply true/false criteria.** A novel isn't wrong because events in
  it didn't happen. Judge it by whether it makes you experience something,
  not by whether its claims check out against a source.
- **"Terms" become characters and episodes.** In `terms.md`, replace defined
  vocabulary with a running list of characters, places, and recurring images
  — track how each is introduced and how it changes, the same way you'd track
  a term's evolving meaning in expository work.
- **Chapter notes follow experience and structure, not argument.** Replace
  "leading propositions" and "arguments (premises → conclusion)" with plot
  movement, turning points, and the emotional or thematic effect of the
  chapter — there is no premise-to-conclusion chain to extract.
- **Recite becomes retelling the story arc so far**, not re-verifying
  propositions against the text.
- **Withhold criticism until you've experienced the whole work.** Judging a
  novel by chapter 3 is like judging a symphony by its first movement —
  synthesis (Step 4) is the earliest point where whole-work judgment belongs.

## History

History mixes narrative fact with the historian's interpretation, and the
two are easy to mistake for each other.

- **Central question adds a layer**: not just "what happened" but "what is
  this historian trying to prove?" Every history is written from a point of
  view; find it before judging the account.
- **Scrutinize sources and bias** as part of "evidence offered" in each
  chapter note — which primary sources does the historian lean on, and whose
  perspective do those sources represent?
- **Syntopical reading is the natural check.** A single history is one
  witness. When the stakes justify it, point the user toward reading a second
  history of the same events (SKILL.md's Syntopical reading section) rather
  than treating one narrative as settled.

## Science and math

Technical argument carries its weight in specific proofs and experiments, not
in the surrounding prose.

- **Anchor on the problem the author poses** before the solution — the
  central question in `map.md` should be the scientific problem, stated in
  the author's own terms, not a summary of the conclusion.
- **Deep-read selectively**, in the spirit of Keshav's pass 3 (see
  [paper-mode.md](paper-mode.md)): reconstruct only the proofs or experiments
  that carry load-bearing conclusions. Skim derivations that are there for
  completeness rather than because the argument depends on them, and say so
  in the chapter note.
- **`terms.md` is the most critical file for this genre.** Definitions here
  are exact, not colloquial — a term redefined precisely in chapter 4 changes
  what every later chapter can validly claim. Treat any imprecision in your
  own notes as a bug to fix immediately, not a rounding error.

## Philosophy

Philosophical arguments rest on premises the author may never state outright.

- **Dig for first principles.** The chapter note's "arguments" field should
  make the author's unstated premises explicit, not just the ones written on
  the page — philosophical disagreements usually trace back to a premise, not
  a logical error.
- **Terms are contested, not fixed.** Words like "justice" or "freedom" carry
  different weight for different philosophers and can shift within one book.
  Use `terms.md`'s "evolves / reused at" column harder here than anywhere else
  — track the meaning shift chapter by chapter, don't just record a single
  definition.
- **Separate positions from arguments for them.** Note what the author
  believes distinctly from why the author believes it — this keeps Step 5's
  critical judgment honest: you can reject an argument while granting the
  position remains plausible on other grounds, or vice versa.

## Textbooks and reference works

These aren't meant to be read start to finish, and treating them like a
narrative book wastes the pipeline's strengths.

- **Reading is modular and non-sequential, driven by purpose.** Use
  `chapters.tsv` and `split-chapters.sh` to give yourself addressable units,
  but let the reading purpose (SKILL.md Step 1) pick which units get a full
  analytical pass — don't default to chapter order.
- **Exercises serve as the Recite step.** Where SQ3R's Recite means re-skimming
  to verify propositions, a textbook's end-of-chapter exercises or worked
  problems are a stronger verification: if you can't work them, the chapter
  note isn't done yet.
- **Expect to revisit this file's other sections.** A textbook chapter on,
  say, historiographic method or a philosophy-of-science text still inherits
  the genre notes above for its actual subject matter — this section governs
  structure and pacing, not what kind of content sits inside each chapter.
