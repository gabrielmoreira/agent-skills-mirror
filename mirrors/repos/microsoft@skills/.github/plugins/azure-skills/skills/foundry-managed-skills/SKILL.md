---
name: foundry-managed-skills
description: |
  Manage SKILL.md files as a Foundry-side resource (preview). Author behavioral guidelines once, store centrally via the Foundry Skills REST API, download into hosted agent containers, and load them as additional session instructions. Decouples behavioral policy from agent code.
  Triggers: "Foundry skills resource", "Skills REST API", "SKILL.md Foundry", "skills_create", "skills_download", "skill in hosted agent", "behavioral policy agent", "skill_directories CopilotClient", "central skill management".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry-Managed Skills

## Before You Build — Discovery (MANDATORY)

The Foundry Skills REST API is in **public preview**. Endpoints, payloads, and SDK shapes change. **Always** verify against current docs before generating code.

Run these `microsoft-docs` MCP queries first:

- `Foundry skills REST API`
- `Use skills with Foundry agents`
- `skill_directories Copilot SDK`
- `azure-ai-projects beta skills`

Verify:

- The exact `api-version` string for `/skills` and `/skills:import`
- The current `Foundry-Features` preview header value (e.g. `Skills=V1Preview`)
- Whether your target language SDK exposes `project.beta.skills.*` (Python / JS) or `AgentSkills` (.NET)
- Required RBAC role (currently **Azure AI User** on the Foundry project)

If any of these have moved, defer to the docs — do not invent.

## Mental Model

A **Foundry Skill** is a single `SKILL.md` file (YAML frontmatter + markdown body) stored as a managed resource inside your Foundry project. At runtime, your hosted agent downloads the file, points at it, and the SDK loads its body as **additional session instructions** alongside the agent's base instructions.

Why this exists:

- **Decouples policy from code.** Update `SKILL.md`, redeploy the agent (or just re-bundle), no source-code change.
- **Reuse across agents.** One escalation policy, one tone-of-voice guide, consumed by N agents.
- **Centralized authorship.** Non-developers (legal, support ops, brand) can own `SKILL.md` PRs.

> **Hosted agents only.** Prompt agents do not consume Foundry-managed skills.

## DISAMBIGUATION

> "Skills" is a heavily overloaded term. Read this carefully before you act.

| Term | What it is | This skill? |
|------|------------|-------------|
| **Foundry-managed Skills** | A Foundry resource type. SKILL.md files stored via the Skills REST API, downloaded into hosted-agent containers. | ✅ Yes — this is the topic. |
| `agent-skills` repo (this repo) | A library of SKILL.md files used as **LLM-side context packages** for coding agents (Copilot, etc.). | ❌ Different layer. |
| Cognitive Services Skills / Azure AI Search skillsets | Enrichment pipelines for indexing. | ❌ Unrelated. |
| Plugin / Tool / Function calling | Executable capability the model can invoke. | ❌ Different mechanism. |

If the user is talking about a `SKILL.md` that lives **inside their Foundry project resource** and is consumed by a **hosted agent at session start**, this is the right skill. Otherwise, redirect.

## SKILL.md Authoring

A skill is a Markdown file with a YAML frontmatter block.

```markdown
---
name: greeting
description: Generate a personalized greeting for the user.
---

# Greeting Skill

You are a friendly greeting assistant.

## Instructions

- Include the user's name if they provided one.
- Keep greetings concise — 1 to 2 sentences.
- Thank the user for trying out this hosted agent.
```

Frontmatter rules:

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Short identifier, no spaces. **Must be unquoted** in YAML — `name: 'greeting'` causes HTTP 500 on import. |
| `description` | Yes | One-liner shown in skill listings. **Must be unquoted.** |
| Body | Yes | Free Markdown. Becomes the injected instructions. |

Layout: one skill per subdirectory — `greeting/SKILL.md`, never a bare `SKILL.md` at the agent root.

