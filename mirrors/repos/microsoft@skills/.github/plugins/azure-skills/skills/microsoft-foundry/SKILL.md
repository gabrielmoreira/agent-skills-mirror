---
name: microsoft-foundry
description: |
  Router skill for the Microsoft Foundry agent platform (preview). Use when the user
  works with Foundry projects/resources, models, hosted agents, intent-based toolboxes,
  multi-agent workflows, Foundry IQ knowledge bases, managed skills, long-term memory,
  observability/evaluations, or governance via the Foundry Control Plane and AI Gateway.
  This skill maps user intent onto the right sub-skill and the right discovery surface
  (Microsoft Docs MCP, Foundry MCP at `mcp.ai.azure.com`, the `azd ai agent` extension,
  and the `az` CLI). USE FOR: build/deploy/invoke a hosted agent, attach a toolbox,
  ground an agent on internal knowledge, set up evals + tracing, govern tools across
  teams, personalize across sessions, orchestrate multiple agents. DO NOT USE FOR:
  generic Azure deployment unrelated to Foundry.
license: MIT
metadata:
  author: Microsoft
  version: "2.0.0"
---

# Microsoft Foundry — Agent Development Lifecycle

This skill is a **router**, not a textbook. It points you at the correct sub-skill
and the correct **live discovery surface** for the refreshed Microsoft Foundry
preview. Foundry is moving fast — never rely on training-data syntax.

## Pre-Execution Discovery (MANDATORY)

> Foundry preview surfaces change weekly. Before generating any non-trivial code,
> command, or YAML for Foundry, run this discovery loop. Skipping it produces
> broken code against stale APIs.

1. **Azure MCP — `foundry` tool.** Call it with no arguments first to enumerate
   the current Foundry methods exposed by Azure MCP. Treat this as the help page.
2. **Foundry MCP server.** Connect to `https://mcp.ai.azure.com` and inspect its
   tool list to discover current Foundry-native operations (model catalog,
   toolboxes, knowledge bases, deployments).
3. **`azd ai agent` extension.** Run `azd ai agent --help` and the relevant
   subcommand `--help` (`init`, `deploy`, `invoke`, `monitor`, …) to see current
   flags. Flags are the source of truth for the hosted-agent lifecycle.
4. **Microsoft Docs MCP.** Search `microsoft-docs` for the specific capability
   (e.g. "Foundry hosted agents protocols", "Foundry toolbox versioning",
   "Foundry IQ knowledge base") before writing code.

If discovery and your memory disagree, **discovery wins**.

## Sub-Skills

Load the sub-skill that matches the user's intent. Sub-skills live as siblings
in this directory.

