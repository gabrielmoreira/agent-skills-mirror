---
name: foundry-governance
description: |
  Govern Microsoft Foundry agent fleets at scale via the Foundry Control Plane and adjacent surfaces. Covers tool catalog visibility, AI Gateway tools governance for MCP routing/policy, RBAC and agent identity, third-party tool considerations, RAI policies on model deployments, and transparency notes for production rollout.
  Triggers: "Foundry control plane", "Foundry governance", "tool catalog Foundry", "AI gateway MCP", "MCP governance", "agent fleet governance", "agent identity RBAC", "RAI policy Foundry", "content filter policy Foundry", "transparency note Foundry", "third-party tool Foundry risk", "tools governance API Management", "agent fleet visibility".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Control Plane + Governance

Centralized visibility, policy, and audit for Microsoft Foundry agent fleets. As you graduate from a single copilot to dozens of autonomous, multi-agent workflows calling tools across teams and tenants, the Control Plane is where you enforce *who* can deploy *what* agent, *which* tools they can call, and *what* safety policy is applied to *which* model.

This skill is **language-agnostic**. SDK-specific syntax should be discovered via the docs MCP at the moment of code generation — preview governance surfaces change weekly.

## Before You Build — Discovery (MANDATORY)

Foundry governance surfaces are evolving. Confirm current syntax, role names, and feature flags **before** generating code or templates.

**Microsoft Docs MCP queries (run these first):**

- `What is Microsoft Foundry Control Plane`
- `Foundry tool catalog discover manage`
- `Govern MCP tools AI gateway preview`
- `Foundry RBAC role assignments`
- `Foundry RAI content filter policy`
- `Foundry agent identity blueprint`
- `Foundry agents governance`
- `API Management policy snippets` (for AI Gateway XML)

**Azure MCP `foundry` tool** — control-plane operations (list projects/agents/tools, deployment policy inspection, role assignment lookup). Always prefer the MCP tool over hand-rolling REST.

**CLIs:** `az role assignment`, `az cognitiveservices account deployment`, `azd ai agent` (for what `azd` auto-grants at deploy time).

---

## Mental Model

The **Foundry Control Plane** is a unified management surface providing **visibility + governance + control** for AI agents, models, and tools across your Foundry enterprise. It is distinct from the *Foundry portal* (developer-facing build experience) — Control Plane is the API/UI surface a platform/governance team uses to oversee everything developers ship.

There are **three layers** to govern, and policies attach to different layers:

| Layer | What governs it | Failure mode if ungoverned |
|---|---|---|
| **Models** (deployments) | RAI content-filter policies, quotas, SKU caps | Unsafe outputs, runaway cost |
| **Tools** (MCP / OpenAPI / A2A) | AI Gateway (APIM) policies, tool catalog ACLs | Data exfil, credential reuse, blast radius |
| **Agents** (hosted runtime) | Entra Agent ID, RBAC, deployment policies | Lateral movement, untracked agents in prod |

Govern each layer independently — a strict RAI policy does not protect a tool from being used badly; an AI Gateway policy does not enforce model safety.

---

## Tool Catalog

The Foundry portal exposes a **central inventory** of tools registered in a project: MCP servers, OpenAPI tools, Azure AI Search indexes, Bing grounding, etc. Find it under **Build → Tools** in the portal, or list it via the Azure MCP `foundry` tool.

Why it matters:

- **Discoverability** — developers find approved tools instead of wiring private MCP endpoints from scratch.
- **Auditability** — security/governance teams can answer "what is this agent allowed to call?" without spelunking source code.
- **Permissions** — only users with the right RBAC on the project can register or modify catalog entries; others can only consume.

Operational rule: if a tool is not in the catalog, it should not be in production. Make catalog registration the gating step, not an afterthought.

See `foundry-toolboxes` for how toolboxes (versioned tool bundles) layer on top of individual catalog entries.

---

## AI Gateway for MCP Tools (Preview)

The **AI Gateway** is a centralized policy enforcement point for MCP tool calls, **built on Azure API Management (APIM)**. It sits between Foundry agents and the MCP servers they call, giving you a single place to apply cross-cutting policy without modifying every agent.

**Capabilities:**

- **Routing** — pick a backend by region or header (multi-region failover, canary, A/B).
- **Auth injection** — inject API keys / tokens at the gateway so agents never see raw credentials.
- **Header sanitization** — strip `Cookie`, `Referer`, and other client headers that should not leak to MCP servers.
- **Correlation IDs** — stamp `x-correlation-id` for cross-cutting trace stitching with App Insights.
- **Allow/deny** — block dangerous tool methods centrally (e.g., refuse `delete_*` on a shared MCP).
- **Rate limiting + quotas** — protect downstream services from runaway agents.

