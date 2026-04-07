# OpenClaw Enterprise Platform — Roadmap

## Completed (v1.0)

### Admin Console — Frontend (18 pages)
- [x] React 19 + Tailwind CSS v4 dark theme + ApexCharts
- [x] Dashboard with 6 KPI cards, conversation trend chart (from API), agent health, channel distribution
- [x] Department Overview — cards view with coverage bars, tree view, detail drawer with BFS sub-department rollup
- [x] Position Management — provision status column, inline bulk provision, default channel config
- [x] Employee Management — activity metrics from API, channel status indicators, agent links, mini bar charts
- [x] Agent Factory — list/detail/create wizard, position-based filtering
- [x] SOUL Editor — three-layer editor with live preview (Global locked, Position/Personal editable)
- [x] Workspace Manager — three-layer file tree with S3 read/write, role-filtered skills
- [x] Skill Platform — 26 skills (6 global + 20 department-scoped), API Key Vault, role permissions matrix
- [x] Agent Assignments — employee-agent overview, bulk provision, routing rules, IM user mappings
- [x] Knowledge Base — document management, scope-based access, retrieval test
- [x] Monitor Center — 3 tabs (Live Sessions, Agent Health from API, Alert Rules from API), system health bar, real-time chart
- [x] Session Detail — conversation stream from API (role-specific), takeover mode, quality metrics, Plan E scan, response time chart
- [x] Audit Center — 4 tabs (AI Insights, Event Timeline, Breakdown with charts, Security Alerts), empty state handling
- [x] Usage & Cost — time range selector, cost trend from API, 4 tabs (Department, Agent, Model breakdown with donut chart, Budget)
- [x] Approvals — pending/resolved queue with DynamoDB persistence
- [x] Playground — Simulate/Live toggle, real AgentCore invocation via Tenant Router
- [x] Settings — LLM model config with per-position overrides, security policy, service status

### Admin Console — UX & Navigation
- [x] Global search bar — functional with deduplicated results, page + feature shortcuts
- [x] Notification bell — real count from pending approvals + active alerts, click → Approvals
- [x] System status indicator — dynamic from alert rules API, click → Monitor
- [x] Cross-page navigation — agent names clickable in Employees/Monitor/Dashboard, affected users in Audit Insights
- [x] Sidebar restructured — Bindings under Organization, Approvals standalone, Agent Factory simplified
- [x] Zero hardcoded frontend data — all data from API (DynamoDB/S3/CloudWatch)

### Admin Console — Backend (FastAPI, 35+ endpoints)
- [x] DynamoDB single-table design with 7 entity types (org, agents, bindings, audit, approvals, config, knowledge)
- [x] DynamoDB usage metrics — per-agent daily usage, sessions, employee activity, cost trend (seeded by seed_usage.py)
- [x] S3 operations — SOUL layers, skills, workspace files, memory, versioning
- [x] Auto-provision on employee creation — `_auto_provision_employee()` creates agent + assignment + SSM mappings + audit trail
- [x] Bulk provision by position — delegates to auto-provision, updates position default channel
- [x] AI Security Scanner — `/api/v1/audit/insights` analyzes audit patterns, memory files, usage anomalies, SOUL version drift
- [x] Alert rules engine — `/api/v1/monitor/alerts` evaluates conditions against real DynamoDB data (budget, idle agents, unbound employees)
- [x] Session detail API — `/api/v1/monitor/sessions/{id}` returns role-specific conversations, quality metrics, Plan E results
- [x] Monitor health API — `/api/v1/monitor/health` returns per-agent metrics + system status
- [x] Usage trend API — `/api/v1/usage/trend` reads 7-day cost trend from DynamoDB
- [x] Employee activity API — `/api/v1/org/employees/activity` reads activity + channel status from DynamoDB

### Admin Console — Seed Scripts
- [x] `seed_dynamodb.py` — org structure, employees, agents, bindings (112+ items)
- [x] `seed_audit_approvals.py` — 20 audit entries + 6 approvals
- [x] `seed_skills_final.py` — 26 skills to S3 with manifests
- [x] `seed_knowledge.py` — knowledge base entries
- [x] `seed_settings.py` — model config, security config
- [x] `seed_workspaces.py` — 6 employee workspace files (IDENTITY.md, USER.md, MEMORY.md)
- [x] `seed_usage.py` — 140 usage records (20 agents × 7 days), 8 sessions, 18 employee activities, 7 cost trend days

### Agent Runtime
- [x] workspace_assembler.py — three-layer SOUL merge at first invocation
- [x] skill_loader.py — S3 skill loading with role-based filtering + SSM key injection
- [x] Delayed assembly in server.py (handles tenant=unknown at startup)
- [x] Docker image with 13 ClawHub built-in skills
- [x] 10 position-specific SOUL templates in S3
- [x] 6 employee workspace files (IDENTITY.md, USER.md, MEMORY.md, daily memory)

