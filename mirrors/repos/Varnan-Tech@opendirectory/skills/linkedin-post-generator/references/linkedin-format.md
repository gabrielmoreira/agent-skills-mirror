# LinkedIn Format Rules

This is the reference document the agent reads before writing any post. All rules here are non-negotiable unless the user explicitly overrides them.

---

## Section 1: Why LinkedIn Format Is Different

LinkedIn's algorithm and UI create constraints you do not have on other platforms:

- Outbound link penalty. Posts with URLs in the body get distributed less. LinkedIn wants to keep users on-platform. Put all links in the first comment.
- The "see more" cutoff. After approximately 210 characters, LinkedIn collapses the post. Only the first 1-2 lines are visible. If those lines do not earn a click, the post is invisible.
- Mobile-first rendering. Most LinkedIn users are on mobile. Walls of text get scrolled past. Blank lines between short paragraphs increase completion rates.
- Engagement signal hierarchy. Comments carry more weight than reactions. Reactions carry more weight than shares. Questions that invite comments are more valuable than statements.

---

## Section 2: Hook Rules

The hook is line 1. It is the only content visible before the "see more" click. Treat it as the entire post.

A good hook must:
- Stand alone as a complete thought
- Create a gap between what the reader knows and what they want to know
- NOT start with "I" (posts starting with "I" consistently underperform)
- NOT be generic or vague

Hook formats that work:

| Format | Example |
|--------|---------|
| Bold claim | "Most developers are measuring the wrong thing." |
| Specific stat | "We cut deploy time from 47 minutes to 4." |
| Story opening (not "I") | "After 6 months of building in silence, we shipped." |
| Direct question | "What do you do when your most-used library gets deprecated overnight?" |
| Counterintuitive observation | "The feature our users love most took 2 hours to build." |
| Problem statement | "Nobody talks about the week after you launch." |

Hook formats to avoid:

- "I'm excited to share..."
- "Big announcement!"
- "Thrilled to announce..."
- "We are pleased to..."
- "Just shipped..." or "Just wanted to share..."
- Any opener starting with "I"

---

## Section 3: Post Body Rules

Paragraph length: Maximum 1-3 lines per paragraph. Always follow with a blank line before the next paragraph. Never write 4 or more consecutive lines without a break.

Sentence length: Short sentences outperform long sentences on mobile. Split any sentence that needs two commas to work.

Story arcs by style:

Founder/Ship:
```
Line 1:     Hook
[blank]
Lines 2-3:  Context: what were you building, for how long, what was the challenge
[blank]
Lines 4-6:  Action: what shipped, concrete and specific
[blank]
Lines 7-8:  Surprise or learning: what you did not expect, what changed
[blank]
Line 9:     Takeaway: the single distilled lesson
[blank]
Line 10:    Closing question
```

Insight:
```
Line 1:     Hook: the claim or counterintuitive statement
[blank]
Lines 2-3:  Assumption: what most people think or do
[blank]
Lines 4-6:  Evidence: what you observed, or data that supports the claim
[blank]
Lines 7-8:  Implication: what this means, what changes when you accept it
[blank]
Line 9:     Closing question
```

Product Launch:
```
Line 1:     Hook: what the product does for the user (outcome, not feature)
[blank]
Lines 2-3:  Problem: the pain this solves, specific not generic
[blank]
Lines 4-6:  What it does: brief and concrete, key differentiator on one line
[blank]
Line 7:     Proof point: beta result, user quote, or metric (skip if none exists)
[blank]
Line 8:     CTA: one clear action
```

Tutorial Summary:
```
Line 1:     Hook: what the reader learns, or what most get wrong
[blank]
Lines 2-3:  Why it matters: who this is for, why standard approaches fail
[blank]
Lines 4-9:  Key steps: 3-5 numbered items, each one line, concrete and actionable
[blank]
Line 10:    Main takeaway: one sentence
[blank]
Line 11:    CTA or question
```

---

## Section 4: Specificity Rules

Concrete details outperform vague claims every time.

| Vague | Concrete |
|-------|----------|
| "saved time" | "saved 4 hours/week" |
| "dramatically faster" | "cut from 47 minutes to 4 minutes" |
| "customers asked for this" | "3 of our top 10 customers requested it" |
| "small team, fast execution" | "shipped in 2 weeks with 2 engineers" |
| "improved performance" | "p95 latency dropped from 1.2s to 180ms" |

If the source material has numbers, use them exactly. If no numbers are available, use specific descriptors rather than superlatives. Never invent metrics.

---

## Section 5: Closing Rules

End with exactly one of the following:

A question that invites genuine response:
- "Has anyone else run into this?"
- "What would you do differently?"
- "What's your approach to [X]?"
- "Am I wrong about this?"

A clear CTA pointing to the first comment:
- "Full post in the first comment."
- "Link to try it in the first comment."
- "The template is in the comments."
- "Tutorial in the first comment."

Do NOT end with both a question and a CTA.

Do NOT use: "Let me know your thoughts!" or "Drop a comment below!" These are low-signal and overused.

---

## Section 6: Link Placement Rule

This rule is non-negotiable. LinkedIn distributes posts with outbound links in the body significantly less.

Rule: All URLs go in the first comment. Never in the post body.

In the post body, refer to the link as: "link in the first comment" or "in the comments."

First comment format:
```
[One context sentence about what the link is]. [URL]
```

Example:
```
Full tutorial on building a production RAG pipeline. https://yourblog.com/rag-guide
```

Post the first comment immediately after publishing.

---

## Section 7: No Hashtags

Do not include hashtags in the post. Hashtags add visual noise and reduce the professional tone of technical content. Posts without hashtags perform equally well for most technical and founder audiences.

---

## Section 8: Length and Format

| Metric | Target |
|--------|--------|
| Optimal character count | 900-1,300 characters |
| Maximum character count | 3,000 characters |
| Minimum to feel substantive | 500 characters |
| Approximate word count at 1,100 chars | 150-180 words |

No markdown formatting. LinkedIn does not render bold or italic. Asterisks and underscores appear as plain characters.

No em dashes. Replace with a period or a comma.

No semicolons.

Emojis: optional. 0-3 per post maximum. Use as visual paragraph separators or to replace bullet points. Do not use for decoration.

---

## Section 9: Validation Checklist

Run through this before finalising any post:

- [ ] First line does NOT start with "I"
- [ ] First line works standalone: interesting without the rest
- [ ] No paragraph exceeds 3 lines before a blank line
- [ ] Blank lines exist between every paragraph block
- [ ] Story arc is present (varies by style)
- [ ] All numbers and claims come from the source material
- [ ] Ends with question OR CTA, not both
- [ ] No URLs in the post body
- [ ] Character count: 900-1,300 ideal, under 3,000 required
- [ ] No em dashes
- [ ] No hashtags
- [ ] No semicolons
- [ ] No forbidden words (see Writing Style in SKILL.md)
- [ ] First comment text prepared with all relevant links
