---
name: instructional-design
description: 'Instructional design method for course planning. Use when sequencing modules, estimating pacing and cognitive load, writing measurable learning outcomes, choosing Bloom taxonomy levels, designing assessments, choosing worked examples, designing a capstone project and its rubric, planning retrieval practice and spacing, or deciding what a lesson should contain. Covers backward design, Bloom verb selection, assessment design, example design, capstone design, retrieval and spacing, and cognitive load heuristics for the curriculum designer, outcomes designer, assessment designer, project designer, and lesson planner.'
user-invocable: false
---

# Instructional Design

Method used by the planning agents. Load this before designing a curriculum, writing
outcomes, or planning a lesson. It exists so that planning decisions are defensible
rather than improvised.

## When to use

| Task | Read |
|---|---|
| Sequencing modules, estimating pacing | [cognitive-load.md](./references/cognitive-load.md) |
| Writing or levelling learning outcomes | [blooms-taxonomy.md](./references/blooms-taxonomy.md) |
| Designing diagnostics, formative items, checkpoints, summatives | [assessment-design.md](./references/assessment-design.md) |
| Choosing and typing the examples inside a lesson | [example-design.md](./references/example-design.md) |
| Deciding where a lesson needs a diagram, and which kind | [diagram-design.md](./references/diagram-design.md) |
| Designing the capstone project, its milestones and rubric | [capstone-design.md](./references/capstone-design.md) |
| Making a course retain — what gets asked for again, and when | [retrieval-and-spacing.md](./references/retrieval-and-spacing.md) |
| Deciding what a course should contain at all | [backward-design.md](./references/backward-design.md) |
| Writing anything a learner reads — prose, tasks, quiz items, rubric levels | [house-style.yaml](./assets/house-style.yaml) |

Verb data is machine-readable in [bloom-verbs.yaml](./assets/bloom-verbs.yaml) and is
enforced by the course-state validator. Edit the data file, never the prose tables.

[house-style.yaml](./assets/house-style.yaml) is one voice for every course and every
learner-facing surface. Its exemplars are the operative part: an instruction about tone is
re-interpreted on every run, and a worked passage is not. Its `limits` and `banned_words`
are enforced for lesson Markdown by the same validator, so change the two together.

## The method in one pass

Work backwards. Design in this order, and never skip ahead.

1. **Destination.** What must the learner be able to *do* afterwards? Not what they will
   be shown. Backward design calls this the desired result.
2. **Evidence.** How would you know they can do it? This becomes the `evidence` field on
   every outcome, and then the items in `assessment.yaml`.
3. **Route.** Only now decide the modules, lessons, and activities that get them there.

Most weak courses are built in the opposite order: content first, outcomes retrofitted.
The symptom is a lesson whose outcomes could be swapped with another lesson's without
anyone noticing.

## Outcome rules

Every outcome must satisfy all five:

1. Starts with exactly one observable verb from the Bloom tables.
2. Describes learner behaviour, not teaching activity. "Explain X", never "Cover X".
3. Is assessable. If you cannot describe the evidence, the outcome is not measurable.
4. Sits at a level the lesson actually reaches. Do not claim `evaluate` for a lesson that
   only explains.
5. Is one outcome. If it contains "and", it is probably two.

Never use `understand`, `know`, `learn`, `appreciate`, or `be familiar with`. They name an
internal state you cannot observe. The full banned list is in the verb data file.

## Levelling heuristics

- A beginner lesson usually spans `remember` through `apply`. Reaching `analyze` in a first
  lesson is possible but should be deliberate.
- Level should trend upward across a module. A later lesson sitting below an earlier one is
  a signal that the sequence is wrong, unless it opens a genuinely new topic.
- A course that never leaves `remember` and `understand` produces learners who can recite
  and cannot act. A course that opens at `evaluate` produces learners who bluff.
- Three to five outcomes per lesson. More than five usually means the lesson is two lessons.

## Pacing heuristics

- Estimate section minutes, then sum upward. Never estimate a lesson total directly and
  divide, because that hides overloaded sections.
- Practice needs at least as much time as theory. If theory dominates a lesson, learners
  will not retain it.
- Total course time must land within 15% of the learner's stated budget. If it does not,
  cut scope rather than compressing each lesson, which only moves the problem.
- Assume learners forget between sessions. A lesson following a week-long gap needs an
  explicit reconnection to the previous one, which is what `references_previous` is for.

## Cognitive load in brief

Rate each module `low`, `medium`, or `high`, and justify it by naming the load sources.
The rating caps new terminology for the module at 6, 10, or 15, and the validator enforces
that against the lesson plans once they exist.
Count new mental models, new terms, new tools, and new syntax. Full rubric and the
overload signals are in [cognitive-load.md](./references/cognitive-load.md).

A module rated `high` next to another rated `high` is a sequencing problem. Separate them
with a consolidation lesson or move one.
