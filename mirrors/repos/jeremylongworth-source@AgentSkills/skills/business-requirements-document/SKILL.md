---
name: business-requirements-document
description: Create, review, and refine Business Requirements Documents (BRDs), business requirements, stakeholder requirements, scope statements, current/future-state workflows, business rules, assumptions, constraints, success criteria, traceability, and approval-ready requirement packages. Use when Codex is asked to write a BRD, gather business requirements, convert discovery notes into business requirements, review requirement completeness, align stakeholders, or prepare business-analysis documentation before solution design.
license: MIT
---

# Business Requirements Document

## Core Workflow

1. Identify the business problem, decision context, sponsor, stakeholders,
   affected teams, customers, systems, process boundaries, and target outcome.
2. Separate business objectives, stakeholder needs, business requirements,
   solution requirements, assumptions, constraints, risks, and open questions.
3. Capture current state, future state, process impacts, business rules, data
   needs, reporting needs, compliance concerns, and operational handoffs.
4. Define measurable success criteria and acceptance signals before discussing
   implementation options.
5. Create traceability from objective to requirement to acceptance criteria,
   owner, evidence source, priority, and validation method.
6. Flag conflicting requirements, missing decision owners, weak evidence,
   unresolved dependencies, and approval gates before handoff.

## BRD Principles

- Keep the BRD business-facing. Describe what the business needs and why before
  proposing how a product, system, vendor, or team should implement it.
- Use clear requirement language: must, should, may, will not.
- Prefer numbered requirements when traceability, signoff, testing, or vendor
  comparison matters.
- Separate in-scope, out-of-scope, and future-consideration items.
- State assumptions as assumptions, not decisions or evidence.
- Convert vague goals into observable business outcomes, metrics, or review
  criteria.
- Include human approval points when requirements affect budget, contracts,
  staffing, customer commitments, compliance, billing, privacy, or operations.

## Safety Rules

- Do not invent stakeholder approval, budget authority, legal obligations,
  compliance status, vendor commitments, or production readiness.
- Do not turn business requirements into technical architecture unless the user
  asks for a solution design or implementation plan.
- Escalate when requirements conflict with policy, legal/compliance, privacy,
  accessibility, security, finance, or contractual commitments.
- Mark missing source material and unresolved decisions explicitly.

## Deliverable Shape

For BRD work, provide:

- Executive summary
- Business background and problem statement
- Goals, non-goals, and success metrics
- Stakeholders, owners, and approval needs
- Scope, out of scope, assumptions, and constraints
- Current state and future state
- Business requirements
- Business rules and process impacts
- Data, reporting, integration, and operational needs
- Risks, dependencies, and open questions
- Acceptance criteria or success validation
- Requirement traceability table
- Signoff or review checklist

## References

- Read `references/brd-checklist.md` when writing or reviewing a BRD.
- Read `references/brd-template.md` when the user needs a structured BRD draft.
