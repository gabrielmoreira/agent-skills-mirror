---
name: de-ai
version: 1.0.0
description: 'Strip the language patterns that mark prose as machine-generated, so the reader engages with the content rather than the style. A diagnostic lens, not a banned-words list. USE WHEN: polishing public-facing prose, reviewing AI-drafted text, applying a finishing pass after Improve has settled the substance. SKIP WHEN: editing verbatim records (transcripts, trail entries, quoted material), or when the prose has already been edited by a human and the AI-tells are operator voice.'
argument-hint: 'The prose target to examine (file, section, or specific passage). Optionally a voice reference - "match this writer", "keep this paragraph as the anchor".'
---

# De-AI

*Read the prose like a reader, not a writer. Where the rhythm announces "AI wrote this", cut.*

*Memory Model role: Reads the destination and recent trail entries for established voice norms; applied as a finishing pass during Improve runs that touch prose. Records realisations about new AI-tells into the trail so they accumulate.*

> **Governing principle:** [Observable Autonomy](../PRINCIPLES.md#principle-2-observable-autonomy) — the trail must be honest, and so must the prose. Mannered AI writing erodes the reader's trust that anything beneath it is real. A reader who notices the style stops engaging with the substance.

This skill exists because LLMs converge on a recognisable prose register: parallel-structure-itis, em-dash bridges, restatement bloat, listicle bait, mannered meta-framing. The patterns are not wrong individually. They become a tell when they cluster. Once a reader recognises the cluster, they read the text as machine output regardless of how good the underlying content is.

This skill is the finishing pass that strips the cluster.

---

## What this skill is not

- **Not a search-and-replace dictionary.** Em-dashes are fine. Three-item lists are fine. The patterns below are diagnostics, not banned tokens. A pattern is a tell when it is the default, not when it appears once.
- **Not a substitute for Improve.** Improve fixes the substance — what the text claims and how it is structured. De-AI runs after, on the surface. Applying De-AI to text that has not been thought through produces well-styled emptiness.
- **Not applied to verbatim records.** Trail entries, transcripts, quoted material, and operator-authored passages keep their original voice — even when AI-flavoured. The whole point of the verbatim layer is that it has not been edited. If the operator's voice happens to use em-dashes heavily, that is the voice.
- **Not a stylistic preference.** This is not "make it sound more like Hemingway." It is "remove the markers that signal *machine*." Some passages will sound flatter after the pass. That is the point — flat-and-honest beats ornate-and-suspicious.

---

## The diagnostic catalogue

Thirteen patterns that mark prose as machine-generated. Apply as a lens; do not run as a checklist. The signal is the cluster, not any single instance.

### 1. Meta-framing

Labelling the structure of the thing instead of just saying the thing.

> ❌ *"I kept hitting two failure modes: reviewing everything until I was approving outputs I hadn't really checked, or trusting the model until I found that a run was wrong after it had already been used."*
> ✅ *"When I reviewed everything, review got faster than thought and approvals went automatic. When I trusted the model, I found out runs were wrong after they had already been used."*

The first version announces "I am about to tell you two things." The second just tells you the two things. Real speech does not narrate its own structure.

Other meta-frame stamps to watch for:
- "There are three considerations here..."
- "Let me break this down."
- "On one hand X, on the other hand Y."
- "It is worth noting that..."
- "What I want to highlight is..."

### 2. Parallel-structure-itis

Three-part lists where the items repeat the same idea in different words. Four-part parallel rhythms that exist for cadence, not content.

> ❌ *"How it read the ask, what it looked at, what it decided, and what it concluded after the fact."*
> ✅ *"Ask, examination, decision, reflection."*

> ❌ *"More visibility builds trust, and more trust earns more autonomy. Less visibility erodes both. No visibility at all means no basis for trust."*
> ✅ *"More visibility earns more autonomy. No visibility earns none."*

If you can compress two of the parallel members into one without losing information, the parallel was rhythmic, not substantive.

### 3. Em-dash as thinking-pause prop

Em-dashes gluing two sentences that want to be separate sentences. Three or more em-dashes per paragraph signal performative deliberation.

> ❌ *"Autonomy and transparency are usually treated as parallel concerns — independent checkboxes. They are causally linked."*
> ✅ *"Autonomy and transparency get treated as independent concerns. They are not."*

The em-dash is fine for genuine interjection. It becomes a tell when it stands in for a sentence break the writer was unwilling to commit to.

**Short-phrase connector** is a sub-class: an em-dash used to append a qualifying clause to a short statement, producing a marketing-copy rhythm.

> ❌ *"Six skills — for any model, any toolset."*
> ✅ *"Six skills."*

Other stamps in this family: *"Built for teams — not just individuals.", "Fast — no setup required.", "Simple — until it needs to be complex."*

The tell: the clause after the dash rarely adds information. It hedges, qualifies, or broadens. Cut it; if the information matters, make it a sentence.

### 4. Restatement bloat

Saying the same thing twice in different words, often with the second restatement marked by a softener.

> ❌ *"These are requirements. An AI setup that ignores them has a structural design problem. Each one names something the AI must never be allowed to decide on its own."*
> ✅ *"Each one names a decision an AI must never make on its own. Skip any and the setup is structurally broken."*

The first version says "requirements" then "structural design problem" then "must never be allowed" — three phrasings of the same claim. The second says it once.

### 5. Hedging vocabulary

Words that soften without adding precision: *tend to, usually, often, generally, typically, precisely, actually, essentially, fundamentally, basically.*

> ❌ *"AI improvement cycles tend to declare completion too early."*
> ✅ *"AI loops stop too early."*

> ❌ *"This is precisely the situation that matters most."*
> ✅ *"This is the situation that matters most."*

"Precisely" and "actually" are the most dangerous because they read like emphasis. They are filler.

### 6. Throat-clearing

Sentences that exist to introduce the next sentence: *It is important to note. It should be said. Worth mentioning. Before we continue. Scroll for more.*

> ❌ *"It's worth noting that the trail is append-only."*
> ✅ *"The trail is append-only."*

If the sentence after the throat-clear says the actual thing, the throat-clear was a stage cue, not content.

### 7. Buzz-stack noun phrases

Strings of technical-sounding adjectives that signal expertise without conveying information.

> ❌ *"...a confidential multi-tenant cloud system with domain-driven service boundaries, multiple collaborating microservices, and fully automated CI/CD."*
> ✅ *"...a confidential multi-tenant cloud system with multiple microservices and automated CI/CD."*

Ask of each adjective: does it change what the reader understands? "Domain-driven service boundaries" and "fully automated" are buzz-words pretending to be specs. "Multiple microservices" is the actual information.

### 8. Listicle bait

Turning everything into "three of X" or "five reasons why Y" when the content does not require enumeration.

> ❌ *"There are three key benefits to this approach: faster iteration, better visibility, and clearer accountability."*
> ✅ *"This is faster, more visible, and more accountable."* — or just say which one matters most.

Three-of-X is genuine when the three items are structurally distinct and named (the three Principles, for example). It is bait when the three items are different angles of one idea.

### 9. Corporate sentence-stamps

Pre-fabricated phrasings that signal "professional copy" without saying anything.

> ❌ *"The workhorse of the suite."*
> ✅ *"The workhorse."*

> ❌ *"This framework is the answer I built for myself."*
> ✅ *"So I built this."*

> ❌ *"At its core, X is all about Y."*
> ✅ *"X is Y."*

These are templates the model has seen ten thousand times. They feel like writing; they are filler.

**Spatial-void substitutes** are a sub-class: abstract gap-metaphors that name an absence instead of the thing that is missing or different.

> ❌ *"We need to close the gap between the audit trail and real accountability."*
> ✅ *"The audit trail does not prove accountability."*

Other stamps in this family: *"bridge the gap", "fill the gap", "narrow the gap", "address the gap".*

The tell: a void is described, not the difference. Replacing the metaphor with the actual claim almost always reveals that the original sentence was stalling.

### 10. False precision

Words that perform precision without delivering it: *exactly, specifically, particularly, in particular.*

> ❌ *"This is exactly what we mean by Observable Autonomy."*
> ✅ *"This is Observable Autonomy."*

"Exactly" used as emphasis is fluff. "Exactly" used to distinguish (*exactly six*, *exactly this case*) is content.

### 11. Mirror-the-question

Restating the question as the opening of the answer.

> ❌ *"Why does the trail matter? The trail matters because..."*
> ✅ *"The trail matters because..."*

Common in FAQ-style structures. The mirror adds nothing and signals AI-Q&A-bot register.

### 12. Compound qualifiers

Stacking softeners on a single claim: *somewhat surprisingly, perhaps importantly, in some sense, in a way.*

> ❌ *"In some sense, this is perhaps the most important point."*
> ✅ *"This is the most important point."* — or cut the sentence; if it is the most important, the surrounding text should already show it.

### 13. Difficulty-announcement frames

Announcing that something is hard, tricky, or a challenge before stating it. The frame substitutes for the claim.

> ❌ *"The hard part is staying accountable for the work."*
> ✅ *"Stay accountable for the work."*

> ❌ *"The tricky part is knowing which outputs were wrong."*
> ✅ *"You won't know which outputs were wrong until they've already been used."*

> ❌ *"The real challenge is maintaining visibility as the system scales."*
> ✅ *"Visibility degrades as the system scales."*

Other stamps in this family: *"The key challenge is...", "The difficult part is...", "What makes this hard is...", "The problem is...", "Here's the catch:..."*

The tell: the writer announces that a difficult thing is coming instead of just saying the difficult thing. Cut the announcement. Say the thing.

---

## The work

### 1. Read the target like a reader, not a writer

Read the prose at normal reading speed, without editing intent. Notice where the eye trips. Notice where the rhythm announces itself. Notice where you can predict the next phrase before reading it. Those are the tells.

If the prose has substantive problems (wrong claim, unclear structure, missing information), **stop and run Improve instead**. De-AI on broken substance produces well-polished broken substance. Substance first, surface last.

### 2. Apply the catalogue as a lens

Walk through the thirteen patterns above. For each, ask: does this prose cluster on this pattern? Not "is there one instance" — *is the pattern the default*.

Name the clusters you find. Two or three is normal for AI-drafted prose. Five or more means the surface is the problem and a substantial rewrite is warranted. Zero clusters in AI-drafted prose almost certainly means you missed something — read again.

### 3. Decide what to cut

Three decision categories:

- **Cut.** The instance is a clear tell and the meaning survives without it.
- **Keep with note.** The instance reads as a tell to you, but it is operator voice (see the "What this skill is not" section). Note it in the trail so future runs can see the call was made deliberately.
- **Rewrite.** The instance carries information but the phrasing is a tell. Restate, do not delete.

Be willing to leave a passage slightly flatter than it was. The goal is honesty, not punch.

### 4. Apply

Make the edits. Prefer compression (cut, restate) over expansion. If a section gets shorter by 30%, that is normal. If it gets shorter by 60%, examine whether you removed substance, not just style.

### 5. Record

If new tell-patterns surfaced that are not in the catalogue above, mark them `[!REALIZATION]` in the trail entry and consider whether they should be added to this skill on the next pass. The catalogue is meant to accumulate — language drift in AI output is ongoing, and what reads as a tell today is different from what read as a tell two years ago.

If the operator pushed back on a cut (e.g., "that phrasing was mine"), mark it `[!REVERSAL]` and update your model of voice for the target.

---

## Self-targeting

This skill must be runnable on itself. Run De-AI on `de-ai/SKILL.md`. If it surfaces unstripped tells in this very document, fix them. The catalogue above is examples, not exemptions.

A known risk: a skill *about* AI-tells will naturally use the vocabulary of AI-tells in its examples. Distinguish between *naming the pattern* (necessary) and *exhibiting the pattern in skill prose* (a tell).

---

## Composition with other skills

- **With [Improve](../improve/SKILL.md):** De-AI runs as a finishing pass *after* Improve has settled the substance. An Improve iteration may close with "and a De-AI pass on the changed sections" — but the substance work happens first.
- **With [Intent](../intent/SKILL.md):** Intent determines what the prose should say. De-AI examines how it says it. Two independent layers.
- **With [Probe](../probe/SKILL.md):** A Probe pair could test whether a reader actually flags a De-AI-stripped passage as more credible than the original. This skill's claims are not currently probe-tested.

---

## What this skill does not do

- It does not produce a numerical "AI-likeness score." Such scores exist and are reverse-engineerable, which makes them gameable. Convergence here is the same as everywhere in this suite: independent readers (human, ideally diverse) finding nothing further to cut.
- It does not rewrite for tone, register, or audience fit. That is a separate concern, handled at the Destination and Improve layers.
- It does not strip personality. If the writer's voice happens to use em-dashes, three-part lists, or hedging, those are voice — not tells. The skill applies *only when the prose has no human author whose voice should be preserved*, or when the human author has asked for the lens to be applied to their own draft.
