---
name: error-learning
description: "**WORKFLOW SKILL** — Register and generalize agent errors into reusable lessons. USE FOR: when the user corrects the agent, capturing what went wrong, analyzing root cause, generalizing the error into a lesson that prevents recurrence. Use to register errors, analyze mistakes, create lessons, generalize corrections. DO NOT USE FOR: general debugging, writing tests, code review."
argument-hint: Describe what went wrong or what was corrected
license: MIT
---

# Error Learning — Register, Generalize, Prevent

You made a mistake and the user corrected you. This is valuable signal. Your job is to turn this correction into a **reusable lesson** that prevents you — and future agents — from repeating it.

## 1. Analyze the Error

When the user points out a correction, identify EXACTLY what went wrong. Classify the root cause:

| Cause | Description | Example |
|-------|-------------|---------|
| `wrong-assumption` | Assumed something without verifying | "Assumi que a API aceitava array mas aceita string" |
| `missing-context` | Didn't read/search before acting | "Editei sem ler o estado atual do arquivo" |
| `unknown-pattern` | Didn't know the correct pattern | "Não sabia que PS 5.1 não suporta ternary" |
| `wrong-scope` | Solved the wrong problem | "Corrigi o sintoma, não a causa raiz" |
| `skipped-verification` | Didn't test/validate before delivering | "Não rodei os testes antes de commitar" |

Be honest. The cause determines how useful the lesson will be.

## 2. Generalize

Transform the specific case into a generic rule that covers SIMILAR scenarios:

- **Specific**: "errei neste regex de conventional commits"
- **Generic**: "sempre validar regex contra spec oficial quando envolve padrão público"

The generalization must cover more than the exact case. Ask yourself: *"In what other situations would this same mistake happen?"* — that's the scope of your rule.

Bad generalization: "não errar em conventional commits regex" (too narrow — just restates the error).
Good generalization: "validar qualquer regex-based matching contra a spec/fonte autoritativa antes de usar" (covers all pattern-matching against public standards).

## 3. Persist as Lesson

Create a lesson file:

- **Location**: `~/.copilot/lessons/` (create directory if it doesn't exist)
- **Name**: `L{NNN}-{slug}.md` — NNN is zero-padded sequential, slug is kebab-case of the title
- **Before creating**: check existing files to determine the next sequential ID

### Template

```markdown
---
id: L{NNN}
tags: [{action}, {domain}]
confidence: 0.7
created: {YYYY-MM-DD}
cause: {cause-classification}
---

# {Title — imperative, max 60 chars}

## Resumo
{Max 2 lines. This is what gets injected into agent context by the lesson-injector hook.
Keep it dense and actionable — the hook injects ONLY this.}

## Registro
- **O que aconteceu**: {describe the concrete error}
- **Causa raiz**: {classification} — {explanation of why it happened}
- **Correção aplicada**: {what the user corrected}
- **Generalização**: {generic rule derived from this case}
```

### Rules for the Template

- The **Resumo** MUST be max 2 lines — it's the injected payload. Dense and actionable.
- The **id** is sequential — list `~/.copilot/lessons/L*.md` and increment from the highest found. Start at `L001` if no lessons exist.
- **confidence** starts at `0.7` for direct user corrections. Higher confidence (0.8-0.9) is reserved for lessons confirmed by multiple occurrences.

## 4. Assign Tags

Tags determine when the lesson-injector hook surfaces this lesson. Use relevant combinations:

**Action tags** (what the agent was doing):
`create`, `modify`, `delete`, `search`, `configure`, `fix`

**Domain tags** (what area was involved):
`file-operations`, `git`, `regex`, `api`, `testing`, `hooks`, `agents`, `skills`, `shell`, `cross-platform`, `yaml`, `json`, `markdown`, `dependencies`

Assign 2-4 tags per lesson. At least one action tag and one domain tag.

## 5. Confirm with the User

Before saving the lesson file, present:
1. The **generalization** you derived
2. The **tags** you chose
3. The **resumo** (2-line summary)

Ask: *"Essa generalização faz sentido? Cobre bem o cenário?"*

Only save after the user confirms or adjusts.

## 6. Consolidation (30+ lessons)

When the lessons directory has 30 or more active lessons:

1. **Identify clusters** — lessons with the same `cause` classification or overlapping tags
2. **Propose merges** — combine similar lessons into one broader lesson with higher confidence
3. **Archive absorbed lessons** — move merged originals to `~/.copilot/lessons/archive/`
4. **Resequence is NOT needed** — IDs are permanent identifiers, gaps are fine

### Merge Example

Before:
- `L003` — "Ler arquivo antes de editar" (tags: modify, file-operations)
- `L012` — "Verificar estado do git antes de commit" (tags: modify, git)
- `L018` — "Checar config existente antes de alterar" (tags: modify, configure)

After merge:
- `L031` — "Sempre verificar estado atual antes de qualquer modificação" (tags: modify, file-operations, git, configure) — confidence: 0.85

Archived: L003, L012, L018 → `~/.copilot/lessons/archive/`

## Rules

- **NEVER** save a lesson without user confirmation of the generalization
- **NEVER** write a resumo longer than 2 lines — the hook has a 500-char context budget
- **ALWAYS** check existing IDs before creating a new lesson — avoid ID collision
- **ALWAYS** classify the root cause — "I made a mistake" is not a classification
- **ALWAYS** generalize beyond the specific case — a lesson that only covers one scenario is a note, not a lesson
- Confidence starts at 0.7 — only increase when the same lesson prevents a recurrence or the user explicitly validates it as high-value

## Integration with lesson-injector Hook

The **lesson-injector** hook (`~/.copilot/hooks/scripts/lesson-injector.ps1`) automatically injects relevant lessons from `~/.copilot/lessons/` into the agent's context at PreToolUse. This closes the feedback loop:

1. User corrects agent → **error-learning** skill creates a lesson
2. Next interaction → **lesson-injector** hook injects relevant lessons
3. Agent avoids repeating the same mistake

You don't need to manually reference lessons — the hook handles injection based on tags and relevance.
