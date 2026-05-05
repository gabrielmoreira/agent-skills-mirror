---
name: foundry-toolboxes
description: |
  Curate intent-based Foundry Toolboxes (preview) — a single MCP-compatible endpoint that bundles tools (MCP, Web Search, Azure AI Search, Code Interpreter, File Search, OpenAPI, A2A, Browser Automation, Computer Use) for any agent to consume. Centrally configured, governed, versioned. Build once, consume everywhere.
  Triggers: "toolbox", "Foundry toolbox", "intent-based toolbox", "create_toolbox_version", "toolbox MCP endpoint", "toolbox version", "Foundry-Features Toolboxes=V1Preview", "MCP tool", "azure_ai_search tool", "web_search tool", "code_interpreter tool", "file_search tool", "openapi tool", "a2a tool", "agent.yaml resources toolbox".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Toolboxes

Foundry Toolboxes (preview) let you curate a reusable, governed set of tools — APIs, MCP servers, Azure AI Search indexes, Code Interpreter, File Search, OpenAPI, agent-to-agent links, browser/computer-use tools — and expose them through a **single MCP endpoint** that any agent can consume. Build once, consume everywhere; the platform handles credential injection, token refresh, and policy enforcement at runtime. This skill covers the conceptual model, every tool type, endpoint patterns, versioning, `azd` authoring, and the non-obvious traps. It is **language-agnostic** — defer SDK call syntax to the docs MCP.

## Before You Build — Discovery (MANDATORY)

Toolboxes are a fast-moving preview. Always confirm current shape before generating code.

**Microsoft Docs MCP queries (run first):**

- `Foundry intent-based toolbox`
- `Foundry toolbox tool types configure`
- `Foundry toolbox versioning default version`
- `agent.yaml resources toolbox kind` and `agent.yaml kind connection authType`
- Per tool type, when relevant: `Foundry web search tool`, `Foundry Azure AI Search tool`, `Foundry MCP tool`, `Foundry code interpreter tool`, `Foundry file search tool`, `Foundry OpenAPI tool`, `Foundry agent-to-agent tool`, `Foundry browser automation tool`, `Foundry computer use tool`
- For region/model fit: `Foundry tool best practice` (canonical: <https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice>)

**Foundry MCP discovery:**

- Connect to `mcp.ai.azure.com` (Foundry MCP) and list its `toolbox*` operations to confirm current REST surface (`toolboxes/{name}/versions`, `toolboxes/{name}/mcp`, etc.).
- Use the developer endpoint with an MCP client SDK to call `tools/list` and `tools/call` against any toolbox before integrating it.

**`azd ai agent` discovery (declarative path):**

- `azd extension install azure.ai.agents`
- `azd ai agent --help`, `azd ai agent init --help` — confirm the current `-m / --manifest` flag and post-init env vars
- Declare toolboxes via `agent.yaml` `resources:` and run `azd ai agent init -m <manifest>` → `azd provision` → `azd deploy`. Bicep is generated for you; no separate SDK calls needed.

> **Stop and confirm versions** before writing code. Tool type names (e.g., `a2a_preview`), the `Foundry-Features` header value, and `api-version` query parameters all change between previews.

## Mental Model

```
        ┌──────────────────────────────────────────────┐
        │  Tools (managed centrally in Foundry)        │
        │                                              │
        │  • Web Search       • Azure AI Search        │
        │  • MCP server       • Code Interpreter       │
        │  • File Search      • OpenAPI                │
        │  • A2A              • Browser Automation     │
        │  • Computer Use                              │
        └──────────────────────────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │  Toolbox Version (vN)    │   immutable snapshot
              │  description + tools[]   │   policies, approval rules
              └──────────────────────────┘
                            │
                 default_version pointer
                            ▼
              ┌──────────────────────────┐
              │  Toolbox (named)         │   served at:
              │  default_version = vN    │   /toolboxes/{name}/mcp
              └──────────────────────────┘
                            │
                            ▼  Single MCP endpoint
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │  Agent A   │  │  Agent B   │  │  IDE / CLI │
        └────────────┘  └────────────┘  └────────────┘
```

**Key terms:**

