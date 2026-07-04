# Quickstart: DevNet Content Search MCP Server

**Feature**: 026-devnet-content-search-mcp
**Date**: 2026-04-09

## Prerequisites

- NetClaw/OpenClaw gateway running
- Internet connectivity to https://devnet.cisco.com

No credentials, API keys, or local installation required.

## Configuration

### 1. Register MCP Server

Add to `~/.openclaw/config/openclaw.json` under `mcpServers`:

```json
"devnet-content-search": {
  "url": "https://devnet.cisco.com/v1/foundation-search-mcp/mcp"
}
```

### 2. Restart Gateway

```bash
openclaw gateway stop
openclaw gateway run
```

### 3. Verify Connection

Ask NetClaw:
```
Search for Meraki L3 firewall API documentation
```

Expected: List of firewall-related API endpoints with descriptions.

---

## Test Scenarios

### Scenario 1: Meraki API Search (US1)

**Test**: Search Meraki documentation for firewall rules

**Steps**:
1. Ask: "Find Meraki L3 firewall API endpoints"
2. Verify: Results include `updateNetworkApplianceFirewallL3FirewallRules` and similar operations
3. Verify: Each result has path, method, and description

**Expected Output**: 2+ API endpoints related to L3 firewall configuration

---

### Scenario 2: Catalyst Center API Search (US2)

**Test**: Search Catalyst Center documentation for device inventory

**Steps**:
1. Ask: "Show me Catalyst Center device inventory APIs"
2. Verify: Results include device listing and management endpoints
3. Verify: Implementation guides are included in results

**Expected Output**: Device management API endpoints with `/dna/intent/api/` paths

---

### Scenario 3: Meraki Operation ID Lookup (US3)

**Test**: Lookup specific operation by ID

**Steps**:
1. Ask: "Get details for Meraki operation createNetworkMerakiAuthUser"
2. Verify: Complete OpenAPI specification is returned
3. Verify: Parameters, request body schema, and responses are included

**Expected Output**: Full operation spec with path `/networks/{networkId}/merakiAuthUsers`

---

### Scenario 4: No Results Handling

**Test**: Search with nonsense query

**Steps**:
1. Ask: "Search Meraki for xyzzy123nonsense"
2. Verify: Clear "no results" or empty results message
3. Verify: No error thrown

**Expected Output**: Empty results or helpful message suggesting refined search

---

### Scenario 5: Invalid Operation ID

**Test**: Lookup non-existent operation

**Steps**:
1. Ask: "Get details for Meraki operation notARealOperation"
2. Verify: Clear error message indicating operation not found
3. Verify: No system crash

**Expected Output**: Error message like "Operation ID not found"

---

## Skill Invocation Examples

### devnet-meraki-search

```
# Natural language
Search Meraki API docs for VLAN management

# Specific queries
Find Meraki wireless SSID configuration APIs
Show me Meraki OAuth authentication documentation
```

### devnet-catalyst-search

```
# Natural language
Search Catalyst Center for policy automation APIs

# Specific queries
Find Catalyst Center device discovery endpoints
Show me DNA Center assurance and troubleshooting APIs
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "MCP server not found" | Server not registered | Add to openclaw.json and restart gateway |
| "Connection refused" | No internet / firewall | Check network connectivity to devnet.cisco.com |
| Empty results | Query too specific | Try broader search terms |
| Timeout | DevNet server slow | Retry; check devnet.cisco.com status |
