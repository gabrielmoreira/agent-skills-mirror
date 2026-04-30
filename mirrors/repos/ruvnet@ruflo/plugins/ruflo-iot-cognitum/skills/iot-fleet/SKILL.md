---
name: iot-fleet
description: Create and manage Cognitum Seed device fleets with firmware policies
allowed-tools: Bash(npx *) mcp__claude-flow__memory_store mcp__claude-flow__memory_search Read
argument-hint: "<create|list|add|remove|delete> [options]"
---
Manage device fleets. Parse subcommand from arguments.

**create**: `npx @claude-flow/cli@latest iot fleet create --name NAME`
**list**: `npx @claude-flow/cli@latest iot fleet list`
**add**: `npx @claude-flow/cli@latest iot fleet add FLEET_ID DEVICE_ID`
**remove**: `npx @claude-flow/cli@latest iot fleet remove FLEET_ID DEVICE_ID`
**delete**: `npx @claude-flow/cli@latest iot fleet delete FLEET_ID`
