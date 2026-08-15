---
name: discover-journey-map
description: "Produces a research-grounded customer journey map: stages, touchpoints, emotional curve, pain points, moments of truth, and opportunity annotations, optionally as mermaid. Use when synthesizing a linear or cyclical journey for a named persona and goal. Not for inventing emotions without labeling them hypothetical; do not use as a substitute for interview synthesis or a service blueprint."
version: 1.0.1
---

## Overview
A journey map is a synthesis artifact, not a brainstorm. Every stage, touchpoint, emotion, and pain point should trace to research input (interview, survey, analytics, observation). Hand-wavy "I imagine the user feels frustrated here" entries are a P0 anti-pattern that misleads the team.

If the user provides research signal, ground the map in that signal. If they provide hypotheses, label entries as hypothetical and recommend validation research.

## When to Use
- Use when you need to produce a customer journey map covering stages, touchpoints, emotional curve, pain points, moments of truth, and opportunity annotations.
- Output is a markdown artifact that may include mermaid timeline / flowchart visualization.
- Supports both linear journey (start to end) and cyclical journey (recurring engagement).
- Composes with `utility-mermaid-diagrams` for visual output.

## Prerequisites
**Required inputs:**
- Persona or customer segment (who the journey is FOR)
- Goal / outcome (what the customer is trying to accomplish)
- Scope: end-to-end (full lifecycle) OR focused (a specific phase like onboarding, checkout, renewal, support)

**Optional but improves quality:**
- Research data: interview synthesis, survey results, customer support tickets, analytics
- Existing journey map to revise or extend
- Specific stages or touchpoints the user wants to ensure are covered
- Linear vs. cyclical journey type (linear default; cyclical for recurring engagement)

## Procedure

1. **Load references:** Read `~\agent-skills\library\discover-journey-map\references\TEMPLATE.md` to structure the output. Read `~\agent-skills\library\discover-journey-map\references\EXAMPLE.md` if you need a complete worked example.
2. **Validate inputs:** Ensure persona, goal, and scope are provided. If missing, execute the refusal protocol (see Pitfalls).
3. **Executive summary:** Produce a 3-5 sentence summary of who the journey is FOR, what they're trying to accomplish, where the biggest pain points and opportunities are, and the most important moment of truth.
4. **Persona / segment:** Write a 1-paragraph summary of the customer. Reference an existing persona if one exists (`foundation-persona`); summarize key attributes if not.
5. **Journey scope:** State explicitly what is included and what is excluded.
6. **Stages:** Define 3-7 named stages. Use customer-language verb forms ("Discovers", "Considers", "Tries", "Decides", "Uses", "Renews"). For each stage, include:
   - Customer goal at this stage
   - Duration estimate (minutes, days, weeks)
   - Trigger that moves them into this stage
   - Exit criterion that moves them out
7. **Touchpoints:** For each stage, list the touchpoints in a table:

   | Stage | Touchpoint | Channel | What happens |
   |---|---|---|---|
   | Discovers | Search result | Search engine | Sees competitor option |
   | Discovers | Landing page | Web | Lands on product page |

8. **Emotional curve:** For each stage, identify what the customer feels using specific emotional labels (frustration, hope, surprise, anxiety, satisfaction) NOT generic ones (happy / sad). Format as a table:

   | Stage | Dominant emotion | Confidence (high / medium / low based on research evidence) | Source |
   |---|---|---|---|
   | Discovers | Curiosity, mild skepticism | Medium | 12 user interviews; 3 mentioned skepticism explicitly |

   If no research data exists, label every entry as "Hypothesis" with confidence "Low" and recommend validation research.

9. **Pain points and moments of truth:** Identify pain points (friction, confusion, blockers) and moments of truth (critical moments where customer perception is formed, limited to 3-5 that determine continue-vs-abandon). Format as a table:

   | Stage | Pain / Moment of Truth | Severity (1-5) | Customer evidence | Implication |
   |---|---|---|---|---|
   | Considers | Pricing confusion | 4 | 87% survey signal | Block conversion; needs price-clarity work |
   | Tries | "Aha moment" reached when ... | Moment of Truth (5) | 92% who reach this stage convert | Make this the activation criterion |