## Skills CRUD via REST API

Endpoint: `{FOUNDRY_PROJECT_ENDPOINT}/skills`
Auth: bearer token from `DefaultAzureCredential` (scope `https://ai.azure.com/.default`).
Preview header: `Foundry-Features: Skills=V1Preview` on every call.

> Defer to the docs MCP for exact payload shapes — only the operation surface is summarized here.

| Operation | HTTP | Purpose |
|-----------|------|---------|
| **Create from JSON** | `POST /skills?api-version=v1` | Submit `name` + `description` + `instructions` text directly. Result has `has_blob: false` (cannot be downloaded). |
| **Import from ZIP** | `POST /skills:import?api-version=v1` (`Content-Type: application/zip`) | Upload a ZIP whose root is `SKILL.md`. Name/description come from the frontmatter. Result has `has_blob: true`. |
| **List** | `GET /skills?api-version=v1` | Cursor pagination via `first_id` / `last_id` + `after` / `before`. |
| **Get** | `GET /skills/{name}?api-version=v1` | Returns metadata. 404 if missing. |
| **Download** | `GET /skills/{name}:download?api-version=v1` | Returns the original ZIP (`application/zip`). 404 for JSON-created skills. |
| **Delete** | `DELETE /skills/{name}?api-version=v1` | Returns `{ "deleted": true }`. |

SDK surface (verify versions):

- **Python:** `project.beta.skills.{create, create_from_package, list, get, download, delete}` (requires `allow_preview=True` on `AIProjectClient`).
- **JavaScript:** `project.beta.skills.{create, createFromPackage, list, get, download, delete}`.
- **.NET:** `AgentAdministrationClient.GetAgentSkills()` → `AgentSkills.{CreateSkill, CreateSkillFromPackage, GetSkills, GetSkill, DeleteSkill}`. Requires a `Foundry-Features: Skills=V1Preview` request-policy and `#pragma warning disable AAIP001`.

`has_blob: true` means downloadable. JSON-created skills are **not** downloadable.

## Bundling Skills into a Hosted Agent

Hosted-agent project layout:

```
├── main.py            (or main.cs / index.ts)
├── agent.yaml
├── agent.manifest.yaml
├── requirements.txt
└── skills/
    ├── greeting/SKILL.md
    └── joke/SKILL.md
```

Agent code points at the `skills/` directory at session-construction time. With the Copilot SDK this is the `skill_directories` parameter:

```python
client = CopilotClient(..., skill_directories=["./skills"])
```

Every `SKILL.md` found in a subdirectory is loaded as **additional instructions** when a session is created. Multiple skills compose — they are concatenated with the base instructions, not merged or deduped.

Update flow:

1. Edit `SKILL.md`
2. Re-bundle into the container image (`COPY skills/ /app/skills/`)
3. Redeploy
4. **Next session** picks up the change. There is no hot reload.

CI tip: keep the canonical `skills/` tree in the agent's repo, run `POST /skills:import` on every change to a `SKILL.md`, and tag the resulting Foundry skill with the commit SHA in the description for traceability.

## Workflow — End-to-End

1. **Author** `SKILL.md` locally under `skills/<skill-name>/SKILL.md`. Validate the YAML frontmatter is unquoted.
2. **Upload** to Foundry — either `POST /skills:import` (ZIP) directly, or commit to a repo and let CI run the import on merge to `main`. Prefer the ZIP/import path so the skill is downloadable later.
3. **Download** into the agent project:
   - Fresh scaffold: `azd ai agent init -m <agent.manifest.yaml URL>` pulls the manifest's bundled skills.
   - Existing project: script a small `skills.download(name)` step that writes the ZIP and unpacks it under `skills/<name>/`.
