---
description: 'Schema and consistency rules for course state YAML artefacts'
applyTo: "courses/**/*.yaml"
---

# Course State YAML Rules

These files are the course's structured state. Full schemas live in the `course-state` skill
at `.github/skills/course-state/references/schema.md` — load it before editing.

## Always

- Start every artefact with `schema_version: 1`.
- Write whole files. Never patch or append to an artefact — regenerate it in full.
- Use two-space indentation, no tabs, no trailing whitespace.
- Quote any string containing `:`, `#`, or a leading `-`. A colon followed by a space does not
  break the parse, it silently turns a list item into a mapping, so nothing complains until
  a check hundreds of lines away reads the wrong type. `- Account for the total: which two
  layers dominate` is a mapping. `"Account for the total: which two layers dominate"` is the
  string you meant. A colon with no space after it, as in `<image>:<tag>`, is safe.
- Use `>` folded blocks for prose fields longer than one line (`rationale`, `load_justification`).
- Use ISO 8601 dates (`YYYY-MM-DD`).
- Use `null` for a deliberately empty scalar, `[]` for an empty list. Never leave a key dangling.

## Voice in learner-facing fields

Exercise tasks and hints, quiz stems and `why_wrong` text, and the capstone brief, milestones
and rubric levels are read by the learner. They carry the same voice as lesson prose, defined
in [house-style.yaml](../skills/instructional-design/assets/house-style.yaml), which holds an
exemplar and counter-exemplar for each of those surfaces.

- Second person, present tense, active voice. Average sentence under 20 words, none over 30.
- Say what a thing is for before you say what it is made of.
- No "just", "obviously", "of course". No emojis. No hype about the subject.
- Fields no learner reads — `rationale`, `load_justification`, `notes_for_writer` — are notes
  to another agent. They need to be clear, not stylish.

## Ids

- Module: `m<NN>` — `m01`. Lesson: `<module-id>-l<NN>` — `m01-l01`. Outcome: `<lesson-id>-o<N>`.
- Slugs are lowercase, hyphen-separated, ASCII, no leading digit.
- Ids are permanent. Retitling never changes an id.

## Referential integrity

Before finishing any edit, verify:

1. Every id referenced in `outcomes.yaml`, `*.plan.yaml`, or `glossary.yaml` exists in `course.yaml`.
2. Every lesson in `curriculum.yaml` exists in `course.yaml` with the same id and title.
3. `lesson.outcomes` in a plan matches that lesson's outcome ids in `outcomes.yaml` exactly.
4. Every outcome is covered by at least one plan section.
5. Every plan section has a non-empty `covers_outcomes`, except `introduction`, `summary`, `next_lesson`.
6. Section `estimated_minutes` sum to `lesson.estimated_minutes`; lesson minutes sum to module minutes.
7. `depends_on` graphs are acyclic and reference only earlier entries.
8. Paths recorded in `course.yaml` resolve to real files whenever status is `current`.
9. Every term in a plan's `terminology_introduced` has a `glossary.yaml` entry, and that entry's
   `first_used` is the lesson that introduces it. No term is introduced by two plans.
10. Every lesson id in `references_previous` is cited in that lesson's prose, by title and id.
11. No artefact is `current` while anything upstream of it is `missing` or `stale`.
12. A lesson's `<lesson>.glossary.yaml` carries exactly its plan's `terminology_introduced`,
    names its own lesson, and sets no `first_used`. The merge into `glossary.yaml` sets that.

These are machine-checked by the `PostToolUse` validation hook, which reports failures back
to you automatically. Fix the cause of each failure, not the symptom.

## Manifest updates

Who updates `course.yaml` depends on whether your stage can run beside another one.

**Exclusive stages** — audience, curriculum, outcomes, assessment, lesson plan — run alone.
Any artefact write must be followed, in the same turn, by an edit to `course.yaml`:

- set that artefact's `status: current`
- set every downstream artefact's `status: stale` (cascade table is in the `course-state` skill)
- update `course.updated`

Then append one line to `.state/run-log.md`.

**Wave stages** — capstone, lesson content, exercises, quiz — may all be running at once, so
they write neither `course.yaml`, `glossary.yaml`, nor the run log. They write their own
artefact and report the manifest change and log line for the orchestrator to apply. Four
agents appending to one file lose each other's writes without any of them failing.

## Never

- Never hand-edit an artefact outside an agent run.
- Never delete or renumber ids to tidy a sequence.
- Never leave an artefact `current` when its upstream is `stale`.
- Never add keys that are not in the schema. Extend the schema deliberately instead.
