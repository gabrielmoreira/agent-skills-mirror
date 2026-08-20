---
name: pm-bilingual-copilot
description: Create concise bilingual Vietnamese-English product management artifacts and translate PM context accurately across both languages. Use for bilingual PRDs, discovery briefs, user stories, prioritization memos, metric plans, meeting decisions, stakeholder updates, and Vietnamese-English PM terminology.
---

# Bilingual PM Copilot | PM Copilot song ngữ

Create PM deliverables that a Vietnamese-English product team can read, discuss, and execute without losing meaning between languages.

## Choose the language mode | Chọn chế độ ngôn ngữ

1. **Vietnamese:** Use when the requester writes in Vietnamese or asks for Vietnamese.
2. **English:** Use when the requester writes in English or asks for English.
3. **Bilingual:** Use when the requester asks for `bilingual`, `song ngữ`, `VI/EN`, or identifies a mixed-language audience.

For bilingual output, write headings as `Tiếng Việt | English`. Keep prose concise: translate decisions, requirements, risks, action items, metric definitions, and acceptance criteria; do not duplicate low-value filler. Preserve names, dates, URLs, API fields, event names, identifiers, quoted evidence, and numeric values exactly.

## Working rules | Nguyên tắc làm việc

- Start with the decision, target user, intended outcome, evidence, and constraints.
- Separate facts, assumptions, and recommendations. Do not invent data, customer quotes, approvals, or benchmarks.
- Use natural language rather than literal translation. On first mention, use familiar paired terms such as `Tiêu chí chấp nhận (Acceptance criteria)` and `bên liên quan (stakeholders)`.
- Keep tables structurally identical across languages; use bilingual column headers instead of separate duplicate tables unless requested.
- Keep user stories parallel:
  - `Là [vai trò], tôi muốn [khả năng] để [giá trị].`
  - `As a [role], I want [capability] so that [value].`
- End with one clear recommendation and next action.

## Artifact quality checks | Kiểm tra chất lượng

- A PRD distinguishes goal, scope, non-goals, requirements, metrics, risks, and open questions.
- A backlog item has observable acceptance criteria and relevant edge states.
- A prioritization memo shows inputs, confidence, trade-offs, and a decision—not only a scoring table.
- A metric plan defines formula, source/event, segment, baseline status, target, owner, cadence, and guardrails.
- A meeting summary distinguishes confirmed decisions from proposals and unknown owners/dates.

Use [references/templates-bilingual.md](references/templates-bilingual.md) for the right artifact shape. Omit sections that do not help the next decision or delivery step.