| Term | Meaning |
|---|---|
| **Toolbox** | Named, mutable container. Has a `default_version` pointer. |
| **Toolbox Version** | Immutable snapshot: `tools[]` + descriptions + per-tool config (e.g., `require_approval`). Created via `create_toolbox_version`. |
| **Default Version** | The version served at the consumer endpoint. First version auto-promotes to v1; you promote subsequent versions explicitly. |
| **Tool** | One entry in `tools[]` with a `type` and per-type config. Carries an optional `name` (required when there are multiple of the same type). |
| **Tool Type** | One of `web_search`, `azure_ai_search`, `code_interpreter`, `file_search`, `mcp`, `openapi`, `a2a_preview`, `browser_automation`, `computer_use` (verify exact strings via docs MCP). |
| **MCP Endpoint** | The single HTTPS URL agents call. Speaks the MCP streamable-HTTP protocol. |
| **Project Connection** | A Foundry connection resource (key, OAuth, agent identity, user Entra token) referenced by `project_connection_id` from a tool. |
| **Allowed Tools** | Optional `allowed_tools: [...]` filter on an MCP entry that whitelists only certain remote tool names. |
| **Server Label** | Required short prefix for an MCP entry; remote tool names are exposed as `{server_label}.{remote_tool_name}`. |

## When to Use Toolboxes vs Inline Tools

For the refreshed Foundry hosted agents preview, **inline tools (`tools=[...]` in agent code) are gone — toolboxes are the path forward.** Hosted agents discover and call tools through the toolbox MCP endpoint that the platform injects at runtime; they do not embed tool definitions in the container.

| You want… | Use a toolbox when… | Use ad-hoc / inline tooling when… |
|---|---|---|
| Reusable across agents | ✅ Always — toolboxes are the unit of reuse and governance | ❌ Forces every agent to re-implement and re-credential |
| Versioning + safe rollout | ✅ Promote a new version with no agent redeploy | ❌ Code change required for every tool tweak |
| Centralized credentials/policies | ✅ Connections live in Foundry, not in agent code | ❌ Secrets sprawl |
| Local prototyping with one tool | Optional — toolboxes still work fine | ✅ Acceptable; migrate to a toolbox before sharing |

## Tool Types

Each tool type below is described with its purpose, key fields, and the `agent.yaml` shape under `resources: - kind: toolbox`. For SDK syntax in any language, query the docs MCP.

### Model Context Protocol (MCP)

Adds a remote MCP server's tools to the toolbox. Tool names are exposed as `{server_label}.{remote_tool_name}`.

**Auth modes** — pick by the `authType` of the connection you reference via `project_connection_id`:

- **No auth** — public MCP server: omit `project_connection_id`.
- **Key-based** — `kind: connection` with `authType: CustomKeys`, e.g. `Authorization: "Bearer {{ api_key }}"`.
- **OAuth (managed connector)** — `authType: OAuth2` + `connectorName: <foundry-managed-connector>`.
- **OAuth (custom app reg)** — `authType: OAuth2` + `authorizationUrl`, `tokenUrl`, `clientID`, `clientSecret`.
- **Entra agent identity** — `authType: AgenticIdentity` + `audience`. Assign the agent's identity the right RBAC role on the target.
- **User Entra token (1P OBO)** — `authType: UserEntraToken` + `audience` (audience is **required** or `tools/list` returns zero tools).

**Useful fields:** `require_approval: "always" | "never"` (agent-enforced, not server-blocked); `allowed_tools: [...]` to whitelist a subset of remote tools.

```yaml
- kind: toolbox
  name: agent-tools
  tools:
    - type: mcp
      server_label: github
      server_url: https://api.githubcopilot.com/mcp
      project_connection_id: github-mcp-conn
      require_approval: never
      # allowed_tools: [list_repos, get_pull_request]
```

### Web Search

Grounded web search powered by Grounding with Bing Search (or Grounding with Bing **Custom** Search via a `bing_custom_search` connection). No connection needed for the default Bing experience.

URL citations are returned in `content[].resource._meta.annotations[]`. Web Search incurs separate Grounding-with-Bing costs and is governed by separate terms (data leaves compliance/geographic boundaries).

```yaml
- kind: toolbox
  name: websearch-tools
  tools:
    - type: web_search
      # description: "Search the web for current events"
```

### Azure AI Search

