---
description: "First-session orientation for a new ACT Edition heir — explains identity, channels, upgrade flow, and overrides"
mode: agent
lastReviewed: 2026-04-30
---

# Welcome to ACT Edition

Run on a fresh heir's first session. Walk the user through the heir's identity and how the brain works.

## Steps

1. **Read the marker** at `.github/.act-heir.json` and report:
   - `heir_id`, `heir_name`, `edition_version`, `deployed_at`
2. **Show the architecture in three tiers**:

   | Tier | Scope | Where |
   |---|---|---|
   | User | Personal preferences, knowledge, profile | OneDrive `AI-Memory/` |
   | Global | Cognitive architecture (instructions, skills, scripts) | This heir's `.github/` (synced from `Alex_ACT_Edition`) |
   | Project | This heir's specific overrides | Heir-owned paths (`copilot-instructions.local.md`, `instructions/local/`, `skills/local/`, `src/`, `tests/`) |

3. **Show the fleet channels**:

   | Direction | Path | Purpose |
   |---|---|---|
   | Inbound | `AI-Memory/announcements/alex-act/` | Read on session start; release notes + user-authored guidance |
   | Outbound | `AI-Memory/feedback/alex-act/` | Write via `/feedback` prompt when surfacing friction |

4. **Show the upgrade command**:

   ```bash
   node .github/scripts/upgrade-self.cjs           # dry-run
   node .github/scripts/upgrade-self.cjs --apply   # write changes
   ```

   Note: `--allow-major` is required for major bumps. The heir reviews the diff and commits manually.

5. **Show the customization points**:
   - **Identity**: edit `.github/copilot-instructions.local.md` (heir-owned, never overwritten)
   - **Local instructions**: drop files in `.github/instructions/local/` (heir-owned)
   - **Local skills**: drop folders in `.github/skills/local/` (heir-owned)
   - **Sync policy**: read `.github/config/sync-policy.json` to see exactly what is heir-owned vs edition-owned
6. **Offer next actions**:
   - Customize identity now? → walk through `copilot-instructions.local.md`
   - Set North Star? → ask for project goal, propose draft
   - Skip and start working? → end the prompt
