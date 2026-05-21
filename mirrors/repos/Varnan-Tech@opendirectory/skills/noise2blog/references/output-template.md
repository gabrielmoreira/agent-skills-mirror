# Output Templates

Four templates: Technical Tutorial, Case Study, Thought Leadership, Explainer.

Select the template that matches the detected or user-specified style. Replace every [BRACKETED SLOT] with content from the raw input. Never leave bracket text in the output. Skip a slot entirely if there is no source material for it — do not invent content to fill it.

---

## Template 1: Technical Tutorial

Use when the raw content is a step-by-step guide, how-to, or code walkthrough.

```markdown
[TITLE — specific result or what most people get wrong. Under 70 chars. Does not start with I/My/We.]

[HOOK — 2-3 sentences. The end result a reader achieves, or the mistake most people make. No "In this post". No "Let's dive in".]

[CONTEXT — 1-2 sentences. Who this is for and what problem it solves. Be specific about the situation.]

## [PREREQUISITE SECTION TITLE — e.g. "What you need"]

[List only prerequisites that are genuinely required. Skip this section if there are none.]

## [STEP 1 TITLE — one action, named concretely]

[Step 1 content. One task. Include the command, code, or UI action. 1-3 paragraphs max.]

## [STEP 2 TITLE]

[Step 2 content.]

## [STEP 3 TITLE]

[Step 3 content.]

## [OPTIONAL: STEP 4 TITLE — common mistake or edge case at this stage]

[What breaks here and why. Only include if the raw input mentions it.]

## [RESULT TITLE — e.g. "What it looks like when it works"]

[2-3 sentences describing the working end state. Include a concrete output — a log line, a screenshot description, a returned value.]

[ACTIONABLE CLOSE — one specific next step or variation the reader can try. Not "I hope this was helpful".]
```

**Worked example:**

Raw input: Rough notes on setting up Playwright for E2E tests in a Next.js app — mentions `npx playwright install`, a config file location, the `page.goto()` pattern, and a note that webkit tests fail without a specific environment variable.

Generated title: "Setting up Playwright in a Next.js app without breaking webkit tests"

Generated opening: "Playwright installs in one command. Getting webkit tests to actually run in CI takes a bit more. Here's the setup that works without the two-hour debugging session."

---

## Template 2: Case Study

Use when the raw content is a build log, before/after story, lessons-learned post, or first-person journey.

```markdown
[TITLE — the end result or the key moment. Under 70 chars. Does not start with I/My/We.]

[HOOK — 2-3 sentences. The end state or the most surprising outcome from the story. Drops the reader into the situation.]

## [CONTEXT TITLE — e.g. "Where things started" or the specific problem]

[Setup: what the situation was before. Be specific about the pain or the constraint. 1-2 paragraphs.]

## [DECISION TITLE — e.g. "What we tried" or "The change we made"]

[The specific action taken. What was built, changed, or dropped. Include concrete details: what was replaced with what, how long it took, who was involved.]

## [OUTCOME TITLE — e.g. "What happened" or "The result"]

[The outcome, including anything unexpected. Specific numbers if available. Do not invent metrics not in the source.]

## [LESSON TITLE — e.g. "What we learned" or "The thing nobody warned us about"]

[The extracted insight. Should be transferable to someone not in the exact same situation. 1-2 paragraphs.]

[ACTIONABLE CLOSE — what the reader should try, check, or think about based on this story.]
```

**Worked example:**

Raw input: Voice transcript about rebuilding a feature that served 10k users — mentions moving from a cron job to an event-driven queue, reducing latency from 8 seconds to 400ms, and the unexpected issue with message ordering after the switch.

Generated title: "Moving 10,000 users from a cron job to a queue: what nobody tells you about message ordering"

---

## Template 3: Thought Leadership

Use when the raw content makes a strong opinion claim, argues against common advice, or takes a counterintuitive position.

```markdown
[TITLE — the contrarian claim stated directly. Under 70 chars. Does not start with I/My/We.]

[HOOK — 2-3 sentences. The claim, stated plainly. Do not hedge. The reader should immediately know what you're arguing.]

## [THE ASSUMPTION — e.g. "What most teams believe"]

[1-2 sentences stating the common belief. Be fair to the other side.]

[1-2 sentences explaining why people hold this belief. What evidence supports it?]

## [THE EVIDENCE — e.g. "What actually happens" or "What the data shows"]

[Specific observations, results, or data points from the raw input. This is the core of the argument. 2-3 paragraphs.]

## [THE IMPLICATION — e.g. "What changes if this is true"]

[Concrete consequences of accepting the claim. What should readers do differently? 1-2 paragraphs.]

## [THE COUNTERARGUMENT — e.g. "The case against this"]

[Steelman the other side. The strongest objection to the claim. 1 paragraph.]

## [THE NUANCE — e.g. "When I'm wrong"]

[Edge cases. When does the claim not hold? Being honest here makes the argument stronger. 1 paragraph.]

[ACTIONABLE CLOSE — what the reader should try or reconsider based on the argument. Ask for pushback specifically if the post invites debate.]
```

**Worked example:**

Raw input: Tweet dump arguing that code reviews slow down small teams more than they help — mentions two data points about merge time, a quote from a teammate, and a suggestion to use async video reviews instead.

Generated title: "Code reviews are slowing your small team down"

---

## Template 4: Explainer

Use when the raw content explains a concept, tool, or trend for readers who are not already familiar with it.

```markdown
[TITLE — what knowing this enables, or the common misconception. Under 70 chars. Does not start with I/My/We.]

[HOOK — 2-3 sentences. The most surprising or counterintuitive thing about this topic. Or the misconception most people have. No "In this post I'll explain".]

## [PROBLEM WITH STANDARD EXPLANATION — e.g. "Why the usual explanation misses something"]

[1-2 paragraphs. What's wrong or incomplete about how most sources explain this.]

## [WHAT IT ACTUALLY IS — e.g. one clear, plain English section title]

[Plain English definition. One paragraph. No jargon unless immediately explained.]

## [HOW IT WORKS — the mechanism]

[The underlying mechanism, not just the interface. 2-3 paragraphs. Use an analogy if it helps. Include a concrete example — a specific tool, command, or situation.]

## [REAL EXAMPLE — specific, not hypothetical]

[Walk through one real use case. Name specific files, tools, or scenarios from the raw input. Do not use generic placeholder examples like "imagine you have an app".]

## [WHEN TO USE IT — and when not to]

[1-2 concrete situations where this is the right choice. 1-2 where it is the wrong choice. Be specific.]

[ACTIONABLE CLOSE — what to try next. A command to run, a resource to read, or a question to ask yourself.]
```

**Worked example:**

Raw input: Notes explaining RAG (retrieval-augmented generation) to developers who've heard the term but don't understand why it's better than fine-tuning — includes an analogy to open-book exams vs memorizing, mentions specific latency tradeoffs.

Generated title: "RAG is not just a smarter search: what the open-book analogy gets wrong"

---

## Fill-In Rules

1. Replace every [BRACKETED SLOT] with content from the raw input or Tavily results
2. Never leave bracket text in the output
3. Skip any slot that has no source material — do not invent content to fill it
4. If a section has no relevant source content, remove the section header too
5. Adjust sections to match the actual content (add or remove H2 sections as needed)
6. Apply all rules from blog-format.md to every paragraph and sentence
7. Count words before presenting; state the count
8. Every claim in the output must trace to the source input or a named Tavily result
