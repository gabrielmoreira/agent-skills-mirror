# Diataxis Patterns

Use this reference when writing, restructuring, or reviewing documentation in
detail. Keep the main `SKILL.md` as the decision guide; use this file for
templates, section patterns, and anti-patterns.

## Quick Classification Questions

Ask these questions in order:

1. What is the reader trying to do right now?
2. Would success mean learning a capability, completing a task, finding facts, or
   understanding a concept?
3. What would annoy this reader most: missing hand-holding, missing steps,
   missing details, or missing rationale?
4. Is this page trying to serve more than one of those needs?

Common cues:

| Cue | Likely type |
| --- | --- |
| "I'm new", "teach me", "getting started", "walk me through" | Tutorial |
| "How do I", "set up", "deploy", "fix", "migrate", "configure" | How-to |
| "What are the fields", "list options", "API", "parameters", "limits" | Reference |
| "Why", "concept", "architecture", "tradeoff", "background" | Explanation |

## Templates

### Tutorial Template

```markdown
# Learn [capability] by building [small concrete result]

## What you will build
[One paragraph describing the concrete result.]

## Before you start
- [Prerequisite 1]
- [Prerequisite 2]

## Step 1: [Do the first action]
[Small action. Include expected result.]

## Step 2: [Add the next concept through action]
[Small action. Include expected result.]

## Check your work
[Observable success criteria.]

## What you learned
[Short recap of the concepts the exercise introduced.]

## Next steps
- [Related how-to]
- [Reference page]
```

Tutorial notes:

- Keep the route narrow. Beginners need a path before they need options.
- Use small checkpoints so mistakes are caught early.
- Teach concepts after the reader has seen them in action.

### How-to Template

```markdown
# How to [achieve task outcome]

## When to use this guide
[Specific situation.]

## Prerequisites
- [Access, tools, prior setup]

## Steps
1. [Action]
2. [Action]
3. [Action]

## Verify the result
[Commands, UI checks, expected state, or acceptance criteria.]

## Troubleshooting
| Problem | Cause | Fix |
| --- | --- | --- |
| [Symptom] | [Likely cause] | [Action] |

## Related
- [Explanation]
- [Reference]
```

How-to notes:

- Start from a task the reader already knows they need.
- Include branches only where the reader must choose.
- Keep background short and operational.

### Reference Template

```markdown
# [Subject] reference

## Summary
[One or two sentences defining the scope.]

## [Entity, command, endpoint, field, policy, or option]

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| [name] | [type] | [yes/no] | [value] | [precise meaning] |

## Examples
[Minimal examples that clarify usage, not a full tutorial.]

## Limits and constraints
- [Limit]
- [Constraint]

## Related
- [How-to]
- [Explanation]
```

Reference notes:

- Prefer repeatable structure over prose variety.
- Put names, defaults, and limits where users can scan them.
- Avoid hiding important facts in narrative paragraphs.

### Explanation Template

```markdown
# Understanding [concept or decision]

## The problem
[What tension, need, or context created this concept.]

## The mental model
[The simplest accurate way to think about it.]

## How it works
[Conceptual description, not a step-by-step procedure.]

## Tradeoffs
| Option | Strength | Cost |
| --- | --- | --- |
| [Option] | [Strength] | [Cost] |

## Consequences
[What this means for users, maintainers, or operators.]

## Related
- [Tutorial]
- [How-to]
- [Reference]
```

Explanation notes:

- Make the reader wiser rather than merely instructed.
- Include alternatives and context when they clarify the design.
- Avoid burying the reader in implementation detail unless it changes the mental
  model.

## Review Patterns

### Diagnose a Confusing Page

1. Mark each section as Tutorial, How-to, Reference, or Explanation.
2. Identify the page's implied promise from the title and introduction.
3. Find sections that break that promise.
4. Decide whether to remove, move, or relabel those sections.
5. Rewrite the opening so the reader knows exactly what job the page serves.

### Restructure a Documentation Set

1. Inventory pages and classify each by reader job.
2. Group pages by type before grouping by implementation component.
3. Add navigation between related types:
   - Tutorial to how-to: "Now solve real tasks."
   - How-to to reference: "Look up fields/options."
   - Reference to explanation: "Understand design rationale."
   - Explanation to tutorial/how-to: "Apply the concept."
4. Rename pages so the type is visible from the title.

### Convert a Mixed "Getting Started" Page

Split into:

- Tutorial: first successful end-to-end path.
- How-to: setup variants, production setup, migration, troubleshooting.
- Reference: configuration options, commands, environment variables.
- Explanation: architecture, concepts, why the system is designed this way.

## Anti-Patterns

### Tutorial Anti-Patterns

- Starting with a long conceptual essay before the first action.
- Presenting every possible option instead of one safe path.
- Requiring the learner to make expert choices too early.
- Ending without a visible success state.

### How-to Anti-Patterns

- Teaching basic concepts instead of completing the task.
- Omitting prerequisites or verification.
- Hiding dangerous side effects in prose.
- Mixing several unrelated tasks into one guide.

### Reference Anti-Patterns

- Incomplete tables, missing defaults, or inconsistent field descriptions.
- Narrative structure that makes lookup slow.
- Examples that imply rules not documented elsewhere.
- Rationale paragraphs that interrupt scanning.

### Explanation Anti-Patterns

- Pretending to be a task guide without ordered steps.
- Explaining every implementation detail rather than the meaningful model.
- Avoiding tradeoffs and alternatives.
- Ending without saying what the concept changes for the reader.

## Review Response Template

Use this structure for concise audits:

```markdown
## Diagnosis
[Dominant type] with [secondary type] mixed in.

## Why it feels confusing
- [Section]: [problem]
- [Section]: [problem]

## Recommended structure
1. [Target page/type]
2. [Target page/type]

## Rewrite notes
- [Concrete change]
- [Concrete change]
```