### Infrastructure
- [x] DynamoDB single-table `openclaw-enterprise` in us-east-2
- [x] S3 bucket `openclaw-tenants-{account}` with versioning
- [x] SSM tenant→position mappings in us-east-1 and us-east-2
- [x] AgentCore IAM role with SES/SNS/Transcribe/Connect permissions
- [x] Admin Console deployed on Gateway EC2 via systemd
- [x] SSM port forwarding for secure access (no open security groups)
- [x] CloudFront distribution with EC2 origin (nginx reverse proxy 80→8099), origin restricted to CloudFront managed prefix list
- [x] ACM wildcard certificate (*.awspsa.com) for HTTPS
- [x] Route 53 A record alias for custom domain access
- [x] AgentCore Runtime v20 with env vars (S3_BUCKET, STACK_NAME, AWS_REGION, BEDROCK_MODEL_ID, DYNAMODB_TABLE)
- [x] Docker image v20: workspace path fix, SOUL identity override, AWS CLI via pip (not binary copy), DynamoDB usage tracking
- [x] SOUL three-layer injection verified: Carol=Finance Analyst, Wang Wu=SDE, Zhang San=SA

### Gateway Architecture
- [x] H2 Proxy (bedrock_proxy_h2.js) — intercepts OpenClaw Bedrock SDK HTTP/2 calls, extracts sender identity from JSON metadata
- [x] Tenant Router (tenant_router.py) — derives tenant_id, invokes AgentCore with session isolation
- [x] H2 Proxy + Gateway as systemd services (auto-restart, survives EC2 reboot)
- [x] Fast-path disabled — all IM messages route through AgentCore (no direct Bedrock fallback)
- [x] Discord Bot connected and verified: DM → Gateway → H2 Proxy → Tenant Router → AgentCore → Bedrock → reply
- [x] Gateway architecture documented in README (one Bot serves all employees)
- [x] Employee onboarding flow documented (pairing code → IT approval → SSM mapping)

### Monitor Center — Runtime Events
- [x] CloudWatch Logs query for microVM lifecycle events (invocations, SIGTERM, assembly, sync)
- [x] Runtime Events tab in Monitor page with summary cards + event timeline
- [x] Auto-refresh every 15 seconds
- [x] Event classification: invocation, response, cold_start, release, sync, plan_a, usage, mapping

### RBAC & Employee Portal
- [x] Three-role system: Admin (full access), Manager (department-scoped), Employee (portal only)
- [x] JWT authentication with role/department claims
- [x] Login page with 8 demo accounts (2 admin, 3 manager, 3+ employee)
- [x] Manager data scoping — all list APIs filter by department (BFS sub-department rollup)
- [x] Employee Self-Service Portal — 5 pages (Chat, Profile, Usage, Skills, Requests)
- [x] Portal Chat with real AgentCore integration (Tenant Router → microVM → OpenClaw → Bedrock)
- [x] Chat history persistence (localStorage) + Markdown rendering (react-markdown)
- [x] Portal Profile with USER.md editor and memory viewer
- [x] Admin Console user display shows real name/role, logout button
- [x] Global notification bell with real pending approvals + active alerts count
- [x] System status indicator dynamic from alert rules API

### SOUL Three-Layer Runtime Injection
- [x] workspace_assembler.py merges Global + Position + Personal → `~/.openclaw/workspace/SOUL.md`
- [x] OpenClaw reads merged SOUL on session start — verified Carol=Finance, Wang Wu=SDE
- [x] Workspace path: `/root/.openclaw/workspace` (OpenClaw default, not `/tmp/workspace`)
- [x] `openclaw.json`: explicit workspace path + `skipBootstrap: true`
- [x] Tenant ID parsing: `channel__employee_id__hash` → extract `employee_id` as base ID
- [x] SOUL merge adds identity override prefix for stronger LLM compliance

