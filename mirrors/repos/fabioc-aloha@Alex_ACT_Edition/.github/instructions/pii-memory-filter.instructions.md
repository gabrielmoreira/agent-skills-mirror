---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "PII filter at memory write boundaries — prevent sensitive data from entering persistent storage tiers"
application: "Always active — unconscious filter before writing to any persistent memory tier"
applyTo: "**"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# PII Memory Filter

Always-active unconscious behavior. Self-monitor before every write to persistent storage.

## Write Boundaries

This filter applies whenever you write to ANY persistent tier:

| Tier | Write Mechanism | Auto-Loaded? |
|------|-----------------|--------------|
| User Memory | `memory create /memories/` | Yes (200 lines) |
| Repo Memory | `memory create /memories/repo/` | No |
| Session Memory | `memory create /memories/session/` | No |
| AI-Memory | File creation in `AI-Memory/` | No |
| Feedback | File creation in `AI-Memory/feedback/` | No |

## Never Write These Categories

Before writing to ANY persistent tier, verify the content does NOT contain:

| Category | Examples | Risk |
|----------|----------|------|
| **Contact info** | Phone numbers, email addresses, physical addresses | L3 identity exposure |
| **Date of birth** | DOB, age calculations, birth year | L3 identity exposure |
| **Health data** | Diagnoses, medications, symptoms, lab values, provider names | L4 — no memory tier is appropriate |
| **Financial data** | Account numbers, balances, income, SSN, tax IDs | L4 — no memory tier is appropriate |
| **Credentials** | API keys, tokens, passwords, connection strings | L4 — use SecretStorage only |
| **File paths with usernames** | `C:\Users\username\...` | L2 identity leakage |
| **Client names** | Employer clients, project clients in fleet context | L3 confidential business data |

## Allowed Content Per Tier

| Tier | Allowed | Not Allowed |
|------|---------|-------------|
| **User Memory** | Workflow preferences, communication style, tool patterns | Any PII, project-specific data |
| **Repo Memory** | Build commands, code conventions, architecture facts | Credentials, user identity |
| **Session Memory** | Task context, file references, in-progress state | Health data, financial data |
| **AI-Memory knowledge** | Patterns, insights, technical knowledge | Contact info, health data |
| **AI-Memory announcements** | Upgrade notices, breaking changes | No PII by design |
| **AI-Memory feedback** | Skill name + category + severity (structured schema only) | Free-text context with domain data |

## Self-Check Protocol

Before writing to persistent storage, ask:

1. **Would I be comfortable if this appeared in a GitHub issue?** If no → don't write it.
2. **Does this contain a name + another identifier?** Name alone is L2. Name + phone/DOB/health = L3/L4.
3. **Is this about the person or about the work?** Work patterns are fine. Personal attributes are not.

## If PII Is Requested

When the user asks to store something containing PII:

- **Contact info** → Store in `AI-Memory/user-profile.json` (L3, on-demand only, never auto-loaded)
- **Health data** → Decline. Explain no memory tier is appropriate for L4 health data.
- **Credentials** → Direct to VS Code SecretStorage or environment variables
- **Work patterns** → Generalize: "prefers TDD" not "wrote 47 tests on Tuesday"
