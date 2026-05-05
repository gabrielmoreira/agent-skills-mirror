---
name: foundry-hosted-agents
description: |
  Build, deploy, and manage Microsoft Foundry hosted agents on the refreshed preview. Containerized agents that expose Responses or Invocations (or both) protocols and run on managed Foundry infrastructure with per-agent Microsoft Entra identity and dedicated endpoint.
  Triggers: "hosted agent", "Foundry hosted agent", "Responses protocol", "Invocations protocol", "agent.yaml", "agent.manifest.yaml", "azd ai agent", "ResponsesAgentServerHost", "InvocationAgentServerHost", "HostedAgentDefinition", "container_protocol_versions", "Foundry-Features HostedAgents=V1Preview".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Microsoft Foundry Hosted Agents

Hosted agents are containerized agentic applications that you bring as code, expose through one or more Foundry **platform protocols** (Responses, Invocations, Activity, A2A), and run on managed Foundry infrastructure. The platform provisions per-session VM-isolated sandboxes, mints a dedicated Microsoft Entra identity per agent, exposes a dedicated endpoint, persists session state, and handles scale-to-zero — you ship the container.

This skill is **language-agnostic**. Protocol libraries exist for Python and C#; the deployment contract (YAML, container, endpoints, RBAC) is the same regardless of language. For exact API names and code, follow the discovery steps below.

---

## Before You Build — Discovery (MANDATORY)

> Hosted agents are in preview and the surface changes weekly. Confirm current syntax before generating code. Never rely on cached SDK knowledge.

**Microsoft Docs MCP queries** (use `microsoft-docs` tool, then `microsoft_docs_fetch` for full pages you identify as authoritative):

1. `Foundry hosted agents concepts refreshed preview`
2. `Foundry hosted agents deploy hosted agent azure-ai-projects HostedAgentDefinition`
3. `Foundry agents protocol library Responses ResponsesAgentServerHost`
4. `Foundry agents protocol library Invocations InvocationAgentServerHost`
5. `azd ai agent extension reference azure.ai.agents`
6. `Foundry hosted agent permissions agent identity Azure AI User`

**Foundry MCP discovery** (`mcp.ai.azure.com` — exposed via the `foundry-mcp` MCP server):

- List models in your project to confirm the deployment name your container will reference.
- List toolboxes for the project to confirm the MCP endpoint your container will connect to (see the separate `foundry-toolboxes` skill).
- List existing hosted agents and their versions to avoid name collisions.

**CLIs** (preview surface — call `--help` first):

```bash
azd ai agent --help
azd ai agent init --help
azd ai agent invoke --help
azd ai agent monitor --help
az cognitiveservices account list-skus  # confirm region availability for Foundry
az rest --help                          # for direct REST against the data plane
```

**Verify SDK versions** before generating code:

- Python: `pip show azure-ai-projects` → must be **≥ 2.1.0** for `HostedAgentDefinition` + `container_protocol_versions`.
- .NET: confirm the latest `Azure.AI.Projects` and `Azure.AI.AgentServer.*` package versions on NuGet.

---

## Mental Model

```
┌─────────────────────┐  docker push  ┌──────────────────────┐
│ Container Image     │ ─────────────▶│ Azure Container      │
│ (agent code +       │               │ Registry (ACR)       │
│  protocol library)  │               └──────────┬───────────┘
└─────────────────────┘                          │ image pull (project MI)
                                                 ▼
   azd up / SDK create_version    ┌──────────────────────────────┐
   ─────────────────────────────▶ │  Foundry Agent Service       │
                                  │  • Provisions sandbox        │
                                  │  • Mints agent Entra ID      │
                                  │  • Mounts dedicated endpoint │
                                  │  • Manages versions          │
                                  └──────────────┬───────────────┘
                            ┌────────────────────┴────────────────────┐
                            ▼                                         ▼
              ┌─────────────────────────┐         ┌──────────────────────────┐
              │ Sessions                │         │ Conversations            │
              │ (compute, $HOME,        │         │ (durable history in      │
              │ /files, 15-min idle,    │         │ Foundry, cross-channel)  │
              │ 30-day max)             │         └──────────────────────────┘
              └─────────────────────────┘
```

**Key terms:**