### Real-time Usage Tracking
- [x] server.py writes usage data to DynamoDB after every successful AgentCore invocation
- [x] Fire-and-forget background thread (non-blocking response)
- [x] Atomic increment via DynamoDB `UpdateItem ADD` (USAGE#{agent}#{date} and SESSION#{tenant})
- [x] AgentCore IAM role updated with DynamoDB write permissions
- [x] Docker image v20 deployed with DYNAMODB_TABLE env var

### Workspace Memory Writeback
- [x] Agent writes memory files during session (e.g., `memory/2026-03-21.md`)
- [x] Watchdog sync (60s interval) writes back to S3 using base employee ID
- [x] S3 path: `s3://{bucket}/{employee_id}/workspace/` — persists across sessions
- [x] Cleanup on SIGTERM: final S3 sync before microVM shutdown
- [x] Excludes assembled files (SOUL.md, AGENTS.md, TOOLS.md, IDENTITY.md) from writeback
- [x] AWS CLI fixed: pip install awscli (not binary copy from builder — avoids Python version mismatch)
- [x] Verified: Carol's `memory/2026-03-21.md` synced to S3 after agent session

## In Progress

### IM Channel User→Employee Mapping (Priority: High)
- [x] SSM user-mapping write/read in Admin Console backend
- [x] IM User Mappings tab in Bindings page (add/delete UI)
- [x] H2 Proxy JSON metadata extraction (sender_id from OpenClaw message format)
- [x] server.py SSM user-mapping lookup for non-emp base IDs
- [ ] Pairing approve integration in Admin Console (subprocess call to openclaw CLI)
- [ ] Auto-create DynamoDB Employee + Agent records from IM mapping

Portal uses `emp-xxx` as user_id, so base ID extraction works. But IM channels use platform IDs:

| Channel | user_id example | base ID extracted | S3 path | Status |
|---------|----------------|-------------------|---------|--------|
| Portal | emp-carol | emp-carol | emp-carol/workspace/ | ✅ Works |
| WhatsApp | 8613800138000 | 8613800138000 | 8613800138000/workspace/ | ❌ Wrong path |
| Telegram | 123456789 | 123456789 | 123456789/workspace/ | ❌ Wrong path |
| Slack | U0123ABC | U0123ABC | U0123ABC/workspace/ | ❌ Wrong path |

**Design:** SSM reverse mapping from channel user_id to employee_id:
```
/openclaw/{stack}/user-mapping/wa__8613800138000 → emp-carol
/openclaw/{stack}/user-mapping/tg__123456789 → emp-z3
```

**Implementation options:**
1. Admin Console Bindings page: when creating a binding with channel + employee, write SSM mapping
2. entrypoint.sh / server.py: on first invocation, look up SSM mapping to resolve base employee ID
3. Tenant Router: resolve employee_id before invoking AgentCore, pass as header/env var

**Tasks:**
- [ ] Add SSM user-mapping write to binding creation API
- [ ] Update server.py `_ensure_workspace_assembled` to check SSM mapping for non-emp user_ids
- [ ] Update entrypoint.sh watchdog to use resolved employee_id
- [ ] Admin Console: show channel user_id in Bindings detail
- [ ] Seed SSM mappings for demo employees' IM accounts

### HEARTBEAT.md — Scheduled Tasks (Priority: High)
AgentCore is serverless — microVM releases after idle timeout. Need external scheduler.

**Design:**
```
EventBridge Scheduler → Lambda → S3 HEARTBEAT scan → Tenant Router → AgentCore cold-start → OpenClaw → Channel delivery
```

**Tasks:**
- [ ] EventBridge Scheduler rules
- [ ] Lambda function to scan S3 for HEARTBEAT.md files
- [ ] Tenant Router integration for scheduled invocations
- [ ] Admin Console UI for managing heartbeat schedules

### Layer 3 Skill Build Pipeline (Priority: Medium)
Pre-build npm-dependent skills into tar.gz bundles to avoid Docker image bloat.

**Design:**
```
Admin Console "Install Skill" → API Gateway → Lambda → CodeBuild (ARM64) → tar.gz → S3 → skill_loader.py extracts at startup
```

**Tasks:**
- [ ] CodeBuild project with ARM64 environment
- [ ] Lambda trigger function
- [ ] Admin Console "Install from ClawHub" flow
- [ ] Move non-core skills from Layer 1 (Docker) to Layer 3 (S3 bundles)

### AWS Service Configuration UI (Priority: Medium)
Admin Console pages for configuring AWS services used by skills.

- [ ] SES: Verify sender email/domain, manage templates
- [ ] SNS: Create topics, manage subscriptions
- [ ] Connect: Instance setup, contact flow configuration
- [ ] Transcribe: Custom vocabulary management
- [ ] Bedrock KB: Knowledge base creation and indexing

## Planned (v1.1)

### Organization Sync
- [ ] Feishu/DingTalk organization sync (webhook + periodic pull)
- [ ] LDAP/Active Directory integration
- [ ] Auto-provision on employee onboarding (already implemented for manual creation)
- [ ] Auto-archive agent on employee offboarding

### Change Management & Approval Workflow
- [ ] SOUL.md change approval workflow (Global: CISO+CTO, Position: dept admin, Personal: self)
- [ ] Draft → Review → Approve → Canary → Full deploy pipeline
- [ ] A/B testing for SOUL versions with quality score comparison
- [ ] Automatic rollback on quality score drop

### Agent Quality System
- [ ] Real quality scoring from CloudWatch metrics (replace seed data)
- [ ] Explicit feedback collection (thumbs up/down via channel)
- [ ] Implicit signal tracking (follow-up questions, conversation abandonment)
- [ ] Quality alerts and automated model downgrade
- [ ] Quality score formula: 0.3×satisfaction + 0.2×toolSuccess + 0.2×responseTime + 0.2×compliance + 0.1×completionRate

### SSO Integration
- [ ] SAML 2.0 / OIDC
- [ ] Feishu SSO
- [ ] DingTalk SSO
- [ ] AWS IAM Identity Center

### Data Export & Portability
- [ ] Export agent config as OpenClaw workspace zip
- [ ] Export department/org data as JSON
- [ ] SOC 2 / GDPR compliance report generation
- [ ] Employee can export personal agent + memory for use in personal OpenClaw

### Real-time Data Pipeline
- [ ] Replace seed usage data with CloudWatch Metrics integration
- [ ] Replace seed sessions with CloudWatch Logs real-time query
- [ ] Replace seed employee activity with aggregated session/audit data
- [ ] WebSocket for live session streaming in Monitor

## Planned (v2.0)

### Multi-Tenancy (MSP Mode)
- [ ] One platform serving multiple enterprise customers
- [ ] Tenant isolation at DynamoDB partition key + S3 prefix level
- [ ] Per-tenant billing and usage tracking
- [ ] Tenant admin console with scoped permissions

### ISV Marketplace
- [ ] Third-party skill/template/connector marketplace
- [ ] Revenue sharing model
- [ ] Skill certification and security review process
- [ ] Community ratings and reviews

### Mobile
- [ ] Responsive Admin Console (current layout is desktop-first)
- [ ] Mobile-optimized Playground
- [ ] Push notifications for approvals and alerts

### Advanced Monitoring
- [ ] Conversation replay from CloudWatch Logs
- [ ] Anomaly detection on usage patterns (ML-based)
- [ ] Agent-to-agent delegation tracking
- [ ] Cost anomaly alerts (sudden spike detection)

### Zero-Trust Security (ref: OpenClaw Enterprise project)
- [ ] Runtime guardrails — credential harvest detection, reverse shell blocking
- [ ] Input sanitization — Unicode normalization, prompt injection pattern detection
- [ ] Supply chain security — Ed25519 code signing for skills
- [ ] Network controls — IP allowlisting, token-bucket rate limiting

## Architecture Reference

```
Gateway EC2 (<YOUR_INSTANCE_ID>, us-east-1)
├── OpenClaw Gateway (port 18789)
├── H2 Proxy
├── Tenant Router (port 8090)
└── Admin Console (port 8099, systemd: openclaw-admin)

AgentCore Runtime v20 (us-east-1)
├── Firecracker microVM per tenant
├── Env: S3_BUCKET=openclaw-tenants-<ACCOUNT_ID>, STACK_NAME=openclaw-multitenancy
├── workspace_assembler.py → three-layer SOUL merge → ~/.openclaw/workspace/SOUL.md
├── skill_loader.py → S3 skill loading with role filtering
├── openclaw.json → workspace=/root/.openclaw/workspace, skipBootstrap=true
└── OpenClaw CLI → Bedrock (Nova 2 Lite default)

DynamoDB: openclaw-enterprise (us-east-2)
├── ORG#acme → DEPT#, POS#, EMP# (with role field), AGENT#, BIND#
├── AUDIT#, APPROVAL#, CONFIG#, KB#
├── USAGE#agent#date, SESSION#, ACTIVITY#emp, COST_TREND#date
├── RULE# (routing rules), CONV#session#seq (conversations)
└── GSI1: TYPE# for cross-entity queries

S3: openclaw-tenants-{account} (global)
├── _shared/soul/global/ (SOUL.md, AGENTS.md, TOOLS.md)
├── _shared/soul/positions/{pos-id}/ (10 position SOUL templates)
├── _shared/skills/{skill-name}/ (26 skill manifests + code)
└── {employee-id}/workspace/ (personal files, memory)

Auth: JWT tokens (HS256)
├── Admin → full access to all APIs
├── Manager → department-scoped (BFS sub-department rollup)
└── Employee → portal endpoints only (/api/v1/portal/*)

Access: SSM port forwarding only (no open security groups)
  aws ssm start-session --target <YOUR_INSTANCE_ID> --region us-east-1 \
    --document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber":["8099"],"localPortNumber":["8199"]}'
  → http://localhost:8199
```