4. **Bundle** — ensure the Dockerfile contains `COPY skills/ /app/skills/` so the files reach the runtime image. Without this, the SDK silently sees zero skills.
5. **Wire** — confirm `skill_directories=["./skills"]` (Copilot SDK) or the equivalent constructor argument in your runtime. The path is relative to the agent's working directory inside the container.
6. **Run + invoke locally** — `azd ai agent run`, then in another terminal `azd ai agent invoke --local '{"input": "..."}'`. Confirm the model's response shows the skill's effect (greeting style, escalation policy, etc.).
7. **Provision + deploy** — `azd provision && azd deploy` (or `azd up`). Test with `azd ai agent invoke '{"input": "..."}'` against the deployed endpoint.
8. **Iterate** — to change behavior: edit `SKILL.md` → re-run import → re-bundle → `azd deploy`. The next session uses the new skill body.

## When to Use Foundry-Managed Skills vs. Agent Instructions

| Use Foundry-managed Skills when… | Use plain agent instructions when… |
|----------------------------------|------------------------------------|
| Policy is reused across **multiple** agents | Policy is unique to one agent |
| Policy changes frequently and needs a separate review/approval flow | Policy is part of the agent's identity and rarely changes |
| Non-developers (legal, brand, support) own the wording | Developers own the wording end-to-end |
| You want central audit/versioning of behavioral guidelines | The agent has a single source of truth in code |

If only one agent ever uses the policy and developers control it, plain agent instructions are simpler.

## Critical Gotchas — Do Not Confuse

- **"Foundry Skills" ≠ "agent-skills" repo.** This is a Foundry resource type. The `agent-skills` repo (where this file lives) is LLM-side coding-agent context. Different layer entirely.
- **Hosted agents only.** Prompt agents do not consume skills (yet). Don't promise this works for prompt agents.
- **Loaded at session start.** Updates require a redeploy / re-bundle. There is no live refresh inside an active session.
- **Goes into model context.** Anything in `SKILL.md` is sent to the model. Never include secrets, PII, customer data, or anything you would not paste into a prompt.
- **`description` is for routing.** When skills are presented to the model, the `description` is what the model uses to decide whether to apply the skill. Make it actionable and specific (e.g. "Use when the user asks for a greeting"), not decorative.
- **YAML frontmatter must be unquoted.** `name: 'greeting'` returns HTTP 500 on import. Use `name: greeting`.
- **`has_blob: false` skills cannot be downloaded.** JSON-created skills exist as metadata only — there is no file to fetch back.
- **ZIP layout matters.** `SKILL.md` must be at the **root** of the ZIP, not nested in a subdirectory.

## Security

- **Treat `SKILL.md` as code.** Require PR review. Skill changes change agent behavior in production.
- **No secrets in `SKILL.md`.** It ends up in model context and may be logged/traced.
- **Audit changes.** Use git history on the `skills/` directory and Foundry-side `created_at` / `last_modified` metadata.
- **Third-party content.** If a skill is authored or supplied by a third party, follow your organization's third-party data-handling guidance — see the `foundry-governance` skill for the broader policy frame.
- **Least privilege.** Only grant the **Azure AI User** role on the Foundry project to identities that need to manage skills.

## Reference Links

- Microsoft Foundry — Use skills with Foundry agents (preview): docs MCP query `Use skills with Foundry agents`
- Skills REST API reference: docs MCP query `Foundry skills REST API`
- Copilot SDK `skill_directories` parameter: docs MCP query `skill_directories Copilot SDK`
- `azure-ai-projects` Python SDK (`beta.skills`): docs MCP query `azure-ai-projects beta skills`
- Foundry sample (Copilot SDK + skills): `microsoft-foundry/foundry-samples` → `samples/python/hosted-agents/bring-your-own/invocations/github-copilot`

Cross-skill references in this repo:

- `azure-hosted-copilot-sdk` — building/deploying the Copilot SDK hosted agent that consumes these skills
- `foundry-governance` — policy / RBAC / data-handling envelope around Foundry resources