10. **Opportunities:** Annotate 1-3 opportunities per stage where the product can intervene to reduce pain or amplify a moment of truth. Format as a table:

    | Stage | Opportunity | What product change addresses it | Effort estimate (rough) |
    |---|---|---|---|
    | Considers | Reduce pricing confusion | Add comparison table on landing page | Small |

11. **Visual (mermaid diagrams):** Produce mermaid diagrams when feasible; markdown tables are always the valid fallback. Use `utility-mermaid-diagrams` for rendering guidance.
    - **Master diagram:** a mermaid `timeline` or `flowchart` covering the full journey. Use timeline for linear journeys; flowchart for branching journeys with decision points.
    - **Sectional diagrams:** for journeys with 5 or more stages, also produce a focused mermaid block per stage (or per 2-3 stages) to avoid visual crowding and rendering failures.
    - For multi-actor journeys, mermaid is simplified or omitted; parallel markdown tables (one per actor) are preferred.

    Example master diagram:
    ```mermaid
    timeline
     title Customer Journey
     Discovers : Sees ad : Lands on website
     Considers : Reads pricing : Watches demo
     Tries : Signs up : Onboarding
     Decides : Upgrades or churns
    ```

12. **Research gaps:** Explicitly state what the map is NOT addressing because data is unavailable, and what follow-up research would close the most important gaps.

## Pitfalls

- **No persona or scope:** Refuse to produce a journey map. "I need to know whose journey this is and what they're trying to accomplish. Provide a persona (or persona summary) and the goal."
- **Fabricate emotional data without research:** If user asks "what does the customer feel here?" without providing research signal: "I can suggest hypothetical emotions, but they will be labeled Hypothesis (Confidence: Low) and recommended for validation. Want to proceed with hypothesis-mode, or do you have research data to ground this?"
- **Service blueprint or architecture diagram request:** This skill covers user-experience artifacts only. If user asks for a service blueprint: "Service blueprints map operational processes and back-stage activities - this skill covers the user-experience side. For a service blueprint, use a diagramming tool directly. Want to continue with a user journey map instead?"
- **Excessive scope:** End-to-end journey for a long-lifecycle product (e.g., 5 years of B2B SaaS engagement) is too coarse. Refuse: "End-to-end over 5 years is too coarse. Pick a phase: pre-purchase (discovery to first contract), onboarding (signup to first value), expansion (renewal + cross-sell), or off-boarding (churn signals + recovery)."
- **Single touchpoint as the whole journey:** If user provides only one touchpoint (e.g., "checkout"): "A single touchpoint isn't a journey. Either expand to the surrounding stages (e.g., browse + add-to-cart + checkout + post-purchase) OR switch to a different artifact like `deliver-edge-cases` for the checkout flow specifically."
- **Multi-actor complexity:** Multi-actor journeys are advanced and complex to maintain. Use parallel markdown tables (one per actor) with shared touchpoints annotated; include a complexity warning noting that multi-actor journeys are harder to validate and research depth should prioritize the primary actor.

## Verification

Before finalizing, verify the following checklist:
- [ ] Persona and scope are stated explicitly.
- [ ] 3-7 named stages, each with goal, duration, trigger, exit criterion.
- [ ] Every emotional-curve entry carries a confidence label and a source (or is marked Hypothesis).
- [ ] Moments of truth are limited to the 3-5 that decide continue-vs-abandon, not every interaction.
- [ ] Each opportunity ties to a specific pain point or moment of truth.
- [ ] Mermaid diagram is present when feasible, with markdown tables as fallback.
- [ ] Research gaps are stated explicitly.

## Related skills
- **Inputs:** `foundation-persona` (the WHO), `discover-interview-synthesis` (qualitative signal), `measure-survey-analysis` (quantitative signal)
- **Outputs feed into:** `define-problem-statement`, `define-hypothesis`, `define-opportunity-tree`
- **Visualization:** `utility-mermaid-diagrams` (timeline or flowchart)
- **Adversarial review:** `/pm-critic` (challenges where emotions and moments of truth lack research evidence)
- **Companion command:** `commands/journey-map.md`
