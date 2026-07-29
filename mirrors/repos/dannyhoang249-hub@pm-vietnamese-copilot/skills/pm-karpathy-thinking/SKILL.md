---
name: pm-karpathy-thinking
description: Stress-test a product decision, PRD, roadmap, experiment, or feature proposal using explicit assumptions, simplicity-first scope, surgical changes, and measurable verification loops. Use when product work is ambiguous, over-scoped, solution-led, risky, or needs a clear go/no-go recommendation.
---

# Karpathy-inspired PM Thinking | Tư duy Karpathy cho PM

Apply four behavior principles—adapted from [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)—to product decisions. Do not copy software implementation guidance into a PM artifact; use the principles to improve decision quality.

## Language | Ngôn ngữ

Match the requester’s language. For a bilingual audience or an explicit `VI/EN` request, use paired Vietnamese-English headings. Translate decisions, assumptions, success criteria, risks, and action items; preserve names, dates, evidence, metrics, URLs, event names, and identifiers exactly.

## Four principles | Bốn nguyên tắc

### 1. Think before acting | Nghĩ trước khi làm

- State facts, assumptions, unknowns, and decision constraints separately.
- Surface material alternative interpretations rather than silently selecting one.
- Name the trade-off and push back if the requested solution does not address the stated problem.
- Ask only questions that would change the recommendation; otherwise proceed with labeled assumptions.

### 2. Simplicity first | Đơn giản trước

- Recommend the smallest viable scope, experiment, analysis, or release that can test the outcome now.
- Do not add speculative features, segments, metrics, processes, dashboards, or future-proofing.
- Prefer an existing workflow, prototype, concierge test, or instrumented release before a large build when it can answer the decision.
- Ask: would an experienced PM call this scope overcomplicated? If yes, simplify.

### 3. Surgical scope | Phạm vi có chủ đích

- Trace every proposed requirement, task, and metric to an explicit user outcome, risk, or constraint.
- Do not turn a narrow request into a strategy reset, full roadmap, or expansive PRD.
- Flag adjacent opportunities and pre-existing issues; do not absorb them into the current commitment unless requested.
- Remove only work made unnecessary by the proposed change; preserve existing commitments unless the decision explicitly replaces them.

### 4. Goal-driven execution | Thực thi theo mục tiêu

- Translate an imperative request into an observable outcome, success criterion, guardrail, and decision rule.
- Define the smallest verification loop as `step → signal → decision`.
- Make each step independently reviewable and reversible where possible.
- End with `proceed`, `simplify then proceed`, or `validate before committing`.

## Output format | Định dạng đầu ra

```markdown
# Decision quality check — [Name] | Kiểm tra chất lượng quyết định — [Tên]

## Decision and intended outcome | Quyết định và outcome mong muốn
## Facts, assumptions, and unknowns | Sự thật, giả định và điều chưa biết
## Simpler viable path | Phương án đơn giản hơn vẫn khả thi
## Scope and trade-offs | Phạm vi và đánh đổi
## Success criteria and verification loop | Tiêu chí thành công và vòng lặp kiểm chứng
| Step / Bước | Verify with / Kiểm chứng bằng | Owner | Decision triggered / Quyết định được kích hoạt |
| --- | --- | --- | --- |

## Recommendation | Khuyến nghị
```

Use this skill as a quality gate before committing to a large feature, roadmap item, launch, experiment, or cross-functional plan.
