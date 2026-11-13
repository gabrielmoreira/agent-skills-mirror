---
name: feature-design
description: Use when the user has a rough idea for a feature, product change, or new capability and wants to brainstorm, shape, design, or spec it before building, such as "I'm thinking of adding…", "how should we approach…", "help me design…", or "write a spec for…".
compatibility: Needs the domain-driven-design, ux-brainstorm, and test-driven-development skills from the same plugin. Works best with a question tool (AskUserQuestion or the harness's equivalent), the Exa MCP for research, a harness that renders HTML or diagrams inline, and an issue tracker CLI or MCP for the handoff.
---

# Feature design

You are the tech lead shaping this feature with its owner. They own what it is for: the problem, who it serves, scope, behavior, and UX. You own how it is built. The result is a spec someone can implement without reopening the conversation, reached with as little of the user's attention as you can manage.

- **Product decision**: a choice about scope, behavior, UX, or user impact. The user makes the few that only they can make; you make the rest.
- **Assumption**: a product decision you made for the user. Each one is listed in the closing reply and in the spec, so they can overrule it.
- **Technical decision**: a choice about how it is built (data, architecture, libraries, protocols). All yours. The user first hears of them in the closing reply.
- **Round**: one use of the question tool, carrying up to five questions. The interview's budget is three rounds, and the closing question in step 6 is outside it.
- **Slice**: a thin end-to-end piece of the feature that someone can see working and that can ship by itself ("staff can propose a swap to a colleague"). A layer ("the database part") is not a slice.

The user sees three kinds of reply: the challenge together with round one, later rounds when they are needed, and the closing reply.

Research with the Exa MCP (when its tools aren't listed yet, look them up with ToolSearch before calling them missing). Only when Exa is missing, unauthenticated, or erroring, use the harness's own web search, and say in the reply that you did.

## 1. Ground

The project and the world are the source of truth; what the user says about them is a claim to check. Before replying at all:

- **Decisions**: read every ADR (they are short, and the one you skip is the one you will contradict), the glossary, the README, and every page under `docs/` that touches the idea.
- **Code**: read what the idea touches: what exists today, what already half-solves the problem, the data and rules behind it, and the stack's constraints.
- **Tracker**: look for issues that already ask for this, or decided against it.
- **Outside**: research how established products solve the same problem, and what the libraries or platforms involved can and can't do. Trust what you find over what you remember.

With subagents, run these in parallel. Done when you hold, each with its source: the real problem, what the project already has toward it, and every point where the idea as stated conflicts with a recorded decision, the code, or the research.

## 2. Challenge

Open the reply with the **brief**: the problem, who has it, the outcome that counts as success, and what is out of scope. Write it in the glossary's terms, and where the user's word differs ("trade" where the project says "swap"), name the project's term.

Then state what you found, in plain words, each finding with its evidence (the ADR, the file, the source):

- what is wrong with the idea as stated: it already exists, it contradicts a recorded decision, it treats a symptom, a much smaller change reaches the same outcome, or research shows it fails in a known way;
- the shape you would give it instead, and why that serves their goal better.

State findings as findings, however sure the user sounded. Their chance to overrule you is the first question of round one: your shape (Recommended) against the idea as they stated it.

Then sort every open decision:

| Decision | Who decides | Where it goes |
| --- | --- | --- |
| Technical | You | Step 4 |
| Product, answerable from the grounding (code, docs, ADRs, common practice) | You | An assumption |
| Product, only the user can know | The user | A question |

Rank the questions by how much of the spec changes with the answer and how costly a wrong guess is to undo. The budget holds fifteen; whatever ranks below that becomes an assumption.

Done when the reply holds the brief, every conflict from step 1 with its evidence, and your shape, and every open decision sits in one row of the table.

## 3. Interview

Send round one in the same turn as the challenge, then wait. Write each later round from the answers to the one before, going from wide to narrow: round one settles the problem and the shape of the solution; later rounds settle behavior, UX, and edge cases.

The budget exists because the user's attention is the scarce resource. Each question has to earn its place, and a round is sent only while some unanswered question would still change the spec.

Ask through the question tool (AskUserQuestion, or whatever the harness offers), so the user picks instead of writes. With no question tool, send the round as numbered questions with lettered options, answerable in one line ("1B 2A 3C").

Each question:

- is about the feature, its users, or its UX;
- names what the user or their users will notice, in the user's own words;
- offers two to four concrete options, each described by what people will see, gain, or lose;
- for a choice, puts your recommended option first, labeled (Recommended);
- for a fact only the user knows (why it happens, how often), offers the likely answers plus "I don't know", and says what you will assume then;
- flags any option that changes how the product behaves today, or goes against a recorded decision.

**Make the question picturable.** A choice the user can't picture gets a guess for an answer. Before the round, or inside the options, show what the options mean with the lightest aid that works:

- an example with realistic data ("Ana offers her Friday shift; Ben sees…"), often enough by itself;
- a diagram for flows, states, or how parts relate (Mermaid when the harness renders it, otherwise ASCII);
- side-by-side mockups in the question tool's option previews, when it has them;
- a small interactive HTML prototype when the choice is about feel or a multi-step flow, rendered inline when the harness can and opened in the browser otherwise. When the whole question is what a screen should look like, hand that part to the ux-brainstorm skill.

**Sharpen the glossary.** Settle the words that come up per the domain-driven-design skill's [language rules](../domain-driven-design/references/language.md); its questions join this round.

After each round, record the answers as numbered decisions. When the third round is answered, or no remaining question would change the spec, turn every question still open into an assumption, using the option you would have recommended.

Done when every ranked question has a numbered decision or an assumption.

## 4. Design

Make every technical decision: architecture, data, interfaces, libraries, rollout. Run the domain-driven-design skill's Architecture part first; the boundaries, architecture, and aggregates it hands back are technical decisions, and its ADRs and context map are linked from the spec. Shape each one from the numbered decisions and the project's constraints (existing architecture, ADRs, stack, scale), research anything you plan to depend on, and choose the smallest design that makes the agreed behavior hold.

Done when each technical decision names the numbered decision or constraint that calls for it.

## 5. Document

Write everything into the repository, so the next session and the next feature design start from files. Formats are in [references/formats.md](references/formats.md); where the project already keeps a glossary, ADRs, or specs, its location and format win.

- **ADRs**, in `docs/adr/`: one per non-trivial decision, product or technical, that domain-driven-design hasn't already recorded. When a decision replaces an earlier ADR, mark the old one superseded and link both ways, so the ADRs agree with each other.
- **Glossary and context map**: domain-driven-design keeps them as terms and boundaries settle; check they hold every one agreed here.
- **Existing docs**: update every page under `docs/` whose description the feature makes wrong.
- **Spec**, in `docs/specs/<slug>.md`: the numbered decisions, the assumptions, the design with a link to each ADR, the acceptance checks, and the slices in implementation order, each with its own checks and what it depends on.

Done when every numbered decision, assumption, and technical decision is in the spec, every non-trivial one has an ADR, and each acceptance check belongs to a slice.

## 6. Close

Send one closing reply. It is the first time the user hears the technical side, and how they check that you understood them:

- **What we agreed**: the brief and the numbered decisions, with each assumption marked as one.
- **How it will be built**: each technical decision as what and why, tied to a need they stated ("Swaps must work with no signal on the shop floor, so the app saves them on the phone first and sends them when it's back online"). Use plain English, and explain any technical word you can't avoid in half a sentence. Add a diagram when the parts and their order matter.
- **What it costs**: limits, risks, and what gets harder later.
- **Files**: the paths you wrote.

End it by asking, through the question tool, how to continue:

1. **Open issues** on the project's tracker.
2. **Implement now**, in a new session with a fresh context.
3. **Both**: issues first, then the new session.

When the user answers with a correction, apply it to the decisions, the ADRs, and the spec, then ask again. When they pick, read [references/handoff.md](references/handoff.md) and follow the part for their pick. Implementation always goes to a new session: this one's context is full of exploration and rejected options, and the spec exists so the work can start clean.

Done when the handoff the user picked is complete, per that file.
