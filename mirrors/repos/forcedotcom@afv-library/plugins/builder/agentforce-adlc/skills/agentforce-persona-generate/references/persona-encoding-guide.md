---
version: "4.0.0"
date: 2026-05-15
---

# Persona Encoding Guide

How to encode a persona document into Agentforce. This guide covers the encoding architecture, field-by-field guidance for each agent authoring tool, and additional encoding options.

**Prerequisite:** A completed persona document — identity traits, Personification, 13 expression dimensions across 5 categories (Register, Voice, Tone, Delivery, Chatting Style), tone boundaries, tone flex rules, phrase book, never-say list, and optionally lexicon and guardrails. See the **Agent Persona Framework** (`references/persona-framework.md`) for how to create one.

## Terminology note: "Subagent" is the new "Topic"

Salesforce has adopted **`subagent`** as the canonical term in `.agent` file syntax (per `forcedotcom/sf-skills/skills/developing-agentforce/`). This guide uses `subagent` for Agent Script discussion. **Agentforce Builder UI still uses "Topic"** — when this guide references Builder's "Topic Instructions" field or "Topic"-named UI elements, that's the Builder term for the same concept. Agent Script's `subagent` block and Builder's "Topic" are interchangeable in encoding semantics; only the UI label differs.

When this guide says **"per-subagent"** in an Agent Script context, it's referring to a `subagent` block. When it says **"Topic Instructions"** in a Builder context, it's the field where the same content goes.

## Two encoding lanes

The skill produces encoding output for two scenarios:

**Greenfield (Use Case A) — start a new agent.**
- ENCODE produces a **minimal valid `.agent` skeleton** with `system`, `config`, `language`, `start_agent` (stub), and one placeholder `subagent`.
- The persona content lives in `system.instructions` and `system.messages`.
- Subagents, actions, variables, and routing are *placeholders for the user to flesh out* — the skill never invents them.
- Output path: `persona/[agent-name]/[agent-name].agent`.

**Brownfield (Use Case B) — re-encode an existing agent.**
- The skill reads the source `.agent` file via `scripts/parse_agent_yaml.py` (read-only).
- ENCODE preserves the existing structure (subagents, actions, routing, variables — all of it) and **only modifies persona-bearing fields**: `system.instructions`, `system.messages.welcome`, `system.messages.error`, per-subagent `system:` overrides, per-subagent `reasoning.instructions:`, per-action `progress_indicator_message:`.
- Output: an annotated proposed-new-file plus a diff summary at `persona/[agent-name]/persona-diff.md`.
- The diff explicitly excludes routing, subagent structure, action contracts.

## Schema authority

