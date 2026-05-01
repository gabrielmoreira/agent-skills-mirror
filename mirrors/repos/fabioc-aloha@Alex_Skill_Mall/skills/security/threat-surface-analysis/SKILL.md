---
type: skill
lifecycle: stable
inheritance: inheritable
name: threat-surface-analysis
description: Discover a codebase's threat surface through systematic investigation — map ecosystem groups, dependency graphs, service connections, authentication mechanisms, and trust boundaries. Use when performing threat modeling, security review, or architectural analysis of any multi-ecosystem repository.
tier: standard
applyTo: '**/*threat*,**/*surface*,**/*analysis*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Threat Surface Analysis

Systematic codebase investigation to discover the attack surface — services, dependencies, authentication, and trust boundaries. Language-agnostic, works across any ecosystem.

## When to Use

- Security review of a new or unfamiliar codebase
- Threat modeling preparation (discovering what to model)
- Architecture discovery for legacy systems
- Identifying external service connections and auth mechanisms
- Finding unprotected endpoints or misconfigured trust boundaries

---

## Core Principles

- **Intent-based classification** — classify by runtime purpose and behavior, not project name
- **Evidence, not conclusions** — record what was found; defer interpretation
- **Unknowns are valuable** — "Auth: Unknown" is better than guessing
- **Source projects are anchors** — entry points (web apps, functions, CLIs) become threat surfaces. Libraries are invisible.
- **Config flows DOWN** — a source project's config covers all its library dependencies

---

## Phase 1: Ecosystem Detection

Discover all programming languages, build systems, and infrastructure-as-code in the repository.

### Procedure (aim for ~5 tool calls)

1. **List workspace root** — one level deep
2. **Scan for manifests** using the table below (1–2 calls)
3. **Identify ecosystem groups** — a repo may contain multiple (e.g., .NET + React + Terraform)
4. **Read workspace descriptors** — `.sln`, `package.json` workspaces, `go.work`, etc.
5. **Form hypothesis** — 2–3 sentences on what the system does

### Manifest → Ecosystem Mapping

| Manifest Pattern | Ecosystem |
| ---------------- | --------- |
| `*.sln`, `*.csproj`, `*.fsproj` | .NET |
| `package.json` | Node.js / TypeScript |
| `go.mod` | Go |
| `pyproject.toml`, `requirements.txt`, `Pipfile` | Python |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java / Kotlin |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `*.bicep`, `*.tf`, `*.tfvars` | Infrastructure as Code |
| `docker-compose.yml`, `Dockerfile` | Container / Docker |
| `azure-pipelines.yml`, `.github/workflows/*.yml` | CI/CD Pipeline |

### Output

```markdown
## Ecosystem Groups

Group 1: <Ecosystem>
  Workspace descriptor: <path>
  Projects: <list>
  Dependency format: <e.g., PackageReference in .csproj>
  Config patterns: <e.g., appsettings.json>

Shared / Cross-cutting:
  IaC files: <list>
  CI/CD files: <list>
```

---

## Phase 2: Project Classification

Classify every project by type and assign preliminary trust boundaries.

### Classification Priority (first match wins)

| Priority | Signal | ProjectType |
| -------- | ------ | ----------- |
| 1 | Test framework dependency (xunit, jest, pytest, etc.) | Test (exclude) |
| 2 | HTTP server framework (Express, ASP.NET, Flask, etc.) | WebApplication |
| 2 | Serverless function framework | FunctionApp |
| 2 | Background worker / task processor | WorkerService |
| 2 | Client-side SPA (React, Angular, Blazor WASM) | ClientApp |
| 2 | gRPC server | GrpcService |
| 3 | Produces executable + CLI entrypoint | ConsoleApplication |
| 4 | No executable output, exports only | Library |

### Trust Boundary Defaults

| Deployment Pattern | Trust Boundary |
| ------------------ | -------------- |
| Cloud-hosted (Azure, AWS, GCP) | Cloud |
| Runs locally / dev tooling | On-Premises |
| CI/CD pipeline tooling | DevOps |
| Client-side / browser | Client |

### Source vs Library Rule

- **Source projects** = entry points (web apps, functions, CLIs, workers). These become threat-surface components.
- **Libraries** = internal code compiled into source projects. Not standalone components.
- **Transitive dependency rule**: SourceProject → Library → SDK → External Service. Only the SourceProject and External Service matter for threat modeling.

