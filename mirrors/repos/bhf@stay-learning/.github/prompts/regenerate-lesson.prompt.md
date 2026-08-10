---
description: "Re-plan and rewrite a single lesson, leaving every other lesson untouched"
agent: course-orchestrator
argument-hint: "lesson id, e.g. m01-l02"
---

Regenerate one lesson: `${input:lesson}`

This is the operation the file-based state exists for. Only the named lesson changes.

1. Read `course.yaml` and locate the lesson. If the id does not exist, list the valid ids and
   stop.
2. Check its upstream artefacts. If `outcomes.yaml` is `stale` or `missing`, stop and report
   it — regenerating a lesson against stale outcomes produces a lesson that disagrees with
   the rest of the course.
3. Ask the user what should change, unless they already said. "Regenerate it" without a
   reason usually means the plan is wrong, not the prose.
4. Delegate to `lesson-planner` for this lesson id only, then to `lesson-writer`. The writer
   is a wave stage: it writes the lesson and its `<lesson>.glossary.yaml` and nothing else.
5. Merge the lesson's glossary fragment into `glossary.yaml` yourself, then mark the lesson's
   own plan and content, and nothing else. A lesson regeneration does not make other lessons
   stale.
6. Check the blast radius before finishing. If the new lesson introduces or drops
   terminology, `glossary.yaml` changes, and a later lesson may reference a term that no
   longer exists here. Report any such case rather than fixing it silently.

Do not touch any other lesson's files.
