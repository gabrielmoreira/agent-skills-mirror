---
name: foundry-workflows
description: |
  Build multi-agent workflows in Microsoft Foundry — declarative agent orchestration for handing off control between specialist agents, plus the Connected Agents pattern and Microsoft Agent Framework workflow patterns. Covers when to use a workflow vs an A2A tool call, and how to author/visualize/test workflows.
  Triggers: "Foundry workflow", "multi-agent", "Connected Agents", "agent handoff", "agent orchestration Foundry", "workflow visual builder", "Agent Framework workflow", "declarative agent workflow", "agents in workflows", "workflow vs A2A".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Foundry Multi-Agent Workflows

Workflows are Microsoft Foundry's first-class surface for **declarative, predefined orchestration** across multiple agents and business logic. This skill teaches the mental model, the three multi-agent patterns Foundry exposes, and how to choose between them. It is intentionally language-agnostic — for SDK syntax, defer to the discovery surfaces below.

---

## Before You Build — Discovery (MANDATORY)

> Foundry's workflow surface changed substantially in the GA Agents Service (the previous "Connected Agents" pattern is now classic). Confirm current shapes before generating code.

**Microsoft Docs MCP — high-yield queries:**

- `microsoft_docs_search`: "Build a workflow in Microsoft Foundry"
- `microsoft_docs_search`: "Connected Agents Foundry" (note: classic surface)
- `microsoft_docs_search`: "Agents in Workflows Foundry"
- `microsoft_docs_search`: "Microsoft Agent Framework workflow orchestrations"
- `microsoft_docs_search`: "Workflow-oriented multi-agent patterns"
- `microsoft_docs_search`: "Add declarative agent workflows VS Code"
- `microsoft_docs_fetch` the canonical workflow concept page once you've identified it (Reference Links below).

**Foundry portal:**

- Open the **Build** menu → **Workflows** tab. The visual builder is the source of truth for shape; YAML view is downstream.
- Use the **Run Workflow** button + chat pane to inspect each node's state.

**Microsoft Agent Framework:**

- Workflow primitives live under `agent-framework/workflows/orchestrations/*`. Each pattern (Sequential, Concurrent, Handoff, Group Chat, Magentic) has its own page with Python and C# samples.

If you skip discovery and use stale patterns (e.g., `ConnectedAgentToolDefinition`, `2025-05-15-preview` API), you will produce code that targets the deprecated classic surface.

---

## Mental Model

A **Workflow** is a *declarative, predefined sequence* of actions that orchestrates **agents + business logic** in a visual builder. Think DAG, not chat loop:

- A workflow is composed of **nodes**. Each node is one of:
  - **Agent invocation** — call a Foundry agent (prompt agent or another workflow agent).
  - **Logic** — `if/else`, `go to`, `for each`.
  - **Data transformation** — set a variable, parse a value (Power Fx expressions).
  - **Basic chat / Ask a question** — send a message or solicit input.
  - **Human-in-the-loop** — pause for approval or clarification.
- A workflow has **versions** — every save creates a new immutable version with full history.
- A workflow can be authored visually **or** as YAML; both views are editable and stay in sync.
- A workflow is itself an **agent type** in Foundry (Workflow agent), alongside Prompt agents and Hosted agents.

**Key terms:**

- **Workflow agent** — a Foundry agent whose definition *is* a workflow.
- **Handoff** — a node transfers control of the user conversation from one agent to another. After handoff, the new agent owns the conversation.
- **System / Local variables** — Power Fx scopes (`System.ConversationId`, `Local.Var01`).
- **Node** — single step in the DAG.

---

## Three Multi-Agent Patterns in Foundry — Choose

| Pattern | What | When |
|---------|------|------|
| **A2A tool call** | Agent A *calls* Agent B as a tool; Agent A keeps control of the user conversation. Response from B is consumed by A. | Sub-task delegation; Agent A is still the user-facing assistant. |
| **Connected Agents (classic)** | Agents grouped in Foundry classic; one "main" agent delegates to specialist sub-agents via natural-language routing. | Existing classic deployments; lighter-weight than full workflow. **Deprecated — retiring 2027-03-31.** Migrate to Workflows. |
| **Workflow** | Declarative DAG; control passes between agents per workflow definition. Visible orchestration with branching, loops, human gates. | Complex business processes; need approval steps; need observability of orchestration; non-developer ownership. |

**Cross-references:**

