# Paper mode: Keshav's three-pass method

Papers, theses, and surveys aren't structured like books, so read this before
starting the inspectional pass on one (SKILL.md Step 1 points here). S.
Keshav's three-pass method for reading academic papers maps directly onto the
deep-reader pipeline — same scripts, same workspace, different rhythm.

## The three passes, mapped onto this pipeline

**Pass 1 — get the gist.** Read the title, abstract, introduction, section
and subsection headings, and the conclusions. Glance at the references to
place the work. In Keshav's original, this takes 5–10 minutes for a paper; here
it's the equivalent of the inspectional pass, and it produces `map.md` exactly
as SKILL.md Step 2 describes — whole-paper question, unity statement,
structure table. The one difference: chapters become sections, so
`chapters.tsv` rows describe sections (`sec01`, `sec02`, ...) and
`split-chapters.sh` cuts section files instead of chapter files.

**Pass 2 — read with care, but not too much.** Read the body carefully, note
key points, but skip proofs and derivations on the first pass through them —
mark where you skipped and why. This is the analytical pass (SKILL.md Step
3), with one adjustment: chapter notes become section notes,
`notes/sec01-<slug>.md` instead of `notes/ch01-<slug>.md`, using the same
template in [note-templates.md](note-templates.md). Add one field Keshav
calls out specifically: an "unread references" list — citations you noted but
didn't chase, so a later pass (or a syntopical reading across papers) knows
where to look next.

**Pass 3 — virtually re-implement the paper.** Attempt to reconstruct the
paper's argument or method from scratch, as if redoing the work, then compare
your reconstruction against what's on the page. This is expensive — reserve it
for the sections that actually matter to the reading purpose, not the whole
paper. It belongs inside the relevant section's note as an expanded
"arguments" subsection: your own reconstruction next to the author's, with
page cites for where they diverge.

## IMRaD anchor points

Most papers follow Introduction / Methods / Results / Discussion (IMRaD).
Use these as fixed reference points regardless of how the paper's actual
headings are worded:

- **Methods** — what was actually done; the evidence-offered field in each
  section note should distinguish "the author claims" from "the author
  measured."
- **Results** — what was found, independent of interpretation.
- **Discussion** — the author's interpretation and claims about significance.

Keeping these three separate in your notes is what makes the "is it true"
question in synthesis answerable: a result can be solid while the discussion
overclaims it, or a method can be weak while the discussion is appropriately
cautious. Collapsing all three into one undifferentiated note loses that.

## When to skip the apparatus

- **Short papers (≤ ~30 pages)** — passes 1 and 2 fit comfortably in one
  conversation turn. Do them inline: read the paper, produce a lightweight
  map and running notes in the chat itself. Building the full workspace
  (`prepare-text.sh`, `chapters.tsv`, per-section files) is overhead a
  30-page paper doesn't need — skip straight to reading and note-taking by
  hand.
- **Long theses and surveys (100–200 pages)** — treat these as a book, full
  stop. Run the full pipeline from SKILL.md Step 0 onward, with "chapters"
  mapped to the thesis's own chapters or the survey's major sections. The
  three-pass framing still applies conceptually (gist → careful read →
  reconstruct), it just runs through the same chapter-by-chapter loop as any
  other book.
