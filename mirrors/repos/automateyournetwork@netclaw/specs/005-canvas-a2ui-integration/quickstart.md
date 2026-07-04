# Quickstart: Canvas / A2UI Network Visualization

**Feature**: 005-canvas-a2ui-integration
**Date**: 2026-03-26

## Prerequisites

1. **OpenClaw** running with Canvas/A2UI support enabled
2. **At least one data source** configured and operational:
   - pyATS MCP server (for topology, health, config data)
   - Grafana MCP server (for dashboards, alerts, metrics)
   - Prometheus MCP server (for direct PromQL queries, alerts)
   - ServiceNow MCP server (for change management timelines)
3. **Existing environment variables** for data source MCP servers already set in `.env`

## No New Environment Variables Required

The Canvas visualization skill uses existing MCP server connections. No new credentials or environment variables are needed beyond what is already configured for the underlying MCP servers.

## Usage

Once the skill is installed, request visualizations via natural language in the OpenClaw chat:

### Topology Maps
```
show me the network topology
show topology for Site-A
show spine topology
```

### Health Dashboards
```
show health dashboard for R1
show site dashboard for Site-A
```

### Alerts
```
show current alerts
show critical alerts only
show syslog alerts for R1
```

### Change Management
```
show change request CR-12345 status
show all active change requests
```

### Configuration Diffs
```
show config diff for R1
show routing changes for R1
show ACL diff for R1
```

### Path Traces
```
trace path from 10.0.1.1 to 10.0.2.1
```

### Health Scorecards
```
show health scorecard for Site-A
show device health for R1
```

## What to Expect

- Visualizations render **inline** in the OpenClaw chat — no separate browser tabs
- If a data source is unavailable, you get a **partial visualization** with clear "unavailable" indicators
- Large topologies (200+ devices) are **automatically clustered** by site
- All visualization requests are **GAIT-logged** for audit compliance
- The existing Three.js HUD at `ui/netclaw-visual/` continues to work independently

## Verification

After installation, verify the skill is working:

1. Ensure pyATS MCP server has CDP/LLDP discovery data loaded
2. Ask: "show me the network topology"
3. Confirm an inline topology map appears with device nodes and health coloring
4. Check GAIT log for the visualization event entry
