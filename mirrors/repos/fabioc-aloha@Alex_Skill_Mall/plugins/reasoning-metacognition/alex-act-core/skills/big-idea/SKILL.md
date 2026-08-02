---
name: big-idea
description: "Distill the central claim before authoring any summary-shaped output: hero copy, commit-message subject, PR title, ADR title, slide title, executive summary, skill description, abstract. Length is format-dependent (1 sentence for titles, up to a short paragraph for complex theses), tested against the Saint-Exupéry rule (remove sentences until removing another would break the claim). Chart summaries use the specialized chart-big-idea skill in the flint-chart-plugin."
lastReviewed: 2026-07-28
---

# Big Idea

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry, _Terre des hommes_ (1939)

Distill the central claim before authoring any summary-shaped output. Every hero subtitle, commit subject, PR title, ADR title, slide title, executive summary, and skill description should carry a Big Idea: a testable thesis that answers _"what changes for the reader?"_, not an enumeration of what's inside the artifact.

Generalized from `chart-big-idea` in the [flint-chart-plugin](https://github.com/fabioc-aloha/flint-chart-plugin), which specializes this discipline for chart authoring. This skill covers everything else.

## When to Fire

| Context                                                                 | Big Idea IS...                                      |
| ----------------------------------------------------------------------- | --------------------------------------------------- |
| Hero copy (doc subtitle)                                                | The doc's thesis                                    |
| Commit-message subject                                                  | The change that matters, not the file diff          |
| PR title                                                                | The reviewer's decision-changer                     |
| ADR title                                                               | The boundary the decision draws                     |
| Slide title                                                             | The claim the slide argues                          |
| Executive summary abstract                                              | The one thing the reader needs from the memo        |
| Skill description (frontmatter `description` field)                     | The "what + when" that makes discovery work         |
| Meeting agenda item                                                     | The decision the discussion should produce          |
| Blog post headline                                                      | The claim the post argues (not the topic it covers) |

## When NOT to Fire

- **Plain body prose** — Big Idea authoring is for headlines, not paragraphs. Body prose defends the Big Idea; it isn't one.
- **Bullet lists inside a doc** — each bullet doesn't need its own thesis. The section header carries the Big Idea if any bullet does.
- **Code comments** — unless the comment IS a thesis (rare — most code comments explain _how_, not _why anything changes_).
- **README intro paragraphs** — those get to be longer than one sentence. Use Big Idea for the README's title tagline, not its opening paragraph.
- **Chart summaries** — use `chart-big-idea` in the flint-chart-plugin instead. That skill's step 5 emits a Chart Brief; this skill's step 5 emits prose.

## The four-step distill (plus emit)

Skipping any step is why summaries drift back to tactical enumeration. Run all four before writing the sentence.

### 1. Read for an existing Big Idea

Scan the source artifact (doc body / commit diff / ADR argument / slide content) for the central claim already stated. Often the Big Idea is buried in a middle paragraph or half-said in a conclusion. If it's there, extract; if not, distill from scratch.

### 2. Distill the claim

What is THE one thing this artifact argues? Not _"what topics does it cover"_ — what _claim_ does it make?

Test: if someone read only this sentence and nothing else, what would they know that they didn't before?

### 3. Story arc

Name the narrative shape — it informs the sentence's grammar and tense:

| Arc               | Signal                           | Big Idea shape                                           |
| ----------------- | -------------------------------- | -------------------------------------------------------- |
| **Chronological** | "we did X, then Y, then Z"       | _"Migration X taught us Y"_ — past tense, cause + lesson |
| **Comparative**   | "A vs B; here's why we picked A" | _"A costs less than B because C"_ — contrastive          |
| **Prescriptive**  | "here's what to do next"         | _"Do X before Y or you'll hit Z"_ — imperative           |
| **Cautionary**    | "here's what to avoid"           | _"Skipping X guarantees Y"_ — warning                    |
| **Diagnostic**    | "here's what broke and why"      | _"Bug X was caused by Y; fix is Z"_ — analysis           |

### 4. Audience + stakes

Who reads this artifact, and what changes for them?

- A Big Idea that names the reader's decision (implicitly or explicitly) is thesis-shaped.
- A Big Idea that names only the topic is TOC-shaped.

Test: read the draft and ask _"so what?"_ If nothing changes for the reader, revise.

### 5. Stance

Is this Big Idea:

- **Consolidating consensus** — confirming what the reader already believes. Safer, less punchy, room for qualifiers.
- **Challenging a norm** — contesting a default assumption. Higher risk, higher payoff, strip qualifiers.

Analogous to TRADITIONAL vs. INNOVATIVE in `chart-big-idea`. The stance sets qualifier budget: consolidating leaves in "often"/"usually"; challenging strips them out.

### 6. Emit and compress

The Saint-Exupéry rule is the actual gate. Draft the Big Idea, then apply the **removal test**: try deleting each sentence. If deleting it leaves the claim intact, delete it. Repeat until removing another sentence would break the claim. What remains is the Big Idea.

Length ceiling depends on format:

| Format                       | Natural ceiling | Why                                                    |
| ---------------------------- | --------------- | ------------------------------------------------------ |
| Chart caption                | 1 sentence      | The chart carries the payload                          |
| Commit subject / PR title    | 1 sentence      | Format-imposed by git / email                          |
| ADR title                    | 1 sentence      | Index-scanning convention                              |
| Slide title                  | 1 sentence      | Reader is glancing                                     |
| Hero copy / doc subtitle     | 1–3 sentences   | Reader is scanning; three beats before commitment      |
| Executive summary / abstract | 2–4 sentences   | Reader has committed; density is the point             |
| Complex-thesis Big Idea      | Short paragraph | Some claims genuinely need setup + insight + qualifier |

Discipline for every sentence that survives the removal test:

- **Answers "what changes for the reader?"**
- **Names a specific claim, not a topic** so the claim is testable.
- **Someone could reasonably argue against it**; if not, it's a truism, not a thesis.
- **Concrete over abstract**: carry a name, number, or contrast where possible.
- **No TOC enumeration**: no bulleted-list-as-sentence.
- **No hedge stacking**: pick one hedge or none.
- **No compression theater**: if a semicolon or colon is doing the work of a full stop and the second clause could stand as its own sentence, split it. Compression is real only when the removal test would break the claim.
- **American English** by default (if your project defines a language rule in `copilot-instructions.md`, follow it — Alex ACT itself uses American English per Cardinal Rule 4). Use `color`, `behavior`, `center`, `catalog`, `license`, `analyze`, `favor`, `honor`, `defense`. Avoid `colour`, `behaviour`, `centre`, `catalogue`, `licence`, `analyse`, `favour`, `honour`, `defence`. Three carveouts stay: the `[behaviour]` commit-tag API string, ACT framework canonical terms, and ported material that retains its source spelling.
- **No AI-tells**, per Cardinal Rule 2 in `copilot-instructions.md` and the full 29-pattern catalog in [humanizer](../humanizer/SKILL.md). No em-dashes as sentence separators (use commas, colons, semicolons, parentheses, or full stops instead); no filler intensifiers (`comprehensive`, `robust`, `leverage`, `seamlessly`, `delve into`, `tapestry`, `weave`, `testament`); no `load-bearing` as a synonym for `important / central / key` (see humanizer Pattern 7 for the technical-vs-decorative carveout); no performative openers (`Certainly!`, `Great question!`, `Let me...`); no meta-description (`This document explains...`, `The following is...`); no ceremonial rule-of-three parallelism used as decoration rather than argument.

## Anti-patterns

| Anti-pattern                      | Symptom                                                                                                                           | Rewrite discipline                                                                                                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **TOC enumeration**               | Lists chapters instead of naming the claim                                                                                        | Ask: _"what does the doc argue?"_ — write that.                                                                                                  |
| **Position statement**            | Names what the doc IS without saying what it CLAIMS                                                                               | Add the _"so what?"_ — what changes because of this thing?                                                                                       |
| **Poetic count-up**               | Rhythmic but content-free (_"one brain, five regions, five loops..."_)                                                            | The rhythm is style, not substance. What's the argument?                                                                                         |
| **Feature enumeration**           | _"A · B · C · D"_ separated by middots                                                                                            | Middots hide missing thesis. Pick one claim; defend with the features in body.                                                                   |
| **Overpromise**                   | Claim exceeds what the artifact delivers                                                                                          | Read the body and cut back to what it actually earns.                                                                                            |
| **Hedge stacking**                | _"May", "could", "often", "usually"_ all in one sentence                                                                          | Pick one hedge or none. Multiple hedges signal you don't believe your own claim.                                                                 |
| **Passive voice on the verb**     | _"Improvements were made to X"_                                                                                                   | Big Ideas have subjects. _"X now Y because Z."_                                                                                                  |
| **Meta-description**              | _"This doc explains..."_                                                                                                          | Skip the _"this doc explains"_ and just make the claim.                                                                                          |
| **British spelling**              | _"colour", "behaviour", "centre", "catalogue", "licence"_                                                                         | American English by default. Three carveouts stay: `[behaviour]` API tag, ACT framework canon, ported material.          |
| **AI-tell vocabulary**            | _"comprehensive", "robust", "leverage", "seamlessly", "delve into", "tapestry", "weave", "testament"_                             | Strip. See [humanizer](../humanizer/SKILL.md) for the 29-pattern catalog and voice replacements.                                                 |
| **Em-dash as sentence-separator** | Em-dash standing in for a colon, semicolon, or full stop                                                                          | Cardinal Rule 2. Use a colon (for "here's why"), a semicolon (for a paired thought), parentheses (for a side note), or split the sentence.       |
| **Performative preamble**         | _"Certainly!", "Great question!", "Let me..."_ before the claim                                                                   | Skip the throat-clearing. The Big Idea is the first word.                                                                                        |
| **Compression theater**           | Semicolon or colon doing the work of a full stop; second clause is either a re-worded first clause or would earn its own sentence | Apply the removal test. If the second clause is a full stop in disguise, split it. If both clauses say the same thing, delete the redundant one. |

## Worked examples

From the 2026-07-28 hero-copy sweep on this repo. Note the shape: before is enumeration of contents; after is a compressed thesis (one or two sentences, per the removal test) with a subject verb and a _because_ or _so_.

| Doc                 | Before (tactical)                                                                                    | After (Big Idea)                                                                                                                                              |
| ------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plan/plan`         | _"From heir-template to plugin-native — every folder, cloud store & identity that touches this box"_ | _"The v1 template lineage costs too much to maintain per heir. Migrating to Copilot CLI plugins moves complexity from twenty-five heirs back to one source."_ |
| `docs/act`          | _"Manifesto · 10 tenets · claims registry · failure modes · engineering binding · curation rules"_   | _"AI is trained to agree with you. ACT is the discipline that makes it push back on the claims that matter."_                                                 |
| `operations/fleet`  | _"Heir markers · hybrid local+GitHub inventory · dashboard · reports"_                               | _"Fleet is visibility, not control. Steward never mutates a heir, so the dashboard reports what heirs decide, not what Steward wants."_                       |
| `plan/fundamentals` | _"One brain, five regions, five loops, seven primitives, ten tenets, one dial, one fleet"_           | _"Every capable AI partner runs the same seven cognitive primitives. Naming them turns AI craft into engineering."_                                           |

## Cross-domain examples (not from a real commit — showing the shape)

**Commit-message subject** (arc: diagnostic; stance: challenging):

- Before: `refactor: update fetch logic to handle timeouts`
- After: `[behaviour] fetch: 3s timeout replaces indefinite hang on unreachable Edition release`

**PR title** (arc: prescriptive; stance: consolidating):

- Before: `Update dependencies`
- After: `Bump marked to 12.0.0 to unlock the token-object renderer API needed by mermaid-in-code-fence support`

**ADR title** (arc: comparative; stance: challenging):

- Before: `ADR-014: Mall v1 to v2 migration approach`
- After: `ADR-014: Mall in-place bump to 3.0.0 (not fork-and-freeze) because 5 of 25 heirs currently route through the affected surface`

## Related

- `chart-big-idea` in the [flint-chart-plugin](https://github.com/fabioc-aloha/flint-chart-plugin) — chart specialization. Both skills share the same six-step arc with offset numbering: chart-big-idea Step 0 (read context) → this skill's Step 1; chart-big-idea Steps 1-4 → this skill's Steps 2-5; chart-big-idea Step 5 emits a Chart Brief while this skill's Step 6 emits prose.
- Skill descriptions ARE Big Ideas — the frontmatter `description` field's "what + when" is the thesis + trigger of the skill's Big Idea.
- [communication-craft](../communication-craft/SKILL.md) — sibling skill for feedback, audience, and elicitation. Communication craft frames the whole message; Big Idea frames only the headline.
- [humanizer](../humanizer/SKILL.md) — the 29-pattern AI-tell catalog and voice replacements. Big Idea authoring routes through humanizer for the AI-tell check before emit.
- [problem-framing-audit](../problem-framing-audit/SKILL.md) — different discipline: audit the frame BEFORE solving. Big Idea distills the claim AFTER solving. Both cite the same _"is this the right thing?"_ test but at different phases.

## Falsifiability

This skill has failed if any of the following occur by **2027-01-28** (6 months from adoption):

- **Inert**: zero invocations outside the hero-copy sweep that inspired it — the discipline never got exercised in a second domain
- **Doesn't land**: Big Ideas authored via this skill still read tactical (TOC-shaped, position-statement-shaped, feature-enumeration-shaped) ≥3 times in a quarter
- **Decorative steps**: the four-step distill (context read → claim → arc → stance → emit) consistently produces identical output to skipping steps 3–5 — the extra steps are ritual, not method
- **Drifts from parent**: `chart-big-idea` upstream evolves in a way this skill can't accommodate — the specialization relationship broke

Track in your project's audit trail (Alex ACT itself tracks in `operations/ledgers/curation-log.md`) tagged `[BIG-IDEA-DRIFT]`.

## Would Revise If

- The skill proves out (≥3 invocations across ≥2 non-hero-copy domains by **2026-10-28**, no drift in the chart-plugin relationship) → **earn promotion**: refactor `chart-big-idea` upstream to depend on this skill as its four-step foundation, so the specialization relationship becomes structural rather than documentary
- Fabio flags ≥3 authored Big Ideas as overreach or mis-claim within the falsification window → the skill's discipline is calibrated wrong; add stronger _"honest to what the artifact delivers"_ language and re-test
- A domain surfaces where step 3 (story arc) doesn't map cleanly to the five listed arcs → extend the table with the missing arc, or reduce to arcs-are-optional guidance