| Term | Definition |
|------|------------|
| **Hosted agent** | A named, versioned, containerized agent in a Foundry project. |
| **Agent version** | An immutable snapshot of image + CPU/memory + protocols + env vars. New version = new deployment. |
| **Container image** | Your code packaged as a Linux x86_64 OCI image, pushed to ACR. |
| **Protocol** | The HTTP contract the container speaks: `responses`, `invocations`, `activity`, `a2a`. A single container can expose several. |
| **Session** | A logical unit of compute with persistent `$HOME` and `/files`. VM-isolated per session. |
| **Conversation** | Durable history (messages, tool calls, responses) stored in Foundry, independent of compute. |
| **Agent identity** | The agent's dedicated Microsoft Entra service principal — used for all runtime authentication. |
| **Project managed identity** | The Foundry project's system-assigned MI — used by the platform for infra (e.g., ACR pulls). Not for runtime. |
| **Toolbox** | A versioned MCP endpoint that exposes Foundry-managed tools to the agent. See the `foundry-toolboxes` skill. |
| **Sandbox** | The per-session VM-isolated runtime environment with a persistent filesystem. |

---

## Choose a Protocol

| Scenario | Protocol | Why |
|----------|----------|-----|
| Conversational chatbot or assistant | **Responses** | Platform manages conversation history, streaming events, and session lifecycle. Any OpenAI-compatible client works. |
| Multi-turn Q&A with RAG or tools | **Responses** | Built-in conversation ID threading and tool result handling. |
| Background / async processing that fits OpenAI Responses polling | **Responses** | `background: true` with platform-managed polling and cancellation. |
| Agent published to Teams or M365 | **Responses** + **Activity** | Responses handles agent logic; Activity handles the channel. |
| Webhook receiver (GitHub, Stripe, Jira) | **Invocations** | External system sends its own JSON shape — you can't change it. |
| Non-conversational processing (classification, extraction, batch) | **Invocations** | Arbitrary JSON in, arbitrary JSON out. |
| Custom streaming protocol (AG-UI, etc.) | **Invocations** | Raw SSE, no OpenAI-compatible framing required. |
| Protocol bridge / inter-service orchestration | **Invocations** | Caller owns the protocol contract. |
| Agent-to-agent delegation | **A2A** | Expose this agent for other agents to call. See "A2A Hosting" below. |

**Default to Responses when unsure.** A single container can expose several protocols simultaneously by declaring each one. Switching/adding protocols later is a new agent version, not a redeploy from scratch.

---

## Choose an Implementation Path

| Path | Use when | What you write |
|------|----------|----------------|
| **Microsoft Agent Framework** | Greenfield Python or C# agent that wants first-party Foundry integration, runtime MCP/Toolbox tools, OpenTelemetry out of the box. | Your `Agent` definition + a one-liner that runs it on the Responses host server. |
| **LangGraph / CrewAI / Pydantic AI / etc.** | You already have an existing graph or agent and want to keep it. | Your existing graph, wired into a `@response_handler` (Responses) or `@invoke_handler` (Invocations). |
| **BYO / custom** | Non-Python/.NET runtime, custom HTTP semantics, or a thin adapter over an internal service. | Either the Python/.NET protocol library, or a hand-rolled container that honors the protocol contract (request/response shape, `/readiness`, port 8088). |

For exact import paths and class names per language, search docs MCP for the Python or .NET protocol library. The skill avoids freezing language-specific syntax because these libraries are still moving.

---

## Sessions vs. Conversations

This is the most-confused pair in the hosted agents model. Read this twice.

| Aspect | **Session** | **Conversation** |
|--------|-------------|------------------|
| What it is | A logical unit of compute with persistent state | A durable record of message history |
| Where state lives | `$HOME` + `/files` on the per-session sandbox | Foundry-managed datastore |
| Tied to | Compute (provisioned on demand, deprovisioned on idle) | Identifier (`conversation_id`) — independent of compute |
| Idle behavior | Compute deprovisioned after **15 min** idle. State persisted and restored on next request. | Always available. |
| Maximum lifetime | **30 days** | No platform-imposed expiry |
| Isolation | VM-isolated per session | Logical record; not isolated compute |
| Primary in **Responses** | Auxiliary — platform creates one and returns its ID for `/files` uploads | **Primary concept.** Platform manages history automatically. |
| Primary in **Invocations** | **Primary concept.** Client manages the session ID. | Not used. You manage state in your own code. |

### Session compute lifecycle

| State | What happens |
|-------|--------------|
| **Active** | Compute is running. Requests are routed to it. `$HOME` and `/files` available. |
| **Idle** | No requests for 15 minutes. Compute deprovisioned. State persisted. |
| **Resumed** | Same session ID is referenced again. Platform provisions new compute and restores state. |

