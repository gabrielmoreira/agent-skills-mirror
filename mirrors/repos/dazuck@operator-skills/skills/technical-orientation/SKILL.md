---
name: technical-orientation
description: Explain technical projects or codebases to a non-engineer. Use for "orient me" or "explain this repo".
---

# Technical Orientation

Help a savvy but non-technical operator understand technical projects, codebases, tools, or documentation quickly and thoroughly.

## Who This Is For

A startup operator, founder, or business person who:

- Needs to understand what technical things do without writing code
- Wants to evaluate tools, make decisions, or manage technical teams
- Is smart and capable but doesn't have an engineering background
- Values their time and wants the "so what" not just the "what"

## How to Approach This

### 1. Start with the One-Liner

Before diving in, give a single sentence that captures what this thing IS:

> "NullAgent is a framework for testing how well AI models perform at specific tasks, with real measurements instead of vibes."

> "Replay Lab is the data infrastructure that feeds market data and charts to AI agents for evaluation."

### 2. Explore Systematically

For a codebase/repo:

```
1. Check the root README.md first
2. Look at package.json or equivalent for project structure
3. Read CLAUDE.md or AGENTS.md if present (AI context docs)
4. Scan the directory structure to understand organization
5. Read key documentation files
```

For documentation/tools:

```
1. Find the "what is this" or overview section
2. Identify the core concepts (usually 3-5)
3. Look for architecture diagrams
4. Find example use cases
```

### 3. Translate to Plain Language

**Never use**:

- Unexplained acronyms
- Jargon without definition
- "It's basically..." followed by more jargon

**Always**:

- Define technical terms the first time they appear
- Use analogies to familiar concepts
- Explain WHY something exists, not just WHAT it is

### 4. Use Visual Formats

**Tables over paragraphs** for comparisons, features, or options:

| Component  | What It Does                | Why It Matters                        |
| ---------- | --------------------------- | ------------------------------------- |
| agent-core | Runs AI agents              | The engine that makes everything work |
| database   | Stores conversation history | AI can "remember" across sessions     |

**ASCII diagrams** for showing how pieces connect:

```
Data Source → Processing → API → Your Application
```

**Bullet hierarchies** for nested concepts:

- Main concept
  - Sub-concept A
  - Sub-concept B

### 5. Always Answer "So What?"

For every component or concept, answer:

- **What problem does this solve?**
- **Who would use this and when?**
- **What happens if this didn't exist?**

### 6. Give a Learning Path

End with concrete next steps based on what they might want to do:

| If You Want To...  | Do This                        |
| ------------------ | ------------------------------ |
| Just understand it | Read X, Y, Z docs              |
| Try it yourself    | Run these commands             |
| Evaluate it        | Compare against these criteria |
| Go deeper          | Explore these files/concepts   |

## Output Structure

For any technical orientation, cover:

1. **One-Liner** — What is this in one sentence?
2. **The Big Picture** — What problem does it solve? Who is it for?
3. **Key Components** — The 3-5 main pieces and how they relate
4. **How It Works** — Visual diagram of the flow
5. **Concrete Example** — What does using this actually look like?
6. **Why This Matters to You** — Connect to their goals/context
7. **Next Steps** — Actionable options based on what they want

## Tone & Style

- **Direct** — No hedging or filler words
- **Confident** — You're the expert translator
- **Practical** — Focus on what they can DO with this knowledge
- **Respectful** — They're smart, just not technical. Never condescend.

## Adapt to Context

Ask clarifying questions if helpful:

- "Are you evaluating this, trying to use it, or managing a team that uses it?"
- "Do you want the 2-minute overview or the deep dive?"
- "What's your goal with this project?"

But don't over-ask. Make reasonable assumptions and offer to go deeper.

## Example Interaction

**User**: "Orient me on this repo: https://github.com/example/cool-tool"

**Response**:

1. Clone and explore the repo
2. Read key docs (README, any architecture docs)
3. Provide:
   - One-liner summary
   - Big picture table of components
   - ASCII diagram of how pieces connect
   - "Why this matters" for their context
   - Concrete next steps

## When to Use This Skill

- User shares a GitHub URL and asks what it does
- User says "explain this to me" about something technical
- User mentions they're "not technical" or "not an engineer"
- User asks to "get up to speed" on a project
- User is clearly a business/ops person dealing with technical things
- User says "orient me" or "break this down"

## When NOT to Use This Skill

- User is clearly an engineer who wants technical details
- User asks a specific coding question
- User wants to debug or write code (use other skills)
