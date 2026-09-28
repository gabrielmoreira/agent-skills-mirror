---
name: terraform-registry
description: "Discover providers and modules from the Terraform Registry."
version: 1.0.0
license: Apache-2.0
author: netclaw
tags: []
---

# Terraform Registry Skill

Discover providers and modules from the Terraform Registry.

## Tools

| Tool | Description |
|------|-------------|
| `search_providers` | Search for providers in the Registry |
| `get_provider_details` | Get provider documentation and versions |
| `search_modules` | Search for modules in the Registry |
| `get_module_details` | Get module documentation and inputs/outputs |
| `list_provider_versions` | List available versions for a provider |
| `list_module_versions` | List available versions for a module |

## Example Queries

```
Search for AWS networking providers

What modules are available for Cisco ACI?

Show details for the hashicorp/aws provider

Find VPC modules in the registry
```

## Prerequisites

- No authentication required for public Registry
- `TFE_TOKEN` required for private modules

## Server

This skill uses the `terraform-mcp` server with Registry toolset enabled.

## Failure Behavior

- On a tool error (timeout, unreachable host, malformed response), report the failure and its error message directly to the user rather than fabricating or guessing at results.
- For a confirmed read-only call, check connectivity and retry once if appropriate. For any call that changes state or sends a message, a timeout does not prove the action failed: inspect current state or delivery status before retrying, preserve the required approval/change gates, and do not repeat an action whose outcome is unknown.