### Operational implications

- For a chatbot using **Responses**: pass `conversation_id` to thread turns. The platform stores history; **don't double-store** in your agent code.
- For a webhook on **Invocations**: pass `agent_session_id` so the platform routes to the same sandbox and your `$HOME` files are there.
- File uploads (`/files` endpoint) are always scoped to a **session ID**. To attach files to a Responses conversation, capture the session ID the platform returns and upload against it.
- Session quota during preview: **50 active concurrent sessions per subscription per region** (adjustable).

---

## azd-First Workflow

`azd ai agent` (extension `azure.ai.agents`) is the canonical lifecycle for a hosted agent. It handles project setup, container build/push, version creation, RBAC, and remote invocation in one tool.

```bash
# 0) One-time: install the Foundry agents extension
azd ext install azure.ai.agents

# 1) Scaffold a new agent from a manifest. -m IS REQUIRED.
azd ai agent init -m ./agent.manifest.yaml
# Do NOT add --no-prompt if your manifest declares {{ param }} secrets —
# --no-prompt skips secret prompts and silently leaves them empty.

# 2) Run the container locally on http://localhost:8088
azd ai agent run

# 3) Test the local container via the same protocol you'll use in prod
azd ai agent invoke --local "What can you do?"

# 4) Provision Foundry resources + deploy the version
azd up
# This builds linux/amd64, pushes to ACR, creates the agent version,
# waits for status=active, configures the dedicated endpoint, and
# assigns Azure AI User on the project to the agent's Entra identity.

# 5) Inspect the deployed agent
azd ai agent show --output table

# 6) Invoke the deployed agent through its dedicated endpoint
azd ai agent invoke "What can you do?"

# 7) Tail logs (Responses + Invocations + readiness probes)
azd ai agent monitor --tail 20

# 8) Tear down
azd down
```

`azd ai agent show` and `azd ai agent monitor` read the agent name and version from the `azd` service entry in `azure.yaml` — they don't take an explicit name flag.

For unattended pipelines, supply secrets and parameters via `azd env set` before `azd ai agent init -m` so prompts have answers; `--no-prompt` is **not** the same as supplying values.

---

## agent.manifest.yaml vs agent.yaml

Two YAMLs, two different jobs. Don't conflate them.

### `agent.manifest.yaml` — scaffolding input

Consumed by `azd ai agent init -m`. Declares the **template**, the **`{{ param }}` placeholders** azd will prompt for, and the **resources** azd should provision (model deployments, connections, toolboxes). Lives in the sample/template repo, not in your deployed agent.

```yaml
name: basic-responses-agent
description: A hosted agent using the Responses protocol.
template:
  name: basic-responses-agent
  kind: hosted
  protocols:
    - protocol: responses
      version: 1.0.0
  environment_variables:
    - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
      value: "{{AZURE_AI_MODEL_DEPLOYMENT_NAME}}"
resources:
  - kind: model
    id: gpt-4.1-mini
    name: AZURE_AI_MODEL_DEPLOYMENT_NAME
```

### `agent.yaml` — deployed agent version

Generated by `azd ai agent init` and shipped with your container source. It is the **agent version definition**: the protocols the container exposes, the resource sizing, and the (non-secret) environment variables for the container.

```yaml
kind: hosted
name: basic-responses-agent
protocols:
  - protocol: responses
    version: 1.0.0
resources:
  cpu: "0.25"
  memory: "0.5Gi"
environment_variables:
  - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
    value: gpt-4.1-mini
```

**Protocol version is `1.0.0`, not `v1`.** This is the protocol contract version inside the YAML. It is independent of the REST `?api-version=v1` query string — see Critical Gotchas.

To expose multiple protocols from the same container, list each entry under `protocols:`:

```yaml
protocols:
  - protocol: responses
    version: 1.0.0
  - protocol: invocations
    version: 1.0.0
```

`tools:` does **not** belong in `agent.yaml`. Tool wiring lives on a Toolbox MCP endpoint that your container connects to at runtime (see the `foundry-toolboxes` skill).

---

## Agent Identity & Endpoint

### Two identities — runtime vs. infra

