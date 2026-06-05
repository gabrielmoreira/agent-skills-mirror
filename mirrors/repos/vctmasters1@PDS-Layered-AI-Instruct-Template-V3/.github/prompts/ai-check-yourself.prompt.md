---
mode: ask
description: Audit AI's instruction alignment. Re-read authoritative rules, conventions, and scope. Reset to baseline.
---

# /ai-check-yourself — Instruction Alignment Audit

Use this when the AI has drifted from project rules and needs to reset.

## What This Does

1. **Re-reads all authoritative rules** for your current directory scope
2. **Checks Project Mode** (Template Development vs Production)
3. **Loads key conventions** (naming, credentials, environment, maintenance)
4. **Generates a digest** of what the AI should remember
5. **Explicitly calls for re-alignment** before proceeding

## How to Use

```
/ai-check-yourself
```

That's it. The AI will:

1. Read `.github/dev-specs.md` → **Project Mode** (CRITICAL first)
2. Read `.ai/index.md` → Master index
3. Walk the depth-priority scope chain and load effective instructions
4. Read `.ai/conventions.md`, `.ai/credentials.md`, `.ai/environment.md`, `.ai/maintenance.md`
5. Generate a summary: "Here's what I should remember"
6. Ask explicitly: "Do you want me to proceed with a fresh understanding?"

## Common Triggers

Use `/ai-check-yourself` when:

- AI suggests committing `.env` files (violation of `.ai/credentials.md`)
- AI suggests modifying adopter machine configs when in Template mode
- AI forgets the naming convention for a file type
- AI creates a file in the wrong place (violating directory structure)
- AI suggests unsafe terminal commands (violates `.ai/environment.md`)
- AI forgets that deeper `.ai/instruct.md` files override shallower ones
- AI violates the AI-INSTRUCT Maintenance Rule (doesn't update `.ai/` with code changes)
- Any other "hey, that violates the framework" moment

## What the AI Will Remind Itself Of

After reading the rules, the AI will output something like:

```
[RESET TO BASELINE]

Project: PDS-Layered-AI-Instruct-Template-V5
Current Scope: K:\PDS-Layered-AI-Instruct-Template-V5
Project Mode: TEMPLATE DEVELOPMENT

Key Rules I Just Re-Read:
✓ Depth-priority: Deepest .ai/instruct.md is authoritative
✓ Never duplicate rules: One source of truth per topic
✓ Template mode: I can modify .ai/, .github/, create plugins; commit framework improvements
✓ Production mode: I never commit adopter machine configs
✓ Naming: Python=snake_case, PowerShell=kebab-case, Markdown=kebab-case
✓ Credentials: Never commit .env (only .env.example); scan for secrets
✓ Archive-first: Never permanently delete; use .archive/ mirroring
✓ AI-INSTRUCT Maintenance: Update .ai/ when architecture changes; run /ai-update-index
✓ Environment: Detect-then-ask for host-mutating commands; never silently install
✓ Ports: Single registry in .ai/ports.md; validator detects drift

Ready to proceed with corrected understanding. What would you like me to do?
```

## Integration with Other Commands

After `/ai-check-yourself`, you might want to run:

- `/ai-validate` — Check instruction drift
- `/ai-env-check` — Audit containment state
- `/ai-ports-check` — Validate port registry
- `/ai-foresight` — Gap/risk analysis before acting

## See Also

- [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — Meta: how the system works
- [`.github/dev-specs.md`](../../.github/dev-specs.md) — **CRITICAL**: Read first (Project Mode, platform)
- [`.ai/index.md`](../../.ai/index.md) — Master index of all rules
- [`.ai/instruct.md`](../../.ai/instruct.md) — Root-level authority
- [`.ai/conventions.md`](../../.ai/conventions.md) — Naming, file organization, TOC rules
- [`.ai/maintenance.md`](../../.ai/maintenance.md) — Archive patterns, never-delete rule
- [`.ai/credentials.md`](../../.ai/credentials.md) — Credential rules, `.env` convention
- [`.ai/environment.md`](../../.ai/environment.md) — Host vs container isolation