---

## Phase 3: Code Investigation

Produce a structured evidence artifact identifying services, dependencies, and authentication.

### Sub-phases

#### 3a — Dependency Graph (3–4 reads)

For each source project:
1. Read project manifests — extract internal references + external packages
2. Resolve transitive dependencies — walk library chain to find all external SDKs
3. Read infrastructure files (Bicep, Terraform, Docker) — reveal services not in code

**SDK-to-Service reasoning**: Every SDK package name reveals the service it connects to. Reason from the service brand name in the package.

#### 3b — Configuration & Auth (2–3 reads)

For each source project, read config from:
1. Project's own directory (authoritative)
2. Library dependencies (transitive)
3. Shared/root config (`.env`, `docker-compose.yml`)
4. IaC files

**URL discovery**: Any config key whose value is a URL or whose name suggests an endpoint (`*BaseUrl`, `*Endpoint`, `*ApiUrl`) points to an external service.

#### 3c — Code Confirmation (2–3 reads)

Read entry points and DI/service registration to confirm:
- Service client construction
- HTTP client usage and targets
- Database connections
- Message broker clients
- Auth middleware
- Telemetry setup

### Authentication Evidence Hierarchy

| Evidence | Classification |
| -------- | -------------- |
| Endpoint URL only, no credentials | `Auth: Unknown` |
| Endpoint + key/secret/token | `Auth: API Key` |
| Endpoint + client ID + secret | `Auth: Service Principal` |
| Endpoint + client ID + certificate | `Auth: Certificate` |
| Endpoint + managed identity / default credential | `Auth: Managed Identity` |
| OAuth scopes without credential | `Auth: OAuth (unconfirmed)` |

---

## Phase 4: Investigation Evidence Output

```markdown
# Investigation Evidence

## System Overview
- **Service Name:** <name>
- **Description:** <1–2 sentences>
- **Ecosystems:** <detected groups>

## Project Topology

| Project | Ecosystem | Type | Role | Trust Boundary | Key External Packages |
| ------- | --------- | ---- | ---- | -------------- | --------------------- |
| MyApp.Api | .NET | WebApplication | Source | Cloud | Azure.Storage, MSAL |
| MyApp.Core | .NET | Library | Library | N/A | — |

## Discovered Services & Resources

### 1. <Service Name>
- **SDK:** <package, which project>
- **Config:** <key, value, which file>
- **IaC:** <resource type, which file>
- **Code:** <client construction, which file>
- **Auth:** <mechanism and evidence>

## Cross-Project Links
- <how source projects relate to each other>

## Auth Summary

| Service | Mechanism | Evidence |
| ------- | --------- | -------- |

## Trust Boundary Diagram

(Generate a Mermaid flowchart showing trust boundaries and data flows)

## Confidence & Open Questions
- **Confidence:** High | Medium | Low
- **Open items:** <unresolved findings>
```

---

## Threat Surface Indicators

After investigation, flag these threat surface concerns:

| Indicator | Risk | Priority |
| --------- | ---- | -------- |
| External endpoint with `Auth: Unknown` | Unauthenticated access | Critical |
| API key in config file (not secrets store) | Credential exposure | High |
| No input validation on HTTP endpoints | Injection attacks | High |
| Cross-boundary data flow without encryption | Data in transit exposure | High |
| Service with broad permissions (admin/owner) | Excessive privilege | Medium |
| Unmonitored external dependency | Supply chain risk | Medium |
| Missing rate limiting on public endpoints | DoS vulnerability | Medium |

---

## Integration with Other Skills

| Skill | Relationship |
| ----- | ------------ |
| `security-review` | Uses this skill's output as input for STRIDE analysis |
| `security-threat-modeler` | Produces formal threat model from investigation evidence |
| `semantic-codebase-intelligence` | Complements with coupling/cohesion metrics |
| `architecture-audit` | Verifies docs match discovered architecture |

---

## Limitations

- Does not produce a formal threat model (use `security-threat-modeler` for that)
- Cannot discover runtime-only services not reflected in code or config
- Auth classification is evidence-based — production secrets are not read
- IaC resources without code references may be missed if not in scanned directories
