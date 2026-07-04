# Quickstart: Zscaler MCP Server Integration

**Feature**: 020-zscaler-mcp-server | **Date**: 2026-04-04

## Prerequisites

1. Zscaler account with API access
2. OneAPI OAuth credentials
3. NetClaw OpenClaw gateway running

## Setup (10 minutes)

### Step 1: Install Zscaler MCP Server

```bash
# Using Go
go install github.com/zscaler/zscaler-mcp-server@latest

# Or download binary from releases
curl -LO https://github.com/zscaler/zscaler-mcp-server/releases/latest/download/zscaler-mcp-server_linux_amd64.tar.gz
tar xzf zscaler-mcp-server_linux_amd64.tar.gz
sudo mv zscaler-mcp-server /usr/local/bin/
```

### Step 2: Create OneAPI Credentials

1. Log in to Zscaler Admin Portal
2. Navigate to **Administration** → **API Keys**
3. Create new OAuth client with required scopes
4. Note the Client ID, Client Secret, and Customer ID

### Step 3: Configure Environment

Add to your `.env` file:

```bash
# Zscaler MCP Server - OneAPI Authentication
ZSCALER_CLIENT_ID=your_client_id_here
ZSCALER_CLIENT_SECRET=your_client_secret_here
ZSCALER_CUSTOMER_ID=your_customer_id_here
ZSCALER_VANITY_DOMAIN=yourcompany

# Services to enable (all 9 services)
ZSCALER_MCP_SERVICES=zia,zpa,zdx,zms,ztw,zinsights,zidentity,easm,zcc

# Optional: Enable write operations (disabled by default)
# ZSCALER_MCP_WRITE_ENABLED=true
```

### Step 4: Register MCP Server

Add to `config/openclaw.json`:

```json
{
  "mcpServers": {
    "zscaler-mcp": {
      "command": "zscaler-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "ZSCALER_CLIENT_ID": "${ZSCALER_CLIENT_ID}",
        "ZSCALER_CLIENT_SECRET": "${ZSCALER_CLIENT_SECRET}",
        "ZSCALER_CUSTOMER_ID": "${ZSCALER_CUSTOMER_ID}",
        "ZSCALER_VANITY_DOMAIN": "${ZSCALER_VANITY_DOMAIN}",
        "ZSCALER_MCP_SERVICES": "${ZSCALER_MCP_SERVICES}"
      }
    }
  }
}
```

### Step 5: Restart OpenClaw Gateway

```bash
# Restart to load new MCP server
openclaw restart
```

## Verification

### Test 1: List ZPA Application Segments

```
List all ZPA application segments
```

**Expected**: Array of application segments with names, domains, and status.

### Test 2: Show ZIA Firewall Rules

```
Show all ZIA firewall rules
```

**Expected**: List of firewall rules with actions, sources, and destinations.

### Test 3: ZDX Experience Scores

```
Show ZDX application scores for the last 24 hours
```

**Expected**: Applications with ZDX scores and affected user counts.

### Test 4: List Users

```
List all Zscaler users
```

**Expected**: Array of users with email, department, and group memberships.

## Skills Available

| Skill | Invocation | Description |
|-------|------------|-------------|
| `/zscaler-zpa` | Private Access | Application segments, policies, connectors |
| `/zscaler-zia` | Internet Access | Firewall rules, URL filtering |
| `/zscaler-zdx` | Digital Experience | User experience monitoring |
| `/zscaler-identity` | Identity | Users, groups, IdP configuration |
| `/zscaler-insights` | Analytics | Threat intelligence, security events |

## Common Queries

### ZPA Operations

```
# List application segments
List all ZPA application segments

# Get segment details
Show details for the SAP application segment

# List access policies
Show all ZPA access policies

# Find connectors
List all ZPA connectors and their status
```

### ZIA Operations

```
# List firewall rules
Show all ZIA firewall rules in order

# Find URL rules
List URL filtering rules for the Finance department

# Check DLP policies
Show DLP dictionaries and their rules

# Location status
List all ZIA locations and their status
```

### ZDX Operations

```
# Application scores
Show ZDX scores for all applications

# User experience
Show ZDX experience for user john@example.com

# Degraded applications
List applications with ZDX score below 70

# Recent events
Show ZDX events from the last hour
```

### Analytics Operations

```
# Threat intelligence
Show threat intelligence summary for today

# Security events
List security events in the last 24 hours

# Blocked threats
Show blocked threats by category

# Traffic analysis
Show traffic analytics by application
```

## Security Notes

- Write operations disabled by default
- Enable with `ZSCALER_MCP_WRITE_ENABLED=true`
- Delete operations require confirmation token
- ServiceNow CR required for production changes
- Use minimum-privilege API credentials

## Troubleshooting

### "Unauthorized" Error

- Verify OAuth credentials are correct
- Check client has required scopes
- Ensure customer ID matches

### "Service Unavailable" Error

- Verify Zscaler cloud is reachable
- Check vanity domain is correct
- Ensure services are enabled in `ZSCALER_MCP_SERVICES`

### "Write Tools Disabled" Error

- Set `ZSCALER_MCP_WRITE_ENABLED=true` to enable
- Optionally use `ZSCALER_MCP_WRITE_TOOLS` to allowlist specific tools
- Ensure ServiceNow CR approval for production

### Large Response Handling

- Some queries return many results
- Use filters to narrow results
- Consider pagination for large datasets