- A2A tool consumption — see `foundry-toolboxes` (A2A is one of the seven built-in toolbox tool types).
- A2A hosting (your hosted agent exposing an A2A endpoint) — see `foundry-hosted-agents`.

---

## Workflow Authoring Surfaces

| Surface | What it gives you | Best for |
|---------|-------------------|----------|
| **Foundry portal visual builder** | Drag-drop node canvas, live preview, version history. | Prototyping; non-developer ownership; stakeholder review. |
| **VS Code declarative workflows** | YAML in `.yaml` files; bi-directional sync with the visual builder; works in VS Code Web. | Source-control; CI; PR review of workflow changes. |
| **Microsoft Agent Framework** | Workflow primitives in Python/.NET (`Sequential`, `Concurrent`, `Handoff`, `Group Chat`, `Magentic`). | Workflow logic embedded in your application code; custom orchestration logic. |

**Rules of thumb:**

- Start in the portal to understand the shape, then export to YAML once you want it in source control.
- The YAML view in the portal exposes a **YAML Visualizer View** toggle — you can edit either side and the other updates.
- The portal does **not auto-save**. Press **Save** after every change.

---

## Building a Workflow — Conceptual Flow

1. **Define your agents.** Each agent in the workflow is a Foundry agent — prompt or workflow agent. (Hosted agents are *not* supported as nodes inside the workflow designer; from a hosted agent, use Agent Framework workflows internally instead. See `foundry-hosted-agents`.)
2. **Identify the orchestration shape.** Pick the pattern: sequential pipeline, parallel fan-out, conditional branch, loop, human-in-the-loop, group chat.
3. **Author the workflow.** Portal for prototyping; VS Code for source control; Agent Framework for in-app orchestration.
4. **Test in the playground.** Use the chat pane in the visualizer or the local playground (VS Code low-code/pro-code). Verify each node completes and saved variables hold the expected values.
5. **Deploy + monitor.** Workflow agents are first-class — they get a dedicated endpoint, dedicated identity, and emit traces. Wire up observability across agent boundaries (see `foundry-observability`).

---

## Built-in Workflow Templates

Foundry ships templates for the common orchestration shapes — start from a template before authoring blank:

| Template | Description | Typical use case |
|----------|-------------|------------------|
| **Human in the loop** | Asks the user a question and awaits input before proceeding. | Approval gates; clarifying questions before continuing. |
| **Sequential** | Passes the result from one agent to the next in a defined order. | Pipelines; multi-stage processing. |
| **Group chat** | Dynamically passes control between agents based on context or rules. | Escalation; expert handoff; iterative refinement. |

For the full list of patterns and Agent Framework parallels, query the docs MCP: "Microsoft Agent Framework workflow orchestrations".

---

## Variables, Expressions, and Power Fx

Workflows pass data between nodes using **variables**. Variables are referenced in Power Fx expressions with a mandatory scope prefix:

- `System.` — system variables (e.g., `System.ConversationId`, `System.Activity`, `System.LastMessage`).
- `Local.` — variables you create in the workflow (e.g., `Local.Var01`).

Common use cases:

- **Save user input.** "Ask a question" node has a `Save user response as` field — supply a variable name (`Local.userName`) and reference it later as `{Local.userName}`.
- **Save agent output.** Agent invocation nodes can save structured JSON output (configure JSON schema response format) into a variable for downstream nodes to consume.
- **Build conditions.** In `if/else` nodes, the condition box accepts Power Fx expressions like `Local.score > 0.8` or `IsBlank(Local.email)`.
- **Transform values.** Use Power Fx functions (`Upper`, `Concat`, `Text`, `Value`, `DateAdd`, `IfError`) inside Send Message and Set Variable nodes.

**Common Power Fx errors:** `Name isn't valid` → forgot the `System.` / `Local.` scope prefix. `Type mismatch` → wrap with `Text()` or `Value()` to coerce.

For the full Power Fx reference, defer to the Power Fx formula docs (linked from the workflow concept page).

---

## Versioning, Notes, and Lifecycle

- **Every save = a new immutable version.** Open the **Version** dropdown to the left of **Save** to view history or delete older versions.
- **YAML view toggle.** Set **YAML Visualizer View** to **On** to source-control the workflow. Edit either side; the other updates live. Saving creates a new version of the YAML.
- **Notes.** Add notes to the visualizer canvas (upper-left **Add note**) to document intent for reviewers.
- **Deletion.** Workflows are deleted version-by-version from the Version dropdown.
- **Publishing.** Publishing a workflow agent gives it a stable endpoint and its own dedicated Microsoft Entra Agent Identity — same lifecycle as prompt agents (see `foundry-projects-resources` for identity setup, `foundry-hosted-agents` for endpoint shape).

