---
applyTo: "**"
---
# Team Copilot Workflow — Developer Guide

> Full guide: [docs/team-copilot-guide.md](../../docs/team-copilot-guide.md)
> Docs structure: [docs/docs-architecture.md](../../docs/docs-architecture.md)
> Research decisions: [docs/RESEARCH-DECISIONS.md](../../docs/RESEARCH-DECISIONS.md)
> **API architecture**: [docs/external-apis/](../../docs/external-apis/)

---

## ⛔ HARD RULES — YOU MUST ENFORCE THESE, NO EXCEPTIONS

> **RULE 1 — NO CODE WITHOUT A PLAN**
> If a developer asks you to write, scaffold, or modify any production code and there is no Issue doc in `docs/issues/` with Phases 1–3 complete, **REFUSE**.
> Respond: *"Before writing any code, this Issue needs to go through `/start-issue` → `/discuss` → `/research` → `/plan`. Run `/start-issue` to begin."*

> **RULE 2 — NO IMPLEMENTATION WITHOUT REQUIREMENTS**
> If a developer asks to write code, implement a feature, or execute a plan without a feature branch, without an Issue doc, or without Phases 1–3 complete, **REFUSE**.
> Respond: *"New work always starts with `/start-issue` — it creates your branch and defines requirements. Run it first."*

> **RULE 3 — NO SKIPPING PHASES**
> Phases must be completed in order: Discuss → Research → Plan → Execute → Verify.
> If a developer tries to jump ahead (e.g., `/plan` without research findings), ask them to confirm the prior phases are complete.

> **RULE 4 — NO MERGING WITHOUT VERIFICATION**
> Never suggest opening a PR or merging code without a Verify agent report confirming all requirements are met.

> **Anti-pattern to REJECT:** Developer says "just write the code for X" or "implement Y quickly" with no prior phase work.
> **Correct response:** Redirect to `/discuss` with the task description.

---

## The Complete Sequential Workflow

Every work item follows this exact sequence. **No skipping. No shortcuts.**

```
🌿 /start-issue   → Create feature branch + confirm clean baseline
        │  ← NEVER implement on main. Feature branches only.
        ▼
🧠 /discuss       → Define requirements, create Issue doc (Phase 1)
        │  ← No planning until requirements are locked.
        ▼
🔍 /research      → Explore codebase, find patterns (Phase 2) [Auto after discuss]
        │  ← No planning without research context.
        ▼
📋 /plan          → Create bite-sized implementation tasks (Phase 3)
        │  ← No code until plan is approved.
        ▼
⚙️ /execute       → TDD: failing test → minimal code → commit (Phase 4)
        │  ← Tests first. No exceptions.
        ▼
✅ /verify        → Check all requirements met, all tests pass (Phase 5)
        │  ← No PR without a clean verify report.
        ▼
🏁 /finish-branch → Choose: merge / create PR / keep / discard
```

## Specialist Agents

| Work Type | Agent | Command | When |
|-----------|-------|---------|------|
| Requirements | Discuss | `/discuss` | Phase 1 |
| Codebase research | Research | auto after Discuss | Phase 2 |
| Implementation plan | Planner | `/plan` | Phase 3 |
| Code + Tests | TDD | `/execute` | Phase 4 |
| Code review | Reviewer | `/code-review` | Before PR |
| Completeness check | Verify | `/verify` | Phase 5 |
| **New external API call** | **ApiBuilder** | `/add-new-api` | **Adding API integrations** |

## Request Architecture (Controller→Service→Wrapper→Transformer)

This project uses a strict layered architecture for all API calls:

```
Controller/Resolver (auth here) → Service (business logic)
  → APIWrapper (HTTP + transform) → External API
```

**Full rules**: `.github/instructions/api-architecture.instructions.md`

**When adding any external API call** → Use `/add-new-api` prompt and read:
- `docs/external-apis/[api-name]/` — fields, auth, query patterns
- `docs/apis/wrappers/[name]-wrapper.md` — existing wrapper methods

## Where Docs Live

```
docs/
├── issues/ISSUE-XXX-name.md          ← One per work item (all 5 phases)
├── apis/[domain]/[endpoint].api.md   ← One per internal API endpoint
├── apis/wrappers/[name]-wrapper.md   ← One per external API wrapper class
├── external-apis/[api-name]/         ← Auth, entities, field mappings per external API
├── flows/[flow-name]-flow.md         ← One per user journey
├── team-notes/[your-name]/           ← Personal notes (no conflicts)
└── templates/                        ← Copy to start new docs
```

## Daily Rules

1. **One session per Issue** — start fresh when switching Issues
2. **Read the Issue doc first**: `"Continue ISSUE-042 — read #docs/issues/ISSUE-042-name.md"`
3. **Read the external API doc before touching a wrapper**: `#docs/external-apis/dynamics/`
4. **Code + docs in same commit** — never separate them
5. **After changing an API** → run `/update-api-doc`

## All Slash Commands

| Command | When | What happens if skipped |
|---------|------|------------------------|
| `/start-issue` | **Start here** for any new work | Code ends up on main branch |
| `/discuss` | Define requirements | Planning in a vacuum |
| `/research` | Codebase context (auto after discuss) | Repeating existing patterns badly |
| `/plan` | Create implementation tasks | Unstructured implementation |
| `/execute` | TDD implementation | Tests written after (or not at all) |
| `/verify` | Check requirements + quality | Broken/incomplete code merged |
| `/finish-branch` | Merge, PR, or discard decision | Branch abandoned or force-pushed to main |
| `/status` | Check current phase and next step | Lost context, unsure what to do next |
| `/add-new-api` | Adding a new external API call | Wrong field names, raw data returned |
| `/code-review` | Reviewing files or PRs | Quality issues missed |
| `/generate-api-doc` | Documenting a new API endpoint | Undocumented API, drift over time |
| `/update-api-doc` | After changing an existing endpoint | Stale docs cause field name bugs |
| `/sync-docs` | After bulk changes or refactoring | Docs out of sync, field names wrong |
| `/summarize` | End of session / before context switch | Lost progress, teammate can't pick up work |
