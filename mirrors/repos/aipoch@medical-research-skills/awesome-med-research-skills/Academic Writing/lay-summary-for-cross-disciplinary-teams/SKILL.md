---
name: lay-summary-for-cross-disciplinary-teams
description: >-
  Rewrites technical research content into a structured lay summary that
  cross-disciplinary teams can quickly understand and act on. Use when the
  user wants to explain research to colleagues outside their specialty —
  clinicians, wet-lab scientists, bioinformaticians, product managers, or
  leadership. Trigger on: "lay summary", "explain my research to the team",
  "non-technical summary", "cross-disciplinary summary", "translate my
  findings", "align our team on the study", or any request to communicate
  research goals, findings, or next steps to a mixed or non-specialist
  audience. Part of the AIPOCH Academic Writing skill hub. Sits midstream:
  after research content is clarified, before downstream deliverables like
  slide decks or graphical abstracts.
license: MIT
author: AIPOCH
---

# Lay Summary for Cross-Disciplinary Teams

Converts technical research into a structured summary that clinical, wet-lab,
bioinformatics, product, and management teams can rapidly read and act on.

## Position in the Research Pipeline

This skill sits **midstream**:

- **Upstream** (should exist first): Clear research question, defined objectives,
  structured results, result narrative
- **This skill**: Translates that clarified content for non-specialist readers
- **Downstream** (natural next steps): Slide Deck for Lab Meeting, Graphical
  Abstract Generator, Reviewer Response Drafter

If the user's research content is still vague or unstructured, prompt them to
clarify objectives and key findings first. A lay summary built on unclear input
will sound smooth but be factually imprecise — worse than no summary.

---

## Step 1 — Gather Input

Ask the user to provide any of:
- Abstract, introduction, or results section
- Key findings in their own words
- A study summary or internal report

Also ask: **Who is the primary audience?**
- `mixed` (default) — all teams listed
- `clinical` — clinicians, medical staff
- `wet-lab` — bench scientists, experimentalists
- `bioinformatics` — computational scientists, data analysts
- `product` — product managers, translational teams
- `management` — leadership, funders, executives

If unspecified, use `mixed` and include all relevant audience bullets.

---

## Step 2 — Extract Core Structure

Before writing, internally map the input to these five elements:

| Element | What to find |
|---|---|
| **Study goal** | Why was this done? What problem does it address? |
| **System / population** | What was studied? (patients, cells, datasets, samples…) |
| **Main finding** | What did the data show? Be specific — avoid vague positives. |
| **Evidence boundary** | What can this support? What remains uncertain or untested? |
| **Next action** | What should each team know or do because of this? |

If any element is missing from the input, note it in the output and invite the
user to fill in the gap.

---

## Step 3 — Write the Lay Summary

Use the output template in `assets/output-template.md`.

Writing principles:
- No unexplained acronyms — define on first use or remove
- Evidence boundary must be explicit: distinguish finding from interpretation
- Each audience bullet should be actionable, not just descriptive
- Quantify findings where possible ("3-fold higher", "in 4 of 6 subtypes")
- The summary must stand alone without access to the original paper

For audience-specific language guidance, read `references/audience-guide.md`.

---

## Step 4 — Quality Check

Before delivering output, verify:

- [ ] No naked jargon or undefined acronyms
- [ ] Finding is accurate — not overstated, not undersold
- [ ] Evidence boundary is clearly hedged
- [ ] Each audience bullet is actionable
- [ ] Summary reads cleanly to someone with no domain knowledge

If a check fails, revise before presenting.

---

## References

- `assets/output-template.md` — the standard 6-section output template with example
- `references/audience-guide.md` — language and framing guidance per audience type
