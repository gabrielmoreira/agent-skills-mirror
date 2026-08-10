---
name: course-state
description: 'Read and write the course state files under courses/<slug>/. Use whenever creating a course, reading or updating course.yaml, audience.yaml, curriculum.yaml, outcomes.yaml, assessment.yaml, project.yaml, glossary.yaml, lesson plan files, lesson Markdown, exercise files, or quiz files. Defines the schema, id rules, artefact status lifecycle, and the stage dependency order for every course authoring agent.'
user-invocable: false
---

# Course State

The course is a structured object on disk, not a chain of prompts. Every authoring agent reads
and writes the same files. Load this skill before any read or write under `courses/`.

## Folder layout

```
courses/<course-slug>/
  course.yaml                     # manifest — the index of truth
  audience.yaml                   # learner profile
  curriculum.yaml                 # modules, sequencing, dependencies, pacing
  outcomes.yaml                   # learning outcomes per lesson, Bloom-tagged
  assessment.yaml                 # diagnostic, formative, checkpoints, summative
  project.yaml                    # capstone: brief, milestones, rubric against skills
  glossary.yaml                   # term -> definition, first-use lesson
  modules/
    m01-<module-slug>/
      l01-<lesson-slug>.plan.yaml # lesson structure, written before prose
      l01-<lesson-slug>.md        # lesson content
      l01-<lesson-slug>.glossary.yaml  # terms this lesson introduces, merged into glossary.yaml
      l01-<lesson-slug>.exercises.yaml # standalone practice, done with the lesson closed
      l01-<lesson-slug>.quiz.yaml      # knowledge check, one item per outcome minimum
  .state/
    run-log.md                    # append-only provenance record
```

Full field-by-field schemas: [references/schema.md](./references/schema.md).
Starting points: [course.template.yaml](./assets/course.template.yaml),
[lesson-plan.template.yaml](./assets/lesson-plan.template.yaml).
Validator: [scripts/validate.py](./scripts/validate.py).

## Id and slug rules

- Slugs are lowercase, hyphen-separated, ASCII, no leading digits: `intro-to-kubernetes`.
- Module id: `m` + zero-padded two digits — `m01`, `m02`.
- Lesson id: `<module-id>-l<NN>` — `m01-l01`. Unique course-wide.
- Outcome id: `<lesson-id>-o<N>` — `m01-l01-o1`.
- Folder and file names carry the slug **and** the number: `modules/m01-foundations/l01-what-is-x.md`.
- Ids are permanent. Renaming a title never renames an id.

## Artefact status lifecycle

`course.yaml` tracks the state of every artefact:

| Status | Meaning |
|---|---|
| `missing` | Not yet generated |
| `current` | Generated and consistent with everything upstream |
| `stale` | An upstream artefact changed after this one was written |

## Stage dependency order

```
audience -> curriculum -> outcomes -> assessment -> lesson plan -> lesson content
                                               |                \-> exercises
                                               |                \-> quiz
                                               \-> project
```

- **Refuse to run** if your upstream artefact is `missing`. Report which stage must run first.
- **Stop and ask the user** if your upstream artefact is `stale`. Do not silently build on it.
- Glossary is written by the lesson writers, one fragment each, and merged by the
  orchestrator. It has no upstream gate.
- Assessment sits before lesson planning on purpose. The evidence that proves an outcome is
  decided before the lesson that produces it, not inferred afterwards from whatever got
  written.
- Lesson content, exercises and quiz are siblings. All three derive from the plan, and none
  of them depends on the others. A quiz derived from the prose could only ever test what the
  prose happened to cover, so it could never reveal that the lesson missed its outcome.
- Examples are not an artefact. They are typed in the plan and rendered in the prose,
  because an example cannot be regenerated without rewriting the paragraphs around it, and a
  file that can never change alone is a lie about granularity.
- The capstone branches off assessment and no lesson depends on it. It marks integration
  across modules, against `skills_unlocked`, where everything else marks one outcome at a
  time.

## Exclusive stages and wave stages

| | Stages |
|---|---|
| Exclusive — one at a time, in stage order | audience, curriculum, outcomes, assessment, lesson plan |
| Wave — any number at once | project, lesson content, exercises, quiz |

Every exclusive stage is upstream of every wave stage, so a course runs as a sequence of
exclusive stages followed by a single wave. Once every lesson plan is `current`, everything
left in the course is a wave stage: the capstone, and the content, exercises and quiz of
every lesson in every module. All of it can run at once.

Lesson planning is exclusive because a plan is written against its siblings — it must not
introduce a term an earlier plan already introduced, and it spends from a module-wide
terminology budget that only the other plans can tell it the balance of. Plans are also the
cheapest stage in the course, so serialising them costs least.

What makes a wave safe is that no two agents in it write the same file. A wave agent writes
exactly one artefact and that artefact belongs to it alone.

## Shared files

Three files are written by more than one stage:

