# Quickstart: Datadog MCP Server Integration

**Feature**: 016-datadog-mcp-server | **Date**: 2026-04-04

## Prerequisites

1. Datadog account with API access
2. NetClaw OpenClaw gateway running
3. Network connectivity to Datadog

## Setup (5 minutes)

### Step 1: Generate Datadog API Keys

1. Log in to Datadog
2. Navigate to **Organization Settings** → **API Keys** → Create New
3. Copy the API key
4. Navigate to **Organization Settings** → **Application Keys** → Create New
5. Copy the Application key

### Step 2: Configure Environment

Add to your `.env` file:

```bash
# Datadog MCP Server
DD_API_KEY=your_api_key_here
DD_APP_KEY=your_application_key_here

# Optional: EU datacenter
# DD_SITE=datadoghq.eu
```

### Step 3: Register MCP Server

Add to `config/openclaw.json`:

```json
{
  "mcpServers": {
    "datadog-mcp": {
      "transport": "remote",
      "url": "mcp://datadog.com/mcp",
      "env": {
        "DD_API_KEY": "${DD_API_KEY}",
        "DD_APP_KEY": "${DD_APP_KEY}",
        "DD_SITE": "${DD_SITE}"
      },
      "toolsets": ["apm", "error_tracking", "feature_flags", "dbm", "security", "llm_observability"]
    }
  }
}
```

### Step 4: Restart OpenClaw Gateway

```bash
# Restart to load new MCP server
openclaw restart
```

## Verification

### Test 1: Log Search

```
Search Datadog logs for BGP errors in the last hour
```

**Expected**: List of log entries with timestamps, messages, and relevant attributes.

### Test 2: Metric Query

```
Show network interface metrics from Datadog for the last 4 hours
```

**Expected**: Time series data with metric values and tags.

### Test 3: Incident List

```
List all active Datadog incidents
```

**Expected**: Array of incidents with title, severity, status, and impact.

### Test 4: APM Trace Search

```
Search APM traces for the network-api service with latency over 500ms
```

**Expected**: Traces with spans, duration, and error information.

## Skills Available

| Skill | Invocation | Description |
|-------|------------|-------------|
| `/datadog-logs` | Log investigation | Search and analyze logs |
| `/datadog-metrics` | Metric analysis | Query metrics and dashboards |
| `/datadog-incidents` | Incident management | View and manage incidents |
| `/datadog-apm` | APM analysis | Trace investigation |

## Common Queries

### Log Operations

```
# Search for errors
Search Datadog logs for status:error in the last hour

# Filter by service
Search logs for service:network-core level:error

# Search with tags
Search logs for @device_type:router in production environment
```

### Metric Operations

```
# Query specific metric
Show avg:system.cpu.user by host for network devices

# List available metrics
List all network-related metrics in Datadog

# Get metric details
Show metadata for interface.traffic.in metric
```

### Incident Operations

```
# List active incidents
Show all active SEV-1 and SEV-2 incidents

# Get incident details
Show details for incident INC-12345

# View incident timeline
Show timeline for the current network outage incident
```

### APM Operations

```
# Search traces
Search traces for network-api service in the last hour

# Find slow traces
Find traces with duration over 1 second

# Service overview
Show performance summary for the network-gateway service
```

## Troubleshooting

### "Unauthorized" Error

- Verify `DD_API_KEY` and `DD_APP_KEY` are set correctly
- Ensure Application Key has required scopes
- Check site setting matches your Datadog region

### "Rate Limited" Error

- Datadog has per-minute rate limits
- Wait and retry
- Consider using smaller time ranges

### "No Data" Results

- Verify data exists in Datadog for the queried time range
- Check query syntax matches Datadog format
- Ensure log indexes are accessible

## Security Notes

- API keys are never logged or displayed
- Use service account keys for production
- Application keys can be scoped to specific permissions
- Consider creating dedicated keys for NetClaw