Searches one or more Azure AI Search indexes, returning chunks with `title`, `url`, `id`, `score` in `result.structuredContent.documents[]`.

Required: `index_name`, `project_connection_id` (pointing to a Foundry connection of category `CognitiveSearch`). Optional: `top_k` (default 5), `query_type` (default `vector_semantic_hybrid`; choices: `simple`, `vector`, `semantic`, `vector_simple_hybrid`, `vector_semantic_hybrid`), `filter`.

```yaml
- kind: connection
  name: aisearch-conn
  category: CognitiveSearch
  authType: ApiKey
  target: https://<search>.search.windows.net/
  credentials: { key: "{{ ai_search_key }}" }
- kind: toolbox
  name: search-tools
  tools:
    - type: azure_ai_search
      name: product-search
      index_name: products-v2
      project_connection_id: aisearch-conn
```

### Code Interpreter

Lets the model write and execute Python in a managed sandbox. No connection required. Optional `container.file_ids: [...]` pre-loads files (upload via `POST {project_endpoint}/openai/v1/files?purpose=assistants`). Output files are listed via `GET /containers/{container_id}/files` and downloaded via the File API.

> **Important:** When called through a toolbox in a hosted agent, **per-user isolation is not supported** — all callers in the project share container context. Treat output files as project-scoped.

```yaml
- kind: toolbox
  name: codeinterp-tools
  tools:
    - type: code_interpreter
```

### File Search

Vector-store-backed search over uploaded documents. Provide `vector_store_ids: [...]` referencing vector stores you created via `POST {project_endpoint}/openai/v1/vector_stores`. Chunk metadata (`title`, `file_id`, `document_chunk_id`, `score`) is embedded in each result item under `_meta`, plus `【index†filename†file_id】` markers in text.

> **Important:** Same isolation caveat as Code Interpreter — when used through a toolbox in a hosted agent, **all users share the vector store**.

```yaml
- kind: toolbox
  name: filesearch-tools
  tools:
    - type: file_search
      vector_store_ids:
        - ${FILE_SEARCH_VECTOR_STORE_ID}
```

### OpenAPI

Exposes any REST API described by an OpenAPI 3.0/3.1 spec. Provide `openapi.name`, `openapi.spec` (inline JSON object — `spec_uri` is also supported in some surfaces; verify via docs MCP), and `openapi.auth`.

**Auth shapes:**

- `auth.type: anonymous` — no auth.
- `auth.type: connection` (REST) / `connection_auth` (azd) — `security_scheme.project_connection_id: <connection>` for key/OAuth/cert via a Foundry connection.
- `auth.type: managed_identity` — Foundry project's managed identity calls the API. Assign the project MI the right RBAC role on the target, or you get `401`.

```yaml
- kind: toolbox
  name: openapi-tools
  tools:
    - type: openapi
      openapi:
        name: my-api
        spec: { openapi: "3.0.1", info: { title: My API, version: "1.0" }, paths: { /search: { get: { operationId: search, parameters: [...], responses: { "200": { description: OK } } } } } }
        auth: { type: connection_auth, connection_id: api-conn }
```

### Agent-to-Agent (A2A)

> **Cross-link:** A2A in a toolbox is the **consumer side** — your agent calls another agent as a tool. To **host** an A2A endpoint, see the **`foundry-hosted-agents`** skill (A2A hosting subsection: agent identity, protocol, exposed routes).