| Identity | Created by | Used for |
|----------|-----------|----------|
| **Agent's dedicated Microsoft Entra ID** | Foundry, automatically at deploy time | **Runtime auth.** Model invocation, tool access, downstream Azure resources, on-behalf-of for M365. |
| **Project managed identity** | The Foundry project resource | **Platform infrastructure only.** ACR Repository Reader for image pulls. Never the agent's runtime principal. |

When you deploy with azd, the role **Azure AI User** at account scope is auto-assigned to the agent's Entra ID. For any **external** resource (your Storage account, Cosmos DB, Key Vault, etc.), you assign RBAC manually to the agent's Entra ID — not to the project MI. Use `--assignee-object-id <principal-id> --assignee-principal-type ServicePrincipal` when calling `az role assignment create` to avoid Microsoft Graph lookup issues with agent identity service principals.

To retrieve the agent's principal ID after deploy, GET the agent and read `instance_identity.principal_id` (REST or SDK).

### Endpoint shape — be precise

Each agent gets a dedicated endpoint under the project:

```
Responses:    {project_endpoint}/agents/{name}/endpoint/protocols/openai/v1/responses
Invocations:  {project_endpoint}/agents/{name}/endpoint/protocols/invocations
Sessions:     {project_endpoint}/agents/{name}/endpoint/sessions
```

- The **Responses path includes `openai/v1`**. The shorthand `/protocols/responses` you may see in older snippets is wrong for this surface.
- All data-plane calls take `?api-version=v1` (this is the REST API version, not the protocol version).
- For REST callers, the `Foundry-Features: HostedAgents=V1Preview` header is mandatory during preview. SDK clients add it automatically.
- For `az rest`, you must pass `--resource https://ai.azure.com` so the correct audience is used; otherwise auth fails.

---

## Multi-Protocol Agents

A single container can expose several protocols. Declare each in `agent.yaml` (or `container_protocol_versions` for SDK/REST), and import each protocol library in your container.

```yaml
protocols:
  - protocol: responses
    version: 1.0.0
  - protocol: invocations
    version: 1.0.0
  - protocol: activity      # Teams / M365 channel adapter
    version: 1.0.0
  - protocol: a2a           # agent-to-agent host endpoint
    version: 1.0.0
```

In your container code, register handlers for each protocol on the same host process so they share state and a single `/readiness` probe. The Foundry gateway routes by URL path. A typical multi-protocol composition uses one host class that subclasses both `ResponsesAgentServerHost` and `InvocationAgentServerHost` (Python) or composes the equivalent ASP.NET extension methods (.NET). Confirm the exact composition pattern in the protocol-library docs before generating code.

---

## A2A Hosting

The Agent-to-Agent (A2A) protocol turns your hosted agent into an **endpoint other agents can call**. It is the *server* side of agent delegation; the *client* side (consuming a remote A2A agent as a tool) is covered in `foundry-toolboxes`.

**When to expose A2A from your hosted agent:**

- You're building a specialist agent (e.g., "tax-calc agent", "PII redactor") that other agents in your org should reuse.
- You want a stable contract that survives the calling agent being rewritten.
- You want the calling side to discover capabilities through an A2A agent card rather than an arbitrary OpenAPI schema.

**To enable A2A hosting:**

1. Add the A2A protocol library to your container (see docs MCP for the current package name per language).
2. Declare `- protocol: a2a, version: 1.0.0` in `agent.yaml` alongside your Responses or Invocations entry.
3. Implement the A2A handler your library exposes; supply the agent card metadata (name, description, capabilities) it requires.
4. Redeploy. The A2A endpoint becomes available at the agent's dedicated endpoint URL under `/protocols/a2a`.

**Cross-links:**

- `foundry-toolboxes` — how *consumers* call your A2A agent as a tool from another agent.
- `foundry-workflows` — when to choose a multi-agent workflow over an A2A tool call (declarative orchestration vs. runtime delegation).

A2A intentionally does not get a standalone skill: hosting is here, consumption is in `foundry-toolboxes`, and orchestration is in `foundry-workflows`.

---

## Container Contract

These constraints apply to every hosted agent container, regardless of language or framework:

- **Architecture:** Linux **x86_64** (`linux/amd64`). On Apple Silicon, build with `docker build --platform linux/amd64 .` or you'll produce an unrunnable ARM image that the platform will refuse.
- **Port:** Serve on **port 8088** locally. The Foundry gateway handles production routing — your container doesn't need a public port.
- **Health:** The protocol library exposes `/readiness`. **Don't hand-roll it.** A missing or non-200 readiness probe fails the version provisioning.
- **Protocol endpoints:** The library handles `/responses`, `/invocations`, `/files`, etc. You register handlers; you don't write the HTTP layer.
- **Identity:** Authenticate to all downstream services with the agent's Entra identity (`DefaultAzureCredential` or equivalent). Never use the project MI from inside the container.
- **No secrets in the image or environment variables.** Use Foundry connections + Key Vault. Environment variables are immutable per version — leaking one means rotating and redeploying.
- **Platform-injected env vars** (read-only, do not redeclare in `agent.yaml`): `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_PROJECT_ARM_ID`, `FOUNDRY_AGENT_NAME`, `FOUNDRY_AGENT_VERSION`, `FOUNDRY_AGENT_SESSION_ID`, `APPLICATIONINSIGHTS_CONNECTION_STRING`. The `FOUNDRY_*` prefix is reserved.
- **Sandbox sizing:** CPU 0.25–2 vCPU, memory 0.5–4 GiB. Set in `agent.yaml` `resources:` or the SDK `cpu`/`memory` fields.
- **State:** `$HOME` and `/files` persist across the 15-min idle deprovisioning. Anything elsewhere on disk is gone.

---

## Direct SDK / REST Deployment

Use this path when you can't use `azd` (CI pipelines outside azd, integration with platform tooling, or programmatic version management). For the first-time path, prefer `azd up`.

**Python SDK** (`azure-ai-projects ≥ 2.1.0`):

- Create the project client with `allow_preview=True`.
- Call `project.agents.create_version(...)` with `HostedAgentDefinition(container_protocol_versions=[ProtocolVersionRecord(protocol=..., version="1.0.0")], image=..., cpu=..., memory=..., environment_variables={...})`.
- Poll `project.agents.get_version(...)` until `status == "active"` (typically 2–5 min).
- For Responses, get an OpenAI-compatible client via `project.get_openai_client(agent_name="...")`.
- Session/files APIs live under `project.beta.agents.*` (preview).

**REST** (HTTP):

- Base URL: `https://{account}.services.ai.azure.com/api/projects/{project}`.
- Use `?api-version=v1` on every call.
- Use `Authorization: Bearer <token>` from the `https://ai.azure.com/.default` scope.
- **Add `Foundry-Features: HostedAgents=V1Preview` to every request.** SDK clients add it for you; raw REST callers must add it.
- Or use `az rest --resource https://ai.azure.com --headers "Foundry-Features=HostedAgents=V1Preview" ...`.

For full request bodies and field names, search docs MCP for the deploy and manage articles — those are the only authoritative sources for the current schema.

---

## Critical Gotchas — Do Not Confuse

| ✗ Do not confuse | ✓ Correct understanding |
|---|---|
| Protocol `version: 1.0.0` ≠ REST `?api-version=v1` | Protocol version is the contract spoken inside `agent.yaml`. API version is the REST API surface. They evolve independently — show both. |
| `/protocols/openai/v1/responses` ≠ `/protocols/responses` | The full Responses path includes `openai/v1`. The short form is wrong for this preview. Invocations remains `/protocols/invocations`. |
| `Foundry-Features` is a REST trap, not a generic SDK rule | SDK clients add it automatically. Raw REST or `az rest` callers must add `HostedAgents=V1Preview` manually. |
| Agent's Entra ID ≠ Project managed identity | Agent identity = runtime auth (models, tools, downstream). Project MI = platform infra (e.g., ACR pulls). RBAC for your Storage/Cosmos goes on the **agent identity**. |
| Session ≠ Conversation | Session = compute, 15-min idle, 30-day max, primary for Invocations. Conversation = durable history in Foundry, primary for Responses. |
| `azd ai agent init -m` ≠ `azd ai agent init --no-prompt` | `-m` points to the manifest and is **required**. `--no-prompt` skips prompts and silently leaves `{{ param }}` secrets empty. Don't combine them unless secrets are pre-set in the env. |
| `tools=[...]` in agent definition is GONE | Tools live on a versioned **Toolbox** (MCP endpoint) the agent connects to at runtime. Do not put a tools array in `agent.yaml` or `HostedAgentDefinition`. |
| `/readiness` is library-provided | Don't write your own. A custom or missing `/readiness` fails provisioning. |
| `latest` tag in production | Use immutable image tags (`:1.2.3`, `:<git-sha>`). The platform takes a version snapshot — `latest` defeats reproducibility. |
| Storing conversation history in Responses agents | Responses platform stores it. Storing it again in your agent code (e.g., `store=True` in client options) duplicates state and confuses traces. |

