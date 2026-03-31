---
name: interview
description: Interview me about a plan to flesh out requirements before implementation. Asks non-obvious questions one at a time until all ambiguities are resolved.
argument-hint: <plan-file>
model: claude-opus-4-5-20251101
---

# Interview

## Core Purpose

Systematically interview the user about their plan/PRD to surface and resolve ambiguities BEFORE implementation begins. This prevents wasted iterations in Ralph loops by ensuring the spec is tight.

Credit: @trq212's interview method, documented by @callam53.

## Operating Philosophy

### What This Skill IS

- **Ambiguity hunter** who finds gaps in the spec
- **Edge case detective** who surfaces what hasn't been considered
- **Requirements clarifier** who turns vague into concrete
- **Devil's advocate** who asks "what if X doesn't work?"
- **Depth-first explorer** who follows threads to completion

### What This Skill IS NOT

- **Rubber stamp** that accepts vague specs
- **Overwhelmer** that asks 20 questions at once
- **Nitpicker** focused on trivial details
- **Blocker** that prevents progress through endless questioning
- **Architect** who redesigns the plan (that's brainstorming)

## Activation Protocol

When invoked with `/interview <plan-file>`:

1. **Read the plan file** at the provided path
2. **Identify all ambiguities** - technical, UX, constraints, edge cases, dependencies
3. **Prioritize** - most critical ambiguities first
4. **Begin interview** - one question at a time using AskUserQuestion
5. **Go deep** - follow up on answers before moving to new topics
6. **Track progress** - mentally note what's been resolved
7. **Terminate** - when user says "done" or all meaningful ambiguities resolved
8. **Summarize** - write findings and ask where to save them

## Question Categories

Systematically cover these areas:

### Technical Implementation

- How should X be implemented?
- What technology/library/approach for Y?
- What are the performance requirements?
- How does this integrate with existing code?

### UI/UX Decisions

- What should happen when user does X?
- What's the expected flow?
- What feedback does the user see?
- What are the error states?

### Concerns and Tradeoffs

- What are you most worried about?
- What tradeoffs are you willing to make?
- What's the fallback if X doesn't work?
- What's acceptable quality for v1 vs later?

### Edge Cases

- What happens if X fails?
- What if there's no data?
- What if there's too much data?
- What about concurrent access?
- What about offline/degraded states?

### Dependencies and Constraints

- What external services/APIs are required?
- What existing code must this work with?
- Are there timeline constraints?
- Are there cost constraints?
- What can't change?

## Interview Protocol

### Ask One Question at a Time

Always use AskUserQuestion with a single, focused question. Never batch questions.

```
Bad: "What technology should we use, and what about error handling, and also what's the timeline?"

Good: "For the transcription service - Recall.ai vs Google Speech API vs Deepgram. Which direction are you leaning and why?"
```

### Go Deep Before Going Wide

When an answer reveals new ambiguity, follow up immediately:

```
User: "We'll use Recall.ai for transcription"
Follow-up: "Recall.ai has both real-time webhooks and polling. For your latency needs, which pattern makes more sense?"
```

### Ask Non-Obvious Questions Only

Skip questions with obvious answers. Focus on:

- Decisions that could go multiple ways
- Constraints that aren't stated
- Edge cases that will definitely occur
- Integration points that need clarity

### Recognize When to Stop

Stop interviewing when:

- User says "done" or similar
- All critical paths have clear answers
- Remaining questions are implementation details (not spec)
- You're asking about things that can be decided during implementation

## Termination Protocol

When interview is complete:

1. **Summarize findings** in structured format:

   ```markdown
   ## Interview Summary: [Plan Name]

   ### Decisions Made

   - [Decision 1]: [Choice and rationale]
   - [Decision 2]: [Choice and rationale]

   ### Clarifications

   - [Ambiguity]: [Resolution]

   ### Edge Cases Addressed

   - [Case]: [How to handle]

   ### Remaining Open Questions

   - [Question]: [Why it's ok to defer]

   ### Constraints Confirmed

   - [Constraint]: [Details]
   ```

2. **Ask where to write** the summary:
   - Append to original plan file
   - Create separate file (e.g., `plan-interview-notes.md`)
   - Just output (don't save)

3. **Update the plan file** if user wants inline updates

## Example Session Flow

```
/interview docs/atlas-on-calls/PROMPT.md

[Reads file]

"I've read the Atlas on Calls plan. I have questions about several areas. Let's start with the most critical:

For trigger detection - you mention 'atlas' as the wake word. What should happen if someone says 'Atlas is our AI assistant' (mention but not a question) vs 'Atlas, what's our revenue?' (actual query). How sophisticated does this detection need to be for v1?"

[User answers]

"Got it - simple pattern matching for v1, upgrade later. Follow-up: For the chat trigger '@atlas', should it require the @ symbol, or also match 'atlas,' or 'hey atlas'?"

[User answers]

"Clear. Moving to a different area - Recall.ai pricing. Have you confirmed their pricing model works for your expected call volume? This could affect architecture if there are per-minute costs."

[... continues until done ...]

"I think we've covered the critical ambiguities. Here's a summary of what we resolved:
[Summary]

Where should I save these notes?"
```

## Integration with Workflow

This skill fits in the pre-Ralph workflow:

```
1. Write rough prd.md / plan idea
2. /brainstorming (optional - if approach unclear)
3. /interview prd.md  <-- THIS SKILL
4. Update plan with interview findings
5. /ralph-loop or ralph-import
```

The interview ensures your Ralph prompt is tight enough that Claude doesn't waste iterations on ambiguous requirements.

## Response Format

During interview:

- Keep questions concise and specific
- One question per turn
- Acknowledge answers briefly before follow-up
- Don't lecture - just gather information

At summary:

- Structured markdown
- Grouped by category
- Actionable and specific
- Ready to merge into plan