---

## Testing and Debugging

1. **Run in the visualizer chat pane first.** Use the chat to step through the workflow interactively. Foundry highlights each node as it executes.
2. **Verify completion.** Confirm every node turns "complete" in the visualizer and that any saved variables hold the expected values.
3. **Inspect JSON outputs.** If an agent node is configured with a JSON schema response format, validate the saved variable matches the schema.
4. **Use the local playground.** From VS Code (low-code or pro-code extensions), run the workflow locally before deploying — faster iteration and no portal round-trips.
5. **Trace cross-agent calls.** Once published, every agent in the workflow emits OpenTelemetry spans. Correlate spans by `traceparent` propagation through the workflow runtime — KQL templates in `foundry-observability`.

**Common failure modes:**

| Symptom | Cause |
|---------|-------|
| Workflows tab missing | Missing **Contributor** RBAC on the project. |
| Changes vanish on refresh | Forgot to press **Save**. Foundry does not auto-save. |
| Agent node fails | Agent slot is unassigned, or referenced agent was deleted. |
| Workflow times out | Break complex workflows into smaller sub-workflows; check external service latency. |
| Power Fx formula error | Missing scope prefix (`System.` / `Local.`) or type mismatch. |

---

## Connected Agents (Classic) Pattern

**Status: classic / deprecated.** The Foundry (classic) portal exposed a *Connected Agents* pattern where one "main" agent delegates to specialist sub-agents via a `ConnectedAgentToolDefinition`. Microsoft is moving everyone to Workflows + A2A. Connected Agents (classic) will be retired **2027-03-31** and is only available on the `2025-05-15-preview` API.

If you encounter an existing Connected Agents deployment:

- **Don't extend it.** Plan the migration to Workflows (`2025-11-15-preview` API and later).
- **Don't author new Connected Agents content.** New work goes into Workflows.
- **Migration path:** the classic main agent becomes a Workflow with sequential/group-chat nodes; each connected sub-agent becomes a node that invokes that agent. Each agent retains its own dedicated Agent Identity after publishing.

For setup details on existing classic deployments only, query: "Build collaborative multi-agent systems with Connected Agents classic portal".

---

## Agent Framework Workflows

When workflow logic must live **inside your application code** (not in the Foundry portal), use Microsoft Agent Framework's workflow primitives. The framework provides built-in orchestration patterns for both Python and .NET:

| Pattern | Shape |
|---------|-------|
| **Sequential** | Agents execute one after another in a defined order. |
| **Concurrent** | Agents execute in parallel. |
| **Handoff** | Agents transfer control to each other based on context. |
| **Group Chat** | Agents collaborate in a shared conversation; an orchestrator (e.g., round-robin) selects the next speaker. |
| **Magentic** | A manager agent dynamically coordinates specialized agents. |

Group Chat detail: agents do **not** share the same `AgentSession` instance; the orchestrator broadcasts each turn to every participant so everyone sees the full history before their next turn.

Agent Framework workflows also support **human-in-the-loop** via approval-required tools and `RequestExternalInput` / `WaitForInput` actions.

**Cross-link:** for SDK-specific implementation, load the matching language plugin skill (e.g., `agent-framework-azure-ai-py`).

---

## When to Use Workflow vs A2A vs Connected Agents

Decision shortcuts:

- Need a **visual diagram** stakeholders can review → **Workflow**.
- Need **strict approval gates** or human-in-the-loop checkpoints → **Workflow**.
- Need **branching/looping logic** without code → **Workflow** (use Power Fx for conditions).
- Agent A delegates **one sub-question** to Agent B, then resumes → **A2A tool call** (configure on Agent A's toolbox).
- Workflow logic must live **inside your own application code** → **Agent Framework workflow**.
- Existing classic Connected Agents deployment → **Connected Agents** (until you migrate to Workflow).
- Hosted agent needs internal multi-agent coordination → **Agent Framework workflow inside the container** (the workflow designer can't have hosted agents as nodes).

---

## Critical Gotchas — Do Not Confuse

1. **Workflow ≠ Connected Agents ≠ A2A tool.** Three distinct patterns with different ownership semantics. Don't conflate them in design discussions.
2. **Handoff transfers ownership.** A workflow handoff transfers responsibility for the user conversation to the next agent. Agent B *owns* the conversation after handoff. Compare with A2A: Agent A keeps ownership and only consumes B's response.
3. **Workflows can call prompt agents and workflow agents — but not hosted agents** as nodes in the workflow designer. To orchestrate from inside a hosted agent, use Microsoft Agent Framework workflows in your container code.
4. **"Multi-agent" ≠ "Workflow".** A2A tool calling is *also* multi-agent; it just keeps the orchestration implicit on Agent A. Pick the surface that fits the *responsibility model* you want.
5. **Foundry doesn't auto-save.** Press **Save** after every visualizer change or you lose the change. Each save creates a new immutable version.
6. **Power Fx scope prefixes are mandatory.** Use `System.` for system variables (e.g., `System.ConversationId`) and `Local.` for local variables — error: "Name isn't valid" means you forgot the prefix.
7. **Don't store secrets in workflow YAML.** No passwords, keys, or tokens in JSON schemas, prompts, or saved variables. Workflow versions are auditable artifacts.
8. **Observability planning is not optional.** Workflows execute across agent boundaries — wire OpenTelemetry tracing on every agent in the workflow so you can correlate spans. See `foundry-observability` for KQL templates and trace correlation across agents.
9. **API version distinction.** Workflows are GA on `2025-11-15-preview` and later. Connected Agents (classic) only exist on `2025-05-15-preview`. Match your API version to the surface you're using.
10. **RBAC required.** Editing workflows requires the **Contributor** role or higher on the project. If the Workflows tab is missing, that's an RBAC issue, not a feature flag.

---

## Cross-Cutting Concerns

- **Identity.** Each agent in the workflow uses **its own dedicated Microsoft Entra Agent Identity** at runtime — not the project managed identity. After publishing, reconfigure RBAC on every shared resource the agents touch (Storage, Search, Cosmos, etc.). See `foundry-projects-resources`.
- **Tools / Toolboxes.** Each agent in the workflow can have its own toolbox with its own tools (Web Search, AI Search, Code Interpreter, File Search, OpenAPI, MCP, A2A). Toolboxes are versioned independently of the workflow version. See `foundry-toolboxes`.
- **Memory.** Workflows that need cross-agent personalization (e.g., the user's history follows them across handoffs) should share a Foundry **memory store**. See `foundry-memory` for scoping (per-user, per-tenant) and prompt-injection risks.
- **Knowledge bases.** Multiple agents in the same workflow can share a Foundry IQ knowledge base — useful for document-heavy workflows (contract review, support triage). See `foundry-iq-knowledge-bases` for ACL + sensitivity-label enforcement.
- **Observability.** Cross-agent traces require correlated `traceparent` propagation. See `foundry-observability` for KQL templates that join traces across agent boundaries and for `azd ai agent monitor` usage.

---

## Reference Links

- **Workflow concept + how-to:** `https://learn.microsoft.com/azure/foundry/agents/concepts/workflow`
- **Declarative workflows in VS Code (low-code):** `https://learn.microsoft.com/azure/foundry/agents/how-to/vs-code-agents-workflow-low-code`
- **Hosted (pro-code) workflows in VS Code:** `https://learn.microsoft.com/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code`
- **Agent types overview (Prompt vs Workflow vs Hosted):** `https://learn.microsoft.com/azure/foundry/agents/overview`
- **Connected Agents (classic — deprecated):** `https://learn.microsoft.com/azure/foundry-classic/agents/how-to/connected-agents`
- **Migration guide (classic → GA Agents Service):** `https://learn.microsoft.com/azure/foundry/agents/how-to/migrate`
- **Agent Framework — workflow orchestrations index:** `https://learn.microsoft.com/agent-framework/workflows/orchestrations/`
- **Agent Framework — Group Chat orchestration:** `https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat`
- **Agent Framework — Declarative workflows overview:** `https://learn.microsoft.com/agent-framework/workflows/declarative`
- **Multi-agent reference architecture:** `https://learn.microsoft.com/azure/architecture/ai-ml/idea/multiple-agent-workflow-automation`

For anything not covered above (or if any link 404s), fall back to `microsoft_docs_search` with the queries listed in **Before You Build** — workflow docs are updated weekly during preview.
