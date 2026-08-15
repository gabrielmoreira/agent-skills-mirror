---
name: render-monitor
description: "Monitors Render services in real time: health, CPU/memory/latency metrics, logs, Postgres slow queries, and Key-Value status via Render MCP or CLI. Use when checking whether a Render deploy is healthy or investigating slow responses. Not for deploying or tearing down Render resources, GitHub Actions CI (github-actions-advanced), or Expo EAS update metrics (eas-update-insights)."
version: 1.0.1
license: MIT
compatibility: Requires Render MCP tools or CLI
metadata:
  author: Render
  category: monitoring
---

# Monitor Render Services

Real-time monitoring of Render services including health checks, performance metrics, logs, database status, and resource usage. Supports both the Render MCP server (preferred, structured data) and the Render CLI (fallback for status and logs).

## When to Use

Activate this skill when users want to:

- Check if one or more Render services are healthy
- View performance metrics (CPU, memory, latency, request count)
- Monitor or search service logs
- Verify a deployment is working or finished
- Investigate slow performance or elevated error rates
- Check PostgreSQL database health, connections, or slow queries
- Inspect Render Key-Value store status

Trigger keywords: *Render status, service health, metrics, logs, latency, CPU, memory, deployment check, database health, slow queries, p95, error rate.*

## Prerequisites

**MCP tools (preferred):** Verify availability by calling `list_services()`. This returns structured data and is the richest path for metrics and database queries.

**CLI (fallback):** Verify with `render --version`. Use the CLI when MCP tools are unavailable. Note: metrics and database queries require MCP; the CLI covers status and logs only.

**Authentication:**

- **MCP:** API key set in the MCP config or via the `RENDER_API_KEY` environment variable, depending on the tool.
- **CLI:** Verify with `render whoami -o json`.

**Workspace:** Confirm the active workspace before querying services.

- MCP: `get_selected_workspace()`
- CLI: `render workspace current -o json`

> **HARD RULE:** If `list_services()` fails because MCP is not configured, guide the user through MCP setup (below) before proceeding. Metrics and database queries are unavailable via CLI fallback.

## Procedure

### 1. Confirm MCP availability and workspace

```
list_services()
get_selected_workspace()
```

If MCP is unavailable, fall back to CLI:

```powershell
render services -o json
render workspace current -o json
```

### 2. MCP Setup (only if `list_services()` fails)

Ask which AI tool the user is on, then provide the matching steps. Always use their own API key—never hardcode.

#### Cursor

1. Get a Render API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Add to `~/.cursor/mcp.json` (replace `<YOUR_API_KEY>`):

```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_API_KEY>"
      }
    }
  }
}
```

3. Restart Cursor, then retry `list_services()`.

#### Codex

1. Get a Render API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Set in shell:

```bash
export RENDER_API_KEY="<YOUR_API_KEY>"
```

3. Add the MCP server:

```bash
codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY
```

4. Restart Codex, then retry `list_services()`.

#### Other Tools

Direct the user to the Render MCP docs for that tool's setup steps and install method.

#### Workspace Selection

After MCP is configured, have the user set the active Render workspace:

```
Set my Render workspace to [WORKSPACE_NAME]
```

### 3. Quick Health Check (5-step core path)

Run these five checks to assess service health. Replace `<service-id>` with the actual service ID from `list_services()`.

```
# 1. Check service status
list_services()

# 2. Check latest deploy
list_deploys(serviceId: "<service-id>", limit: 1)

# 3. Check for errors
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)

# 4. Check resource usage
get_metrics(resourceId: "<service-id>", metricTypes: ["cpu_usage", "memory_usage"])

# 5. Check latency
get_metrics(resourceId: "<service-id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.95)
```

### 4. Service Health

#### Status

```
list_services()
get_service(serviceId: "<id>")
```

#### Deployments

```
list_deploys(serviceId: "<service-id>", limit: 5)
```

| Status | Meaning |
|--------|---------|
| `live` | Deployment successful |
| `build_in_progress` | Building |
| `build_failed` | Build failed |
| `deactivated` | Replaced by newer deploy |

#### Errors

```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
list_logs(resource: ["<service-id>"], statusCode: ["500", "502", "503"], limit: 50)
```

### 5. Performance Metrics

> **Load `references/metrics-guide.md`** when the user needs detailed metric interpretation, advanced filtering (by path, quantile, time window), or metric-specific thresholds beyond the summary tables below.

#### CPU & Memory

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage", "cpu_limit", "memory_limit"]
)
```

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU | <70% | 70–85% | >85% |
| Memory | <80% | 80–90% | >90% |

#### HTTP Latency (p95)

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpLatencyQuantile: 0.95
)
```

