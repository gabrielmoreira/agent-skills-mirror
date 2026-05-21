# Blog Format Guide

## Section 1: Why Format Matters

Most blog posts fail at the first paragraph. Readers scan — they read the title, the first sentence, and maybe one or two more. If nothing grabs them, they're gone. Format is not about aesthetics: it is about keeping someone reading past the first scroll.

Short paragraphs signal that reading this will not be painful. Concrete details signal that the author has done real work. A specific title signals that the post is about one thing, not a vague survey of a topic.

---

## Section 2: Title Rules

The title is the single highest-leverage element. A bad title kills a good post.

Must:
- Name the specific thing the post is about
- Create a reason to click (curiosity gap, specific benefit, or counterintuitive claim)
- Be under 70 characters
- Use conversational English

Must not:
- Start with "I", "My", or "We"
- Use: "A Comprehensive Guide to", "The Ultimate Guide to", "Everything You Need to Know About"
- Use clickbait that the post does not deliver on

Formats that work:
- Specific result: "How we cut deploy time from 47 minutes to 4"
- Counterintuitive claim: "The feature our users love most took 2 hours to build"
- How-to with specifics: "How to set up agent memory that actually persists"
- Problem statement: "Why your RAG pipeline is slower than it needs to be"
- Tool comparison with a point: "Playwright vs Puppeteer: what actually matters for E2E tests"

---

## Section 3: Opening Paragraph Rules

The opening paragraph must hook without announcing what you are about to do.

Must not:
- "In this post, I will..."
- "Today we're going to explore..."
- "This article covers..."
- "Welcome to this guide on..."
- Any variation of "let's dive in"

Do:
- Open with the most surprising or concrete thing from the post
- State a problem the reader recognizes
- Make a bold claim you will back up
- Drop into a specific moment or situation

Examples that work:
- "We spent three weeks debugging a race condition that turned out to be a single missing await."
- "Most developers add caching too late. By the time you notice the N+1 query, your database is already the bottleneck."
- "The CSV export feature took two hours. Users mentioned it in 40% of support tickets."

---

## Section 4: Body Rules

**Paragraph length:** 1-3 lines max, then a blank line. Never 4 consecutive lines without a break.

**Sentence length:** Mix short and long. Short sentences hit hard. Then follow up with a sentence that gives context, adds nuance, or shows the reader why it matters.

**Specificity:** Every section needs at least one concrete detail — a number, a file name, a command, a tool name, a before/after comparison. Remove any sentence that could apply to any post on the topic.

**Headers (H2):** 3-5 major sections. Each section covers one idea. Use headers to break the scan path for readers who skip ahead.

**Code blocks:** Use triple-backtick fenced blocks. Never inline code in a paragraph when a block would be clearer.

**Lists:** Use for steps, options, or comparisons. Do not force a list when prose would flow better.

---

## Section 5: Story Arcs by Style

### Technical Tutorial
```
[Hook — the end result, or what most people get wrong about this]
[Why this matters — who this is for, what problem it solves]
[Prerequisites — only what is actually needed]
[Step 1 — one action]
[Step 2 — one action]
[Step 3 — one action]
[Common mistake — what breaks here and why]
[Result — what working looks like]
[Actionable close — next step or variation]
```

### Case Study
```
[Hook — the end result or the key moment that changed things]
[Setup — where things started, what the problem was]
[Decision — what was tried or changed]
[What happened — the outcome, including surprises]
[What we learned — the lesson extracted]
[What to take from this — for the reader, not just the author]
[Actionable close]
```

### Thought Leadership
```
[Hook — the contrarian claim stated directly]
[The assumption — what most people believe and why]
[The evidence — what you actually observed]
[The implication — what changes if the claim is true]
[The counterargument — steelman the other side]
[The rebuttal — why the position holds]
[The nuance — edge cases and when this does not apply]
[Actionable close — what should change as a result]
```

### Explainer
```
[Hook — what knowing this enables, or the common misconception]
[The problem with the standard explanation]
[What X actually is — plain English, one paragraph]
[How it works — mechanism, not just definition]
[Real example — concrete, not hypothetical]
[When to use it vs alternatives]
[Actionable close — try this or read this next]
```

---

## Section 6: Closing Rules

End with exactly one of:
- An actionable next step: "Try this on your next feature branch and check if the diff size changes."
- A direct question that invites real responses: "What's the bottleneck in your current setup?"
- A pointer to the next logical resource: "If this applies to your stack, the GitHub repo is in the description."

Do not use:
- "In conclusion..."
- "To summarize..."
- "I hope this was helpful."
- "Thanks for reading."
- Two CTAs at once

---

## Section 7: Length Guide

| Post type | Target word count |
|-----------|------------------|
| Tutorial (focused, one task) | 800-1,200 words |
| Case study (a real story) | 1,000-1,600 words |
| Thought leadership (one argument) | 800-1,400 words |
| Explainer (one concept) | 900-1,500 words |

Under 600 words feels shallow unless it is a quick tip. Over 2,000 words requires a very strong argument for staying that long.

---

## Section 8: Banned Words

Do not use any of these in any paragraph or heading:

incredible, amazing, leveraging, synergize, game-changing, game changer, let's dive in, buckle up, it's worth noting, delve, harness, unlock, groundbreaking, cutting-edge, remarkable, paradigm, revolutionize, disruptive, transformative, thrilled, excited to share, powerful, innovative, comprehensive, actionable, crucial, vital, pivotal, elucidate, utilize, robust, seamless, unprecedented, state-of-the-art, at its core, the landscape of, in the world of, whether you're a beginner or an expert, from X to Y this covers everything, look no further, in today's rapidly evolving

If you see one of these in a draft section, rewrite that sentence before presenting.

---

## Section 9: No Em Dashes

Do not use em dashes (—) anywhere in the post. Replace with:
- A comma where a pause belongs
- A period to break a long sentence into two
- A colon before an explanation

---

## Section 10: Validation Checklist

Before presenting the draft, verify:

- [ ] Title does not start with "I", "My", or "We"
- [ ] Title is specific (not "a guide", not "the ultimate", not "everything about")
- [ ] Opening paragraph hooks without announcing the topic
- [ ] No em dashes in any line
- [ ] No semicolons
- [ ] No paragraph longer than 3 lines without a blank line
- [ ] No banned words
- [ ] Every claim traces to the raw input or a Tavily result
- [ ] Post ends with an action, a question, or a pointer — not a summary statement
- [ ] Word count is in target range (state the count)
- [ ] Logical flow throughout (each section leads to the next)
