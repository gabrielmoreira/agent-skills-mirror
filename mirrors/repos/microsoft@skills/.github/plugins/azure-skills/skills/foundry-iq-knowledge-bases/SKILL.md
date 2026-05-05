---
name: foundry-iq-knowledge-bases
description: |
  Build Microsoft Foundry IQ knowledge bases (preview) — multi-source, permission-aware grounding for agents. Connect knowledge sources (Blob, SharePoint, OneLake, web), use the agentic retrieval pipeline (query decomposition + parallel search + reranking), and connect via MCP to hosted or prompt agents.
  Triggers: "Foundry IQ", "knowledge base", "knowledge source", "agentic retrieval", "Azure AI Search agentic", "MCP knowledge base", "ground agent on docs", "RAG Foundry", "SharePoint knowledge source", "OneLake knowledge source", "blob knowledge source", "permission-aware retrieval", "ACL retrieval", "sensitivity label retrieval".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry IQ — Knowledge Bases

Foundry IQ is the **managed knowledge layer for enterprise data**. It gives Foundry agents a single, permission-aware grounding surface across Azure Blob, SharePoint Online, OneLake, and the public web — backed by Azure AI Search agentic retrieval and exposed to agents over MCP.

This skill is language-agnostic. It teaches the mental model, the connection topology, and the non-obvious traps. For current API shapes and CLI flags, **always discover first** (next section).

---

## Before You Build — Discovery (MANDATORY)

Foundry IQ is in public preview and the surface area changes frequently. Confirm current syntax before you generate code or `az`/`azd` commands.

**Microsoft Docs MCP queries** (run these first):

- `Foundry IQ knowledge base`
- `agentic retrieval Azure AI Search`
- `knowledge source overview`
- `Foundry IQ connect agent MCP`
- `agentic retrieval how to create pipeline`
- `remote SharePoint knowledge source`
- `query-time ACL RBAC enforcement`

**Azure MCP search tools** (for live operations against an existing search service):

- `search_index_*` — list/create/inspect underlying Azure AI Search indexes
- `search_knowledge_*` — list/create/inspect knowledge bases and knowledge sources

**Foundry MCP** (`mcp.ai.azure.com`):

- Knowledge-base discovery tools — list connected knowledge bases on a Foundry project, fetch their MCP endpoints, inspect knowledge sources
- Use these instead of guessing endpoint URLs

**CLIs:**

- `az search` — manage the underlying AI Search service
- `azd ai agent` — wire up the agent side (for hosted agents)

> Rule of thumb: do not invent API versions, URL paths, or SDK class names from training memory. Confirm against docs MCP every time.

---

## Mental Model

Foundry IQ is **a managed knowledge layer**, not an SDK. The pieces:

- **Knowledge base** — top-level resource. Orchestrates retrieval across one or more knowledge sources. Exposes a single MCP endpoint that agents call. Defines retrieval reasoning effort: `minimal` | `low` | `medium`.
- **Knowledge source** — a connection to indexed or remote content. A knowledge base references one or more sources.
- **Agentic retrieval pipeline** — multi-query engine that:
  1. **Decomposes** the user question into subqueries (LLM-planned),
  2. Runs subqueries **in parallel** (keyword, vector, or hybrid),
  3. **Semantically reranks** results,
  4. Returns a **unified, citation-rich** response.
- **Underlying infrastructure** — Azure AI Search (the search service must be on a SKU that supports agentic retrieval).

```
┌─ Agent (hosted/prompt) ──────────────────────┐
│   tool: MCP → knowledge_base_retrieve        │
└──────────────┬───────────────────────────────┘
               │  MCP (project_connection_id, OBO)
               ▼
┌─ Knowledge base (Azure AI Search) ───────────┐
│   agentic retrieval: decompose → parallel    │
│   subqueries → semantic rerank → unify       │
└──┬─────────┬──────────┬─────────┬────────────┘
   │         │          │         │
   ▼         ▼          ▼         ▼
 Blob    SharePoint   OneLake    Web
 (idx)   (remote OBO) (idx)      (Bing)
```

