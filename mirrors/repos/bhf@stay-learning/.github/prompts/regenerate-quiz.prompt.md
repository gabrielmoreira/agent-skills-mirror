---
description: "Regenerate the quiz for a single lesson, leaving the lesson itself untouched"
agent: course-orchestrator
argument-hint: "lesson id, e.g. m01-l02"
---

Regenerate the quiz for one lesson: `${input:lesson}`

The quiz is a leaf artefact. Nothing depends on it, so this is the cheapest regeneration in
the pipeline — and the only correct outcome is that the lesson's `.md` and `.plan.yaml` come
out byte-identical.

1. Read `course.yaml` and locate the lesson. If the id does not exist, list the valid ids and
   stop.
2. Check the lesson's `.plan.yaml`. If it is `missing` or `stale`, stop and report it. A quiz
   built against a stale plan tests a lesson that no longer exists.
3. Ask the user what is wrong with the current quiz, unless they already said. The usual
   answers are a weak distractor, an item pitched above its outcome, or an outcome the quiz
   never reaches — and each one leads somewhere different.
4. Delegate to `quiz-generator` for this lesson id only. Pass on what the user said; the
   subagent cannot see this conversation.
5. Update only that lesson's `quiz` entry in `course.yaml`, and append the log line the
   subagent reported. The quiz generator is a wave stage and writes neither, so if you skip
   this the manifest is left disagreeing with the disk. Regenerating a quiz marks nothing
   stale, in either direction.
6. Before finishing, confirm the lesson's `.md` and `.plan.yaml` were not modified. If either
   changed, the subagent exceeded its remit — report it rather than reverting quietly, since
   it means the agent's constraints need fixing, not just this run.

Do not touch the lesson content, the plan, the glossary, or any other lesson.