**Policy XML — short patterns only.** Full policy authoring is out of scope here; defer to docs MCP query `API Management policy snippets`.

```xml
<!-- Stamp a correlation ID so traces in App Insights link agent → gateway → MCP -->
<set-header name="x-correlation-id" exists-action="skip">
  <value>@(context.RequestId)</value>
</set-header>
```

```xml
<!-- Strip client headers that should never reach the MCP server.
     DO NOT strip Authorization blindly — the gateway may need to forward
     a service token or rewrite it. Strip only headers you understand. -->
<set-header name="Cookie" exists-action="delete" />
<set-header name="Referer" exists-action="delete" />
```

```xml
<!-- Backend routing by region header -->
<choose>
  <when condition="@(context.Request.Headers.GetValueOrDefault("x-region","") == "eu")">
    <set-backend-service base-url="https://mcp-eu.contoso.com" />
  </when>
  <otherwise>
    <set-backend-service base-url="https://mcp-us.contoso.com" />
  </otherwise>
</choose>
```

The gateway is **optional** — Toolbox MCP works without it. Add the gateway when you need centralized policy, observability, or credential brokering across multiple agents.

---

## RBAC for Foundry

Foundry uses standard Azure RBAC. The roles that matter for agent workloads:

| Role | Scope | Use for |
|---|---|---|
| **Azure AI User** | Foundry project | Least-privilege role required by developers, agent identities, and end-users (OAuth flows) |
| **Azure AI Project Manager** | Foundry project | Manage projects, connections, tool catalog |
| **Contributor** / **Owner** | Subscription / RG | Provisioning, RBAC management — restrict tightly |

**Assignment patterns:**

- **Developer Entra ID** → `Azure AI User` on the project.
- **Each hosted agent's dedicated Entra ID** → `Azure AI User` on the project. `azd ai agent` auto-assigns this for the agent it deploys; you must add it manually for agents not deployed via `azd`.
- **Agent identity → downstream services** — assign resource-specific data-plane roles per agent: `Storage Blob Data Reader` on a storage account, `AcrPull` on a registry, `Search Index Data Reader` on AI Search, `Cosmos DB Data Reader` on a Cosmos account, etc.

**Least-privilege rule:** never grant an agent a wildcard role at subscription scope. Scope each grant to the specific resource the agent must touch.

For provisioning-time RBAC (resource creation, network setup), see `foundry-projects-resources`.

---

## Agent Identity (Microsoft Entra Agent ID)

**Every hosted agent gets a dedicated Microsoft Entra identity**, auto-created at deploy time. Use it for:

- **Model invocations** from inside the container (token call against the project endpoint).
- **Tool access** — Toolbox auth, MCP server connections, A2A endpoints.
- **Downstream Azure resources** — Storage, AI Search, Cosmos, Key Vault, etc.

**Distinct from the project managed identity**, which is reserved for *platform infrastructure* (e.g., ACR pulls during deploy). Do not reuse the project MI for runtime data-plane calls — it usually has too-broad scopes.

**Do not share agent identities across agents.** One identity per agent is the entire point: if Agent A is compromised, its blast radius is bounded by Agent A's role assignments only.

---

## RAI Policies on Model Deployments

Every model deployment in Foundry has an associated **Responsible AI (RAI) policy**. The default is `Microsoft.Default` unless explicitly overridden at deployment time.

**Categories enforced:**

- Hate
- Sexual
- Violence
- Self-harm
- Jailbreak / Indirect Attack (prompt-injection detection)
- Profanity
- Protected Material (copyright)

Each category has per-direction (prompt vs. completion) **severity thresholds**: Low / Medium / High. Custom policies are created in the Foundry portal or via the cognitiveservices REST API.

**Apply policy at deployment time**; you can update it later on the same deployment without redeploying the model. See `foundry-models` for the deployment workflow that wires a policy to a model.

**Important boundary:** the RAI policy applies to the **model deployment**, not to the agent. To layer additional safety (custom evaluators, factuality, jailbreak resilience runs against your specific scenarios), use **evaluators** — see `foundry-observability`.

---

## Third-Party Tool Considerations (preview risk — read this)

Hosted agents can connect to **third-party MCP servers, A2A endpoints, and OpenAPI endpoints**. When they do, **Microsoft has no responsibility** for the third party's data handling, retention, geographic location, or safety posture.

