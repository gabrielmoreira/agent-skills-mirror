---
name: dashclaw-platform-intelligence
description: DashClaw platform expert for integration, troubleshooting, and governance. Snapshot-based — always prefer live queries via `python -m livingcode query`.
---

# DashClaw Platform Intelligence

**Shape snapshot:** `sha1:090d2e11f6a088493894729c69c128229678dcbc`
**This file is auto-generated.** Do not edit by hand — regenerate with:

```bash
python -m livingcode emit skill --output <path-to-SKILL.md>
```

## Prefer Live Queries

The facts below are a snapshot. Before answering any question about DashClaw's current
structure, routes, env vars, or schema — run a live query:

```bash
python -m livingcode query summary     # High-level shape
python -m livingcode query routes      # Current API surface
python -m livingcode query env         # Current env vars
python -m livingcode query tables      # Current schema
python -m livingcode query all --json  # Full machine-readable shape
```

If the snapshot below disagrees with a live query, **trust the live query**.

## At a Glance

- **174** active API routes across **44** categories
- **4** required + **101** optional environment variables
- **73** database tables

## API Surface

### `actions`

- `DELETE, GET, POST` `/api/actions`
- `GET, PATCH` `/api/actions/[actionId]`
- `GET` `/api/actions/[actionId]/artifacts`
- `GET` `/api/actions/[actionId]/graph`
- `GET` `/api/actions/[actionId]/messages`
- `GET` `/api/actions/[actionId]/trace`
- `GET` `/api/actions/costs`
- `GET, POST` `/api/actions/loops`
- `GET, PATCH` `/api/actions/loops/[loopId]`
- `GET` `/api/actions/stats`

### `activity`

- `GET` `/api/activity`

### `agents`

- `GET` `/api/agents`
- `GET` `/api/agents/[agentId]`
- `GET` `/api/agents/[agentId]/profile`
- `GET, POST` `/api/agents/connections`
- `POST` `/api/agents/heartbeat`

### `analytics`

- `GET` `/api/analytics`

### `approvals`

- `POST` `/api/approvals/[actionId]`

### `artifacts`

- `GET, POST` `/api/artifacts`
- `DELETE, GET` `/api/artifacts/[artifactId]`
- `POST` `/api/artifacts/evidence-bundle`

### `assumptions`

- `GET, POST` `/api/assumptions`
- `GET, PATCH` `/api/assumptions/[assumptionId]`

### `auth`

- `-` `/api/auth/[...nextauth]`
- `GET` `/api/auth/config`
- `DELETE, POST` `/api/auth/local`

### `billing`

- `POST` `/api/billing/checkout`
- `GET` `/api/billing/portal`

### `capabilities`

- `GET, POST` `/api/capabilities`
- `DELETE, GET, PATCH` `/api/capabilities/[capabilityId]`
- `GET, POST` `/api/capabilities/[capabilityId]/access`
- `DELETE` `/api/capabilities/[capabilityId]/access/[ruleId]`
- `GET` `/api/capabilities/[capabilityId]/access/check`
- `GET` `/api/capabilities/[capabilityId]/health`
- `GET` `/api/capabilities/[capabilityId]/history`
- `POST` `/api/capabilities/[capabilityId]/invoke`
- `POST` `/api/capabilities/[capabilityId]/test`
- `GET` `/api/capabilities/health`

### `compliance`

- `GET` `/api/compliance/evidence`
- `GET, POST` `/api/compliance/exports`
- `DELETE, GET` `/api/compliance/exports/[exportId]`
- `GET` `/api/compliance/exports/[exportId]/download`
- `GET` `/api/compliance/frameworks`
- `GET` `/api/compliance/gaps`
- `GET` `/api/compliance/map`
- `GET` `/api/compliance/report`
- `GET, POST` `/api/compliance/schedules`
- `DELETE, PATCH` `/api/compliance/schedules/[scheduleId]`
- `GET` `/api/compliance/trends`

### `cron`

