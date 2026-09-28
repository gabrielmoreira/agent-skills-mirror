---
name: splunk-indexes
description: "Discover and inspect Splunk indexes and configuration."
version: 1.0.0
license: Apache-2.0
author: netclaw
tags: []
---

# Splunk Indexes Skill

Discover and inspect Splunk indexes and configuration.

## Tools

| Tool | Description |
|------|-------------|
| `get_indexes` | List all available indexes |
| `get_config` | Get Splunk server configuration |

## Example Queries

```
List all Splunk indexes

What indexes contain network data?

Show Splunk server configuration
```

## Prerequisites

- `SPLUNK_HOST` Splunk server hostname
- `SPLUNK_PORT` Management port (default: 8089)
- `SPLUNK_USERNAME` Service account username
- `SPLUNK_PASSWORD` Service account password

## Server

This skill uses the `splunk-mcp` server via npx.

## Failure Behavior

- On a tool error (timeout, unreachable host, malformed response), report the failure and its error message directly to the user rather than fabricating or guessing at results.
- For a confirmed read-only call, check connectivity and retry once if appropriate. For any call that changes state or sends a message, a timeout does not prove the action failed: inspect current state or delivery status before retrying, preserve the required approval/change gates, and do not repeat an action whose outcome is unknown.
