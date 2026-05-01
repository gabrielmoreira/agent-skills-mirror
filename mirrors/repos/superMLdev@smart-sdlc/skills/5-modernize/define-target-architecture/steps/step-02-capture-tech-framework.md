# Step 02 — Capture Company Technology Framework

**Previous step:** `step-01-assess-legacy.md`
**Next step:** `step-03-design-architecture.md`

---

## Why This Step Cannot Be Skipped

Architecture decisions without a technology framework produce unusable designs. If Rex picks Spring Boot and your company standardizes on .NET — the entire design is wrong. This step ensures every architecture decision is aligned with company standards before the first diagram is drawn.

---

## Technology Framework Interview

Rex asks the following questions. Some are required; some are optional but influence architecture decisions.

Present all questions at once, grouped by category:

```
🏛️ Technology Framework Capture
══════════════════════════════════════════════════════════
I need to understand your company's approved technology stack.
Please answer what you know — say "unknown" or "not decided" for anything uncertain.

BACKEND
  1. Primary language/framework: (e.g., Java/Spring Boot, .NET/C#, Node.js/Express,
                                   Python/FastAPI, Go, Kotlin/Ktor, other)
  2. API style: (REST | GraphQL | gRPC | Mix)
  3. Service pattern: (Monolith | Modular Monolith | Microservices | not decided)
  4. Authentication/Authorization: (JWT/OAuth2 | LDAP | SAML | Custom | not decided)

FRONTEND (if applicable)
  5. Frontend framework: (React | Angular | Vue | Blazor | None — API only | not decided)
  6. Mobile: (iOS native | Android native | React Native | Flutter | None)

DATA
  7. Primary database: (PostgreSQL | MySQL | SQL Server | Oracle | MongoDB | other)
  8. Caching: (Redis | Memcached | None | not decided)
  9. Search: (Elasticsearch | OpenSearch | None | not decided)

MESSAGING / INTEGRATION
  10. Message broker: (Kafka | RabbitMQ | Azure Service Bus | AWS SQS | None | not decided)
  11. Integration approach: (API-first | Event-driven | Batch files retained | Mix)

INFRASTRUCTURE
  12. Cloud provider: (AWS | Azure | GCP | On-premise | Hybrid | not decided)
  13. Container/orchestration: (Kubernetes (EKS/AKS/GKE) | Docker Compose | None)
  14. CI/CD: (GitHub Actions | Azure DevOps | Jenkins | GitLab CI | other)
  15. IaC: (Terraform | Bicep | CloudFormation | Pulumi | None | not decided)

OBSERVABILITY
  16. Logging: (ELK/Opensearch | Azure Monitor | CloudWatch | Datadog | Splunk | other)
  17. APM/Tracing: (Datadog | New Relic | Dynatrace | Jaeger | None | not decided)

SECURITY
  18. Secret management: (HashiCorp Vault | AWS Secrets Manager | Azure Key Vault | not decided)
  19. API gateway: (Kong | AWS API Gateway | Azure APIM | Nginx | not decided)

DEVELOPMENT STANDARDS
  20. Architecture patterns preferred: (DDD | Hexagonal | Clean | Layered | not decided)
  21. Any approved libraries/frameworks we must use?
  22. Any technologies explicitly BANNED in your organization?

══════════════════════════════════════════════════════════
Take your time — accurate answers here ensure the architecture fits your standards.
```

---

## Handling "Not Decided" Responses

For items marked "not decided", Rex uses sensible defaults aligned with the language choice:

```
If backend = Spring Boot (Java):
  Default database: PostgreSQL (industry standard for new projects)
  Default messaging: Kafka (if event-driven needed)
  Default auth: Spring Security + OAuth2/JWT

If backend = .NET/C#:
  Default database: SQL Server or PostgreSQL
  Default messaging: Azure Service Bus (if on Azure) or RabbitMQ
  Default auth: ASP.NET Core + OAuth2/JWT

If backend = Node.js:
  Default database: PostgreSQL
  Default messaging: RabbitMQ or Kafka
  Default auth: Passport.js + JWT
```

Rex states assumptions explicitly:
> "For items marked 'not decided', I'll use these defaults — please correct any that conflict with your standards:
> - Database: PostgreSQL (standard for new relational workloads)
> - Messaging: Kafka (given the event-driven needs of order processing)
> - Auth: OAuth2/JWT"

---

## Architecture Constraints

After capturing the framework, derive constraints:

```
Architecture Constraints (derived from tech framework):
  
  CONSTRAINT-01: All services must be containerized (Docker) for Kubernetes deployment
  CONSTRAINT-02: All inter-service communication via REST API (GraphQL not approved)
  CONSTRAINT-03: No direct database access across service boundaries
  CONSTRAINT-04: All secrets in HashiCorp Vault — no hardcoded credentials
  CONSTRAINT-05: Auth via company OAuth2 identity provider — no custom auth
  CONSTRAINT-06: Kafka for all async events (RabbitMQ not approved)
  
  BANNED TECHNOLOGIES: {list anything user mentioned}
```

---

## Write Tech Framework Document

Write `{project-root}/_superml/modernization/tech-framework.md`:

```markdown
# Company Technology Framework — {project_name}

> Captured on {date}. Validated by: {name/role}.
> This is the constraint document for all architecture decisions.

## Backend
- Language/Framework: {e.g., Java 21 / Spring Boot 3.x}
- API Style: REST
- Service Pattern: Microservices
- Auth: OAuth2/JWT via Okta

## Frontend
- Framework: React 18+
- Mobile: React Native (iOS + Android)

## Data
- Primary DB: PostgreSQL 16
- Cache: Redis 7
- Search: Elasticsearch 8

## Messaging
- Broker: Apache Kafka
- Pattern: Event-driven for async, REST for sync

## Infrastructure
- Cloud: AWS (us-east-1 primary, us-west-2 DR)
- Containers: Kubernetes (EKS)
- IaC: Terraform

## Observability
- Logging: ELK (company-managed)
- APM: Datadog

## Security
- Secrets: HashiCorp Vault
- API Gateway: Kong

## Standards
- Pattern: Hexagonal Architecture (ports and adapters)
- Required libraries: {list}
- Banned: {list}

## Architecture Constraints (derived)
| ID | Constraint |
|----|-----------|
| C-01 | All services containerized (Docker) |
| C-02 | No direct DB access across services |
| C-03 | Secrets only via Vault |
| C-04 | Auth via Okta OAuth2 |
```

⏸️ **STOP** — Present the captured framework for confirmation.

> "Here's what I've captured as your technology framework. Before I design the architecture, please confirm:
> 1. Is anything here wrong or outdated?
> 2. Is anything missing?
> 3. Are there technology choices that are still being decided that might affect architecture?"

---

## Save State

Update `{project-root}/_superml/modernize-state.yml`:
```yaml
step: "arch-step-02-capture-tech-framework"
status: "complete"
tech_framework_captured: true
backend: "{language/framework}"
database: "{db}"
cloud: "{provider}"
service_pattern: "{monolith|modular-monolith|microservices}"
constraints_count: {n}
```

Load and follow `./step-03-design-architecture.md`.
