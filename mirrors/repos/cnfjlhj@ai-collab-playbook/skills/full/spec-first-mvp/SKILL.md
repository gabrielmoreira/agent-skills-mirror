---
name: spec-first-mvp
description: "Use when one idea feels exciting enough that the user may rush into implementation before the scope is stable. Turn the idea into a spec seed, define 1-3 throwaway MVP probes, and set a go/no-go gate before full design or execution."
---

# Spec First MVP

## Overview

Use this skill when the danger is not lack of ideas, but too much momentum too early.

The goal is to stop cyber-wishing-machine behavior by inserting one lightweight gate:

```text
raw idea
  -> spec seed
  -> throwaway MVP probe
  -> inspect evidence
  -> go / no-go
  -> only then move to brainstorming, planning, or implementation
```

## Rules

- Separate `problem`, `guess`, `solution shape`, and `wishful extras` before proposing implementation.
- Distill the raw idea into a `spec seed` first:
  - problem
  - user / context
  - first value to prove
  - explicit non-goals
  - pass / fail signal
- Propose only `1-3` throwaway MVP probes. Each probe must answer one important uncertainty.
- Prefer probes that are cheap, inspectable, and disposable:
  - one prompt plus example I/O
  - one static page or mock
  - one minimal retrieval path
  - one scoring or evaluation script
  - one tiny data flow
- Treat the first MVP as a `problem probe`, not as the first production version.
- After the probe, update the spec from evidence instead of expanding the original fantasy unchanged.
- Route onward only after the user can say what was learned and what should happen next.

## When to Use

Use when:

- the user has one promising idea but keeps jumping straight to "just build it"
- requirements drift quickly after a polished generated artifact already exists
- the user asks for `MVP`, `最小验证`, `先做个最小的`, `先收敛一下`, or `先不要赛博许愿机`
- the work involves a tool, workflow, research helper, personal knowledge system, or product concept whose shape is still unstable
- the user wants a small probe or subagent prototype specifically to expose missing spec details

Do not use when:

- multiple materially different directions still need comparison; use `brainstorming`
- the task is already precise and ready to implement
- the main deliverable is a durable plan or spec document rather than a validation loop

## Workflow

1. Triage the raw idea.
   - What problem is definitely real?
   - What part is still a guess?
   - What part is only "would be cool"?

2. Write a `spec seed`.

```markdown
### SPEC SEED
- Problem:
- User / Context:
- First Value To Prove:
- Non-Goals For This Round:
- Pass / Fail Signal:
```

3. Define `1-3` throwaway MVP probes.
   - Each probe tests one risky assumption.
   - Each probe should be small enough that throwing it away is acceptable.

4. Recommend one first probe.
   - Explain why it reduces uncertainty fastest.
   - State what evidence to inspect after it runs.

5. Set the go/no-go gate.

```markdown
### GO / NO-GO
- Continue if:
- Stop or reshape if:
- Open questions after probe:
```

6. Route forward.
   - validated enough -> `brainstorming`, `planning-with-files`, or direct execution
   - still ambiguous -> another `spec-first-mvp` loop

## Common Mistakes

- turning the throwaway probe into a hidden full build
- keeping too many goals in the first round
- using generated polish as proof that the concept works
- comparing giant systems before the core value has been isolated
- calling something an MVP when it is still trying to validate five things at once

## References

- `references/spec-seed-template.md`