- `GET` `/api/cron/integration-health`
- `GET` `/api/cron/learning-episodes-backfill`
- `GET` `/api/cron/learning-recommendations`
- `GET` `/api/cron/memory-maintenance`
- `GET` `/api/cron/policy-suggestions`
- `GET` `/api/cron/reset-meters`
- `POST` `/api/cron/routing-maintenance`
- `GET` `/api/cron/signals`

### `docs`

- `GET` `/api/docs/raw`

### `doctor`

- `GET` `/api/doctor`
- `POST` `/api/doctor/fix`

### `drift`

- `GET, POST` `/api/drift/alerts`
- `DELETE, PATCH` `/api/drift/alerts/[alertId]`
- `GET` `/api/drift/metrics`
- `GET` `/api/drift/snapshots`
- `GET` `/api/drift/stats`

### `evaluations`

- `GET, POST` `/api/evaluations`
- `GET, POST` `/api/evaluations/runs`
- `GET, PATCH` `/api/evaluations/runs/[runId]`
- `GET, POST` `/api/evaluations/scorers`
- `DELETE, PATCH` `/api/evaluations/scorers/[scorerId]`
- `GET` `/api/evaluations/stats`

### `guard`

- `GET, POST` `/api/guard`
- `GET` `/api/guard/decisions`

### `health`

- `GET` `/api/health`

### `identities`

- `GET, POST` `/api/identities`
- `DELETE` `/api/identities/[agentId]`

### `integrations`

- `GET` `/api/integrations/health`

### `keys`

- `DELETE, GET, POST` `/api/keys`
- `GET` `/api/keys/reveal`

### `knowledge`

- `GET, POST` `/api/knowledge/collections`
- `DELETE, GET, PATCH` `/api/knowledge/collections/[collectionId]`
- `GET, POST` `/api/knowledge/collections/[collectionId]/items`
- `POST` `/api/knowledge/collections/[collectionId]/search`
- `POST` `/api/knowledge/collections/[collectionId]/sync`

### `learning`

- `GET, POST` `/api/learning`
- `GET, POST` `/api/learning/analytics/curves`
- `GET` `/api/learning/analytics/maturity`
- `GET` `/api/learning/analytics/summary`
- `GET, POST` `/api/learning/analytics/velocity`
- `GET` `/api/learning/lessons`
- `GET, POST` `/api/learning/recommendations`
- `PATCH` `/api/learning/recommendations/[recommendationId]`
- `POST` `/api/learning/recommendations/events`
- `GET` `/api/learning/recommendations/metrics`
- `GET, POST` `/api/learning/suggestions`

### `mcp`

- `POST` `/api/mcp`

### `messages`

- `GET, PATCH, POST` `/api/messages`
- `GET` `/api/messages/attachments`
- `GET, PATCH, POST` `/api/messages/threads`
- `GET` `/api/messages/threads/[threadId]`

### `model-strategies`

- `GET, POST` `/api/model-strategies`
- `DELETE, GET, PATCH` `/api/model-strategies/[strategyId]`
- `POST` `/api/model-strategies/[strategyId]/complete`

### `operations`

- `GET` `/api/operations/feed`
- `GET` `/api/operations/summary`

### `orgs`

- `GET, POST` `/api/orgs`
- `GET, PATCH` `/api/orgs/[orgId]`
- `DELETE, GET, POST` `/api/orgs/[orgId]/keys`

### `pairings`

- `GET, POST` `/api/pairings`
- `GET, PATCH` `/api/pairings/[pairingId]`
- `POST` `/api/pairings/[pairingId]/approve`

### `policies`

- `DELETE, GET, PATCH, POST` `/api/policies`
- `POST` `/api/policies/generate`
- `POST` `/api/policies/import`
- `GET` `/api/policies/proof`
- `POST` `/api/policies/simulate`
- `GET` `/api/policies/templates`
- `POST` `/api/policies/test`

### `prompts`

- `GET` `/api/prompts/agent-connect/raw`
- `POST` `/api/prompts/render`
- `GET` `/api/prompts/runs`
- `GET` `/api/prompts/sdk-coverage/raw`
- `GET` `/api/prompts/server-setup/raw`
- `GET` `/api/prompts/stats`
- `GET, POST` `/api/prompts/templates`
- `DELETE, GET, PATCH` `/api/prompts/templates/[templateId]`
- `GET, POST` `/api/prompts/templates/[templateId]/versions`
- `GET, POST` `/api/prompts/templates/[templateId]/versions/[versionId]`