Use the A2A tool to delegate to a specialist agent. Provide `base_url` (the remote agent's HTTPS root) and, if it requires auth, `project_connection_id` of category `RemoteA2A`. Tool `type` is `a2a_preview` during preview — confirm via docs MCP.

`tools/call` argument shape: `{"message": {"parts": [{"type": "text", "text": "..."}]}}`.

```yaml
- kind: connection
  name: a2a-conn
  category: RemoteA2A
  authType: None
  target: https://your-remote-agent.azurecontainerapps.io
- kind: toolbox
  name: a2a-tools
  tools:
    - type: a2a_preview
      name: research-specialist
      description: "Delegate deep research questions"
      base_url: https://your-remote-agent.azurecontainerapps.io
      project_connection_id: a2a-conn
```

### Browser Automation

Headless browser tool for the agent to navigate, click, fill forms, and read pages. Runs in a **sandboxed**, Microsoft-managed environment.

> **Security note:** Browser Automation can fetch arbitrary URLs and execute scripts as part of page rendering. Treat it as an untrusted execution surface — never combine it with a freely written-to memory store, and prefer `require_approval: "always"`-style human-in-the-loop gating for sensitive sessions. Verify regional availability and current parameter shape via the docs MCP query `Foundry browser automation tool`. See <https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice>.

### Computer Use

A computer-use tool gives the agent vision + mouse/keyboard control over a sandboxed virtual desktop, typically backed by a model variant trained for computer-use grounding (availability is constrained — not every region/model supports it).

> **Security note:** Same untrusted-surface posture as Browser Automation, plus **model availability constraints** — a project region that supports the toolbox endpoint may not support computer use. Confirm via docs MCP queries `Foundry computer use tool` and `Foundry tool best practice` before declaring this tool. Pair with strict `require_approval` gating in your agent runtime.

## Multi-Tool Restrictions

A single toolbox can include **at most one unnamed instance per tool type**. Add a unique `name` field to each subsequent instance of the same type, or the API returns:

```
400 invalid_payload: Multiple tools without identifiers found...
```

```yaml
tools:
  - type: azure_ai_search
    name: product-search        # unique name → OK
    azure_ai_search: { indexes: [{ index_name: products, project_connection_id: search-conn }] }
  - type: azure_ai_search
    name: support-search        # second of same type, also named → OK
    azure_ai_search: { indexes: [{ index_name: support, project_connection_id: search-conn }] }
```

Always add a `description` to each tool — the model uses descriptions to choose the right tool for a request.

## Endpoint Patterns

There are exactly two MCP endpoints and they serve different audiences. **Get them wrong and either your tests hit production or your agents pin to a stale version.**

| Role | Endpoint | When to use |
|---|---|---|
| **Toolbox developer** | `{project_endpoint}/toolboxes/{toolbox_name}/versions/{version}/mcp?api-version=v1` | Validate a specific version *before* promoting it to default. |
| **Toolbox consumer** | `{project_endpoint}/toolboxes/{toolbox_name}/mcp?api-version=v1` | What every agent calls. Always serves `default_version`. |

> **Do Not Forget — required header on every request:**
>
> ```
> Foundry-Features: Toolboxes=V1Preview
> ```
>
> Calls that omit this header **fail**. Some SDKs add it automatically (e.g., `langchain_azure_ai.tools.AzureAIProjectToolbox`); raw HTTP, REST tools, and many MCP clients do not. Set it in every HTTP client, MCP transport, or SDK wrapper that touches the toolbox endpoint.

Auth: bearer token from Microsoft Entra; **scope `https://ai.azure.com/.default`**. Wrong scope → `401`.

## Versioning + Default Promotion

Toolbox versions are **immutable snapshots**. Each `create_toolbox_version` call mints a new `ToolboxVersionObject`; the parent `ToolboxObject.default_version` decides which version the consumer endpoint serves.

**Lifecycle:**

1. **Create v1** — auto-promotes to `default_version` (this is the only auto-promotion).
2. **Create v2** — does *not* auto-promote. Consumer endpoint still serves v1.
3. **Validate v2** by hitting `/versions/v2/mcp` (developer endpoint) with `tools/list` and `tools/call`.
4. **Promote** by `PATCH {project_endpoint}/toolboxes/{name}` with `{"default_version": "v2"}`. `default_version` cannot be empty — only replaced.
5. **All consuming agents pick up v2 with no code change and no redeploy.** That is the entire point.

`azd` only supports **creating** versions during deploy. Use Python/.NET/JS/REST SDKs for list/get/promote/delete.

## CLI-First Authoring (azd)

Declare toolboxes (and their connections) in `agent.yaml` and let `azd ai agent` generate Bicep, create connections, build the container, register the agent version, and create the toolbox in one workflow.

**Folder layout** (under a `manifest/` directory referenced via `-m manifest/`):

```
my-agent/
└── manifest/
    ├── agent.yaml          # template + parameters + resources
    ├── main.py             # agent entry point
    ├── requirements.txt
    └── Dockerfile
```

**`agent.yaml`** — connection + toolbox combining `web_search`, `mcp` (key-auth), and `azure_ai_search`:

```yaml
kind: hosted
name: my-toolbox-agent
template:
  kind: hosted
  protocols:
    - { protocol: responses, version: 1.0.0 }
  environment_variables:
    - { name: AZURE_AI_MODEL_DEPLOYMENT_NAME, value: ${AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o} }
    - { name: TOOLBOX_NAME,                   value: ${TOOLBOX_NAME=agent-tools} }
parameters:
  github_pat:    { secret: true, description: GitHub PAT for the GitHub MCP server }
  ai_search_key: { secret: true, description: Azure AI Search admin key }
resources:
  - kind: connection
    name: github-mcp-conn
    target: https://api.githubcopilot.com/mcp
    category: RemoteTool
    authType: CustomKeys
    credentials: { keys: { Authorization: "Bearer {{ github_pat }}" } }
  - kind: connection
    name: aisearch-conn
    target: https://my-search.search.windows.net/
    category: CognitiveSearch
    authType: ApiKey
    credentials: { key: "{{ ai_search_key }}" }
  - kind: toolbox
    name: agent-tools
    description: Web search, GitHub MCP, and product index
    tools:
      - type: web_search
      - type: mcp
        server_label: github
        server_url: https://api.githubcopilot.com/mcp
        project_connection_id: github-mcp-conn
      - type: azure_ai_search
        name: product-search
        index_name: products
        project_connection_id: aisearch-conn
```

**Deploy:**

```bash
azd ai agent init -m manifest/ --project-id "$PROJECT_ID" -e my-env
# Interactive secret prompts happen here. Do NOT pass --no-prompt or
# {{ param }} values stay empty.
azd env set enableHostedAgentVNext "true" -e my-env
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME "gpt-4o" -e my-env
azd provision -e my-env       # creates connections via Bicep
azd deploy   -e my-env        # creates toolbox version + container + agent version
azd ai agent invoke --new-session "list me 5 PRs in the foundry repo" --timeout 120
```

## Connecting an Agent to a Toolbox

For **hosted agents**, the platform injects:

- `FOUNDRY_AGENT_TOOLBOX_ENDPOINT` — base URL of the toolbox MCP endpoint.
- `TOOLBOX_{TOOLBOX_NAME}_MCP_ENDPOINT` — the full per-toolbox endpoint (uppercased name). E.g., toolbox `agent-tools` → `TOOLBOX_AGENT_TOOLS_MCP_ENDPOINT`.

Your agent connects with any MCP streamable-HTTP client (e.g., `MCPStreamableHTTPTool` in Microsoft Agent Framework, `AzureAIProjectToolbox` in LangChain Azure AI, raw `mcp.client.streamable_http.streamablehttp_client`, or the .NET / JS MCP client SDKs). The auth pattern is identical across SDKs:

1. Acquire an Entra token with scope `https://ai.azure.com/.default` (use `DefaultAzureCredential` in production).
2. Include `Authorization: Bearer <token>` and `Foundry-Features: Toolboxes=V1Preview` on every request.
3. `initialize` → `tools/list` → `tools/call` (always with `stream=True`).
4. Pass MCP tools to your model loop. Tool names from MCP servers come back prefixed (`myserver.get_info`); some frameworks (e.g., the Copilot SDK) require a `.` → `_` rewrite.

**Read tool approval policy** from each `tools/list` entry's `_meta.tool_configuration.require_approval`. If `"always"`, your runtime must gate the call with human confirmation — the toolbox MCP proxy itself does **not** block.

## Critical Gotchas — Do Not Confuse

1. **`Foundry-Features: Toolboxes=V1Preview` on every request.** Missing → request fails. SDKs vary on whether they inject it; raw HTTP and REST always need it.
2. **Tool names are prefixed with `server_label`** for MCP entries (`github.list_repos`, not `list_repos`). Other tool types use the `name` field or the default tool name.
3. **`tools/call` must use streaming.** Non-streaming returns `500`. Always pass `stream=True` (or framework equivalent).
4. **`prompts/list` is not implemented.** Pass `load_prompts=False` (or equivalent) to your MCP client constructor; otherwise it `500`s on connect.
5. **`send_ping()` is not implemented.** If your framework auto-pings (e.g., Microsoft Agent Framework's `MCPStreamableHTTPTool._ensure_connected()`), disable or no-op it; otherwise it `500`s.
6. **Do not prefix custom env vars with `FOUNDRY_`.** The platform reserves that prefix and may silently overwrite. Use `TOOLBOX_…` or any non-`FOUNDRY_` name.
7. **Multiple unnamed tools of the same type → `400 invalid_payload: Multiple tools without identifiers`.** Add `name` to all but at most one per type.
8. **Tool descriptions matter.** The model picks tools by description. Empty or duplicated descriptions cause poor selection — always set `description` per tool.
9. **`require_approval` is agent-enforced, not server-enforced.** The toolbox proxy will execute `tools/call` regardless. Read the value at startup from `tools/list` and gate in your runtime.
10. **Token scope is `https://ai.azure.com/.default`.** Using a different scope returns `401`.
11. **`UserEntraToken` connections require `audience`** or `tools/list` returns zero tools.
12. **Code Interpreter and File Search through a hosted-agent toolbox have no per-user isolation** — files and vector stores are project-shared.

## Common Errors

| Symptom | Likely cause | Fix |
|---|---|---|
| `tools/list` returns 0 tools (MCP / A2A) | Bad/missing connection credentials, wrong RBAC for managed identity / agent identity | Verify `project_connection_id`, test the MCP/A2A target directly, confirm RBAC on target |
| `tools/list` returns 0 tools (OpenAPI) | Invalid OpenAPI 3.0/3.1 spec | Validate `paths`, `operationId`, parameter schemas; for managed-identity auth, confirm RBAC |
| Fewer tools than expected | `allowed_tools` misspelled (case-sensitive, MCP naming rules) | Drop `allowed_tools`, run `tools/list`, copy exact names back |
| `400 invalid_payload: Multiple tools without identifiers` | Two unnamed tools of same type | Add `name` to all but one per type |
| `CONSENT_REQUIRED` (`-32006`) | OAuth-based MCP needs first-time user consent | Open the URL in `error.message`, complete OAuth, retry |
| `401 Unauthorized` on MCP endpoint | Expired token or wrong scope | Refresh token with scope `https://ai.azure.com/.default` |
| `500` on `tools/call` | Non-streaming mode | Use `stream=True` |
| `500` on `prompts/list` / `send_ping()` | Unimplemented MCP methods | Disable both in client |
| Env vars overwritten at runtime | Custom var prefixed `FOUNDRY_` | Rename without that prefix |
| `tools/list` 0 tools (built-in) right after create | Toolbox not yet provisioned | Wait ~10s and retry |

## Virtual Network Support

When the project uses network isolation (private link), tool support varies:

| Tool type | VNet support | Traffic flow |
|---|---|---|
| MCP | ✅ | Through your VNet subnet |
| Azure AI Search | ✅ | Through private endpoint |
| Code Interpreter | ✅ | Microsoft backbone |
| Web Search | ✅ | Public Bing endpoint |
| OpenAPI | ✅ | Depends on target API network config |
| File Search | ❌ | Not yet supported in private-link projects |
| A2A | ✅ | Through private endpoint |
| Browser Automation / Computer Use | Verify via docs MCP | — |

## Region & Model Compatibility

Tool availability is **further constrained** by project region and (for some tools, e.g. Computer Use) by model deployment. A region that hosts the toolbox endpoint will not necessarily host every tool type. **Do not inline the matrix here — it changes.** Always confirm via <https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice> or the docs MCP query `Foundry tool support by region and model`.

## Reference Links

- Toolboxes overview & lifecycle: <https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox/overview>
- Configure tools (per-tool authoring): <https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox/configure-tools>
- Tool best practice (region/model matrix): <https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice>
- MCP specification (tool naming, error codes): <https://modelcontextprotocol.io/specification/2025-03-26/server/tools>
- `azd ai agent` extension: <https://learn.microsoft.com/azure/developer/azure-developer-cli/reference#azd-ai-agent>
- Network isolation for Foundry projects: <https://learn.microsoft.com/azure/foundry/how-to/configure-private-link>
- Cross-skill — A2A **hosting** side: see `foundry-hosted-agents` (this skill covers A2A consumption).
