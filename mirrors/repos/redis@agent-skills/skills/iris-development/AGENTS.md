# Iris Development

**Version 1.0.0**  
Redis, Inc.  
May 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring Iris applications. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Iris is Redis's umbrella for AI-focused products. This guide covers one of them — Redis Agent Memory (RAM) on Redis Cloud: provisioning a service, authenticating with the official SDKs, appending session events, creating and searching long-term memories, and tuning background promotion. Code examples use the redis-agent-memory (Python) and @redis-iris/agent-memory (TypeScript) SDKs. Optimized for AI agents and LLMs.

---

## Table of Contents

1. [Setup & Cloud Service](#1-setup--cloud-service) — **HIGH**
   - 1.1 [Authenticate the SDK with a Store API Key](#11-authenticate-the-sdk-with-a-store-api-key)
   - 1.2 [Create a Memory Service on Redis Cloud](#12-create-a-memory-service-on-redis-cloud)
2. [Session Memory / Events](#2-session-memory-/-events) — **HIGH**
   - 2.1 [Append a Session Event Correctly](#21-append-a-session-event-correctly)
   - 2.2 [Choose Session Events vs Long-Term Memory](#22-choose-session-events-vs-long-term-memory)
   - 2.3 [Retrieve Session Memory and Individual Events](#23-retrieve-session-memory-and-individual-events)
3. [Long-Term Memory](#3-long-term-memory) — **HIGH**
   - 3.1 [Create Long-Term Memories in Bulk with Idempotent IDs](#31-create-long-term-memories-in-bulk-with-idempotent-ids)
   - 3.2 [Organize Long-Term Memory with namespace, ownerId, topics, and memoryType](#32-organize-long-term-memory-with-namespace-ownerid-topics-and-memorytype)
   - 3.3 [Search Long-Term Memory Semantically with Filters](#33-search-long-term-memory-semantically-with-filters)
4. [Memory Promotion](#4-memory-promotion) — **MEDIUM**
   - 4.1 [Understand Background Memory Promotion](#41-understand-background-memory-promotion)

---

## 1. Setup & Cloud Service

**Impact: HIGH**

Creating a service on Redis Cloud, authenticating with the official SDKs, and store provisioning.

### 1.1 Authenticate the SDK with a Store API Key

**Impact: HIGH (Wrong scheme causes 401s on every call; leaked keys expose the entire store)**

Every data-plane request carries `Authorization: Bearer <store-api-key>`. The SDKs add this header for you — just pass the key (and store ID) at client construction. Both SDKs follow the same convention:

| Field | Python | TypeScript | Environment variable |
|---|---|---|---|
| Server URL | `server_url` (1st positional) | `serverURL` | (set yourself, e.g. `AGENT_MEMORY_BASE_URL`) |
| API key | `api_key` | `apiKey` | `AGENT_MEMORY_API_KEY` |
| Store ID | `store_id` (global) | `storeId` (global) | `AGENT_MEMORY_STORE_ID` |

`store_id` / `storeId` is a *global parameter* — set it on the client once and every per-store operation uses it by default. You can still override it per call.

**Correct: Read the key from a secrets manager (or environment) and construct the client once per process.**

**Python:**

```python
import os
from redis_agent_memory import AgentMemory

# Construct once at startup; reuse across requests.
# The `with` block ensures the underlying httpx client is closed cleanly.
def make_client() -> AgentMemory:
    return AgentMemory(
        os.environ["AGENT_MEMORY_BASE_URL"],         # e.g. https://gcp-us-east4.memory.redis.io
        store_id=os.environ["AGENT_MEMORY_STORE_ID"],
        api_key=os.environ["AGENT_MEMORY_API_KEY"],
    )

with make_client() as agent_memory:
    agent_memory.health()
```

**TypeScript:**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

// Construct once at module scope; the SDK is safe to share across requests.
export const agentMemory = new AgentMemory({
  serverURL: process.env.AGENT_MEMORY_BASE_URL!,
  storeId:   process.env.AGENT_MEMORY_STORE_ID!,
  apiKey:    process.env.AGENT_MEMORY_API_KEY!,
});

await agentMemory.health();
```

**Incorrect: Hard-coding the key, building the client per request, or constructing the bearer header by hand.**

```typescript
// Bad: rebuilding the Authorization header manually defeats the SDK's typing,
// retry, and error-class machinery.
const res = await fetch(`${URL}/v1/stores/${SID}/session-memory/events`, {
  method:  "POST",
  headers: { Authorization: `Bearer ${KEY}` },
  body:    JSON.stringify(event),
});
```

**Rotation: Regenerate the key from the Cloud console. There is no short-lived-token flow — rotation is the only mitigation if a key leaks.**

**Per-operation override: Both SDKs accept a `store_id` / `storeId` argument on every call, which overrides the global. Use this when one process talks to multiple stores; do not use it to "scope" calls — global is fine for single-store apps.**

Reference: [https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory)

### 1.2 Create a Memory Service on Redis Cloud

**Impact: HIGH (Provisions a managed store, API key, and worker in minutes)**

Redis Cloud provisions the memory store, the backing Redis database, the background promotion worker, and the LLM/embedding provider credentials. Each store gets a unique `storeId` and a **store API key** used as a bearer token on every data-plane request.

**Correct: Provision through the Redis Cloud Agent Memory console.**

```bash
export AGENT_MEMORY_BASE_URL="https://gcp-us-east4.memory.redis.io"
export AGENT_MEMORY_STORE_ID="<your-store-id>"
export AGENT_MEMORY_API_KEY="<your-store-api-key>"
```

1. Sign in at [https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory).

2. Click **New service** and pick the correct settings for the user.

3. After provisioning, copy three values from the console:

   - **Server URL** — the production data-plane URL is `https://gcp-us-east4.memory.redis.io` (your exact URL is shown in the Cloud console)

   - **Store ID** — 32-character UUID without dashes

   - **Store API key** — Bearer token (treat like a secret)

4. Export them so the SDKs can read them from the environment:

5. Install the SDK and run a smoke test.

**Python** — `pip install redis-agent-memory`:**

```python
import os
from datetime import datetime, timezone
from redis_agent_memory import AgentMemory, models

with AgentMemory(
    os.environ["AGENT_MEMORY_BASE_URL"],
    store_id=os.environ["AGENT_MEMORY_STORE_ID"],
    api_key=os.environ["AGENT_MEMORY_API_KEY"],
) as agent_memory:
    # Health check
    print(agent_memory.health())

    # Sanity write
    res = agent_memory.add_session_event(
        actor_id="user-42",
        role=models.MessageRole.USER,
        content=[{"text": "hello"}],
        created_at=datetime.now(timezone.utc),   # tz-aware UTC datetime
    )
    print(res.event.event_id)
```

**TypeScript** — `npm add @redis-iris/agent-memory`:**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

const agentMemory = new AgentMemory({
  serverURL: process.env.AGENT_MEMORY_BASE_URL!,
  storeId:   process.env.AGENT_MEMORY_STORE_ID!,
  apiKey:    process.env.AGENT_MEMORY_API_KEY!,
});

async function smokeTest() {
  console.log(await agentMemory.health());

  const res = await agentMemory.addSessionEvent({
    actorId:   "user-42",
    role:      "USER",
    content:   [{ text: "hello" }],
    createdAt: new Date(),                       // SDK serializes to UTC ISO-8601
  });
  console.log(res.event.eventId);
}

smokeTest();
```

Store the API key in a secrets manager. It scopes access to a single store; rotating it requires regenerating from the Cloud console.

Reference: [https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory), [https://pypi.org/project/redis-agent-memory/](https://pypi.org/project/redis-agent-memory/), [https://www.npmjs.com/package/@redis-iris/agent-memory](https://www.npmjs.com/package/@redis-iris/agent-memory)

---

## 2. Session Memory / Events

**Impact: HIGH**

Working-memory conversation history. Appending events, retrieving session memory, and choosing when to use sessions vs long-term memory.

### 2.1 Append a Session Event Correctly

**Impact: HIGH (Each event triggers a promotion job — malformed events drop turns and corrupt LTM extraction)**

`AgentMemory.add_session_event(...)` (Python) / `agentMemory.addSessionEvent(...)` (TypeScript) appends a single event to a session. The session is created on first write; if `session_id` / `sessionId` is omitted the server generates one (32-char UUID without dashes) and returns it on the response. Every successful write also enqueues a promotion job — so payload quality directly affects what lands in long-term memory.

**Correct: Pass `actor_id`, `role`, `content`, and a **tz-aware UTC `created_at`** on every turn. Carry the same `session_id` for the whole conversation.**

**Python** — `created_at` is a `datetime.datetime` (UTC, tz-aware):**

```python
from datetime import datetime, timezone
from redis_agent_memory import AgentMemory, models

def append_event(
    agent_memory: AgentMemory,
    *,
    session_id: str,
    actor_id:   str,
    role:       models.MessageRole,
    text:       str,
    metadata:   dict | None = None,
):
    return agent_memory.add_session_event(
        session_id=session_id,                       # client-supplied — keeps the turn ordered with prior turns
        actor_id=actor_id,                           # who said this (user-42, agent-1, system)
        role=role,                                   # MessageRole.USER | .ASSISTANT | .SYSTEM
        content=[{"text": text}],                    # list of typed content parts
        created_at=datetime.now(timezone.utc),       # tz-aware UTC datetime — required
        metadata=metadata,                           # any JSON, ≤ 16 KB
    ).event                                          # → server-assigned eventId, etc.

append_event(
    agent_memory,
    session_id="chat-2026-05-18-42",
    actor_id="user-42",
    role=models.MessageRole.USER,
    text="What did we agree on yesterday?",
)
```

**TypeScript** — `createdAt` is a `Date` (SDK serializes to UTC ISO-8601):**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

async function appendEvent(
  agentMemory: AgentMemory,
  args: {
    sessionId: string;
    actorId:   string;
    role:      "USER" | "ASSISTANT" | "SYSTEM";
    text:      string;
    metadata?: Record<string, unknown>;
  },
) {
  const res = await agentMemory.addSessionEvent({
    sessionId: args.sessionId,
    actorId:   args.actorId,
    role:      args.role,
    content:   [{ text: args.text }],
    createdAt: new Date(),                         // UTC Date — required
    metadata:  args.metadata,
  });
  return res.event;                                // server-assigned eventId, etc.
}

await appendEvent(agentMemory, {
  sessionId: "chat-2026-05-18-42",
  actorId:   "user-42",
  role:      "USER",
  text:      "What did we agree on yesterday?",
});
```

**Incorrect: Letting the server generate a new `session_id` on every turn, or passing a naive (tz-less) datetime in Python.**

```python
from datetime import datetime

# Bad: omitting session_id on every call creates a new session per turn,
# so the session memory contains exactly one event and promotion has no
# context to extract from.
agent_memory.add_session_event(
    actor_id="user-42",
    role=models.MessageRole.USER,
    content=[{"text": msg}],
    created_at=datetime.now(),                     # <-- naive datetime; ambiguous timezone.
                                                   #     Use datetime.now(timezone.utc).
)
```

**Constraints worth remembering:**

```python
import asyncio
from datetime import datetime, timezone

async def main():
    async with AgentMemory(URL, store_id=SID, api_key=KEY) as agent_memory:
        await agent_memory.add_session_event_async(
            session_id="chat-1",
            actor_id="user-42",
            role=models.MessageRole.USER,
            content=[{"text": "hi"}],
            created_at=datetime.now(timezone.utc),
        )

asyncio.run(main())
```

- `store_id`, `session_id`, `actor_id`: 1–64 chars, `[a-zA-Z0-9-]` only.

- `role`: one of `USER`, `ASSISTANT`, `SYSTEM`.

- `content`: list of typed parts; today only `{"text": "..."}` is supported.

- `created_at` / `createdAt`: tz-aware UTC `datetime` (Python) or `Date` (TypeScript). The SDKs serialize to ISO-8601 on the wire.

- `metadata`: any valid JSON document, ≤ 16 KB.

- Session TTL is governed by the store's short-memory TTL (configured at store creation). Each new event refreshes the TTL on the session key.

The response (`res.event` / `result.event`) includes the server-generated `event_id` / `eventId` (32-char UUID without dashes) — store it if you might need `delete_session_event` / `deleteSessionEvent` later. It also includes a `system_timestamp` / `systemTimestamp` (set by the data plane on ingestion) alongside the client-supplied `created_at` — see `session-retrieval` for how to use the two timestamps.

The Python SDK exposes an `_async` variant for every method when used inside an `async` function:

### 2.2 Choose Session Events vs Long-Term Memory

**Impact: HIGH (Wrong tier wastes LLM budget on promotion or loses cross-session recall)**

Redis Agent Memory has two tiers. They serve different jobs — picking the wrong one is the single biggest source of cost and correctness problems.

| Tier | What it stores | Retrieval | Lifetime | Cost shape |
|---|---|---|---|---|
| **Session memory** | Raw, ordered conversation events for one session | Whole session or by `eventId` | Session-scoped TTL (configured at store creation) | Cheap writes, no LLM cost on the write path |
| **Long-term memory** | Extracted facts/summaries/messages | Semantic search across sessions | Default 1 year TTL | Each promotion runs an LLM call |

**Correct: Append every turn of the conversation as a session event. Let the background promotion worker decide what becomes long-term memory.**

**Python:**

```python
from datetime import datetime, timezone
from redis_agent_memory import AgentMemory, models

# Every user/assistant turn → add_session_event. That's it.
agent_memory.add_session_event(
    session_id=session_id,
    actor_id="user-42",
    role=models.MessageRole.USER,
    content=[{"text": user_msg}],
    created_at=datetime.now(timezone.utc),
)
agent_memory.add_session_event(
    session_id=session_id,
    actor_id="agent-1",
    role=models.MessageRole.ASSISTANT,
    content=[{"text": reply}],
    created_at=datetime.now(timezone.utc),
)
# Promotion happens asynchronously — see promotion-overview.
```

**TypeScript:**

```typescript
await agentMemory.addSessionEvent({
  sessionId: sessionId,
  actorId:   "user-42",
  role:      "USER",
  content:   [{ text: userMsg }],
  createdAt: new Date(),
});
await agentMemory.addSessionEvent({
  sessionId: sessionId,
  actorId:   "agent-1",
  role:      "ASSISTANT",
  content:   [{ text: reply }],
  createdAt: new Date(),
});
```

**Correct: Write to long-term memory directly when you already have a structured fact and don't want to pay for extraction.**

**Python:**

```python
# Pre-known fact — skip the LLM and write LTM directly.
agent_memory.bulk_create_long_term_memories(memories=[
    {
        "id":          "user-42-timezone",
        "text":        "User 42 is in Europe/Sofia (UTC+2/+3).",
        "memory_type": models.MemoryType.SEMANTIC,
        "owner_id":    "user-42",
        "topics":      ["profile", "timezone"],
    },
])
```

**TypeScript:**

```typescript
await agentMemory.bulkCreateLongTermMemories({
  memories: [
    {
      id:         "user-42-timezone",
      text:       "User 42 is in Europe/Sofia (UTC+2/+3).",
      memoryType: "semantic",
      ownerId:    "user-42",
      topics:     ["profile", "timezone"],
    },
  ],
});
```

**Incorrect: Using long-term memory as the conversation buffer.**

```python
# Bad: each turn pays for embedding + LTM write, and the agent loses turn order.
for turn in conversation:
    agent_memory.bulk_create_long_term_memories(memories=[{
        "id":          f"{session_id}-{turn.idx}",
        "text":        turn.text,
        "memory_type": models.MemoryType.MESSAGE,
    }])
```

Why it's bad: LTM is vector-indexed (cost per write) and unordered (you re-paginate to reconstruct a session). Session memory is append-only and keeps `createdAt` order for free.

**Rule of thumb: if you'd want to retrieve it in a *different* future conversation, it belongs in LTM (usually via promotion). If you only need it for the current turn or the rest of this session, it stays in session memory.**

### 2.3 Retrieve Session Memory and Individual Events

**Impact: MEDIUM (Fetching the right SDK method avoids re-paginating an entire session to find one turn)**

The SDK exposes three read paths against session memory; pick the narrowest one for the job.

| Python | TypeScript | Returns | Use when |
|---|---|---|---|
| `get_session_memory(session_id=...)` | `getSessionMemory(sessionId)` | All events for the session in order, plus `owner_id` | Rebuilding the prompt context for a conversation |
| `get_session_event(session_id=..., event_id=...)` | `getSessionEvent(sessionId, eventId)` | One event | You already have the `eventId` (e.g. from `addSessionEvent` response) |
| `list_sessions(limit=..., page_token=...)` | `listSessions({limit, pageToken})` | Page of session IDs + `total` | Admin/debug listing of sessions in a store |

The session's `owner_id` is set from the **first** event's `actor_id` and is immutable for the lifetime of the session.

**Correct: Fetch the whole session when reconstructing the agent's working context.**

**Python:**

```python
def load_session(agent_memory, session_id: str) -> list:
    res = agent_memory.get_session_memory(session_id=session_id)
    # res.session_id, res.owner_id, res.events (ordered by created_at)
    return res.events
```

**TypeScript:**

```typescript
async function loadSession(agentMemory: AgentMemory, sessionId: string) {
  const res = await agentMemory.getSessionMemory(sessionId);
  // res.sessionId, res.ownerId, res.events (ordered by createdAt)
  return res.events;
}
```

**Two timestamps on each event.** Every `SessionEvent` in the response carries:**

- `created_at` / `createdAt` — the **client-supplied** UTC timestamp you passed at write time. This is what the agent considers "when the turn happened" and what events are ordered by.

- `system_timestamp` / `systemTimestamp` — a **server-set** UTC timestamp recording when the data plane ingested the event. Useful for diagnostics (e.g. clock skew between agent and server, or detecting replayed events with stale `created_at` values).

Both are `datetime` (Python) / `Date` (TypeScript) on the SDK side; serialized as UTC ISO-8601 on the wire.

**Correct: Page through sessions for admin tools.**

**Python:**

```python
def iter_session_ids(agent_memory):
    token = None
    while True:
        page = agent_memory.list_sessions(limit=200, page_token=token)
        yield from page.sessions
        token = page.next_page_token
        if not token:
            return
```

**TypeScript:**

```typescript
async function* iterSessionIds(agentMemory: AgentMemory) {
  let pageToken: string | undefined;
  while (true) {
    const page = await agentMemory.listSessions({ limit: 200, pageToken });
    yield* page.sessions;
    if (!page.nextPageToken) return;
    pageToken = page.nextPageToken;
  }
}
```

**Incorrect: Paging the full session list to find one event you already have an ID for.**

```python
# Bad: O(sessions) just to find one eventId you already have.
for sid in iter_session_ids(agent_memory):
    for ev in load_session(agent_memory, sid):
        if ev.event_id == target_event_id:
            return ev
```

Use `get_session_event` / `getSessionEvent` instead — it is an O(1) lookup.

**Pagination limits:**

- `list_sessions.limit` defaults to 100, max 1000.

- `next_page_token` / `nextPageToken` is opaque — pass it back verbatim, don't try to decode it.

**Deletion:**

- `delete_session_memory(session_id=...)` / `deleteSessionMemory(sessionId)` removes the entire session and all its events.

- `delete_session_event(session_id=..., event_id=...)` / `deleteSessionEvent(sessionId, eventId)` removes one event.

- Already-promoted long-term memories are **not** affected — delete those separately via `bulk_delete_long_term_memories` / `bulkDeleteLongTermMemories`.

---

## 3. Long-Term Memory

**Impact: HIGH**

Persistent, semantically searchable memory records. Bulk create, semantic search with filters, and organizing records with namespace/ownerId/topics/memoryType.

### 3.1 Create Long-Term Memories in Bulk with Idempotent IDs

**Impact: HIGH (Per-record calls cost N round-trips and N embeddings — the bulk method batches both)**

`bulk_create_long_term_memories` (Python) / `bulkCreateLongTermMemories` (TypeScript) accepts up to **100 records per call**. The client supplies the `id` for each record so a retry never creates a duplicate. The response splits into `created` (IDs that landed) and `errors` (per-ID failures).

**Correct: Generate a deterministic ID per logical fact and batch up to 100.**

**Python:**

```python
import uuid
from redis_agent_memory import AgentMemory, models

def upsert_facts(agent_memory: AgentMemory, facts: list[dict]):
    # Cap at 100 per call — the API enforces this.
    res = agent_memory.bulk_create_long_term_memories(memories=[
        {
            "id":          fact["id"],                           # stable, deterministic
            "text":        fact["text"],                         # 1–50000 chars
            "memory_type": fact.get("memory_type", models.MemoryType.SEMANTIC),
            "session_id":  fact.get("session_id"),
            "owner_id":    fact.get("owner_id"),
            "namespace":   fact.get("namespace"),
            "topics":      fact.get("topics", []),
        }
        for fact in facts[:100]
    ])
    # res.created = [...ids...], res.errors = [BulkOperationError(...)]
    return res

# Deterministic IDs make retries safe: same fact → same id → no duplicate.
facts = [{
    "id":         f"user-42-pref-{uuid.uuid5(uuid.NAMESPACE_OID, 'theme:dark')}",
    "text":       "User 42 prefers dark mode.",
    "owner_id":   "user-42",
    "topics":     ["profile", "ui-preferences"],
}]
upsert_facts(agent_memory, facts)
```

**TypeScript:**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

async function upsertFacts(
  agentMemory: AgentMemory,
  facts: Array<{
    id: string; text: string;
    memoryType?: "semantic" | "episodic" | "message";
    sessionId?: string; ownerId?: string; namespace?: string;
    topics?: string[];
  }>,
) {
  const res = await agentMemory.bulkCreateLongTermMemories({
    memories: facts.slice(0, 100).map((f) => ({
      id:         f.id,
      text:       f.text,
      memoryType: f.memoryType ?? "semantic",
      sessionId:  f.sessionId,
      ownerId:    f.ownerId,
      namespace:  f.namespace,
      topics:     f.topics ?? [],
    })),
  });
  // res.created: string[], res.errors?: Array<{id: string; error: string}>
  return res;
}
```

**Incorrect: One call per memory, or random IDs on every retry.**

```python
# Bad: N round-trips + N embedding calls — slow and hammers your rate limit.
for fact in facts:
    agent_memory.bulk_create_long_term_memories(memories=[{
        "id":   str(uuid.uuid4()),            # <-- new id on every retry → duplicates on transient failures
        "text": fact["text"],
    }])
```

**Partial-success contract — always inspect `errors`:**

```typescript
const res = await upsertFacts(agentMemory, facts);
if (res.errors?.length) {
  for (const err of res.errors) {
    console.warn("LTM create failed", err.id, err.error);
  }
  const failedIds = new Set(res.errors.map((e) => e.id));
  await retryLater(facts.filter((f) => failedIds.has(f.id)));
}
```

**Constraints:**

- `memories`: 1–100 items per call.

- `id`: 1–64 chars, `[a-zA-Z0-9-]`.

- `text`: 1–50000 chars.

- `memory_type` / `memoryType`: `semantic` | `episodic` | `message`.

- `topics`: up to 50, each 1–100 chars.

- TTL: defaults to **1 year** (`31_536_000` seconds) unless the store's long-term-memory TTL overrides it.

To update a record's text or tags later, use `update_long_term_memory(memory_id=...)` / `updateLongTermMemory(memoryId, ...)` rather than re-creating with the same ID.

### 3.2 Organize Long-Term Memory with namespace, ownerId, topics, and memoryType

**Impact: MEDIUM (Good metadata makes every later search a filter-then-vector query instead of a full scan)**

LTM records carry four structured fields that exist purely to scope search. They cost nothing extra to populate at write time and make every later search call faster and more precise.

| Field | Type | Purpose | Typical use |
|---|---|---|---|
| `owner_id` / `ownerId` | 1–64 chars `[a-zA-Z0-9-]` | The user/agent the memory is *about* | Multi-tenant scoping — always set this for per-user memories |
| `namespace` | 1–64 chars `[a-zA-Z0-9-]` | Logical bucket within a store | Separate `profile` facts from `interactions` from `tools` |
| `topics` | List of up to 50 tags, each 1–100 chars | Categorical labels | `["preferences", "ui"]`, `["incident", "p1"]` |
| `memory_type` / `memoryType` | `semantic` \| `episodic` \| `message` | What the record *is* | See below |

**`memory_type` semantics:**

- `semantic` — a durable fact ("user prefers dark mode"). Cheapest to keep around long-term; survives across sessions.

- `episodic` — something that happened at a point in time ("user asked about pricing on 2026-05-10"). Pair with `created_at` filters.

- `message` — a raw conversational turn that was deemed worth retaining verbatim.

**Correct: Populate every applicable field at create time.**

**Python:**

```python
from redis_agent_memory import models

agent_memory.bulk_create_long_term_memories(memories=[
    {
        "id":          "user-42-pref-theme",
        "text":        "User 42 prefers dark mode in the dashboard.",
        "memory_type": models.MemoryType.SEMANTIC,
        "owner_id":    "user-42",
        "namespace":   "preferences",
        "topics":      ["ui", "theme"],
    },
    {
        "id":          "user-42-incident-7821",
        "text":        "User 42 hit a 500 on /api/checkout on 2026-05-10 and was refunded.",
        "memory_type": models.MemoryType.EPISODIC,
        "owner_id":    "user-42",
        "namespace":   "interactions",
        "topics":      ["incident", "billing"],
    },
])
```

**TypeScript:**

```typescript
await agentMemory.bulkCreateLongTermMemories({
  memories: [
    {
      id:         "user-42-pref-theme",
      text:       "User 42 prefers dark mode in the dashboard.",
      memoryType: "semantic",
      ownerId:    "user-42",
      namespace:  "preferences",
      topics:     ["ui", "theme"],
    },
    {
      id:         "user-42-incident-7821",
      text:       "User 42 hit a 500 on /api/checkout on 2026-05-10 and was refunded.",
      memoryType: "episodic",
      ownerId:    "user-42",
      namespace:  "interactions",
      topics:     ["incident", "billing"],
    },
  ],
});
```

Later searches can then scope cheaply:

**Python:**

```python
from datetime import datetime, timedelta, timezone

# All preferences for one user
agent_memory.search_long_term_memory(
    filter_={"owner_id": {"eq": "user-42"}, "namespace": {"eq": "preferences"}},
)

# Incidents across all users in the last 7 days
seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
agent_memory.search_long_term_memory(
    text="checkout failure",
    filter_={
        "topics":     {"all": ["incident", "billing"]},
        "created_at": {"gte": seven_days_ago},     # tz-aware UTC datetime
    },
)
```

**TypeScript:**

```typescript
// All preferences for one user
await agentMemory.searchLongTermMemory({
  filter: { ownerId: { eq: "user-42" }, namespace: { eq: "preferences" } },
});

// Incidents across all users in the last 7 days
const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
await agentMemory.searchLongTermMemory({
  text: "checkout failure",
  filter: {
    topics:    { all: ["incident", "billing"] },
    createdAt: { gte: sevenDaysAgo },             // Date
  },
});
```

**Incorrect: Stuffing all of these into the `text` field.**

```python
# Bad: structured signals hidden inside free text. Search can't filter on them
# without an LLM re-parse, and similarity threshold becomes the only knob.
agent_memory.bulk_create_long_term_memories(memories=[{
    "id":   "fact-1",
    "text": "[owner=user-42][namespace=preferences][topic=ui] prefers dark mode",
}])
```

**Updating organization later: `update_long_term_memory(memory_id=..., ...)` / `updateLongTermMemory(memoryId, ...)` accepts `namespace`, `owner_id`, `session_id`, `topics`, and `memory_type`. To clear a field, send an empty string (`""`) — omitting the field leaves it unchanged.**

**Avoid leakage between owners.** If a record can be attributed to one user, set `owner_id`. A search request without an `owner_id` filter will happily return facts from any user in the same store.

### 3.3 Search Long-Term Memory Semantically with Filters

**Impact: HIGH (Pre-filtering by ownerId/namespace cuts vector-search scope by orders of magnitude)**

`search_long_term_memory(...)` (Python) / `searchLongTermMemory(...)` (TypeScript) runs a vector search over LTM records and applies structured filters in the same call. Combining both is the supported path — do not pull a wide vector result and filter on the client.

**Correct: Pre-filter by the structured fields you already know, then rank by semantic similarity.**

**Python:**

```python
from redis_agent_memory import AgentMemory, models

def recall(
    agent_memory: AgentMemory,
    *,
    owner_id:  str,
    query:     str,
    namespace: str | None = None,
    k:         int        = 5,
):
    filt = {
        "owner_id":    {"eq": owner_id},
        "memory_type": {"in": ["semantic", "episodic"]},
    }
    if namespace is not None:
        filt["namespace"] = {"eq": namespace}

    res = agent_memory.search_long_term_memory(
        text=query,                              # embedded server-side
        similarity_threshold=0.7,                # normalized cosine, 0–1
        filter_op=models.FilterConjunction.ALL,  # AND across filter keys
        filter_=filt,                            # NB: trailing underscore — `filter` is reserved in Python
        limit=k,                                 # 1–100, default 10
    )
    return res.memories
```

**TypeScript:**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

async function recall(
  agentMemory: AgentMemory,
  args: { ownerId: string; query: string; namespace?: string; k?: number },
) {
  const res = await agentMemory.searchLongTermMemory({
    text:                args.query,
    similarityThreshold: 0.7,
    filterOp:            "all",                  // AND across filter keys
    filter: {
      ownerId:    { eq: args.ownerId },
      ...(args.namespace ? { namespace: { eq: args.namespace } } : {}),
      memoryType: { in: ["semantic", "episodic"] },
    },
    limit: args.k ?? 5,
  });
  return res.memories;
}
```

**Incorrect: Querying with only `text` and filtering client-side.**

```python
# Bad: pulls up to 100 unrelated records per user, then re-filters in Python.
# Pays the vector-search cost on the full store, and capped at 100 results
# you may miss the one you needed.
hits = agent_memory.search_long_term_memory(text=query, limit=100).memories
for m in hits:
    if m.owner_id == owner_id and m.namespace == namespace:
        ...
```

**Filter operators: per field**

| Field | Operators |
|---|---|
| `session_id`, `owner_id`, `namespace` | `eq`, `ne`, `in`, `all` |
| `topics`, `memory_type` | `eq`, `ne`, `in`, `all` (tag filter) |
| `created_at` | `gt`, `lt`, `gte`, `lte`, `eq` (tz-aware `datetime` / `Date`) |

`filter_op` / `filterOp` controls how the **top-level filter fields** combine: `"all"` (default, AND) or `"any"` (OR). Inside one field, `eq` / `ne` / `in` / `all` are mutually exclusive — set exactly one.

**Similarity threshold: Normalized cosine similarity (0–1). Start at 0.7 and tune per workload — too high returns empty pages; too low returns noise.**

**Pagination: Pass `next_page_token` / `nextPageToken` back verbatim. Don't decode it; the server may change the encoding.**

```typescript
async function* iterResults(
  agentMemory: AgentMemory,
  args: { query: string; ownerId: string },
) {
  let pageToken: string | undefined;
  while (true) {
    const page = await agentMemory.searchLongTermMemory({
      text: args.query,
      filter: { ownerId: { eq: args.ownerId } },
      limit: 50,
      pageToken,
    });
    yield* page.memories;
    if (!page.nextPageToken) return;
    pageToken = page.nextPageToken;
  }
}
```

**No-query browsing: Omit `text` to apply only the structured filters (vector ranking is skipped, results are returned in record order).**

---

## 4. Memory Promotion

**Impact: MEDIUM**

Background extraction from session events to long-term memory. Understanding the deduplication window and eventual-consistency semantics.

### 4.1 Understand Background Memory Promotion

**Impact: HIGH (Treating LTM as synchronous after a session write produces flaky tests and missing recall)**

Every successful `add_session_event` / `addSessionEvent` enqueues a **promote-working-memory** job, fire-and-forget. The data plane never blocks on the LLM call; Redis Cloud's worker pool consumes the job, reads the session's events, calls an LLM to extract durable facts, and writes resulting records into long-term memory.

Submitting a job per event would mean an LLM call per turn. To prevent that, the worker groups events into time windows. Jobs whose deduplication key would collide are run **only once** for that window.

- Two events landing in the same window for the same session share a deduplication key, so only one promotion job runs for that bucket.

- Window: **5 minutes** (managed by Redis Cloud — not user-configurable today).

- The job is **delayed** until the end of the window so it sees every event in that bucket.

After an `add_session_event` returns 200, a `search_long_term_memory` for the extracted facts may not see them for *up to one deduplication window plus the LLM round-trip*. Don't assert synchronously in tests; poll.

**Python:**

```python
import time
from redis_agent_memory import AgentMemory

def wait_for_ltm(
    agent_memory: AgentMemory,
    *,
    query:     str,
    owner_id:  str,
    timeout_s: float = 30,
):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        hits = agent_memory.search_long_term_memory(
            text=query,
            filter_={"owner_id": {"eq": owner_id}},
            limit=5,
        ).memories
        if hits:
            return hits
        time.sleep(1.0)
    raise AssertionError("promotion did not materialize in time")
```

**TypeScript:**

```typescript
import { AgentMemory } from "@redis-iris/agent-memory";

async function waitForLtm(
  agentMemory: AgentMemory,
  args: { query: string; ownerId: string; timeoutMs?: number },
) {
  const deadline = Date.now() + (args.timeoutMs ?? 30_000);
  while (Date.now() < deadline) {
    const res = await agentMemory.searchLongTermMemory({
      text:   args.query,
      filter: { ownerId: { eq: args.ownerId } },
      limit:  5,
    });
    if (res.memories.length) return res.memories;
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error("promotion did not materialize in time");
}
```

**Incorrect: Assuming LTM is updated synchronously with the session write.**

```python
# Bad: race. The promotion job is enqueued but the worker hasn't run yet.
agent_memory.add_session_event(...)
results = agent_memory.search_long_term_memory(text="...").memories
assert results, "expected the new fact to be retrievable"   # flaky
```

- Submission errors are logged on the data plane but **do not fail the write** — `add_session_event` still returns 200. The trade-off is that a queue outage silently delays promotion until Cloud's monitoring picks it up.

- Worker-side failures (LLM timeout, embedding-provider 429) are retried by the workflow engine.

- Sessions that have stopped receiving events may keep trailing turns un-promoted until the next event for that session arrives.

---

## References

1. [https://cloud.redis.io/#/agent-memory](https://cloud.redis.io/#/agent-memory)
2. [https://pypi.org/project/redis-agent-memory/](https://pypi.org/project/redis-agent-memory/)
3. [https://www.npmjs.com/package/@redis-iris/agent-memory](https://www.npmjs.com/package/@redis-iris/agent-memory)
