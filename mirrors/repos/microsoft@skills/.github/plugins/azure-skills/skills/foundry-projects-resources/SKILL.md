---
name: foundry-projects-resources
description: |
  Provision Microsoft Foundry resources and projects, configure project connections (key-auth, OAuth, managed identity, agent identity), and set up standard or private-network agent infrastructure. Covers az / azd workflows, RBAC, and Azure auth best practices for Foundry.
  Triggers: "create Foundry project", "create Foundry resource", "Foundry resource", "AIServices account", "project connection", "project_connection_id", "RemoteA2A connection", "OAuth connection", "managed identity Foundry", "standard agent setup", "private network Foundry", "Bring Your Own VNet Foundry", "DefaultAzureCredential", "ManagedIdentityCredential".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Projects + Resources

Provisioning, connections, and authentication for Microsoft Foundry. Use this skill whenever you stand up new infrastructure (resource, project, standard agent setup, private network), wire a project to an external service (Storage, AI Search, MCP, A2A, OAuth provider), or pick a credential type for an agent or developer client.

## Before You Build — Discovery (MANDATORY)

Foundry control-plane behavior, region availability, and `az`/`azd` flag names change frequently. **Run discovery before generating any provisioning command, ARM template, or auth snippet.**

1. **microsoft-docs MCP** — query the most recent guidance for what you are about to do:
   - "Foundry create project"
   - "Foundry resource type AIServices"
   - "Foundry project connection"
   - "Foundry standard agent setup"
   - "Foundry private network configure"  /  "Foundry configure private link"
   - "Azure Identity DefaultAzureCredential vs ManagedIdentityCredential"
2. **CLI help** — verify flags against the installed CLI (do not trust memory):
   ```bash
   az cognitiveservices account --help
   az cognitiveservices account create --help
   azd up --help
   azd init --help
   ```
3. **Azure MCP `foundry` tool** — for live project + resource operations (list, show, create projects/connections), prefer the MCP tool over hand-rolled REST.
4. **State assumptions explicitly.** If region, SKU, subdomain, or auth model is unclear — ask the user before provisioning. Foundry resources have properties that **cannot be changed after creation** (custom subdomain, network isolation mode).

## Mental Model

```
Foundry resource (Microsoft.CognitiveServices/accounts, kind: AIServices)
└── *.services.ai.azure.com           ← unified data plane endpoint
    ├── Project A
    │   ├── Connections   (Storage, AI Search, MCP, A2A, OAuth, CustomKeys, …)
    │   ├── Models        (deployments inherited from the resource)
    │   ├── Agents        (versions, instructions, tool wiring)
    │   ├── Toolboxes     (File Search, Code Interpreter, Browser, …)
    │   └── Knowledge bases / Indexes
    ├── Project B
    └── Project C
```

- **Foundry resource** = the `AIServices` account that owns model deployments and hosts the unified API.
- **Foundry project** = a workspace inside that resource for agents, connections, evals, traces. **Many projects per resource** (unlike classic Azure AI Foundry hubs, which were 1 project per workspace).
- **Endpoint shape:**
  ```
  https://<resource>.services.ai.azure.com/api/projects/<project>
  ```
  This is the value of `AZURE_AI_PROJECT_ENDPOINT` and what every Foundry SDK client expects.

## Provisioning Workflows

Three supported paths. Pick based on how repeatable and infrastructure-as-code-friendly the deployment must be.

### Path A — `azd` template (recommended)

Bicep-driven, one-shot project + standard agent setup. Pin to an official sample template.

- **When to use:** new project, want repeatable CI/CD, want standard agent setup wired in (Storage + AI Search + Cosmos + RBAC) without hand-authoring Bicep.
- **Inputs:** environment name (becomes RG name `rg-<env>`), location, optional `ENABLE_HOSTED_AGENTS`.
- **Outputs:** `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_PROJECT_ID` (ARM ID), `AZURE_RESOURCE_GROUP`, App Insights connection string, project MI principal ID.
- **Caveats:** template choice matters — basic vs standard vs private-network templates provision very different topologies; verify with the template README before `azd up`.

### Path B — `az` CLI (granular)

Use when you need to add a project to an **existing** Foundry resource, or when policy forbids `azd`-style top-level deployments.

- **When to use:** existing AIServices account; scripted bootstrap from a runbook; teams that prefer imperative provisioning.
- **Inputs:** resource group, region, `--kind AIServices`, `--sku S0` (only supported tier), `--custom-domain <subdomain>` (required for token-based auth scenarios).
- **Outputs:** ARM resource ID, endpoint hostname; create project subresource separately via Foundry MCP `foundry_project_create` or REST `PUT .../projects/<name>`.

### Path C — Foundry portal (UI)

Click-driven at <https://ai.azure.com>.

- **When to use:** prototyping, demos, exploratory setup. Not for production.
- **Outputs:** same as Path B, but no IaC artifact — capture the endpoint and ARM ID into env vars manually.

## Connections

Connections are **project-scoped resources** that store the auth + endpoint Foundry uses to call a downstream service on behalf of an agent. **Many tools require a `project_connection_id` before they can run** (AI Search tool, Bing grounding, Remote MCP, A2A, custom HTTP).

