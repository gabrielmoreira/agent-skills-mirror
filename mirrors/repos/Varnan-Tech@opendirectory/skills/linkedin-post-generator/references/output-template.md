# Output Templates

Four templates, one per post style. Fill every [BRACKETED SLOT] with content from the source material. Never use the bracket text literally in the output. Preserve all blank lines exactly as shown. Apply the Writing Style rules from SKILL.md to every sentence.

---

## Template 1: Founder/Ship

Use when the content is a personal story of building or shipping something.

```
[HOOK: bold claim, surprising result, or key build moment. Does not start with "I".]

[CONTEXT: 1-2 lines. What were you building, how long, what was the challenge.]

[ACTION: 2-3 lines. What you shipped. Concrete and specific. Include the key feature or decision.]

[SURPRISE OR LEARNING: 1-2 lines. What you did not expect. What changed after shipping.]

[TAKEAWAY: 1 line. The single distilled lesson.]

[CLOSING QUESTION: Invite genuine response. "What did you learn from your last launch?" or "Has anyone else seen this?"]
```

Worked example:

```
6 months of building in silence. Then 400 signups in 48 hours.

Here is what we did not expect.

The feature we almost cut, the one that felt too simple, was the one everyone messaged us about.

We built a one-click CSV export. No filters, no customisation, export only. Took 2 hours to build.

The feedback from users: "Finally. I've been manually copying this data for a year."

Sometimes the boring feature is the important one.

What's a feature you almost did not ship that turned out to matter?
```

---

## Template 2: Insight

Use when the content is an educational observation, pattern, or lesson. Works for articles, opinions, and thought leadership.

```
[HOOK: a bold claim or counterintuitive statement. Specific, not vague.]

[ASSUMPTION: 1-2 lines. What most people think or do. Set up the contrast.]

[EVIDENCE: 2-3 lines. What you observed, or the data and examples that support the claim.]

[IMPLICATION: 1-2 lines. What this means. What changes when you accept this.]

[CLOSING QUESTION: Open a genuine conversation. "Am I wrong about this?" or "What's your experience with [X]?"]
```

Worked example:

```
Most developers are optimising the wrong bottleneck.

The assumption: your app is slow because of database queries.

The reality: after profiling 50+ production apps, the biggest wins almost always come from fixing N+1 queries and response payload size. Adding indexes helps less than you think.

Unindexed columns rarely cause the latency spikes that make users leave.

The bottleneck is almost always what you're sending, not how fast you're finding it.

Where do you look first when you see a latency spike?
```

---

## Template 3: Product Launch

Use when announcing a new tool, product, feature going public, or beta release.

```
[HOOK: what the product does for the user (outcome, not feature). Frame it as a benefit, not a capability.]

[PROBLEM: 1-2 lines. The pain this solves. Be specific. Avoid "teams struggle with..." or "developers find it hard to...".]

[WHAT IT DOES: 2-3 lines. What the product does, brief and concrete. Key differentiator on one line.]

[PROOF POINT: 1 line. A beta result, user quote, or specific metric. Skip this block entirely if none exists.]

[CTA: one clear action. "Link to try it in the first comment." or "Sign-up link in the first comment."]
```

Worked example:

```
Your AI agent reads any website in under 3 seconds. No browser needed.

Most scraping tools either need a headless browser (slow and fragile) or miss JavaScript-rendered content entirely.

We built a lightweight extraction layer that bypasses both problems. No Playwright. No Puppeteer. No Chrome.

Beta users are pulling structured data from 200+ pages per minute on a $5 VPS.

Sign-up link in the first comment.
```

---

## Template 4: Tutorial Summary

Use when distilling a long tutorial, technical deep-dive, or step-by-step guide into a tight takeaway post.

```
[HOOK: what the reader learns from this, or what most people get wrong about this topic.]

[WHY IT MATTERS: 1-2 lines. Who this is for. Why the standard approach fails.]

[KEY STEPS: 3-5 numbered items, each one line. Concrete and actionable. Tight phrases work better than full sentences.]

[MAIN TAKEAWAY: 1 line. The single most important thing.]

[CTA OR QUESTION: "Full tutorial in the first comment." or "What would you add to this list?"]
```

Worked example:

```
Set up a production-ready RAG pipeline in an afternoon. Most tutorials make it seem harder than it is.

Here is what actually matters:

1. Chunk by semantic unit, not by token count
2. Store embeddings and original text together. You will need both at retrieval time.
3. Hybrid search (BM25 + vector) beats pure vector search for most use cases
4. Rerank before you return. The top-10 results are rarely in the right order.
5. Eval early. 10 hand-labelled queries will save you days of guessing.

The system is only as good as your eval set.

What's the hardest part of RAG you've wrestled with?
```

---

## Fill-in Rules

1. Replace every [BRACKETED SLOT] with content derived from the source material. Never output the bracket text.
2. Preserve all blank lines between paragraphs exactly as shown.
3. Count characters before presenting. State the count.
4. Skip blocks with no source data rather than inventing content.
5. Apply Writing Style rules: no em dashes, no hashtags, no semicolons, no forbidden words, active voice only.
6. Address the reader with "you" and "your" where the post speaks to the audience.
