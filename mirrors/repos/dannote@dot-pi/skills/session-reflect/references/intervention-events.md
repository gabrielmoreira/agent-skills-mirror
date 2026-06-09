# Intervention events

Use this reference to analyze moments where the user interrupts, redirects, challenges, or intensifies the interaction. This is broader than profanity or shouting.

## Definition

An **intervention event** is a user turn that appears to change, challenge, constrain, stop, or reframe the current agent trajectory.

Do not equate intervention with anger. Profanity, all-caps, and repeated punctuation are only retrieval signals. Calm turns like “Ask me what I want to do” or “This is the wrong abstraction” can be higher-signal than profanity.

## Detection signals

Use these as retrieval leads, not final labels.

### Emotional intensity

- profanity or insults
- all-caps spans
- repeated punctuation: `!!!`, `???`, `?????`
- emphatic markers: `WTF`, `NO`, `STOP`

### Direction reversal

- stop / pause / wait
- revert / undo / do not continue
- “not what I asked”
- “wrong direction”

### Abstraction mismatch

- “wrong concept” / “wrong abstraction”
- “this is not how X works”
- “we are building X, not Y”
- “wrong layer”

### Evidence challenge

- “where are the numbers?”
- “did you verify?”
- “are you sure?”
- “show me”
- “you claimed the opposite”

### Convention violation

- “we intentionally…”
- “project already does…”
- “why new namespace?”
- “why JSON?”
- “don’t hand-roll”

### Autonomy boundary

- “discuss before implementing”
- “ask me what I want to do”
- “why did you do X?”
- “stop autoresearch”
- “I want to understand where we are”

### Quality disgust

- “AI slop”
- “terrible name”
- “stupid”
- “what is this shit”
- “looks bad / pure shit”

### Orientation reset

- “what is going on?”
- “remind me”
- “where are we?”
- “recap”
- “what are next steps?” when used after confusion/drift

## Annotation schema

For each candidate event, annotate manually after reading context.

```yaml
message_key:
session_path:
user_turn:
signal_markers:
  - emotional_intensity
  - direction_reversal
  - abstraction_mismatch
  - evidence_challenge
  - convention_violation
  - autonomy_boundary
  - quality_disgust
  - orientation_reset
  - other
target:
  - agent_behavior
  - code_quality
  - architecture_or_api
  - naming
  - missing_evidence
  - external_tool_or_library
  - generated_ai_slop
  - process_or_loop
  - user_state_or_orientation
  - unclear
severity:
  - low
  - medium
  - high
  - stop_the_line
context_radius_needed:
  - immediate
  - medium
  - session_arc
what_happened_before:
what_user_changed_or_challenged:
what_agent_did_after:
worked_recovery:
failed_recovery:
alternative_interpretation:
confidence:
  - low
  - medium
  - high
```

## Context radii

Inspect more than the immediate previous turn when needed.

- **Immediate**: 3 turns before / 5 after. Good for direct correction.
- **Medium**: 10 turns before / 10 after. Good for accumulated drift.
- **Session arc**: initial goal, recent summaries, current branch of work. Good for autoresearch, architecture, or convention violations.

## Control comparison

Before claiming a common pattern, compare against controls:

- intervention cases with the suspected trigger
- intervention cases without the suspected trigger
- non-intervention cases with the suspected trigger

Example: If the suspected trigger is “agent overbuilds”, also inspect overbuild-like cases that did not trigger intervention.

## False-positive notes

Common false positives:

- pasted code, diffs, logs, or shell commands containing uppercase identifiers
- file names like `PR_SUMMARY.md`
- quoted assistant/user text from a previous discussion
- acronym-heavy technical text
- benchmark output or stack traces

Mitigations:

- use `--min-score 2` or higher
- use `--max-len` to skip long pasted turns
- keep the default `--pasted exclude` for ordinary intervention retrieval
- use `--pasted include` to audit all candidates
- use `--pasted only` to inspect likely pasted/code/log false positives
- use `--signal` to inspect a narrower class
- use `--context` before interpreting
- treat `score` as retrieval priority, not severity
- treat `paste_score` as a noise heuristic, not a reason to discard evidence permanently

## Recovery protocol for the agent

When the user produces a high-signal intervention event, do not continue the previous trajectory by default.

1. **Stop** the current action path. Do not make more edits/commands unless needed for safety/status.
2. **Classify the likely intervention target**: intent, evidence, autonomy boundary, quality, orientation, convention, external tool, or unclear.
3. **Restate the corrected constraint** in the user's terms.
4. **Check current state** if code/files/processes may have changed: git status, changed files, running processes, or relevant artifact state.
5. **Offer one narrow recovery action**: revert, patch, inspect, measure, discuss, or ask user choice.
6. **Avoid defending the previous path**. Explain only what is needed to recover.
7. **Resume autonomy only after explicit approval** when the intervention was about autonomy, abstraction, or direction.

Use this short response shape:

```markdown
Stopped.
I think the intervention is about: <target>.
Corrected constraint: <constraint>.
Current state: <brief status or "not checked yet">.
Best recovery action: <one action>.
```

If the user says “go ahead” after this, proceed with the narrow recovery action, not the old broader plan.

## Reporting standards

Use cautious language:

- “This appears to be…”
- “In sampled contexts…”
- “One plausible trigger is…”
- “Counterexample / uncertainty…”

Do not write: “The user gets angry when X” unless the target and trigger are very clear across multiple context-checked examples.

Prefer:

```markdown
Pattern: Agent trajectory intervention after wrong abstraction
Evidence: 4 context-checked examples
Target: agent behavior / abstraction level
Trigger: agent starts implementing at wrong layer before discussion
Recovery that worked: stop, restate corrected abstraction, ask before proceeding
Confidence: medium-high
Uncertainty: some cases may be about accumulated drift rather than one turn
```