### Common kinds

| Kind | Purpose | Typical auth |
|---|---|---|
| `AzureStorageAccount` | Blob storage for files / datasets | Entra (project MI) |
| `AzureAISearch` | Vector / hybrid retrieval index | API key or Entra |
| `RemoteTool` (MCP) | Remote MCP server endpoint | `CustomKeys` (Bearer) or OAuth |
| `RemoteA2A` | Agent-to-agent connection to another Foundry/3P agent | Agent identity or `CustomKeys` |
| `CustomKeys` | Arbitrary HTTP API with header-based auth | Static key in custom header |
| `OAuth` | OAuth-protected SaaS (managed connector or your app reg) | OAuth 2.0 authorization code |
| `UserEntraToken` | Skill proxies the **end user's** Entra token (OBO) | User token at runtime |

### Auth modes — quick guide

- **Key-based** — `CustomKeys` with `Authorization: Bearer …` or a custom header (e.g., `x-api-key`). Fast, simple, but you own key rotation.
- **OAuth** — for SaaS providers; pick a managed connector when one exists, otherwise register your own app and configure the connection's redirect URI.
- **Agent identity** — connection stores no creds; the **agent's dedicated Entra ID** authenticates at runtime. Use for downstream Azure resources where the agent should appear as itself.
- **User Entra token (OBO)** — for skills that must act **as the calling user** (e.g., reading their mailbox). The runtime forwards the user's token; downstream service must accept the audience.

### Example connection declaration (`agent.yaml`)

Language-agnostic shape — same fields whether you author it via Bicep, Foundry MCP, REST, or YAML:

```yaml
kind: connection
name: my-mcp-server
type: RemoteTool
target: https://mcp.example.com/sse
auth:
  type: CustomKeys
  credentials:
    Authorization: Bearer ${MCP_BEARER_TOKEN}    # rotate via Key Vault reference
metadata:
  category: mcp
```

The full connection ID returned by Foundry follows:

```
/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}/connections/{connectionName}
```

Most SDKs accept the **short name** and resolve the full ID; REST and some TypeScript samples want the full ID — resolve via Foundry MCP `project_connection_get` if unsure.

## Authentication Best Practices

> Condensed guidance. For language-specific snippets, query the docs MCP or load the matching `azure-identity-*` skill.

**Golden rule:** managed identity + Azure RBAC in production; `DefaultAzureCredential` for **local development only**.

| Environment | Credential | Why |
|---|---|---|
| Production (Azure-hosted) | `ManagedIdentityCredential` (system or user-assigned) | No secrets, auto-rotated |
| Production (CI/CD) | `WorkloadIdentityCredential` / federated GitHub OIDC | Pipeline-scoped identity, no long-lived secrets |
| Production (on-prem) | `ClientCertificateCredential` | Deterministic, no fallback chain overhead |
| Local development | `DefaultAzureCredential` | Chains `az`/`azd`/VS Code creds for convenience |

**Why not `DefaultAzureCredential` in production:**

1. Walks an **unpredictable fallback chain** — adds latency, makes failures hard to diagnose.
2. Probes env vars and CLI tokens that **should not exist** in production — broad surface area.
3. **Non-deterministic** — which credential actually authenticates depends on the host.
4. Each failed probe adds a network round-trip before the next attempt.

**Environment-aware pattern (pseudocode):**

```text
if env(NODE_ENV | ASPNETCORE_ENVIRONMENT | AZURE_FUNCTIONS_ENVIRONMENT) == "Development":
    credential = DefaultAzureCredential()
elif env(AZURE_CLIENT_ID) is set:
    credential = ManagedIdentityCredential(client_id=env.AZURE_CLIENT_ID)   # user-assigned
else:
    credential = ManagedIdentityCredential()                                # system-assigned
```

## RBAC for Foundry

| Role | Scope | Use |
|---|---|---|
| **Azure AI User** | Project | Least-privilege for **developers, agent identities, and end users in OAuth flows**. Required to call agents, threads, runs. |
| **Azure AI Project Manager** | Project | Create/manage projects, connections, deployments. |
| **Cognitive Services Contributor** | Resource | Manage Foundry resource (model deployments, capability host). |
| **Contributor** / **Owner** | RG / Subscription | Provision the resource itself; needed for `azd up`. |

**Critical:** When an agent calls a downstream resource (Storage, AI Search, third-party API), assign RBAC **on the downstream resource to the agent's dedicated Entra ID** — not the project's managed identity. Project MI is for control-plane operations on the project itself.

## Standard Agent Setup

The default "production-ready" infra layout:

- AI Services account (the Foundry resource)
- Foundry project
- **Capability host** (agents) attached to the project
- **Bring-your-own:** Azure Storage (file uploads), Azure AI Search (vector store), Azure Cosmos DB (thread/state if used)
- App Insights (tracing) + project managed identity + RBAC role assignments

**When to use the bundled `standard` template:** any production workload that needs control over data residency, vector search index, or long-term thread storage. Use the official Bicep at the [foundry-samples standard agent setup](https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep) folder.

