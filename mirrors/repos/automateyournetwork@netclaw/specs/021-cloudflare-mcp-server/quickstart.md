# Quickstart: Cloudflare MCP Server Integration

**Feature**: 021-cloudflare-mcp-server | **Date**: 2026-04-04

## Prerequisites

1. Cloudflare account
2. API token with required permissions
3. NetClaw OpenClaw gateway running

## Setup (10 minutes)

### Step 1: Create Cloudflare API Token

1. Log in to Cloudflare Dashboard
2. Navigate to **My Profile** → **API Tokens**
3. Create a custom token with these permissions:
   - Zone: DNS: Read
   - Zone: Analytics: Read
   - Account: Access: Apps and Policies: Read
   - Account: Account Settings: Read
   - Account: Audit Logs: Read
4. Copy the token and your Account ID

### Step 2: Configure Environment

Add to your `.env` file:

```bash
# Cloudflare MCP Servers
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here

# Optional: Default zone for DNS operations
# CLOUDFLARE_ZONE_ID=your_zone_id_here
```

### Step 3: Register MCP Servers

Add to `config/openclaw.json`:

```json
{
  "mcpServers": {
    "cloudflare-dns-analytics": {
      "transport": "remote",
      "url": "dns-analytics.mcp.cloudflare.com",
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    },
    "cloudflare-observability": {
      "transport": "remote",
      "url": "observability.mcp.cloudflare.com",
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    },
    "cloudflare-audit-logs": {
      "transport": "remote",
      "url": "audit-logs.mcp.cloudflare.com",
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    },
    "cloudflare-casb": {
      "transport": "remote",
      "url": "casb.mcp.cloudflare.com",
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    },
    "cloudflare-radar": {
      "transport": "remote",
      "url": "radar.mcp.cloudflare.com",
      "env": {
        "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}",
        "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}"
      }
    }
  }
}
```

### Step 4: Restart OpenClaw Gateway

```bash
# Restart to load new MCP servers
openclaw restart
```

## Verification

### Test 1: List DNS Zones

```
List all my Cloudflare DNS zones
```

**Expected**: Array of zones with names, status, and nameservers.

### Test 2: DNS Analytics

```
Show DNS analytics for example.com for the last 24 hours
```

**Expected**: DNS query metrics and performance data.

### Test 3: Audit Logs

```
Show Cloudflare audit logs from today
```

**Expected**: List of account actions with timestamps and actors.

### Test 4: Traffic Insights

```
Show global Internet traffic insights from Cloudflare Radar
```

**Expected**: Traffic trends and regional distribution.

## Skills Available

| Skill | Invocation | Description |
|-------|------------|-------------|
| `/cloudflare-dns` | DNS management | Zones, records, DNS analytics |
| `/cloudflare-zerotrust` | Zero Trust | Access apps, policies, tunnels, CASB |
| `/cloudflare-analytics` | Analytics | Traffic, logs, Radar insights |
| `/cloudflare-workers` | Workers | Deployment, bindings, builds |
| `/cloudflare-security` | Security | Firewall, audit, threats |

## Common Queries

### DNS Operations

```
# List zones
List all my Cloudflare DNS zones

# Get zone details
Show details for the example.com zone

# DNS records
List all DNS records for example.com

# DNS performance
Show DNS query performance for example.com
```

### Zero Trust Operations

```
# List access apps
Show all Cloudflare Access applications

# Access policies
List access policies for the internal-app application

# Tunnels
Show all Cloudflare Tunnels and their status

# CASB findings
List CASB security findings
```

### Analytics Operations

```
# Zone analytics
Show traffic analytics for example.com today

# Search logs
Search Cloudflare logs for 403 errors in the last hour

# Radar insights
Show global Internet traffic trends from Radar

# URL scan
Scan https://suspicious-site.com for threats
```

### Security Operations

```
# Firewall events
Show firewall events for example.com today

# Audit logs
Show audit logs for the last 24 hours

# Threat score
Check threat score for IP 1.2.3.4

# Security events
List security events for example.com
```

## Security Notes

- Use minimum-privilege API tokens
- Zone-specific tokens recommended for DNS
- Account-wide read tokens for analytics
- Write operations require explicit confirmation
- All API calls logged in Cloudflare audit

## Troubleshooting

### "Unauthorized" Error

- Verify API token is correct
- Check token hasn't expired
- Ensure token has required permissions

### "Zone Not Found" Error

- Verify zone exists in account
- Check zone ID is correct
- Ensure token has zone permission

### "Rate Limited" Error

- Cloudflare has API rate limits
- Wait and retry
- Consider caching frequent queries

### Server Connection Failed

- Verify network connectivity to Cloudflare
- Check remote MCP URL is correct
- Ensure mcp-remote is configured properly
