---
description: "Create a new course from a topic and audience, running the full authoring pipeline"
agent: course-orchestrator
argument-hint: "Course topic and target audience"
---

Create a new course.

Brief: `${input:brief}`

Before starting, make sure you have all of these. Ask for anything missing, as one batch:

- the topic, and what the learner should be able to do at the end
- who the learner is, and their experience level
- the total time available, and the session length
- any constraints on tooling, data, or environment

Then:

1. Scaffold `courses/<slug>/` if it does not exist, including an empty `glossary.yaml`
   (`schema_version: 1`, `terms: []`). Without it the validator stops early and every lesson
   plan is written unchecked.
2. Run the stages in order: audience, curriculum, outcomes, assessment.
3. Stop after assessment and report the module sequence, the time budget, the outcome count,
   and how each outcome is assessed. Wait for the user to approve the shape of the course
   before any lesson is planned. This is the whole contract the lessons will be built to
   satisfy, so it is the last cheap moment to change it.
4. On approval, plan every lesson, one `lesson-planner` run at a time, in lesson order across
   the whole course. Plans are written against each other — a plan must not introduce a term
   an earlier plan already introduced — so this stage cannot be parallelised, and it is the
   cheapest stage in the course anyway.
5. Stop again once every plan is `current`. Report the section shape and the terminology
   budget per module, and check every plan carries a `continuity` block and that no term is
   claimed by two plans. Both are what make the next step safe.
6. Then dispatch the wave: `project-designer` once, and `lesson-writer`,
   `exercise-generator` and `quiz-generator` for every lesson, all in one batch. Nothing in
   the wave reads anything else in the wave.
7. When the wave returns, merge the lesson glossary fragments into `glossary.yaml`, land
   every reported manifest change in one edit, and append the run log lines. In that order:
   the manifest claims the glossary is current, so merging second would mean saying so
   before it was true.

Do not write any artefact yourself. Delegate every stage. The glossary merge, the manifest
and the run log are yours — that is bookkeeping, not authoring.