| User Intent | Sub-Skill | What it covers |
|---|---|---|
| Provision a Foundry resource / project, wire connections, set up auth | [`foundry-projects-resources`](../foundry-projects-resources/SKILL.md) | Resource + project creation, standard vs private-network setup, connections (key, OAuth, managed identity, agent identity), auth best practices |
| Deploy a model, find capacity, manage quota | [`foundry-models`](../foundry-models/SKILL.md) | Preset and customized model deployments, capacity discovery across regions, quota and SKU planning |
| Build, deploy, invoke, or monitor a hosted agent | [`foundry-hosted-agents`](../foundry-hosted-agents/SKILL.md) | Hosted agents (Responses + Invocations protocols, protocol version `1.0.0`), `agent.yaml` / `agent.manifest.yaml`, `azd ai agent` lifecycle, dedicated agent identity, sessions vs conversations, A2A hosting |
| Give an agent tools (search, code, files, OpenAPI, MCP, A2A, browser, computer use) | [`foundry-toolboxes`](../foundry-toolboxes/SKILL.md) | Intent-based toolboxes, the 7 built-in tool types, browser automation + computer use, version + default promotion, MCP endpoint patterns, `Foundry-Features: Toolboxes=V1Preview` header, A2A consumption |
| Orchestrate multiple agents (visual builder, Connected Agents, Agent Framework workflows) | [`foundry-workflows`](../foundry-workflows/SKILL.md) | Foundry workflows, Connected Agents, Agent Framework workflows, when to use a workflow vs an A2A tool call |
| Ground an agent on internal docs / Blob / SharePoint / OneLake / Web | [`foundry-iq-knowledge-bases`](../foundry-iq-knowledge-bases/SKILL.md) | Foundry IQ knowledge bases, agentic retrieval, ACL + sensitivity-label enforcement, MCP-tool wiring from agent to knowledge base |
| Bundle reusable instruction files as a Foundry resource | [`foundry-managed-skills`](../foundry-managed-skills/SKILL.md) | `SKILL.md` as a managed Foundry resource via the Skills REST API, CRUD lifecycle, loading skills at session start |
| Personalize across sessions, retain user profile / chat summary | [`foundry-memory`](../foundry-memory/SKILL.md) | Long-term memory stores, user-profile vs chat-summary memory, scoping, prompt-injection / memory-corruption risks, retention |
| Trace, evaluate, run RAI evals, curate datasets, monitor in CI | [`foundry-observability`](../foundry-observability/SKILL.md) | OpenTelemetry tracing from protocol libraries, App Insights + KQL templates, eval ↔ trace correlation, batch evals, built-in quality + safety/RAI evaluators, dataset curation, regression detection |
| Govern tools, agents, models across teams; AI Gateway; RBAC; RAI policies | [`foundry-governance`](../foundry-governance/SKILL.md) | Foundry Control Plane, tool catalog, AI Gateway for MCP, RBAC + agent identity, third-party tool considerations, RAI policies and transparency notes |

## Infrastructure Lifecycle

Match user intent to the correct infrastructure workflow.

| User Intent | Workflow |
|-------------|---------|
| "Create Foundry" / "Set up Foundry" (ambiguous) | Use `AskUserQuestion`: (a) just an AI Services resource, (b) a project with public access, or (c) a project with network isolation? Route: (a) → [resource/create](resource/create/create-foundry-resource.md), (b) → [project/create](project/create/create-foundry-project.md), (c) → [private-network](resource/private-network/private-network.md) |
| Set up Foundry with VNet isolation | [private-network](resource/private-network/private-network.md) |
| Create a Foundry project (public) | [project/create](project/create/create-foundry-project.md) |
| Create a bare Foundry resource | [resource/create](resource/create/create-foundry-resource.md) |

## Agent Development Lifecycle

Map common end-to-end intents to an ordered sub-skill workflow. Read each
sub-skill in order.

| End-to-End Intent | Workflow |
|---|---|
| Build my first hosted agent end-to-end | `foundry-projects-resources` → `foundry-models` → `foundry-hosted-agents` → `foundry-observability` |
| Add a tool to my agent | `foundry-toolboxes` (then `foundry-hosted-agents` if a redeploy is needed) |
| Ground my agent on internal docs | `foundry-iq-knowledge-bases` (+ `foundry-toolboxes` for the AI Search tool wiring) |
| Govern tools and agents across teams | `foundry-governance` |
| Set up evals + monitoring (and CI gating) | `foundry-observability` |
| Personalize an agent across sessions | `foundry-memory` |
| Multi-agent orchestration | `foundry-workflows` (cross-link to `foundry-hosted-agents` and `foundry-toolboxes`) |
| Publish an agent to Teams / M365 | `foundry-hosted-agents` (Responses + Activity protocols) → companion `m365-agents-*` skill |
| Migrate from initial-preview hosted agents | `foundry-hosted-agents` (migration callout) |

## Forward-Looking Anchors

When you generate code or YAML, conform to the **refreshed** preview model:

- **Protocol version** is `1.0.0` inside `agent.yaml`. The Azure REST `api-version`
  is separate (still `v1`). Do not conflate them.
- **Dedicated agent identity.** Each hosted agent gets its own Microsoft Entra ID
  at deploy time. Use it for runtime auth — not the project managed identity
  (which is for platform infrastructure such as ACR pull).