> ⚠️ **Capability host provisioning is asynchronous (10–20 min).** Poll the deployment until it succeeds — do not assume it's ready as soon as `az deployment group create` returns.

**When to customize:** existing Storage/Search/Cosmos accounts you must reuse, custom encryption keys (CMK), or non-default network rules.

## Private-Network (BYO VNet) Setup

Use when data residency, VNet isolation, customer-managed keys, or compliance requires that **no Foundry traffic traverses the public internet**.

**Key components:**

- **VNet** with two `/24` subnets:
  - **Agent subnet** — delegated to `Microsoft.App/environments`, **exclusive** to one Foundry account.
  - **Private endpoint subnet** — hosts PEs for AI Services, Storage, AI Search, Cosmos.
- **Private endpoints** for every dependency (resource, storage, search, cosmos, key vault).
- **Private DNS zones** linked to the VNet so `*.services.ai.azure.com` and dependency hostnames resolve to PE IPs.
- **All resources in the same region as the VNet.**

**Tool support gotcha:** **File Search is NOT supported in private-network mode** (per Toolboxes docs). If your agent needs File Search, use standard setup or proxy via a custom retrieval connection.

For step-by-step Bicep + RBAC, query the docs MCP: **"Foundry configure private link"** and use the official [private-network standard agent setup Bicep](https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep) sample.

## CLI Cheat Sheet

```bash
# ---------- Discover existing ----------
az cognitiveservices account list \
  --query "[?kind=='AIServices'].{name:name, rg:resourceGroup, region:location, endpoint:properties.endpoint}" \
  -o table

az cognitiveservices account show -n <resource> -g <rg>

# ---------- Create resource (Path B) ----------
az group create -n <rg> -l <region>

az cognitiveservices account create \
  -n <resource> -g <rg> -l <region> \
  --kind AIServices --sku S0 \
  --custom-domain <subdomain> \
  --yes

# ---------- Create project on the resource ----------
# Prefer the Foundry MCP `foundry_project_create` tool (or portal).
# Direct REST: PUT /subscriptions/.../accounts/<resource>/projects/<project>?api-version=...

# ---------- Path A: azd template ----------
mkdir my-foundry-app && cd my-foundry-app
azd init -t Azure-Samples/get-started-with-ai-agents -e my-foundry-app --no-prompt
azd up                                  # provision + (optionally) deploy
azd env get-values                      # capture AZURE_AI_PROJECT_ENDPOINT, etc.

# ---------- Verify the project endpoint ----------
echo "$AZURE_AI_PROJECT_ENDPOINT"
# Expect: https://<resource>.services.ai.azure.com/api/projects/<project>
```

> Always `--help` the version installed in your shell — flags drift between CLI releases.

## Critical Gotchas — Do Not Confuse

- **Foundry resource ≠ Azure OpenAI resource.** Foundry exposes the unified `/api/projects/*` endpoint and supports agents, evals, connections. Azure OpenAI exposes only `/openai/v1`. They have different SDKs and different control planes — do not mix endpoints.
- **Connection auth ≠ agent auth.** A connection stores **how** to call a downstream service (key, OAuth, MI). The agent's identity governs **when and as whom** it invokes that connection. Both must be set correctly.
- **`DefaultAzureCredential` is FINE locally — NOT in production.** Pick `ManagedIdentityCredential` (or `WorkloadIdentityCredential` in CI/CD) for any deployed workload.
- **`Azure AI User` role is required on the PROJECT for both developer AND agent identity** (and for end users in OAuth/OBO flows). Granting it only to the developer breaks runtime calls from the agent.
- **Custom subdomain is required for some token-based auth scenarios and CANNOT be changed after resource creation.** Always pass `--custom-domain` on `az cognitiveservices account create`.
- **Capability host provisioning is async (10–20 min).** Standard / private-network templates return success on the ARM deployment well before the host is usable. Poll before invoking agents.
- **Private-network mode disables File Search.** Choose a different retrieval pattern up front.
- **Project connection IDs:** SDK code usually accepts the short `connectionName`; REST + some TS samples need the full `/subscriptions/.../connections/<name>` ID. Resolve via `project_connection_get` if you hit `Invalid connection ID format`.

## Reference Links

- [Azure AI Foundry overview](https://learn.microsoft.com/azure/ai-foundry/)
- [Standard agent setup](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/standard-agent-setup)
- [Configure private link for Foundry](https://learn.microsoft.com/azure/ai-foundry/how-to/configure-private-link)
- [Foundry RBAC roles](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-azure-ai-foundry)
- [Capability hosts — agent setup types](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/capability-hosts)
- [Azure Identity client libraries](https://learn.microsoft.com/dotnet/azure/sdk/authentication/)
- [Managed identities for Azure resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview)
- [`az cognitiveservices account` reference](https://learn.microsoft.com/cli/azure/cognitiveservices/account)
- [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [foundry-samples — infrastructure Bicep](https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep)
- Sibling skills: `microsoft-foundry`, `foundry-managed-skills`, `azure-identity-*`, `entra-app-registration`
