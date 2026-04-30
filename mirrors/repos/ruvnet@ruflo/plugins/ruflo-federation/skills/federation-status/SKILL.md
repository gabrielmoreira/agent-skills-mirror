---
name: federation-status
description: Show federation health — peers, sessions, trust levels, and message metrics
allowed-tools: Bash(npx *) mcp__claude-flow__memory_search Read
argument-hint: ""
---
Show the current state of the federation.

Steps:
1. `npx @claude-flow/cli@latest federation status` -- overall health
2. `npx @claude-flow/cli@latest federation peers` -- list peers with trust levels and scores
3. Summarize: active sessions, messages exchanged, PII redactions, threat detections

Search memory for federation history:
`mcp__claude-flow__memory_search({ query: "federation peer trust", namespace: "federation" })`