### `scoring`

- `POST` `/api/scoring/calibrate`
- `GET, POST` `/api/scoring/profiles`
- `DELETE, GET, PATCH` `/api/scoring/profiles/[profileId]`
- `POST` `/api/scoring/profiles/[profileId]/dimensions`
- `DELETE, PATCH` `/api/scoring/profiles/[profileId]/dimensions/[dimensionId]`
- `GET, POST` `/api/scoring/risk-templates`
- `DELETE, PATCH` `/api/scoring/risk-templates/[templateId]`
- `GET, POST` `/api/scoring/score`

### `security`

- `GET, POST` `/api/security/prompt-injection`
- `POST` `/api/security/scan`
- `GET` `/api/security/status`

### `sessions`

- `GET, POST` `/api/sessions`
- `GET, PATCH` `/api/sessions/[sessionId]`
- `GET` `/api/sessions/[sessionId]/events`

### `settings`

- `DELETE, GET, POST` `/api/settings`
- `GET` `/api/settings/llm-status`
- `POST` `/api/settings/test`

### `setup`

- `POST` `/api/setup/live-proof`
- `POST` `/api/setup/migrate`
- `POST` `/api/setup/ping`
- `GET` `/api/setup/proof`
- `GET` `/api/setup/status`

### `signals`

- `GET` `/api/signals`

### `stream`

- `GET` `/api/stream`

### `swarm`

- `GET` `/api/swarm/graph`
- `GET` `/api/swarm/link`

### `team`

- `GET` `/api/team`
- `DELETE, PATCH` `/api/team/[userId]`
- `DELETE, GET, POST` `/api/team/invite`

### `telegram`

- `POST` `/api/telegram/webhook`

### `usage`

- `GET` `/api/usage`
- `GET` `/api/usage/costs`

### `webhooks`

- `DELETE, GET, POST` `/api/webhooks`
- `GET` `/api/webhooks/[webhookId]/deliveries`
- `POST` `/api/webhooks/[webhookId]/test`
- `POST` `/api/webhooks/stripe`

### `workflows`

- `POST` `/api/workflows/draft`
- `GET, POST` `/api/workflows/templates`
- `DELETE, GET, PATCH` `/api/workflows/templates/[templateId]`
- `POST` `/api/workflows/templates/[templateId]/duplicate`
- `POST` `/api/workflows/templates/[templateId]/execute`
- `POST` `/api/workflows/templates/[templateId]/launch`
- `GET` `/api/workflows/templates/[templateId]/runs`
- `GET` `/api/workflows/templates/[templateId]/runs/[runActionId]`
- `POST` `/api/workflows/templates/[templateId]/runs/[runActionId]/cancel`
- `POST` `/api/workflows/templates/[templateId]/runs/[runActionId]/resume`

## Required Environment Variables

These must be set — DashClaw will fail to start without them.

- **`DASHCLAW_API_KEY`** - referenced in 66 file(s)
- **`DATABASE_URL`** - referenced in 77 file(s)
- **`ENCRYPTION_KEY`** - referenced in 8 file(s)
- **`NEXTAUTH_SECRET`** - referenced in 6 file(s)

## Optional Environment Variables

These have fallbacks or only activate specific features.