- `course.yaml`
- `glossary.yaml`
- `.state/run-log.md`

An exclusive stage writes them itself; nothing else is running. **A wave stage never writes
them.** It reports the manifest change and the log line it would have written, and the
orchestrator applies both once the wave is in.

This is not caution about file locking. Four agents appending to one log, or re-sorting one
glossary, lose each other's writes without any of them failing — and a lost status flip is
worse than a wrong one, because nothing downstream can tell it went missing.

## Write procedure

### Exclusive stages

1. Read `courses/<slug>/course.yaml`.
2. Verify your upstream artefact status (see stage order above).
3. Write your artefact as a **whole file**. Never append to or patch an existing artefact —
   regenerate it in full so re-running an agent is idempotent.
4. Update `course.yaml`:
   - set your own artefact `status: current`
   - set every downstream artefact `status: stale`
   - update `course.updated` to today's date (ISO 8601)
5. Append one line to `.state/run-log.md`:
   `- 2026-08-01 | curriculum-designer | wrote curriculum.yaml | marked stale: outcomes, 4 plans, 4 lessons`

### Wave stages

1. Read `courses/<slug>/course.yaml`.
2. Verify your upstream artefact status. For all four wave stages that is one artefact:
   `assessment.yaml` for the capstone, this lesson's `.plan.yaml` for the other three.
3. Write your artefact as a whole file — and, if you are the lesson writer, its glossary
   fragment. Write nothing else.
4. Report, in your final message and in this form, so the orchestrator can apply it without
   re-deriving it:
   - `manifest: <artefact key> -> current`, plus anything you marked stale, which for all
     four wave stages is nothing
   - `log: - <date> | <agent> | wrote <path> | marked stale: none`

Between step 3 and the orchestrator's write, `course.yaml` disagrees with what is on disk.
That is the manifest-vs-disk warning, and during a wave it is expected. It clears when the
orchestrator lands the wave.

**The exception.** The curriculum designer backfills `address_in` on each misconception in
`audience.yaml`, because lesson ids do not exist when the profile is written. This is a
link-only edit: it changes no other field, does not set `audience` to `stale`, and does not
cascade. No other cross-stage edit is permitted.

## Writing prose into YAML

Every prose field in these artefacts is Markdown: stems, options, `why_wrong`, tasks,
solutions, definitions, rubric levels. Markdown prose routinely contains the two characters
that plain YAML scalars cannot start or carry, and a course about regex, shell or JSON
contains them in almost every line.

**Never write a prose value as a bare plain scalar.** Use a block scalar:

```yaml
      text: >-
        The lower-case `error` in `error-code: 10`
      why_wrong: >-
        `\d` already means a digit, so `[\d]` adds nothing.
```

The two failures this prevents, both of which make the file unreadable to the validator and
invisible in the web viewer:

