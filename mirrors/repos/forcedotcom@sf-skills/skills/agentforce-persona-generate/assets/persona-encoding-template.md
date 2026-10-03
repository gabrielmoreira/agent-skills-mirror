---
version: "3.0.0"
date: 2026-05-15
---

# [Agent Name] — Persona Encoding

**Agent Authoring Tool:** [Agent Script (default) / Agentforce Builder]
**Mode:** [Greenfield (starter skeleton) / Brownfield (re-encoding existing .agent file)]
**Channel:** [web chat / mobile chat / SMS / email / telephony / multimodal-with-audio / embedded / other]
**Date:** [date]
**Source persona:** [agent-name]-persona.md
**Source .agent file (brownfield only):** [path]

---

## Agent Script Encoding (.agent file)

*Include this section when tool = Agent Script. Output must be valid Agent Script syntax per the schema in `forcedotcom/sf-skills/skills/developing-agentforce/`.*

### Greenfield: Starter `.agent` Skeleton

For new agents, the encoding output is a minimal valid `.agent` file. Subagents, actions, variables, and routing are placeholders for the user to flesh out — the skill never invents structure.

```agentscript
system:
    instructions: |
        [Full persona content as a literal block: Identity Traits, Negative Identity,
        Personification, all 13 dimensions with behavioral rules, Phrase Book,
        Tone Boundaries, Tone Flex rules, Never-Say List, Lexicon (global), Guardrails
        (if any), Immutable content with "use exactly as written" directive.]
    messages:
        welcome: "[Static welcome in persona voice]"
        error: "[Static error in persona voice]"

config:
    developer_name: "[snake_case_name]"            # API identifier; matches directory name
    agent_label: "[Display Name]"                   # User-facing display name (from NAME spoke)
    description: "[Functional one-liner — what the agent does]"
    agent_type: "[AgentforceServiceAgent | AgentforceEmployeeAgent]"
    default_agent_user: "[username]"                # Required only for ServiceAgent

language:
    default_locale: "en_US"                         # BCP 47

start_agent entry:
    description: "[Routing description — what intent this entry point handles]"
    reasoning:
        instructions: |
            [Routing logic — placeholder for the user to implement]

subagent main:
    description: "[Placeholder — replace with actual subagent purpose]"
    reasoning:
        instructions: |
            [Placeholder — the persona's global instructions are inherited from
            system.instructions. Per-subagent calibration goes here when the user
            adds real subagents.]
```

**Formatting rules** (per developing-agentforce):
- 4-space indentation, never tabs
- Strings double-quoted
- Booleans `True` / `False` capitalized
- Identifiers `[a-zA-Z][a-zA-Z0-9_]*`, max 80 chars

### Brownfield: Re-Encoding Existing `.agent`

For brownfield mode, the encoding output is a **proposed-new-file** with annotated changes — only persona-bearing fields are modified. Routing, subagent structure, action contracts, and variables stay exactly as the source had them.

The persona-bearing fields the skill modifies:
- `system.instructions`
- `system.messages.welcome`
- `system.messages.error`
- Each subagent's `system:` override (if used) — only when tone flex warrants
- Each subagent's `reasoning.instructions:` (the persona-relevant portion)
- Each action's `progress_indicator_message:`

A companion diff summary at `persona/[agent-name]/persona-diff.md` lists what changed and why, scoped to persona only.

### Per-Subagent Calibration *(optional, only when subagents are declared)*

```agentscript
subagent [subagent_name]:
    description: "[subagent purpose]"
    system:                                         # Optional override; reserve for major persona shifts
        instructions: |
            [Full alternate system block — replaces global for this subagent]
    reasoning:
        instructions: |
            Persona reminder: [one-line recall of global identity/persona]
            Brevity: [calibration for this subagent]
            Tone flex: [Emotional Coloring + Empathy shifts for this subagent context]
            Lexicon: [subagent-specific terms with brief definitions]
            Phrase book: [situational phrases relevant to this subagent]
            Humor: [guidance for this subagent — often "drop to None for escalation"]
```

*Repeat per subagent that needs persona calibration.*

### Per-Action Loading Text *(optional, only when actions exist + voice channel)*