- `AGENT_ONLINE_WINDOW_MS` *(undocumented)*
- `AGENT_PRIVATE_KEY` *(undocumented)*
- `AGENT_PRIVATE_KEY_JWK` *(undocumented)*
- `ALERT_FROM_EMAIL` *(undocumented)*
- `ALLOWED_ORIGIN` *(undocumented)*
- `ANTHROPIC_API_KEY` *(undocumented)*
- `API_SECRET` *(undocumented)*
- `BASE_URL` *(undocumented)*
- `CI` *(undocumented)*
- `CONVERGENCE_BENCH_CONCURRENCY` *(undocumented)*
- `CONVERGENCE_BENCH_ITERATIONS` *(undocumented)*
- `CONVERGENCE_REPLAY_CONNECT_TIMEOUT_MS` *(undocumented)*
- `CONVERGENCE_RETRY_429_MAX` *(undocumented)*
- `CONVERGENCE_RETRY_429_WAIT_MS` *(undocumented)*
- `CONVERGENCE_SSE_SEND_COUNT` *(undocumented)*
- `CONVERGENCE_VERBOSE` *(undocumented)*
- `CRON_SECRET` *(undocumented)*
- `DASHCLAW_AGENT_ID` *(undocumented)*
- `DASHCLAW_ALERTS_TELEGRAM` *(undocumented)*
- `DASHCLAW_API_KEY_ORG` *(undocumented)*
- `DASHCLAW_BASE_URL` *(undocumented)*
- `DASHCLAW_CLOSED_ENROLLMENT` *(undocumented)*
- `DASHCLAW_DB_DRIVER` *(undocumented)*
- `DASHCLAW_DB_POOL_MAX` *(undocumented)*
- `DASHCLAW_DISABLE_RATE_LIMIT` *(undocumented)*
- `DASHCLAW_GUARD_FALLBACK` *(undocumented)*
- `DASHCLAW_LOCAL_ADMIN_PASSWORD` *(undocumented)*
- `DASHCLAW_MODE` *(undocumented)*
- `DASHCLAW_RATE_LIMIT_MAX` *(undocumented)*
- `DASHCLAW_RATE_LIMIT_WINDOW_MS` *(undocumented)*
- `DASHCLAW_URL` *(undocumented)*
- `DISABLE_PROMPT_INJECTION_SCAN` *(undocumented)*
- `ENFORCE_AGENT_SIGNATURES` *(undocumented)*
- `GITHUB_CLIENT_ID` *(undocumented)*
- `GITHUB_CLIENT_SECRET` *(undocumented)*
- `GITHUB_ID` *(undocumented)*
- `GITHUB_REPO_NAME` *(undocumented)*
- `GITHUB_REPO_OWNER` *(undocumented)*
- `GITHUB_SECRET` *(undocumented)*
- `GITHUB_TOKEN` *(undocumented)*
- `GOOGLE_AI_API_KEY` *(undocumented)*
- `GOOGLE_CLIENT_ID` *(undocumented)*
- `GOOGLE_CLIENT_SECRET` *(undocumented)*
- `GOOGLE_ID` *(undocumented)*
- `GOOGLE_SECRET` *(undocumented)*
- `GUARD_LLM_BASE_URL` *(undocumented)*
- `GUARD_LLM_KEY` *(undocumented)*
- `GUARD_LLM_MODEL` *(undocumented)*
- `GUARD_WEBHOOK_SECRET` *(undocumented)*
- `MEMORY_DIR` *(undocumented)*
- `MOONSHOT_API_KEY` *(undocumented)*
- `NEXTAUTH_URL`
- `NEXT_PUBLIC_APP_URL` *(undocumented)*
- `NEXT_PUBLIC_DASHCLAW_MODE` *(undocumented)*
- `NEXT_PUBLIC_DASHCLAW_VERSION` *(undocumented)*
- `NEXT_PUBLIC_ENABLE_VERCEL_ANALYTICS` *(undocumented)*
- `NODE_ENV` *(undocumented)*
- `OIDC_AUTHORIZATION_URL` *(undocumented)*
- `OIDC_CLIENT_ID` *(undocumented)*
- `OIDC_CLIENT_SECRET` *(undocumented)*
- `OIDC_DISPLAY_NAME` *(undocumented)*
- `OIDC_ISSUER_URL` *(undocumented)*
- `OIDC_TOKEN_URL` *(undocumented)*
- `OIDC_USERINFO_URL` *(undocumented)*
- `OPENAI_API_KEY` *(undocumented)*
- `ORG_ID` *(undocumented)*
- `PORT` *(undocumented)*
- `PW_BASE_URL` *(undocumented)*
- `PW_SMOKE_PORT` *(undocumented)*
- `PYTHON` *(undocumented)*
- `PYTHONPATH` *(undocumented)*
- `REALTIME_BACKEND` *(undocumented)*
- `REALTIME_ENFORCE_REDIS` *(undocumented)*
- `REALTIME_MAX_LISTENERS` *(undocumented)*
- `REALTIME_MEMORY_MAX_LISTENERS` *(undocumented)*
- `REALTIME_REDIS_URL` *(undocumented)*
- `REALTIME_REPLAY_MAX_EVENTS` *(undocumented)*
- `REALTIME_REPLAY_WINDOW_SECONDS` *(undocumented)*
- `REDIS_URL` *(undocumented)*
- `RESEARCH_API_KEY` *(undocumented)*
- `RESEARCH_API_URL` *(undocumented)*
- `RESEND_API_KEY` *(undocumented)*
- `SERVICE_NAME` *(undocumented)*
- `STARTUP_SMOKE_BASE_URL` *(undocumented)*
- `STARTUP_SMOKE_INTERVAL_MS` *(undocumented)*
- `STARTUP_SMOKE_TIMEOUT_MS` *(undocumented)*
- `STRIPE_PRICE_BUSINESS` *(undocumented)*
- `STRIPE_PRICE_PRO` *(undocumented)*
- `STRIPE_SECRET_KEY` *(undocumented)*
- `STRIPE_WEBHOOK_SECRET` *(undocumented)*
- `TARGET_ENV` *(undocumented)*
- `TELEGRAM_ADMIN_CHAT_ID` *(undocumented)*
- `TELEGRAM_APPROVER_ORG_ID` *(undocumented)*
- `TELEGRAM_BOT_TOKEN` *(undocumented)*
- `TELEGRAM_WEBHOOK_SECRET` *(undocumented)*
- `TRUST_PROXY` *(undocumented)*
- `UPSTASH_REDIS_REST_TOKEN` *(undocumented)*
- `UPSTASH_REDIS_REST_URL` *(undocumented)*
- `VERCEL` *(undocumented)*
- `VERCEL_URL` *(undocumented)*
- `WEBHOOK_ALLOWED_DOMAINS` *(undocumented)*