| p95 Latency | Status |
|-------------|--------|
| <200ms | Excellent |
| 200–500ms | Good |
| 500ms–1s | Concerning |
| >1s | Problem |

#### Request Count

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count"]
)
```

#### Filter by Endpoint

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpPath: "/api/users"
)
```

### 6. Database Monitoring

#### PostgreSQL Status

```
list_postgres_instances()
get_postgres(postgresId: "<postgres-id>")
```

#### Connection Count

```
get_metrics(resourceId: "<postgres-id>", metricTypes: ["active_connections"])
```

#### Query Database

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)
```

#### Find Slow Queries

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
)
```

#### Key-Value Store

```
list_key_value()
get_key_value(keyValueId: "<kv-id>")
```

### 7. Log Monitoring

#### Recent Logs

```
list_logs(resource: ["<service-id>"], limit: 100)
```

#### Error Logs

```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
```

#### Search Logs

```
list_logs(resource: ["<service-id>"], text: ["timeout", "error"], limit: 50)
```

#### Filter by Time

```
list_logs(
  resource: ["<service-id>"],
  startTime: "2024-01-15T10:00:00Z",
  endTime: "2024-01-15T11:00:00Z"
)
```

#### Stream Logs (CLI)

```powershell
render logs -r <service-id> --tail -o text
```

### 8. CLI Fallback Quick Reference

Use these when MCP tools are unavailable. Metrics and database queries are not available via CLI.

```powershell
# Service status
render services -o json
render services instances <service-id>

# Deployments
render deploys list <service-id> -o json

# Logs
render logs -r <service-id> --tail -o text          # Stream logs
render logs -r <service-id> --level error -o json   # Error logs
render logs -r <service-id> --type deploy -o json   # Build logs

# Database
render psql <database-id>                           # Connect to PostgreSQL

# SSH for live debugging
render ssh <service-id>
```

## Pitfalls

- **MCP not configured:** If `list_services()` fails, do not attempt metrics or database queries via CLI—they are MCP-only. Walk the user through MCP setup first.
- **Wrong workspace:** Queries return services from the active workspace. Always confirm with `get_selected_workspace()` or `render workspace current -o json` before investigating "missing" services.
- **Metrics require MCP:** `get_metrics`, `query_render_postgres`, and `get_postgres` have no CLI equivalents. Do not invent CLI flags for them.
- **Deploy status confusion:** `deactivated` is normal—it means a newer deploy replaced the old one. Only `build_failed` indicates a problem.
- **Latency quantile defaults:** If `httpLatencyQuantile` is omitted, you may get average latency which hides tail spikes. Always specify `0.95` for p95.
- **Log time filters:** `startTime` and `endTime` must be ISO 8601 with `Z` suffix. Local time strings will fail silently or return empty results.
- **`pg_stat_statements` availability:** Slow-query detection requires the extension to be enabled on the PostgreSQL instance. If the query errors, inform the user.
- **Never delete resources:** This skill is read-only monitoring. Do not call any delete, scale-down, or teardown operations, even if a user asks during a debugging session—redirect to the deploy or debug skills.

## Verification

After running monitoring checks, confirm results with these checkable outputs:

```
# Verify MCP connectivity
list_services()
# Expected: returns a list of services with ids, names, and status fields

# Verify deploy is live
list_deploys(serviceId: "<service-id>", limit: 1)
# Expected: status == "live"

# Verify no recent errors
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)
# Expected: empty or negligible error count

# Verify healthy resource usage
get_metrics(resourceId: "<service-id>", metricTypes: ["cpu_usage", "memory_usage"])
# Expected: CPU <70%, Memory <80%

# Verify p95 latency
get_metrics(resourceId: "<service-id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.95)
# Expected: <500ms for "Good" status
```

### Healthy Service Indicators (summary)

| Indicator | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Deploy Status | `live` | `update_in_progress` | `build_failed` |
| Error Rate | <0.1% | 0.1–1% | >1% |
| p95 Latency | <500ms | 500ms–2s | >2s |
| CPU Usage | <70% | 70–90% | >90% |
| Memory Usage | <80% | 80–95% | >95% |

## References

- **Metrics guide:** `references/metrics-guide.md` — Load this file when the user needs detailed metric interpretation, advanced filtering by path/quantile/time window, or metric-specific thresholds beyond the summary tables in this skill.

## Related Skills

- **deploy:** Deploy new applications to Render
- **debug:** Diagnose and fix deployment failures
