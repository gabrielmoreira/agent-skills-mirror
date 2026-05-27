---
name: iris-development
description: Iris is Redis's umbrella for AI-focused products. Use this skill when integrating with the Iris Redis Agent Memory (RAM) data plane on Redis Cloud — recording session events for an AI agent, creating or searching long-term memories, configuring a memory store, or tuning background memory promotion. Code examples use the official `redis-agent-memory` (Python) and `@redis-iris/agent-memory` (TypeScript) SDKs.
license: MIT
metadata:
  author: redis
  version: "1.0.0"
---

# Iris: Redis Agent Memory

**Iris** is the umbrella brand for Redis's AI-focused products. This skill currently covers one product in that family: **Redis Agent Memory (RAM)** — the persistent memory layer for AI agents, delivered as a managed service on Redis Cloud. Additional Iris products will be added as separate sections when they ship.

Redis Agent Memory exposes a REST/JSON data-plane API with two memory tiers:

- **Session memory** — append-only conversation history per session (working memory).
- **Long-term memory** — semantically searchable records extracted from sessions (or created directly).

A background **promotion** worker — managed by Redis Cloud — extracts durable facts from session events and writes them into long-term memory.

## Official SDKs

All code samples use the official SDKs:


| Language   | Package                    | Class         | Install                            |
| ---------- | -------------------------- | ------------- | ---------------------------------- |
| Python     | `redis-agent-memory`       | `AgentMemory` | `pip install redis-agent-memory`   |
| TypeScript | `@redis-iris/agent-memory` | `AgentMemory` | `npm add @redis-iris/agent-memory` |


Both SDKs read the bearer token from `AGENT_MEMORY_API_KEY` and the default store ID from `AGENT_MEMORY_STORE_ID`. The production data-plane URL is `https://gcp-us-east4.memory.redis.io`; the exact URL for your service is also shown in the Cloud console after provisioning.

## When to Apply

Reference these guidelines when:

- Creating a memory service on Redis Cloud ([https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory))
- Wiring an agent to call `AgentMemory.add_session_event(...)` / `addSessionEvent(...)`
- Searching long-term memory with `search_long_term_memory(...)` / `searchLongTermMemory(...)`
- Choosing between session events and direct long-term memory writes

## Rule Categories by Priority


| Priority | Category                | Impact | Prefix       |
| -------- | ----------------------- | ------ | ------------ |
| 1        | Setup & Cloud Service   | HIGH   | `setup-`     |
| 2        | Session Memory / Events | HIGH   | `session-`   |
| 3        | Long-Term Memory        | HIGH   | `ltm-`       |
| 4        | Memory Promotion        | MEDIUM | `promotion-` |


## Quick Reference

### 1. Setup & Cloud Service (HIGH)

- `setup-cloud-service` - Create a Memory service on Redis Cloud
- `setup-auth-token` - Authenticate the SDK with a store API key

### 2. Session Memory / Events (HIGH)

- `session-when-to-use` - Choose session events vs direct long-term memory
- `session-add-event` - Append a session event correctly
- `session-retrieval` - Retrieve session memory and individual events

### 3. Long-Term Memory (HIGH)

- `ltm-bulk-create` - Create long-term memories in bulk with idempotent IDs
- `ltm-search` - Search long-term memory semantically with filters
- `ltm-organize` - Organize records with namespace, ownerId, topics, and memoryType

### 4. Memory Promotion (MEDIUM)

- `promotion-overview` - How background promotion works

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/setup-cloud-service.md
rules/session-add-event.md
rules/promotion-overview.md
```

Each rule file contains:

- Brief explanation of why it matters
- Correct example(s) with Python and TypeScript SDK code
- Either an "Incorrect" example or "When to use / When NOT needed" guidance
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`