## Database Tables

All 73 tables defined in `schema/schema.js` (Drizzle ORM):

- `action_embeddings`
- `action_records`
- `activity_logs`
- `agent_connections`
- `agent_identities`
- `agent_messages`
- `agent_pairings`
- `agent_presence`
- `agent_schedules`
- `agent_sessions`
- `api_keys`
- `assumptions`
- `calendar_events`
- `compliance_snapshots`
- `contacts`
- `content`
- `context_entries`
- `context_points`
- `daily_totals`
- `decisions`
- `drift_alerts`
- `drift_baselines`
- `drift_snapshots`
- `entities`
- `eval_runs`
- `eval_scores`
- `executions`
- `feedback`
- `goals`
- `guard_decisions`
- `guard_policies`
- `guardrails_test_runs`
- `health_snapshots`
- `ideas`
- `interactions`
- `learning_curves`
- `learning_episodes`
- `learning_recommendation_events`
- `learning_recommendations`
- `learning_velocity`
- `message_threads`
- `milestones`
- `notification_preferences`
- `open_loops`
- `organizations`
- `profile_scores`
- `prompt_runs`
- `prompt_templates`
- `prompt_versions`
- `risk_templates`
- `routing_agent_metrics`
- `routing_agents`
- `routing_decisions`
- `routing_tasks`
- `scheduled_jobs`
- `scoring_dimensions`
- `scoring_profiles`
- `session_events`
- `shared_docs`
- `snippets`
- `token_budgets`
- `token_snapshots`
- `topics`
- `usage_meters`
- `user_approaches`
- `user_moods`
- `user_observations`
- `user_preferences`
- `users`
- `waitlist`
- `webhook_deliveries`
- `webhooks`
- `workflows`

## Detecting Drift

To check whether this snapshot matches the current codebase:

```bash
python -m livingcode diff
```

If the diff shows changes, this skill is stale — regenerate it.