### The three IQ workloads (don't confuse them)

| Workload | Layer | Data |
| --- | --- | --- |
| **Foundry IQ** | Managed knowledge for **enterprise data** | Blob, SharePoint, OneLake, web — for grounding |
| **Fabric IQ** | Semantic intelligence for **business analytics** | Ontologies, semantic models, OneLake/Power BI |
| **Work IQ** | Contextual intelligence for **M365 collaboration** | Documents, meetings, chats, workflows |

They are standalone but composable. This skill is only about Foundry IQ.

---

## When to Use What

Pick the right grounding mechanism per data lifecycle:

| Need | Use | Why |
| --- | --- | --- |
| Stable, organizational corpora with ACLs (HR policies, product docs, SharePoint sites) | **Foundry IQ knowledge base** | Centralized, multi-source, permission-aware, shared across agents |
| Ephemeral, per-session docs the user just uploaded | **File Search tool** in the agent's toolbox | Lifetime is the conversation; no indexing pipeline |
| User-specific facts that should persist across sessions ("my preferences", "what we discussed last week") | **Memory** (see `foundry-memory`) | Per-user state, not shared corpus |
| Public web facts | **Web Search tool** in toolbox, or a **Web knowledge source** inside a KB | Web tool = ad-hoc; KB web source = curated within the same retrieval pipeline |

A single agent can use all four together. They are not mutually exclusive.

---

## Knowledge Sources — Supported Types

Two families: **indexed** (content is chunked, embedded, and stored in your search index) and **remote** (content stays in the source system; queried at request time).

### Indexed sources (auto-chunk + embed)

| Source | Notes |
| --- | --- |
| **Azure Blob Storage** | Bring documents (PDF, Office, text). KB pipeline chunks, embeds, and indexes. Supports incremental indexer schedules. ACLs honored if the index includes permission metadata fields. |
| **OneLake** | Indexes content from a Fabric workspace. Same chunking/embedding pipeline. |
| **SharePoint Online (indexed mode)** | Pulls documents from configured sites into the search index. Use indexed mode when you want full-text search latency, embeddings under your control, and you can tolerate refresh lag. |

Setup pattern: configure a **connection** to the data source on the search service → create a knowledge source → KB pipeline runs the indexer (one-shot or scheduled) → vector + keyword index is queryable.

### Remote sources (query-time, no indexing)

| Source | Notes |
| --- | --- |
| **SharePoint Online (remote mode)** | Content is **not** indexed in AI Search. Each query is forwarded to SharePoint via the Copilot Retrieval API with the user's bearer token, so SharePoint enforces document-level permissions in real time. Best when permissions change frequently or you need zero replication. |
| **Web** | Bing-grounded web search routed through the agentic retrieval pipeline. |
| **Other search indexes** | An existing AI Search index can be wrapped as a knowledge source so an existing RAG corpus participates in the multi-source retrieval. |

Discover the exact connection schema for each source via docs MCP — fields and required identity setup vary by source type.

---

## Permission-Aware Retrieval

This is the most important reason to choose Foundry IQ over a hand-rolled RAG stack.

- **ACL sync from supported sources.** SharePoint and Blob (with role-based access) propagate ACLs into the index as permission metadata fields. The search index must include those fields — see *Document-level access control* in the docs MCP.
- **Microsoft Purview sensitivity labels** are honored end-to-end. A document tagged Confidential will only surface to identities cleared for that label.
- **Query-time enforcement via the caller's Microsoft Entra identity.** When the agent invokes the knowledge base, the user's bearer token is passed through the `x-ms-query-source-authorization` header. The search service applies ACL/RBAC filters before returning results. Users only see what they are entitled to see.
- **End-to-end OBO flow** when invoked from agent tools. The hosted/prompt agent forwards the caller's identity to the KB, which forwards it to the source system (e.g., SharePoint Copilot Retrieval API) when needed.

Web sources are **public** — no permissions to enforce. Mixing a permissioned source and a web source in the same KB is fine; results are still filtered per source.