**You — not Microsoft — must review:**

- **Every payload field** the agent will share with the third party. Tool inputs frequently contain user PII, internal identifiers, or business data.
- **Retention policies** of the third-party service. Does it train on your inputs? Log them? For how long?
- **Geographic / compliance boundary impact.** A third-party endpoint in another region may break GDPR, data-residency, or sovereign-cloud commitments.
- **The third party's own transparency / safety claims.** They are claims, not guarantees.

**Mitigations:**

- Route all third-party traffic through the **AI Gateway** so you can inspect, sanitize, and log payloads centrally.
- Restrict who can register third-party connections via **project RBAC** — third-party registrations should require governance review.
- Audit Foundry traces for third-party tool calls (cross-link `foundry-observability` for the KQL).
- Prefer Microsoft-hosted equivalents (Bing grounding, Azure AI Search) when the data is sensitive.

This is the single biggest residual risk of agent fleets in production. Treat third-party tool review as a checklist gate, not advice.

---

## Transparency Notes

Every Microsoft AI service publishes a **transparency note** describing capabilities, limitations, intended uses, evaluation methods, and Responsible AI considerations. Foundry agents have one — it is **required reading before production rollout**.

Verify the current URL via the docs MCP (links move). Last known location:
`https://learn.microsoft.com/azure/ai-foundry/responsible-ai/agents/transparency-note`

Use the transparency note to set realistic expectations with stakeholders, scope acceptable use cases, and document RAI commitments in your own product's transparency disclosures.

---

## Audit + Compliance Touchpoints

| Source | What it captures | Use for |
|---|---|---|
| **Azure Activity Logs** (Azure Monitor) | Control Plane operations: project create, deployment, role assignment | Compliance audits, change tracking |
| **Foundry diagnostic logs → App Insights** | Agent + tool runtime, traces, evals | Incident response, eval/trace correlation |
| **Azure Policy** | Subscription-scoped enforcement of Foundry deployment standards | Pre-deploy guardrails (e.g., "no model deployment without an RAI policy") |
| **AI Gateway logs** (APIM) | Tool-call traffic, headers, status codes | Forensics on third-party tool usage |

Cross-link: `foundry-observability` for the App Insights / OpenTelemetry side, including KQL templates.

---

## Critical Gotchas — Do Not Confuse

1. **Project MI ≠ Agent MI.** Different identities, different scopes. Project MI = platform infra (ACR pull). Agent MI = runtime data-plane. Mixing them is the most common privilege-escalation footgun.
2. **Foundry Control Plane ≠ Foundry portal.** Control Plane is the management API/UI for governance teams. Portal is the developer build experience. Same product, different audiences and feature surfaces.
3. **AI Gateway is OPTIONAL.** Toolbox MCP works without it. Add the gateway when you need centralized policy, observability, or credential brokering — not by default.
4. **RAI policy scope.** RAI applies to the **model deployment**, not the agent. Layered safety (custom safety, factuality, jailbreak resilience for *your* scenarios) requires evaluators — see `foundry-observability`.
5. **Third-party tool risk is YOURS.** Microsoft governs the platform; you govern what your agents do with third-party tools. There is no shared-responsibility shortcut here.
6. **Tool catalog is not enforcement.** Catalog presence aids discovery and audit. Enforcement still requires RBAC on connections + (optionally) AI Gateway policy on the call path.
7. **Don't strip `Authorization` blindly** in AI Gateway policies — the gateway often needs to forward or rewrite it.

---

## Reference Links

Verify each via docs MCP — preview docs move.

- **Foundry Control Plane overview** — search docs MCP: `What is Microsoft Foundry Control Plane`
- **Govern MCP tools using AI Gateway** — search: `Govern MCP tools AI gateway preview`
- **Foundry agents governance** — search: `Foundry agents governance`
- **Tool best practices for Foundry Agent Service** — search: `Tool best practices Foundry Agent Service`
- **Transparency note for Foundry agents** — `https://learn.microsoft.com/azure/ai-foundry/responsible-ai/agents/transparency-note`
- **Azure RBAC for Foundry** — search: `Foundry RBAC role assignments`
- **API Management AI Gateway policies** — search: `API Management AI gateway policy reference`

**Related skills in this plugin:**

- `foundry-projects-resources` — provisioning, connections, setup-time RBAC
- `foundry-models` — model deployment workflow, RAI policy attachment
- `foundry-toolboxes` — tool catalog, MCP toolbox versioning, A2A consumption
- `foundry-observability` — tracing, evals, KQL templates, RAI evaluators
