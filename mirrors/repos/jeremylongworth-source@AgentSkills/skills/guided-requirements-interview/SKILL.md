---
name: guided-requirements-interview
description: Facilitate "grill me" style guided discovery interviews that ask the user focused questions, progressively elicit missing requirements, and build an aligned draft artifact such as a BRD, PRD, feature spec, implementation brief, decision memo, or project plan. Use when Codex should interview the user, clarify ambiguous goals, gather stakeholder context, fill requirement gaps, keep the user aligned during planning, or turn partial ideas into structured requirements through an interactive question flow.
license: MIT
---

# Guided Requirements Interview

## Core Workflow

1. Identify the target artifact: BRD, PRD, feature spec, implementation brief,
   decision memo, project plan, research plan, or another structured output.
2. Start with a compact working draft from what is already known.
3. Ask one to three focused questions at a time, ordered by decision value:
   outcome, users/stakeholders, scope, current state, future state, constraints,
   success metrics, risks, approvals, and handoff needs.
4. After each answer, update the working draft silently or with a short delta
   summary when alignment matters.
5. Separate confirmed facts, assumptions, options, open questions, and decisions
   still needed.
6. Stop questioning when the next question would not materially improve the
   artifact, then provide the completed draft plus remaining gaps.

## Interview Style

- Be direct, specific, and low-friction. Prefer practical questions over generic
  discovery prompts.
- Keep the user aligned by showing short checkpoints: what is known, what was
  decided, what remains uncertain, and what the next question will unlock.
- Use progressive disclosure. Ask broad framing questions first, then drill into
  details only when the answer changes requirements, scope, acceptance criteria,
  risk, or approval needs.
- Avoid interrogating the user with a long questionnaire. If many gaps exist,
  group them into short rounds and explain the purpose of each round.
- Offer reasonable defaults when the user is unsure, but label them as defaults
  or assumptions.
- Preserve user language for goals, pain points, and stakeholder concerns when
  it may affect alignment.

## Question Ladder

Use the smallest useful subset:

1. Outcome: What business or user outcome should this create?
2. Audience: Who is affected, who decides, and who approves?
3. Problem: What is broken, costly, slow, risky, unclear, or missing today?
4. Scope: What must be included, excluded, or deferred?
5. Current state: How does the workflow, system, or decision happen now?
6. Future state: What should be different when this is successful?
7. Requirements: What must be true for the result to work?
8. Constraints: What limits budget, timing, tools, data, policy, compliance, or
   staffing?
9. Success: How will success be measured or accepted?
10. Risks: What could fail, be misunderstood, or create rework?
11. Handoff: Who needs the artifact next, and what decision should it support?

## Safety Rules

- Do not pressure the user into decisions. Mark unresolved items as open.
- Do not invent approvals, budgets, legal/compliance status, customer promises,
  deadlines, or technical feasibility.
- Do not keep asking questions after enough information exists for a useful
  draft; finish with assumptions and gaps instead.
- Escalate when answers imply privacy, security, legal, finance, accessibility,
  regulated-domain, or customer-commitment risk.

## Deliverable Shape

For guided interview work, provide:

- Current working draft or final artifact
- Confirmed facts
- Assumptions and defaults used
- Decisions made during the interview
- Open questions and owners if known
- Requirement or acceptance-criteria gaps
- Recommended next round of questions only if it materially improves the result

## References

- Read `references/guided-interview-checklist.md` before running a long or
  high-stakes discovery interview.
