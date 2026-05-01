# Create Architecture — Workflow

**Goal:** Produce a comprehensive architecture document that gives developers everything they need to build without guessing.

**Output:** `{planning_artifacts}/architecture/{project_name}-architecture.md`

---

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Load PRD from `{planning_artifacts}/prd/` (ask which one if multiple)
3. Load `project-context.md` if it exists (for brownfield context)
4. Say: "I'll design the architecture from your PRD. I'll ask clarifying questions as needed and document all trade-offs."

---

## Section 1: System Overview

Ask / derive from PRD:
1. **System type**: Web app, API service, CLI tool, mobile backend, data pipeline, ML system?
2. **Deployment target**: Cloud (which provider?), on-premise, hybrid, edge?
3. **Scale expectations**: Concurrent users, requests/sec, data volume?
4. **Availability requirements**: SLA? Acceptable downtime?

Write:
```markdown
## System Overview
[2–3 sentence description of what is being built at the system level]

### System Type
...
### Scale & Availability
...
```

⏸️ **STOP** — present and confirm before proceeding.

---

## Section 2: Architecture Pattern

Propose an architecture pattern with explicit trade-offs.

Consider and document:
- **Chosen pattern** (Monolith, Modular Monolith, Microservices, Event-Driven, Serverless, etc.)
- **Why this pattern**: specific reasons tied to the project's scale, team, and timeline
- **Alternatives considered**: list 2 alternatives and why they were rejected
- **Trade-offs accepted**: what we're giving up by choosing this pattern

```markdown
## Architecture Pattern

**Chosen:** {pattern}

**Rationale:** ...

**Alternatives Considered:**
| Alternative | Why Rejected |
|-------------|--------------|
| ... | ... |

**Trade-offs:**
- We accept: ...
- We gain: ...
```

---

## Section 3: Component Design

Design the key system components:

For each component:
- Name and responsibility (single sentence)
- Boundaries — what it owns, what it does NOT own
- Interface (API it exposes or events it produces)
- Technology choice + rationale

Generate a Mermaid component diagram:

```mermaid
graph TD
  [components and their connections]
```

⏸️ **STOP** — review diagram with user before continuing.

---

## Section 4: Data Architecture

Define:
- **Primary data store(s)** — type, technology, rationale
- **Core data model** — entity list with key fields
- **Data flow** — how data moves between components
- **Caching layer** — if applicable
- **Event/message bus** — if applicable

Generate ER diagram for core entities:

```mermaid
erDiagram
  [entities]
```

---

## Section 5: API Design

For each external-facing interface:
- Protocol (REST, GraphQL, gRPC, WebSocket)
- Authentication mechanism
- Key endpoints or operations (top 10 by importance)
- Error handling strategy
- Versioning strategy

---

## Section 6: Security Architecture

Required for every system — never skip:
- **Authentication**: mechanism and provider
- **Authorization**: model (RBAC, ABAC, ownership-based)
- **Data protection**: encryption at rest and in transit
- **Input validation**: where and how
- **Secrets management**: no hardcoded credentials — how secrets are stored and accessed
- **Audit logging**: what events are logged and where

---

## Section 7: Observability

Define:
- **Logging**: format, levels, centralization
- **Metrics**: what to measure, dashboards
- **Tracing**: distributed tracing if applicable
- **Alerting**: critical thresholds and on-call routing
- **Health checks**: endpoints and checks

---

## Section 8: Infrastructure and Deployment

Define:
- **Environment strategy**: dev, staging, production
- **Containerization**: Docker, container registry
- **Orchestration**: Kubernetes, ECS, App Service, etc.
- **CI/CD pipeline**: stages, gates, deploy strategy
- **Infrastructure as Code**: Terraform, Bicep, CDK, etc.

---

## Section 9: Architecture Decision Records (ADRs)

For each significant decision made above, create a compact ADR entry:

```markdown
### ADR-001: {Decision Title}
**Status:** Accepted
**Context:** Why this decision was needed
**Decision:** What was decided
**Consequences:** What changes as a result (positive and negative)
```

---

## Finalize and Save

Compile all sections into `{planning_artifacts}/architecture/{project_name}-architecture.md`.

Update frontmatter:
```yaml
project: {project_name}
version: 1
status: approved
created: {date}
owner: {user_name}
prd_version: {version of PRD this was based on}
```

Ask:
> "Architecture document complete. Would you like to:
> 1. Create epics and stories from this architecture (`create-epics-stories`)
> 2. Push to Confluence (`confluence-push-doc`)
> 3. Both"
