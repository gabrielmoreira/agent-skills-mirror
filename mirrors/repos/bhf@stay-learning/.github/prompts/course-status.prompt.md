---
description: "Report the state of a course and the next action required"
tools: [read, search]
argument-hint: "course slug (optional)"
---

Report the state of the course: `${input:course}`

If no course was named, report on every course under `courses/`.

Read `course.yaml` and the `.state/run-log.md`. Load the `course-state` skill as well — the
stage order and the cascade table are what turn a list of statuses into a next action. Do
not write anything, this is a read-only report.

Report:

1. **Course** — slug, title, status, last updated.
2. **Artefacts** — a table of audience, curriculum, outcomes, assessment, project, glossary
   with their statuses.
3. **Lessons** — a table of lesson id, title, and the status of each of its four artefacts:
   plan, content, exercises, quiz.
4. **Progress** — out of the total number of lessons, how many are planned, written, and
   have both an exercise set and a quiz. Report the capstone separately: it branches off
   assessment rather than following the lessons, so it is not part of that count.
5. **Next action** — the single next stage, derived from the stage order in the
   `course-state` skill, and which agent performs it. The capstone may run any time after
   assessment is `current`; if it is outstanding, say so alongside the next lesson stage
   rather than instead of it.
6. **Blockers** — anything `stale`, any manifest entry that disagrees with what is on disk,
   and any artefact that is `current` while something upstream of it is not. The cascade
   table in the `course-state` skill says what is upstream of what; content, exercises and
   quiz all sit downstream of the lesson plan. Say what each one means for the next run.

If everything is `current`, say so and report what the course would need to be considered
finished.

Keep it to tables and short lines.