- A value beginning with a backtick — <code>text: \`\d\` matches a digit</code>. A backtick
  cannot start a plain scalar at all; YAML reserves it.
- A `: ` anywhere inside the value — `text: the field error-code: 10`. YAML reads it as a
  nested key and the file either fails to parse or silently becomes a mapping.

`>-` folds newlines to spaces and strips the trailing one, which is what prose wants. Use
`|-` only where the line breaks are meaningful. Prefer `>-` over `>` for any value the
validator compares verbatim against another artefact — `>` leaves a trailing newline and
the comparison fails.

Single-line values with neither hazard may stay plain. If you are unsure, use `>-`.

## Glossary fragments

The lesson writer authors the definitions it uses and needs them before it writes a word, so
it cannot wait for the orchestrator to hand them back. It writes them to a fragment of its
own, beside the lesson:

```
modules/<module-slug>/<lesson-slug>.glossary.yaml
```

The fragment holds only the terms that lesson introduces, and carries no `first_used`: the
file belongs to one lesson, so the field would restate the filename. The orchestrator merges
every fragment into `glossary.yaml` after the wave — terms sorted alphabetically, `first_used`
set to the fragment's lesson.

A term is introduced by exactly one plan, so a merge collision cannot legitimately happen. If
two fragments define the same term, the planning is wrong; the validator reports it rather
than picking a winner, because either definition might be the good one and the merge cannot
tell.

Fragments are not tracked separately in `course.yaml`. A lesson's fragment shares the status
of its content, because the same agent writes both in the same run.

## Validation

[scripts/validate.py](./scripts/validate.py) checks every invariant below, plus the lesson
content rules. You do not run it yourself and you do not need shell access. The
`PostToolUse` hook in `.github/hooks/` runs it after every edit and blocks with the failure
list when the course is inconsistent.

When you are handed a validation failure, fix the cause rather than the symptom. A minute
total that disagrees with the curriculum usually means one of the two is wrong, not that the
numbers need forcing into line.

Some checks report `WARN` instead of `FAIL`. These are states that are correct midway
through a write procedure but wrong once you stop — chiefly the manifest disagreeing with
what is on disk, which is unavoidable between step 3 and step 4. A warning does not block
you. It does mean your run is unfinished: complete the remaining steps and it clears.
Never end a turn with a warning outstanding.

A human can run it directly:

```bash
./scripts/setup.sh    # once, to create .venv with the dependencies
.venv/bin/python .github/skills/course-state/scripts/validate.py courses/<slug>
.venv/bin/python .github/skills/course-state/scripts/validate.py --strict   # warnings become failures
```

## Downstream cascade

When an artefact is rewritten, everything after it in the stage order becomes `stale`:

| Rewritten | Marked stale |
|---|---|
| `audience.yaml` | curriculum, outcomes, assessment, project, all plans, all lesson content, all exercises, all quizzes |
| `curriculum.yaml` | outcomes, assessment, project, all plans, all lesson content, all exercises, all quizzes |
| `outcomes.yaml` | assessment, project, all plans, all lesson content, all exercises, all quizzes |
| `assessment.yaml` | project, all plans, all lesson content, all exercises, all quizzes |
| `project.yaml` | nothing |
| `<lesson>.plan.yaml` | that lesson's content, exercises and quiz only |
| `<lesson>.md` | nothing |
| `<lesson>.exercises.yaml` | nothing |
| `<lesson>.quiz.yaml` | nothing |

A lesson plan rewrite never marks other lessons stale. The four leaf artefacts never mark
anything stale, which is what makes regenerating a quiz cheap and safe.

## Invariants

These hold at all times. Verify them before finishing a write.

1. `schema_version: 1` is present in every YAML artefact.
2. Every id referenced in `outcomes.yaml`, `*.plan.yaml`, and `glossary.yaml` exists in `course.yaml`.
3. Every lesson listed in `curriculum.yaml` appears in `course.yaml` with matching id and title.
4. Every outcome is covered by at least one plan section.
5. Every plan section maps to at least one outcome, except `introduction`, `summary`, and `next_lesson`.
6. Every term in `terminology_introduced` has a `glossary.yaml` entry once the lesson is written.
7. File paths in `course.yaml` resolve to real files whenever status is `current`.
8. Every lesson id in a plan's `references_previous` is actually cited in that lesson's prose,
   by both title and id.
9. No artefact is `current` while anything upstream of it is `missing` or `stale`.
10. Every outcome has at least one formative assessment item, and no item is pitched above
    the Bloom level of the outcome it assesses.
11. Every outcome at `apply` or above has at least one exercise, and every outcome has at
    least one quiz item, once those artefacts exist for the lesson.
12. Every example is typed against the five kinds, carries the fields its kind requires and
    none from another, and appears in the prose as an `###` heading. A lesson with an
    outcome at `apply` or above has at least one `worked` or `completion` example.
13. Every rubric criterion names a skill some module declares in `skills_unlocked`, and every
    skill some module declares is named by a rubric criterion. Both directions fail.
14. Every glossary term is asked for in an exercise or a quiz at or after the lesson that
    introduces it, and is met again in learner material after that lesson — a later lesson
    or the capstone. The lesson's own quiz does not count as meeting it again. Every module
    after the first re-uses some earlier module's terminology.
15. No term appears in the `terminology_introduced` of two lesson plans. One lesson
    introduces a term; every later lesson reuses it.
16. Where a lesson has a glossary fragment, that fragment carries exactly its plan's
    `terminology_introduced`, and `glossary.yaml` holds every one of those terms with
    `first_used` set to that lesson. A lesson written before fragments existed has none;
    regenerating it produces one.
17. Every diagram a plan declares appears in that lesson's prose as a Mermaid block of the
    kind it names, and the prose carries no Mermaid block the plan did not declare. Every
    block declares `accTitle` and `accDescr`, no node label exceeds 30 characters, no edge
    label exceeds 24, and no diagram declares more than 12 nodes.

Invariant 14 counts terms verbatim, including plural and simple suffixed forms. A later
passage that paraphrases a term rather than using it does not satisfy it, which is the
intended reading: defining vocabulary and then avoiding it teaches the concept and withholds
the language.

These are machine-checked. Run the validator rather than reasoning about them by hand.

## Creating a new course

1. Derive the slug from the course title.
2. Create `courses/<slug>/` and `courses/<slug>/.state/run-log.md`.
3. Copy [course.template.yaml](./assets/course.template.yaml) to `course.yaml` and fill in
   `course.*`. Leave `modules: []` — the curriculum designer populates it.
4. Write an empty `glossary.yaml`: `schema_version: 1` and `terms: []`.
5. All artefacts start at `status: missing`, including the glossary. The file exists and the
   artefact does not, which is the one place those two come apart on purpose.

Step 4 is why the validator can see anything before the wave. It stops at the first artefact
file that is absent and reports the course as in progress, so with no `glossary.yaml` on disk
every lesson plan in the course is written unchecked — and the plans are what the wave is
built from. An empty glossary costs nothing and buys the checkpoint its teeth.
