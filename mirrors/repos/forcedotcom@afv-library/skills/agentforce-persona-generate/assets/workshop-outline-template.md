---
version: "1.0.0"
date: 2026-05-15
---

# Persona Design Workshop — {{AGENT_NAME or "[Agent Name]"}}

> Date: {{DATE}}
> Generated from: `{{agent-name}}-persona.md`
> Audience: customer's internal stakeholders (Brand, Legal, Experience, Subject-matter)
> Format: ~30-45 minutes, async-friendly (questions can be answered in writing)

---

## Background (for the facilitator)

{{ONE_PARAGRAPH_BACKGROUND}}

A short paragraph (≤4 sentences) summarizing where the persona stands today — what's been drafted, what's been validated by signal, what's open. The goal of this workshop is to surface stakeholder input on the open items, not to walk through everything. Stakeholder time is the scarce resource.

---

## Activity 1 — Identity calibration

*~10 min. Validate the agent's character at the highest-leverage level.*

{{N}} questions. Each is open-ended and asks stakeholders to confirm, push back, or pick.

- **Q1.** {{QUESTION_1}}
  - Style: {{validate | choose-between | open-spectrum}}
  - Dimension(s): {{Identity, Personification, ...}}

- **Q2.** {{QUESTION_2}}
  - Style: ...
  - Dimension(s): ...

- *(more if needed; aim for 2-3 in this activity)*

---

## Activity 2 — Tone in difficult moments

*~10-15 min. Surface tradeoffs the persona will face under pressure. Would-you-rather format.*

For each pair, stakeholders pick A or B. The two options must be **meaningfully different** with different consequences.

- **Pair 1.** Scenario: {{SCENARIO_FROM_SEED — e.g., "A customer expresses frustration"}}
  - **A:** {{Response option A in the persona's voice}}
  - **B:** {{Response option B — meaningfully different}}
  - What's at stake: {{one-line consequence framing}}

- **Pair 2.** Scenario: {{SCENARIO}}
  - **A:** ...
  - **B:** ...
  - What's at stake: ...

- *(2-4 pairs total; pick scenarios from `references/workshop-scenario-seeds.md` that align with the agent's use cases and the dimensions where stakeholder input is wanted)*

---

## Activity 3 — Spectrum check

*~10 min. For dimensions where the brand input is silent or where stakeholder convergence is needed.*

These are dimension cards — printable / FigJam-able. Stakeholders place a dot or sticky on the spectrum.

- **{{DIMENSION_NAME}}** — *{{one-line definition from framework}}*
  ```text
  {{POSITION_1}}  ⟷  {{POSITION_2}}  ⟷  {{POSITION_3}}  ⟷  {{POSITION_4}}
  ```
  *Place the agent here.*

- **{{DIMENSION_NAME}}** — *{{one-line definition from framework}}*
  ```text
  {{POSITION_1}}  ⟷  {{POSITION_2}}  ⟷  {{POSITION_3}}
  ```
  *Place the agent here.*

- *(only include dimensions where confidence is low or stakeholder input is genuinely useful — don't ask the spectrum question for dimensions where the brand input already gave a strong answer)*

---

## Pre-read materials

- **Persona draft:** [{{agent-name}}-persona.md]({{agent-name}}-persona.md)
- **Sample dialog:** [{{agent-name}}-sample-dialog.md]({{agent-name}}-sample-dialog.md)
- **Brand guide:** {{LINK if provided}}

Stakeholders should read these before the workshop. The activities assume familiarity.

---

## After the workshop

Bring stakeholder answers back to the skill. Run AUGMENT (FILL OUT spoke) or re-run DRAFT to incorporate the answers, then re-run SCORE to see how the persona moved.

If a key dimension answer surfaced a contradiction with what the skill drafted, expect SCORE's Conflict-Pair check to flag it — that's a feature, not a bug. Reconcile in the next pass.