- **Dedicated endpoint per agent**, e.g.
  `{project_endpoint}/agents/{name}/endpoint/protocols/openai/v1/responses` and
  `{project_endpoint}/agents/{name}/endpoint/protocols/invocations`.
- **Sessions vs conversations.** Sessions are compute-bound (15-min idle, 30-day
  max) and persist `$HOME` / `/files`. Conversations are durable history stored
  in Foundry, accessible across channels.
- **Tools live on toolboxes**, not in the agent version definition. Toolboxes
  are versioned and promoted to default; agents bind to a toolbox + version.
- **REST callers must add `Foundry-Features` headers** themselves
  (`HostedAgents=V1Preview`, `Toolboxes=V1Preview`). SDK clients add them
  automatically.
- **`agent.yaml` (deployed) vs `agent.manifest.yaml` (init scaffolding).** Don't
  swap them.
- **`azd ai agent init -m`** uses a manifest; `--no-prompt` silently leaves
  `{{ param }}` placeholders empty.

## CLI-First Tooling

Prefer the highest-level surface that exposes what you need. Discover before
invoking.

| Surface | Use For | How To Discover |
|---|---|---|
| `azd ai agent` extension | Hosted agent init, deploy, invoke, monitor lifecycle | `azd ai agent --help` and per-subcommand `--help` |
| `azd up` / `azd provision` / `azd deploy` | Provision Foundry infra and deploy code together | `azd --help` |
| `az cognitiveservices account` | Foundry resource + model deployment management | `az cognitiveservices --help` |
| Azure MCP `foundry` tool | Programmatic Foundry operations from your editor | Call with no arguments to enumerate methods |
| Foundry MCP (`mcp.ai.azure.com`) | Foundry-native operations: model catalog, toolboxes, knowledge bases, deployments | Inspect the MCP server's tool list |
| Microsoft Docs MCP | Always-current API and SDK reference | Search before generating code |

## Companion Skills (in their language plugins)

Foundry agents commonly compose with adjacent SDKs. These do **not** live in
this plugin — load them from their language plugins as needed.

- **AI Search** — `azure-search-documents-{py,dotnet,ts}` — vector / hybrid
  search backing knowledge bases.
- **VoiceLive** — `azure-ai-voicelive-{py,dotnet,ts,java}` — real-time voice
  agents.
- **Content Safety** — `azure-ai-contentsafety-{py,ts,java}` — standalone harm
  detection (Foundry RAI policies cover platform-level enforcement).
- **M365 Agents** — `m365-agents-{py,dotnet,ts}` — Teams / Copilot Studio
  channel integration.
- **Azure AI Projects SDK** — `azure-ai-projects-{py,dotnet,ts,java}` — direct
  SDK reference for any language.

## Tool Usage Conventions

- Use `ask_user` (or the equivalent question tool) to collect missing inputs
  such as project endpoint, agent name, environment, region, or subscription.
- Always run the **Pre-Execution Discovery** loop **before** generating code
  against preview APIs.
- Prefer the Azure MCP `foundry` tool over hand-rolled `az` calls when the
  operation is Foundry-specific.
- Use the `azd ai agent` workflow for the hosted-agent lifecycle. Do **not**
  hand-roll container build, push, and SDK-based deployment unless the user
  explicitly opts out of azd.
- Cite Microsoft Learn URLs you found via the docs MCP when explaining
  preview behavior — do not invent URLs.

## Reference Links

- Foundry overview: <https://learn.microsoft.com/azure/ai-foundry/what-is-azure-ai-foundry>
- Hosted agents: <https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents>
- Foundry toolboxes: <https://learn.microsoft.com/azure/ai-foundry/agents/concepts/toolboxes>
- Foundry IQ: <https://learn.microsoft.com/azure/ai-foundry/concepts/foundry-iq>
- `azd ai agent` extension: <https://learn.microsoft.com/azure/developer/azure-developer-cli/reference>
- Microsoft Foundry Control Plane: <https://learn.microsoft.com/azure/ai-foundry/concepts/control-plane>