Set on the **action definition** (the `target:` action under the subagent's top-level `actions:` block), not on the `reasoning.actions` tool reference:

```agentscript
    actions:
        [action_name]:
            target: "flow://[FlowName]"
            description: "[What this action does]"
            progress_indicator_message: "[In-character loading text]"
            include_in_progress_indicator: True
```

*Repeat per action that needs in-character loading text. The progress message is most impactful in voice channels (telephony, multimodal-with-audio).*

### Dynamic Welcome Message *(optional)*

*If the user opts for a dynamic welcome supplementing the static one. See [Salesforce greeting design guide](https://www.salesforce.com/blog/design-better-greetings-agentforce-builder/).*

```agentscript
# Dynamic welcome encoded as logic in start_agent.reasoning.instructions
# (time-of-day, returning user, context-aware opening)
```

---

## Agentforce Builder Encoding

*Include this section when tool = Agentforce Builder.*

### Agent Configuration Fields

| Field | Limit | Value | Chars |
|---|---|---|---|
| **Name** | 80 | [agent name] | [count] |
| **Role** | 255 | [functional summary — what the agent does, who it serves. No persona style.] | [count] |
| **Company** | 255 | [company context] | [count] |
| **Welcome Message** | 800 (aim ≤ 255) | [welcome in persona voice] | [count] |
| **Error Message** | — | [error in persona voice] | — |

### Agentforce Builder Settings

| Setting | Recommendation | Rationale |
|---|---|---|
| **Tone** | [Casual / Neutral / Formal] | [mapping to Register + Formality] |
| **Conversation Recs on Welcome** | [On / Off] | [rationale] |
| **Conversation Recs in Responses** | [On / Off] | [rationale] |

### Global Persona Block

*For a dedicated global instructions topic.*

```text
[Full persona content: identity, dimensions, phrase book, tone
boundaries (including profanity boundary if set), never-say list,
chatting style rules. This is the primary encoding surface in Builder.]
```

### Immutable Terms *(include when applicable)*

*Brand-defined and legal/compliance terms that must be preserved exactly as written in all agent output.*

| Term | Type | Usage |
|---|---|---|
| [term] | [brand / legal] | [usage rule — e.g., "Always use this exact term for the loyalty program"] |
| [term] | [brand / legal] | [usage rule] |

*Encode in global instructions with explicit "use exactly as written" directive. If a term appears in both brand and legal contexts with different wording, the resolution chosen during design is noted here.*

### Per-Topic Persona Instructions (Agentforce Builder)

*Builder UI still labels these "Topics" even though Agent Script renamed the concept to "Subagent." When used here, "Topic" refers to the Builder field; the same concept maps to a `subagent` block in Agent Script.*

*Include when topics are provided.*

**[Topic Name]:**
```text
Persona reminder: [one-line recall of global identity/persona]
Brevity: [calibration for this topic]
Tone: [tone flex encoding for this topic context]
Lexicon: [domain terms and usage notes for this topic]
Phrase book: [situational phrases relevant to this topic]
Humor: [guidance — e.g., "drop to None for escalation"]
```

*Repeat for each topic.*

### Loading Text

| Action | Loading Text |
|---|---|
| [action name] | [in-character loading text] |
| [action name] | [in-character loading text] |
| Generic (fallback) | [in-character loading text] |

---

## Voice Encoding

*Include this section when modality includes telephony/voice.*

### Voice Selection

**Selection criteria:**

| Criteria | Target | Persona Rationale |
|---|---|---|
| **Language** | [primary language] | [why] |
| **Gender** | [inferred or specified] | [source — name, pronouns, or user input] |
| **Voice Qualities** | [what to look for — e.g., warm, professional, measured pace] | [which persona dimensions drive this] |

**Recommended voices** (from default library — verify in your org, listen to previews):

| Voice | Gender | Accent | Style | Why |
|---|---|---|---|---|
| [name] | [m/f] | [accent] | [style] | [persona match reasoning] |
| [name] | [m/f] | [accent] | [style] | [persona match reasoning] |
| [name] | [m/f] | [accent] | [style] | [persona match reasoning] |

**Fine-tuning starting points** (experiment in voice preview — these are starting points, not prescriptions):

| Parameter | Starting Point | Why |
|---|---|---|
| **Speed** | [value] | [e.g., "Concise brevity + hospitality warmth → moderate pace, not rushed"] |
| **Stability** | [value] | [e.g., "Encouraging coloring needs expressiveness → lower stability"] |
| **Similarity** | [value] | [e.g., "Default — no reason to deviate from base voice"] |

### Key-Term Prompting

| Term |
|---|
| [brand name] |
| [product name] |
| [domain term] |

### Pronunciation Dictionary *(optional)*

| Word | Pronunciation (IPA) | Verified? |
|---|---|---|
| [term] | [approximate IPA] | Verify in voice preview |

### Voice Welcome Message

```text
[Shorter than text welcome. Includes AI disclosure. In persona voice.]
```

### Voice Instruction Adjustments

- Brevity: [text default] → [voice adjustment, one position shorter]
- Formatting: suppressed (no emoji, bullets → ordinals)
- [Any pausing guidance for structured data]
