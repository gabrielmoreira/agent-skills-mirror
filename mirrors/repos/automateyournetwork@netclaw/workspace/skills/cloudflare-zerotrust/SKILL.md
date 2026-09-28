---
name: cloudflare-zerotrust
description: "Inspect Cloudflare Zero Trust access applications, policies, tunnels, and CASB findings."
version: 1.0.0
license: Apache-2.0
author: netclaw
tags: []
---

# Cloudflare Zero Trust Skill

Inspect Cloudflare Zero Trust access applications, policies, tunnels, and CASB findings.

## Tools

| Tool | Description |
|------|-------------|
| `list_access_applications` | List Zero Trust Access applications |
| `get_access_application` | Get details for an access application |
| `list_access_policies` | List access policies for an application |
| `get_access_policy` | Get details for an access policy |
| `list_tunnels` | List Cloudflare Tunnels |
| `get_tunnel` | Get tunnel details and connection status |
| `list_casb_findings` | List CASB security findings |
| `get_casb_finding` | Get details for a CASB finding |

## Example Queries

```
List all Cloudflare Access applications

Show access policies for the internal-dashboard app

What Cloudflare Tunnels are configured and their status?

List CASB security findings for SaaS misconfigurations
```

## Prerequisites

- `CLOUDFLARE_API_TOKEN` with Access:Read, Account:Read scopes
- `CLOUDFLARE_ACCOUNT_ID` from dashboard

## Servers

This skill uses:
- `cloudflare-casb` remote MCP server at `casb.mcp.cloudflare.com`
- `cloudflare-audit-logs` for access audit trails

## Failure Behavior

- On a tool error (timeout, unreachable host, malformed response), report the failure and its error message directly to the user rather than fabricating or guessing at results.
- For a confirmed read-only call, check connectivity and retry once if appropriate. For any call that changes state or sends a message, a timeout does not prove the action failed: inspect current state or delivery status before retrying, preserve the required approval/change gates, and do not repeat an action whose outcome is unknown.