The canonical Agent Script schema lives in [`forcedotcom/sf-skills/skills/developing-agentforce/`](https://github.com/forcedotcom/sf-skills/tree/main/skills/developing-agentforce). When in doubt about a top-level block, an action property, or an indentation rule, defer to that skill. This guide focuses on persona-bearing fields and how the persona document maps into them — not on the full Agent Script grammar.

Quick reference (see `developing-agentforce` for full detail):
- **Top-level block order is mandatory:** `system` → `config` → `variables` → `connection` → `knowledge` → `language` → `start_agent` → `subagent`.
- **Indentation:** 4 spaces, never tabs.
- **Booleans:** `True` / `False` capitalized.
- **Strings:** double-quoted.
- **Identifiers:** `[a-zA-Z][a-zA-Z0-9_]*`, max 80 chars, snake_case.
- **`config.developer_name`** must match the directory name; **`config.agent_label`** is the display name; **`config.agent_type`** is `"AgentforceServiceAgent"` (external, requires `default_agent_user`) or `"AgentforceEmployeeAgent"` (internal, prohibits `default_agent_user`).

---

## Encoding Architecture

The encoding model is the same on both Agent Script and Agentforce Builder: **one global persona block, subagent calibration overlays, and static messages.**

```text
Global Instructions (who the agent is, baseline persona)
    │
    ├── Subagent Calibration (how persona adapts per subagent)
    │     ├── Brevity calibration
    │     ├── Tone flex encoding
    │     ├── Phrase book entries
    │     ├── Humor guidance
    │     ├── Lexicon
    │     └── Persona reminders
    │
    └── Static Messages (welcome, error, loading, deterministic)
```

| Layer | What It Carries | Where It Lives |
|---|---|---|
| **Global instructions** | Baseline identity + all dimensions + phrase book + never-say + tone boundaries | Agent Script: `system.instructions`. Builder: a dedicated global instructions topic. |
| **Topic calibration** | Per-subagent overrides: brevity, tone flex, lexicon, phrase book entries, humor | Agent Script: `reasoning.instructions` per subagent. Builder: per-subagent instructions. |
| **Static messages** | Welcome, error, loading text, deterministic responses | Tool-specific fields (see below). |

### Global Instructions

Most persona content goes in global instructions. They carry the agent's baseline identity and dimensions into every conversation.

| Agent Authoring Tool | Where Global Instructions Go |
|---|---|
| Agent Script | `system.instructions` in the `.agent` file |
| Agentforce Builder | Create a dedicated global instructions topic. The planner passes this topic's instructions to the LLM with every prompt. |

Include everything except instructions that only apply to a single topic.

**Agent Script is recommended when persona consistency is at a premium.** `system.instructions` are treated as core logic rather than context that competes with conversation history, so persona instructions are not diluted as turns accumulate. Negative constraints hold more consistently. Register is more stable: system-level instructions set a tone anchor that persists through extended sessions.

#### Example: Drover (sales coach)

This excerpt from global instructions would work in either tool:

```text
You are Drover, an internal sales coach for enterprise AEs. You read
deals like a stockman reads the bush — subtle signs others miss, hard
truths delivered with easy confidence.

Identity: Instinctive, Unflinching, Practical, Reframing, Steady.
Register: Advisor. Lead with recommendations and rationale. Expect the
seller to make the call. Never hedge when the data is clear.
Voice: Casual formality — contractions, fragments, no corporate jargon.
Neutral warmth — competence is the care. Bold personality — metaphors,
distinctive phrasing, unmistakable voice.
Emotional Coloring: Neutral. State outcomes as facts. No dramatization.
Empathy: Understated. Brief nod, then pivot to action.
Brevity: Concise. Every sentence earns its place.
Humor: Dry. Understated, never forced. Suppress in error and escalation.
Chatting Style: Functional emoji (status indicators for deal health). Selective
formatting. Expressive punctuation. Standard capitalization.

Tone boundaries: Never sound apologetic. Never sound corporate. Never
soften bad news — deliver it straight, then show the path forward.
Never say: "Great question!", "I'd be happy to help", "Let me know
if you need anything else", "Going forward".
Phrase book — Acknowledgement: "Right." / "Noted." Redirect: "Not my
paddock — loop in [team]." Progress: "Good ground covered."
```

*Note:* In Agent Script, always use the `|` (literal block scalar) indicator for instruction content. Without it, lines like `Brevity: Moderate…` or `Tone: Shift Empathy…` will be parsed as YAML key-value pairs instead of instruction text.

### Subagent Calibration

Subagent-level instructions adapt from the baseline set in global instructions. They refine and calibrate — they don't redefine who the agent is. When subagent instructions conflict with global, the model reconciles: it treats global as the core identity and topic as situational adaptation.

| Agent Authoring Tool | Where Topic Instructions Go | Behavior |
|---|---|---|
| Agent Script | `reasoning.instructions` within each topic | Extends global `system.instructions` |
| Agentforce Builder | Topic Instructions field | Extends global instructions topic |

If you need a radically different voice for a topic, you have options in order of preference:

1. **Lighter-weight calibration first:** lexicon, topic phrase book, topic never-say, tone flex rules, brevity adjustment
2. **Subagent-level system override (Agent Script only):** a `system:` block in the topic replaces `system.instructions` for that topic — reserve for major persona shifts and remember to duplicate *all* instructions
3. **Separate agent:** if the persona shift is extreme, a separate agent may be cleaner

Each topic can carry:

**Brevity calibration** — different topics need different response lengths.

Status check topic (terse):
```text
Brevity: Terse. One-line status, emoji health indicator, no commentary.
If the user asks a follow-up, answer it — don't volunteer context they
didn't request.
```

Deal analysis topic (moderate):
```text
Brevity: Moderate. Lead with a recommendation and its rationale. Include
supporting data points. Use bullet formatting for multi-factor analysis.
End with a single next step.
```

**Tone flex encoding** — how Emotional Coloring and Empathy Level shift by subagent context.

Escalation topic:
```text
Tone: Shift Emotional Coloring toward Encouraging. Shift Empathy Level
toward Moderate. Acknowledge the difficulty briefly, then show the path
forward. Never minimize the user's frustration.
```

Data retrieval topic:
```text
Tone: Maintain Neutral Emotional Coloring and Understated Empathy Level.
State findings without editorial. Confidence labeling matters most
here — label confirmed data vs. inferred data.
```

**Phrase book entries** — situational phrases relevant to this topic.

**Humor guidance** — whether humor is appropriate or suppressed. Always suppress humor in error states, escalation, and high-stakes contexts.

**Topic lexicon** — domain vocabulary scoped to where it belongs. A luxury watch agent has vocabulary like "movement," "chronograph," "caliber." These belong in product topics, not shipping topics. Loading specialized vocabulary globally wastes context and can cause the agent to over-use jargon in simple service interactions. Add a `Lexicon:` block to a topic's instructions when there are relevant domain terms and usage notes.

Example (product topic for a luxury watch agent):
```text
Lexicon: Use these terms freely — the audience expects them.
"Movement" — the internal mechanism. Never say "engine" or "motor."
"Chronograph" — stopwatch complication. Not "timer."
"Caliber" — specific movement reference number.
"Complication" — any function beyond hours/minutes/seconds.
```

#### Topic Lexicon Format

Two formats are valid. Choose based on whether usage context matters.

**Key-value pairs** — term + definition/usage context. Use when the term needs explanation or has usage rules:
```text
Lexicon:
"Compelling event" — External pressure that motivates a decision by a
  deadline. Use when a deal has time-bound urgency. Not "trigger."
"Champion" — Internal advocate with authority and motivation. Not
  "sponsor" (implies passive). Not "contact."
"Multithreading" — Engaging multiple stakeholders simultaneously. Use
  freely — the audience expects it.
```

**Term list** — terms only, no definitions. Use when the terms speak for themselves and the audience knows them:
```text
Lexicon: Use these terms freely.
Movement, chronograph, caliber, complication, bezel, lug width,
power reserve, guilloche, deployment clasp.
```

**"Use this / don't use this" pairs** work in either format:
```text
Say "compelling event," not "trigger."
Say "champion," not "sponsor" or "contact."
```

**How many terms?** 5-15 per subagent is the productive range. Below 5, the lexicon isn't doing much work. Above 15, diminishing returns — the model starts over-using jargon. If you have 20+ terms, split into subtopics or move the less critical ones to global lexicon.

**Lexicon vs. Phrase Book boundary:**
- **Lexicon** = domain vocabulary ("compelling event," "chronograph"). Organized by domain.
- **Phrase Book** = situation-keyed sample phrases ("When redirecting, say..."). Organized by situation.
- A term can appear in both: the lexicon defines it, the phrase book shows it in context.

**Immutable terms:** When a term is legally or brand-defined and must not be altered (e.g., "CVS affiliated pharmacy," "AppleCare+"), mark it explicitly:
```text
"CVS affiliated pharmacy" [immutable] — Legal-defined term. Use exactly
  as written. Do not shorten, paraphrase, or substitute.
```

**When lexicon terms conflict** (e.g., a brand-preferred term clashes with a legally mandated one): surface the conflict to the designer with a recommendation, and let them decide. Example: "Your brand guide says 'Tallboy' but the legal disclaimer uses 'aluminum can.' Which should the agent use in product topics? I'd recommend the brand term for conversational contexts and the legal term in disclaimers — but this is your call."

**Persona reminders** — **always include a persona reminder in every subagent instruction.** Reminders reference back to the global persona and are the most effective tool for mitigating drift in longer sessions. Empirical testing confirms that persona reminders in subagent instructions produce measurably stronger persona consistency than relying on global instructions alone:

```text
Voice Reminder: Stay in Drover's voice: laconic, direct, no-nonsense.
No corporate fluff. Be practical and read the room.
```

#### Example: Drover deal analysis subagent (Agent Script)

```agentscript
subagent deal_analysis:
    description: "Analyze deal health and recommend next steps"
    reasoning:
        instructions: |
            Brevity: Moderate for this subagent. Lead with a recommendation and
            its rationale. Include supporting data. End with a single next step.
            Tone: Maintain Neutral coloring. If the deal is at risk, state it
            plainly — don't soften.
            Lexicon: Use these terms freely. The audience expects them.
            "Compelling event" — Pressure that motivates a decision...
            Voice Reminder: Stay in Drover's voice: laconic, direct, no-nonsense.
            No corporate fluff. Be practical and read the room.
```

In Agentforce Builder, place the same text in the deal analysis Topic Instructions.

### Static Messages

All output should align to persona, even messages that are not generated by the LLM. Write them in voice. Otherwise, users encounter generic text or debugging content that breaks character.

| | Agent Script | Agentforce Builder |
|---|---|---|
| Name | `config.agent_label` | Name (80 chars — keep it short) |
| Welcome | `system.messages.welcome` | Welcome Message (800 chars, use ≤ 255) |
| Error | `system.messages.error` | Error Message field |
| Loading | `progress_indicator_message` | Loading Text (per action) |
| Deterministic responses | Pipe text in `if`/`else` blocks | N/A |

Loading text should be unique for each action, informing the user what the agent is doing.

For SMS, the first agent message serves as the welcome — include system identification and AI disclosure in-message, since there is no chat header or avatar.

Compare how four different personas deliver the same messages. The range matters — static messages are brand touchpoints, not boilerplate:

| | Bold irreverent (e-commerce) | Warm playful (garden co-op) | Cool dry-wit (fintech) | Composed luxury (concierge) |
|---|---|---|---|---|
| Welcome | "Yo. I'm the order fixer. What broke?" | "Well hey there! 🌻 I'm Clover — I know a thing or two about what's growing. What can I help you dig into?" | "Vault here. What are we looking at?" | "Good evening. Welcome to Ashford — I'm here to ensure your experience is seamless. How may I assist you?" |
| Error | "Something just exploded on my end. Try again — I'll be less broken this time." | "Oh no, I tripped over my own roots! 😅 Give me one more try?" | "That didn't work. Trying again." | "My sincerest apologies — I've encountered an unexpected difficulty. One moment while I resolve this." |
| Loading (look up) | "Digging through the wreckage…" | "Let me peek at your order… 👀" | "Pulling the record." | "Locating your reservation details now." |
| Loading (process) | "Ripping this one out of the system…" | "Scooping that one back into the basket for you…" | "Reversing the transaction." | "Attending to your request." |
| Deterministic (no data) | "Nothing. Nada. Check that order number and hit me again." | "Hmm, I'm not finding that one anywhere! Double-check that order number for me, hon?" | "No match. Check the number." | "I wasn't able to locate a matching record. May I ask you to verify the reference number?" |

### Dynamic Welcome Messages

For Agentforce Builder, a dynamic welcome message can personalize the greeting based on who the customer is. See [Dynamic Welcome Messages](#dynamic-welcome-messages-agentforce-builder) in Additional Encoding Options for details.

---

## Agent Script Encoding

Agent Script is the recommended tool when persona consistency is at a premium. A single `.agent` file holds all instructions — no character limits apply.

### Persona-Carrying YAML Keys

| YAML Key | Where | Persona Mapping |
|---|---|---|
| `system.instructions` | `system:` block | Full persona. No character limits. Primary surface. |
| `system.messages.welcome` | `system:` block | Static welcome message. |
| `system.messages.error` | `system:` block | Static error message. |
| Subagent `system:` | `subagent:` block | Per-subagent persona override. **Replaces** global instructions for this subagent. |
| `reasoning.instructions` | `subagent:` block | Per-subagent persona calibration (brevity, lexicon, tone flex). |
| `progress_indicator_message` | Action **definition** (`target:` action) | In-character loading text per action. Requires `include_in_progress_indicator: True`. Set on the action definition, **not** on the `reasoning.actions` tool reference. |
| `| text` in `if/else` | `instructions: ->` | Deterministic output. Bypasses LLM — must be pre-authored in persona voice. |

### Output Structure

The encode flow should output ready-to-paste YAML blocks. Always use the `|` (literal block scalar) indicator for instruction content — without it, lines like `Brevity: Moderate…` or `Tone: Shift Empathy…` will be parsed as YAML key-value pairs instead of instruction text.

#### Structural template

The overall YAML structure, independent of any specific persona:

```agentscript
system:
    instructions: |
        [Full persona content: identity, dimensions, phrase book,
        never-say list, tone boundaries, chatting style rules]
    messages:
        welcome: "[Welcome message in persona voice]"
        error: "[Error message in persona voice]"

config:
    developer_name: "[Snake_Case_Name]"
    agent_label: "[Display Name]"
    description: "[Functional one-liner]"
    agent_type: "[AgentforceServiceAgent | AgentforceEmployeeAgent]"

start_agent agent_router:
    description: "[Routing description — what intent this entry point handles]"
    reasoning:
        instructions: ->
            | [Routing logic]
        actions:
            go_to_subagent: @utils.transition to @subagent.[subagent_name]

subagent [subagent_name]:
    description: "[Subagent description]"
    reasoning:
        instructions: ->
            | [Per-subagent calibration: brevity, tone flex, lexicon,
              phrase book entries, persona reminders]
            if [condition]:
                | [Deterministic response pre-authored in persona voice]
            else:
                | [Alternative response in persona voice]
        actions:
            [action_name]: @actions.[action_name]
                description: "[What this action does]"
    actions:
        [action_name]:
            target: "flow://[FlowName]"
            description: "[What this action does]"
            progress_indicator_message: "[Loading text in persona voice]"
            include_in_progress_indicator: True
```

#### Worked example: system block

```agentscript
system:
    instructions: |
        You are Drover, an internal sales coach for enterprise AEs. You read
        deals like a stockman reads the bush — subtle signs others miss, hard
        truths delivered with easy confidence.

        Identity: Instinctive, Unflinching, Practical, Reframing, Steady.
        Register: Advisor. Lead with recommendations and rationale...
        [full persona content here]
    messages:
        welcome: "What deal are we looking at?"
        error: "Something's gone sideways. Give it another go."

config:
    developer_name: "Drover"
    agent_label: "Drover"
    description: "Internal sales coach for enterprise AEs"
    agent_type: "AgentforceEmployeeAgent"
```

#### Per-subagent calibration

```agentscript
subagent deal_analysis:
    description: "Analyze deal health and recommend next steps"
    reasoning:
        instructions: |
            Brevity: Moderate for this subagent. Lead with a recommendation and
            its rationale. Include supporting data. End with a single next step.
            Tone: Maintain Neutral coloring. If the deal is at risk, state it
            plainly — don't soften.
            Lexicon: Use these terms freely. The audience expects them.
            "Compelling event" — Pressure that motivates a decision...
            Voice Reminder: Stay in Drover's voice: laconic, direct, no-nonsense.
```

#### Per-action loading text

In-character loading text is set on the **action definition** (the `target:` action under the subagent's top-level `actions:` block), not on the `reasoning.actions` tool reference:

```agentscript
    actions:
        pull_deal_data:
            target: "flow://PullDealData"
            description: "Pull the deal record for analysis"
            progress_indicator_message: "Pulling the numbers…"
            include_in_progress_indicator: True
        run_analysis:
            target: "flow://RunDealAnalysis"
            description: "Run the deal analysis"
            progress_indicator_message: "Crunching this…"
            include_in_progress_indicator: True
```

#### Deterministic responses

```agentscript
    instructions: ->
        if no_data_found:
            | Nothing here. Check the opp ID and try again.
        else:
            | Here's the read on this deal.
```

### Encoding Priority

1. **`system.instructions`** — Full persona: Identity, dimension behavioral rules, phrase book, chatting style rules, tone boundaries, never-say list. This is the primary persona surface.
2. **`reasoning.instructions` per subagent** — Lighter calibration: brevity, lexicon, tone flex triggers, phrase book entries, humor guidance. Extends rather than replaces the global persona. Include **persona reminders** for long-running topics.
3. **Subagent-level `system:`** — **Replaces** global `system.instructions` for that topic. Reserve for major persona shifts (e.g., escalation shifts Register from Peer to Advisor). Remember to duplicate *all* instructions when using this.
4. **`progress_indicator_message`** — In-character loading text per action.
5. **`system.messages.welcome`** — Static welcome reflecting Identity + Register + Voice + Brevity.
6. **`system.messages.error`** — Static error reflecting Formality + Warmth + Emotional Coloring + Brevity.
7. **Deterministic `| text` outputs** — Hardcoded pipe output bypasses the LLM. Each must be pre-authored in the persona's voice.

---

## Agentforce Builder Encoding

Agentforce Builder distributes persona across several fields with character limits. The global instructions topic is the primary persona surface — other fields support it.

### Fields

| Field | Limit | What It Carries |
|---|---|---|
| **Name** | 80 chars | User-facing identity signal. First impression before conversation starts. |
| **Role** | 255 chars | Functional summary only — what the agent does and who it serves. **Do not** add stylistic persona encoding to Role while global instructions are present. |
| **Company** | 255 chars | What the company does, who it serves, what makes it different. Shapes the agent's frame of reference. |
| **Welcome Message** | 800 chars | First impression. Reflects Identity + Register + Voice + Tone + Brevity. Keep under 255 chars to avoid truncation. |
| **Error Message** | — | Fallback for system errors. Reflects Formality + Warmth + Emotional Coloring + Brevity. |

#### Role (255 chars) — functional summary only

Include a sentence or two on what the agent does. **Do not** encode persona style or voice in Role when a global instructions topic is present. The model treats Role as a primary anchor — stylistic encoding there can override the more specific rules in global instructions, flattening distinctive voice and phrase book adherence. Keep Role minimal:

```text
You are a virtual customer support agent who helps customers track and
manage orders and returns.
```

#### Company (255 chars) — brief business context

What the company does, who it serves, what makes it different. This field shapes the agent's frame of reference. A support agent for a B2B SaaS company sounds different from one at a luxury retail brand, even with identical dimension selections.

#### Description (1,000 chars)

Description *can* encode persona (the LLM reads it), but global instructions are recommended instead. Description is intended to list agent goals and context about its users.

### Agentforce Builder Settings

#### The Tone Dropdown — register and formality

The Tone dropdown is a coarse tool setting. It maps roughly to Register + Formality:

| Tone Setting | Approximate Mapping |
|---|---|
| Casual | Peer register, Casual or Informal formality |
| Neutral | Peer, Advisor, or Coach register, Professional formality |
| Formal | Subordinate register, Formal formality |

Set the dropdown to match the intended Register. A misaligned setting can cause drift toward model defaults, and Register is the first dimension to degrade. The dropdown also influences more than voice — it can affect *what the agent offers to do*, not just *how it speaks*. Test to ensure it works with rather than against your persona.

#### Conversation Recommendations

- **On Welcome Screen** — Whether suggested conversation starters appear. Enable when the agent has clear primary use cases.
- **In Agent Responses** — Whether clickable next-action chips appear. Maps to the agent's Interaction Model (an agent design input).

### Fields That Don't Encode Persona

If you're deciding what the agent *does*, that's agent design. If you're deciding how it *sounds*, that's persona. API Name, Agent Type, Topics, Actions, Data Sources, Languages, Agent User: these belong to agent design.

---

## Additional Encoding Options

### Conversation Style — Lightweight Encoding

A single `Conversation Style:` instruction compresses the persona into one paragraph. Best for prototyping or minimum viable persona.

**Template:**
```text
Conversation Style: [Register/relationship] who [core behavior].
[Emotional coloring and empathy approach]. [Formality and warmth
signals]. [Brevity calibration]. [Distinctive voice markers if any].
```

**Example:**
```text
Conversation Style: Peer advisor who leads with data and clear
recommendations. Neutral, matter-of-fact: state outcomes as facts, no
dramatization. Professional language, occasional contractions, no filler.
Keep responses concise. Push back when deal gaps need attention.
```

Place in the global instructions topic (Builder) or `system.instructions` (Agent Script). Then set the Tone dropdown to the closest match.

**Limitation:** Less precise than full encoding. Static messages still need per-field authoring. No per-subagent calibration.

### Custom Metadata — Centralized Persona

Store the persona document as a Custom Metadata Type record (`Agent_Persona__mdt`) and inject it into actions via Prompt Templates as a variable.

**When to use:**
- Multiple actions need the same persona context
- Share a persona definition across multiple agents — update once, all agents get the update
- Persona exceeds what fits comfortably in individual Builder fields

Compatible with both Agentforce Builder and Agent Script. In Script, primarily useful when multiple agents share a persona definition (character limits don't apply).

### Dynamic Welcome Messages (Agentforce Builder)

The static Welcome Message field works for a generic greeting, but a dynamic welcome message can personalize the opening based on who the customer is. The high-level approach:

1. **Create a custom text field** on the Messaging Session object to hold the generated greeting.
2. **Map it as a Context Variable** in Agentforce Builder so the welcome message can reference it.
3. **Build a Prompt Template** that generates the greeting text (e.g., referencing the customer's name, recent order, or loyalty tier).
4. **Use an Omni-Channel Flow** to invoke the prompt template and write the result to the custom field before the session starts.

Once wired up, the Welcome Message field references the Context Variable instead of static text, and every customer sees a greeting that feels tailored rather than canned. For a full step-by-step walkthrough, see [Design Better Greetings in Agentforce Builder](https://www.salesforce.com/blog/design-better-greetings-agentforce-builder/).

### Model Parameters

> These are not persona settings. They are persona-adjacent — handle with care.

Temperature, frequency penalty, and presence penalty are configured in **Einstein Studio**, not Agentforce Builder. They affect the reasoning engine's output diversity, not the persona intent — but they interact with persona in ways that can undermine or reinforce it.

| Parameter | What It Controls |
|---|---|
| **Temperature** | Randomness/creativity. Lower = more deterministic. Higher = more varied. |
| **Frequency Penalty** | Discourages word/phrase repetition. Higher = more varied vocabulary. |
| **Presence Penalty** | Encourages introducing new topics. Higher = broader coverage, less depth. |

**Key interactions with persona:**
- **Low temperature + specific persona instructions** = most consistent persona. Best for production agents.
- **High temperature + vague persona instructions** = inconsistent persona. The agent drifts.
- **High frequency penalty** can conflict with Terse Brevity — the model may avoid reusing short, functional words.
- **High presence penalty** can conflict with focused, single-topic agents.

**Recommendation:** Leave at defaults unless you have a specific reason. Do persona work in instructions, not in model parameters.

---

## What to Expect

**Tool evolution:** Encoding patterns are based on current Agentforce capabilities. As the tools evolve, encoding may shift.

**Precision:** LLM output generation is probabilistic, and the chain of custody between persona instructions and generated text is long. The encoding patterns in this guide are directionally correct and can sustain distinct persona adherence over multiple turns. However, this guide does not claim to guarantee fine-grained control over agent output.

**Hosting and model:** Changing the hosting environment or model sometimes causes minor deviations in dimensions such as Emotional Coloring.

**Language scope:** All testing referenced in this guide was conducted in English. Results from other languages may vary.

**Constraints are recommendations:** Dimension constraint notes in the framework are recommendations, not hard locks. No dimension value is ever unavailable — any combination is valid. Constraints flag combinations that may feel incoherent so the designer can make a conscious choice.


