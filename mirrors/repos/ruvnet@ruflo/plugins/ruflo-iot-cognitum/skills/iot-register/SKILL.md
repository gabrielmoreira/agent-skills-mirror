---
name: iot-register
description: Register a Cognitum Seed device by endpoint and establish agent bridge
allowed-tools: Bash(npx *) mcp__claude-flow__memory_store Read
argument-hint: "<endpoint> [--token PAIRING_TOKEN]"
---
Register a Cognitum Seed device. Creates a SeedClient connection, fetches identity, and assigns initial trust level.

Steps:
1. `npx @claude-flow/cli@latest iot register ENDPOINT`
2. If pairing token provided: `npx @claude-flow/cli@latest iot pair DEVICE_ID`
3. Show device status: `npx @claude-flow/cli@latest iot status DEVICE_ID`

Store registration event:
`mcp__claude-flow__memory_store({ key: "iot-register-DEVICEID", value: "Registered at ENDPOINT", namespace: "iot-devices" })`