---

## Common Errors

| Error / symptom | Cause | Fix |
|---|---|---|
| `preview_feature_required` | REST call missing the preview feature header | Add `Foundry-Features: HostedAgents=V1Preview`. Verify SDK client is current. |
| `image_pull_failed` / `AcrImageNotFound` / `InvalidAcrPullCredentials` (401) / `UnauthorizedAcrPull` (403) | Wrong image URL/tag, or the project MI lacks ACR pull access (or the assignment hasn't propagated) | Use immutable tags. Grant **Container Registry Repository Reader** (or **AcrPull**) to the project MI on the registry. Re-check scope and wait for propagation. |
| Agent works locally but not in Foundry | Built an ARM image on Apple Silicon, or referenced a missing env var | Build with `--platform linux/amd64`. Declare custom env vars in `agent.yaml`. |
| `PermissionDenied` calling models or tools at runtime | Agent's Entra identity lacks RBAC | Grant **Azure AI User** on the project (azd does this) and any external-resource roles (e.g., **Storage Blob Data Contributor**) on the **agent identity**, not the project MI. |
| Provisioning stays in `creating`, then `failed` with no obvious cause | `/readiness` not exposed (custom HTTP server) or container crashes on startup | Use the protocol library to serve. Run `docker run` locally, hit `http://localhost:8088/readiness`, fix any startup error. |
| Conversation history duplicated | Agent stores history while the Responses platform also stores it | Disable client-side history storage (e.g., `store=False`) for Agent Framework / OpenAI clients running inside a Responses host. |
| `az rest` returns 401 against the data plane | Missing `--resource` parameter | Add `--resource https://ai.azure.com` so the correct AAD audience is requested. |
| Sessions hit per-region quota | Default 50 active sessions per subscription per region during preview | Open a quota request via Microsoft Support; consider grouping work into fewer sessions. |

---

## Migration from Initial-Preview Hosted Agents

The initial-preview hosted-agents backend is being retired. New work should not use `ImageBasedHostedAgentDefinition`, capability hosts, protocol `version="v1"`, `tools=[...]` inside the agent definition, shared project MI for runtime, or `agent_reference` invocation routing. The forward path is everything in this skill: `HostedAgentDefinition` + `container_protocol_versions`, protocol version `1.0.0`, dedicated agent Entra identity, dedicated endpoint, and Toolboxes for tool wiring.

**Migration checklist:**

- [ ] Replace `ImageBasedHostedAgentDefinition` with `HostedAgentDefinition` + `container_protocol_versions`.
- [ ] Change protocol `version` from `"v1"` to `"1.0.0"`.
- [ ] Remove `tools=[...]` from agent definitions; move tools to a Toolbox (see `foundry-toolboxes`).
- [ ] Remove capability host creation / start / stop / replica scaling code.
- [ ] Replace shared-project invocation with the per-agent dedicated endpoint or `project.get_openai_client(agent_name=...)`.
- [ ] Reassign downstream resource RBAC from the project MI to the agent's Entra identity.
- [ ] Redeploy with `azd up` or `create_version`; wait for `status == "active"`.

Full migration guide: <https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-hosted-agent-preview>

---

## Reference Links

| Resource | URL |
|----------|-----|
| Hosted agents concepts | <https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents> |
| Deploy a hosted agent | <https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent> |
| Manage hosted agents | <https://learn.microsoft.com/azure/foundry/agents/how-to/manage-hosted-agent> |
| Manage hosted agent sessions | <https://learn.microsoft.com/azure/foundry/agents/how-to/manage-hosted-agent-sessions> |
| Quickstart: create and deploy a hosted agent | <https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent> |
| Hosted agent permissions reference | <https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions> |
| Agent identity concepts | <https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity> |
| Migration from initial-preview hosted agents | <https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-hosted-agent-preview> |
| Foundry samples (hosted agents) | <https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents> |
| `azd ai agent` extension reference | Run `azd ai agent --help` for the current command surface |

**Companion skills:** `foundry-toolboxes` (wire Foundry-managed tools incl. A2A consumption, Browser Automation, Computer Use), `foundry-workflows` (workflow vs. A2A call for multi-agent orchestration), `foundry-projects-resources` (project, connections, networking), `foundry-observability` (tracing, App Insights/KQL, evals, `azd ai agent monitor`).
