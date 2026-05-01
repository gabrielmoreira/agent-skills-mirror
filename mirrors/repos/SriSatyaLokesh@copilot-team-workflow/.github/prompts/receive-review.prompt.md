---
description: 'Use when receiving code review feedback — when the Reviewer agent returns findings, a PR has review comments, or a developer asks how to handle review suggestions. Requires verifying suggestions before implementing, not blind agreement.'
agent: 'TDD Implementer'
---
# Receiving Code Review Feedback

Code review is technical evaluation, not emotional performance.
**Verify before implementing. Evidence before criticism. Technical correctness over social comfort.**

---

## The Response Pattern

```
1. READ   — Complete feedback without reacting
2. RESTATE — Restate each item in your own words to confirm understanding
3. VERIFY  — Check each suggestion against the actual codebase
4. EVALUATE — Is this technically correct for THIS codebase?
5. RESPOND — Technical acknowledgment, OR reasoned pushback
6. IMPLEMENT — One item at a time, run npm test after each
```

---

## Forbidden Responses

**NEVER say:**
- "You're absolutely right!" — performative, adds nothing
- "Great point!" — performative
- "Excellent feedback!" — performative
- "Let me implement that right now" — before verifying

**INSTEAD:**
- State the requirement: "The suggestion is to [X] because [reason]"
- Or just start fixing — action {\>} words

---

## Before Implementing Any Suggestion

For each review item, ask:
1. Is this technically correct for this codebase?
2. Does it break any existing tests?
3. Is there a reason the current implementation is the way it is?
4. Does the reviewer have full context?

```bash
# Search for relevant context before implementing
# Does this pattern already exist? Is there a reason for the current approach?
```

---

## Handling Unclear Feedback

**If any item is unclear — STOP. Do not implement anything yet.**

Ask for clarification on ALL unclear items before implementing ANYTHING.

> Why? Items may be related. Partial understanding = wrong implementation.

```
❌ WRONG: Implement items 1,2,3 now, ask about items 4,5 later
✅ RIGHT: "I understand items 1,2,3. Need clarification on 4 and 5 before proceeding."
```

---

## When to Push Back

Push back when:
- Suggestion breaks existing tests or functionality
- Reviewer lacks context about why the current implementation exists
- Suggestion adds unused features (YAGNI)
- Technically wrong for this exact tech stack
- Conflicts with an architectural decision in the Issue doc

**How to push back:**
```
✅ "Checked — build target is 10.15+, this API requires 13+. Removing it would break backward compat. Should I drop pre-13 support instead?"
✅ "Grepped the codebase — this endpoint isn't called anywhere. Should I remove it (YAGNI) rather than improve it?"
❌ "I don't think that's right" (no evidence)
❌ Long defensive explanation
```

---

## Implementation Priority Order

When you have multiple review items:

1. 🔴 **Critical** — fix first (breaks functionality, security holes)
2. 🟠 **Simple fixes** — typos, missing imports, naming (fix quickly)
3. 🟡 **Important** — logic issues, missing tests (fix before next batch)
4. 🔵 **Suggestions** — optimization, style (note for later)

**Test after each fix — not all at the end.**

```bash
# After each individual fix:
npm test -- --testPathPattern="affected/test/path"
```

---

## When Feedback Is Correct

```
✅ "Fixed — [brief description of what changed]"
✅ "Good catch — [specific issue]. Fixed in [file:line]."
✅ [Just fix it and show the diff]

❌ "You're absolutely right!"
❌ "Thanks for catching that!"
❌ Any gratitude expression
```

The code itself shows you heard the feedback.

---

## If You Pushed Back and Were Wrong

```
✅ "You were right — I checked [X] and it does [Y]. Implementing now."
✅ "Verified this — my understanding was wrong. Fixing."

❌ Long apology
❌ Defending the pushback
❌ Over-explaining
```

State the correction, move on.
