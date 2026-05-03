---
type: skill
lifecycle: stable
inheritance: inheritable
name: "dialog-engineering"
description: CSAR Loop and structured conversation patterns for effective AI dialog -- Clarify, Summarize, Act, Reflect
tier: core
applyTo: '**/*dialog*,**/*engineering*'
currency: 2026-04-20
lastReviewed: 2026-04-30
---

# Dialog Engineering


> Single prompts fail at complex problems. Structured dialog succeeds.

## The CSAR Loop

Every effective AI conversation follows four phases in a loop:

| Phase | Purpose | Signal |
|-------|---------|--------|
| **Clarify** | Provide context, constraints, scope, and domain specifics | "I'm building X with Y for Z" |
| **Summarize** | State the goal in one sentence so both sides align | "Show me the service layer for..." |
| **Act** | AI generates output: code, docs, analysis, plan | Output is produced |
| **Reflect** | Evaluate, iterate, go deeper, or pivot | "Go deeper on...", "What did I miss?" |

```
  Clarify ──→ Summarize ──→ Act ──→ Reflect
     ↑                                  │
     └──────────────────────────────────┘
```

The loop is not one-shot. Complex tasks cycle 3-5 times. Each cycle narrows the solution space.

## Why Dialog Beats Single Prompts

| Single Prompt | Dialog |
|---------------|--------|
| Front-loads all requirements | Discovers requirements together |
| Hopes AI guesses right | Steers toward the vision |
| Restarts on failure | Refines incrementally |
| 1 attempt, pass/fail | Multiple iterations, continuous improvement |
| Cognitive overload (for AI) | Manageable chunks |

## Turn Design Patterns

### Turn 1: The Anchor (Clarify + Summarize)

State context AND goal in the first turn. Include:

- Tech stack and constraints
- What output you want (code, doc, plan, analysis)
- What you DON'T want (avoids the most common waste)

**Good**: "I need to add authentication to my Express/TypeScript API. Current stack: Express 4, Prisma, PostgreSQL. What approaches do you recommend? Keep it simple."

**Bad**: "Build me a complete user authentication system with login, registration, password reset, JWT tokens, refresh tokens, email verification, rate limiting, and tests."

### Turn 2+: Steering Moves

| Move | When to Use | Example |
|------|-------------|---------|
| **The Probe** | Need deeper reasoning | "Why did you choose X over Y?" |
| **The Constraint** | Add a new requirement | "Now make it work with [limitation]" |
| **The Pivot** | Wrong direction | "Actually, let's try a different approach" |
| **The Checkpoint** | Align before continuing | "Before we continue, let me summarize what we've decided..." |
| **The Rubber Duck** | Think out loud | "Let me reason through this -- tell me where I'm wrong..." |
| **The Handoff** | Split work | "I'll implement this part. You do the tests." |
| **The Zoom** | Go deeper on one thing | "Go deeper on error handling" |
| **The Zoom Out** | Step back | "Are we solving the right problem?" |

### The Closing Turn (Reflect)

End sessions by asking:

- "What did we miss?"
- "What would break this?"
- "Summarize the decisions we made"

This catches blind spots and creates a record for future sessions.

## Dialog Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| The Wall of Text | 500-word prompt with 20 requirements | Break into CSAR turns |
| The Yes-Man | Accepting first output without reflecting | Always do at least one Reflect turn |
| The Restart | Starting over instead of iterating | Use Pivot or Constraint moves |
| Context Amnesia | Not restating decisions in later turns | Use Checkpoint for alignment |
| Premature Specificity | "Use exactly this library with this config" too early | Clarify first, constrain later |

## When to Use Each CSAR Phase

| Task Complexity | Clarify Depth | Summarize | Act Cycles | Reflect Depth |
|-----------------|--------------|-----------|------------|---------------|
| Simple (bug fix) | 1 sentence | Implicit | 1 | Quick check |
| Medium (feature) | 2-3 turns | Explicit | 2-3 | "What would break?" |
| Complex (architecture) | 3-5 turns | Written summary | 3-5+ | Adversarial review |
| Research | 5+ exploratory turns | Multiple pivots | Iterative | Cross-validate sources |

### CSAR Implementation

```typescript
// Implement CSAR loop tracking in conversation
enum CSARPhase {
  Clarify = 'clarify',
  Summarize = 'summarize', 
  Act = 'act',
  Reflect = 'reflect'
}

interface DialogState {
  currentPhase: CSARPhase;
  cycleCount: number;
  contextGathered: Map<string, string>;
  goalStatement: string | null;
  lastAction: string | null;
}

function detectPhaseFromMessage(message: string): CSARPhase {
  // Clarify signals: providing context
  if (message.match(/I'm building|current stack|constraint is|using/i)) {
    return CSARPhase.Clarify;
  }
  // Summarize signals: stating goal
  if (message.match(/show me|I need|the goal is|help me/i)) {
    return CSARPhase.Summarize;
  }
  // Reflect signals: evaluation/iteration
  if (message.match(/what did|go deeper|what if|why did you/i)) {
    return CSARPhase.Reflect;
  }
  // Default: Act phase (generation expected)
  return CSARPhase.Act;
}

function suggestNextMove(state: DialogState): string {
  switch (state.currentPhase) {
    case CSARPhase.Clarify:
      return state.goalStatement 
        ? 'Ready to act on your goal.'
        : 'What specifically do you want to accomplish?';
    case CSARPhase.Act:
      return 'Shall I go deeper on any aspect?';
    case CSARPhase.Reflect:
      return state.cycleCount < 3 
        ? 'Want to refine further, or ready to proceed?'
        : 'We\'ve iterated well. Ready to finalize?';
    default:
      return '';
  }
}
```

## Integration with the AI assistant Skills

- **Meditation**: The Reflect phase maps to meditation's "what did I learn?" step
- **Research-first-development**: Clarify phases should invoke research skills before acting
- **Code review**: Reflect phase should invoke adversarial review checklist
- **Knowledge synthesis**: End-of-session Reflect should capture insights for global knowledge