> Gotcha: in the current Foundry Agent Service preview, MCP tool headers are **set in the agent definition and apply to all invocations** — they cannot vary per request. For per-user authorization on remote SharePoint sources, use the Azure OpenAI Responses API instead. Confirm via docs MCP.

---

## Workflow — Portal

Fast path for proof-of-concept (no code).

1. Sign in to the Microsoft Foundry portal (`ai.azure.com`). Make sure the **New Foundry** toggle is on.
2. Create or select a project.
3. From the top menu, select **Build**.
4. Open the **Knowledge** tab:
   1. Create or connect to an Azure AI Search service that **supports agentic retrieval** (verify SKU).
   2. Create a knowledge base — add knowledge sources one at a time.
   3. Configure retrieval behavior (reasoning effort, etc.).
5. Open the **Agents** tab:
   1. Create or select an agent.
   2. Connect it to your knowledge base.
   3. Use the **playground** to send messages and refine instructions.

The portal handles managed identity wiring for the playground. Before promoting to code, replace playground auth with the production identity model your org uses.

---

## Workflow — Programmatic

Five steps. Discover the exact API shapes via docs MCP and the Azure MCP `search_*` tools — do not paste from memory.

1. **Create knowledge sources.** One per data store you want to ground on.
2. **Create the knowledge base** referencing those sources (`knowledge_base_create` on the search service, with reasoning-effort and source-list parameters).
3. **Get the knowledge base MCP endpoint.** Pattern:
   ```
   {search_service_endpoint}/knowledgebases/{knowledge_base_name}/mcp?api-version={preview-api-version}
   ```
   Confirm the current `api-version` via docs MCP — do not hard-code.
4. **Create a project connection** in your Foundry project pointing at the AI Search service. The connection uses `category: RemoteTool` with `authType: ProjectManagedIdentity` and `audience: https://search.azure.com/`. The project's managed identity needs **Search Index Data Reader** on the search service (and Contributor only if writing).
5. **Configure the agent's MCP tool** with `project_connection_id` set to the connection name and `server_url` set to the KB MCP endpoint. The only currently supported KB MCP tool name is `knowledge_base_retrieve`.

---

## Connecting an Agent to a Knowledge Base

This is the **core integration pattern**. The agent ↔ knowledge base bridge is **MCP-based** — there is no built-in "knowledge base tool" type. The KB is just an MCP server that the agent's MCP tool talks to.

### What goes in `agent.yaml`

For hosted agents and prompt agents declared via `azd ai agent`, you declare two things:

1. A `kind: connection` resource pointing to the AI Search service that hosts the KB (the project connection from step 4 above).
2. An **MCP tool** in the agent's toolbox pointing at the KB MCP endpoint, with `project_connection_id` referencing that connection and `allowed_tools: ["knowledge_base_retrieve"]`.

For the exact YAML schema and toolbox declaration syntax, see the sibling skill **`foundry-toolboxes`** — it owns the MCP tool config surface.

### SharePoint-backed KBs need an extra header

If the KB includes a remote SharePoint knowledge source, the MCP tool config must also include the `x-ms-query-source-authorization` header carrying a bearer token for the `https://search.azure.com/.default` scope. This is the OBO mechanism that lets SharePoint enforce per-document ACLs at query time. See the gotcha in *Permission-Aware Retrieval* about per-request header limitations.

### Required identity + RBAC

- Project's managed identity → **Search Index Data Reader** on the search service.
- Caller (user) → Entra identity must be present on every request for ACL filtering to work.
- For ARM operations (creating the project connection): **Azure AI Project Manager** on the project's parent resource.

---

## Optimizing Agent Instructions for Retrieval

The agent will not call the KB unless its instructions tell it to. A minimum-viable system prompt:

```
You are a helpful assistant.

Use the knowledge base tool to answer user questions.
If the knowledge base doesn't contain the answer, respond with "I don't know".

When you use information from the knowledge base, include citations to the
retrieved sources.
```

