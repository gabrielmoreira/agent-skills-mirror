---
name: frontdesk-intake
description: Convert user conversation into macro workflow requests and present curated clarification or final artifacts.
---

# Frontdesk Intake

Use this skill for user-facing workflow intake and reporting.

## Inputs

- user request
- current macro decisions
- broker question artifact
- final or escalation artifact

## Outputs

- macro task request for planner
- concise user clarification display
- final summary or escalation report

## Rules

- Do not perform implementation.
- Do not manage runtime capacity.
- Do not show raw noisy execution logs unless escalation requires evidence.
- Preserve user decisions as macro constraints for planner.