Patterns that move the needle:

- **Add a decision rule.** "Use the policy knowledge base for HR questions before answering from training data." Explicit routing increases tool-invocation rate.
- **Force citations.** Require an annotation format (e.g., `【message_idx:search_idx†source_name】`). Citation-shaped output makes hallucinations easier to spot in evals.
- **Forbid silent fallback to model knowledge.** "You must never answer from your own knowledge under any circumstances. If you cannot find the answer in the provided knowledge base you must respond with 'I don't know'." Trade off: higher refusal rate, lower hallucination rate.
- **Iterate.** This template is a starting point. Run evals (see `foundry-observability`) and tune.

---

## Critical Gotchas — Do Not Confuse

1. **Knowledge base ≠ Azure AI Search index.** A KB is an orchestration layer over one or more sources (which may themselves be indexes). Querying the KB is *not* the same as querying an index directly — you get query decomposition, parallel execution, and semantic reranking on top.
2. **File Search tool ≠ knowledge source.** File Search lives in the agent's toolbox and is for ephemeral, per-session uploads. A knowledge source is durable, organizational, and shared across agents. Wrong choice → wrong data lifecycle.
3. **Permission enforcement is OBO at query time.** It only works if you propagate the caller's Entra identity through to the KB (`x-ms-query-source-authorization`). The project's managed identity is for *infrastructure access*, not for impersonating the user. Web sources are public — no enforcement applies.
4. **MCP tool headers are per-agent, not per-request** in the current Foundry Agent Service preview. For per-user SharePoint OBO, switch to the Azure OpenAI Responses API.
5. **Reasoning effort trades latency for retrieval quality.** `minimal` is fastest, `medium` plans more subqueries and reranks more aggressively. Pick based on your latency budget; instrument both via `foundry-observability`.
6. **The search service SKU matters.** Not every AI Search SKU supports agentic retrieval. Verify SKU before creating the KB or you will get cryptic provisioning errors.
7. **Deleting the agent does not delete the KB.** Knowledge bases and knowledge sources are AI Search resources with their own lifecycle. Clean them up explicitly when tearing down.
8. **The KB MCP endpoint exposes only `knowledge_base_retrieve` today.** Don't write code that assumes other MCP tool names — confirm via docs MCP.
9. **Citation URLs vary by source.** Blob sources return the original document URL. Search-index sources fall back to the KB MCP endpoint. Plan your UI accordingly.
10. **For user-specific personalization, use Memory, not a KB.** A KB is for shared organizational facts. Cross-link: `foundry-memory`.

---

## Reference Links

Confirm currency via docs MCP — these URLs are stable but content evolves.

- **Foundry IQ overview** — `learn.microsoft.com/azure/foundry/agents/concepts/foundry-iq` (search docs MCP for "What is Foundry IQ")
- **Knowledge base how-to** — `learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base`
- **Agentic retrieval overview** — `learn.microsoft.com/azure/search/agentic-retrieval-overview`
- **Knowledge source overview** — `learn.microsoft.com/azure/search/agentic-knowledge-source-overview`
- **End-to-end pipeline tutorial** — `learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-pipeline`
- **Connect a Foundry agent to a KB** — `learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect`
- **Document-level access control** — `learn.microsoft.com/azure/search/search-document-level-access-overview`
- **Query-time ACL/RBAC enforcement** — `learn.microsoft.com/azure/search/search-query-access-control-rbac-enforcement`
- **Remote SharePoint knowledge source** — `learn.microsoft.com/azure/search/agentic-knowledge-source-how-to-sharepoint-remote`

### Sibling skills (cross-links)

- **`foundry-toolboxes`** — owns the MCP tool declaration syntax used to wire a KB into an agent's toolbox.
- **`foundry-memory`** — for per-user personalization that should *not* live in a shared KB.
- **`foundry-hosted-agents`** — for agent.yaml lifecycle and `azd ai agent` workflow.
- **`foundry-observability`** — for eval datasets, retrieval-quality metrics, and trace correlation.
