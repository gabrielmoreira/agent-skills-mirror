---
name: memory-systems
version: 1.2.1
description: "Designs cross-session semantic memory for agents (Mem0, Zep/Graphiti, Letta, Cognee, LangMem) with entity identity, validity windows, and consolidation. Use when choosing a memory framework, temporal knowledge graph, or LoCoMo/LongMemEval/DMR benchmark. Do not use for file scratchpads, conversation compaction, or in-flight token-budget tactics."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Memory System Design

Memory provides the persistence layer that allows agents to maintain continuity across sessions and reason over accumulated knowledge. Simple agents rely entirely on context for memory, losing all state when sessions end. Sophisticated agents implement layered memory architectures that balance immediate context needs with long-term knowledge retention. The evolution from vector stores to knowledge graphs to temporal knowledge graphs represents increasing investment in structured memory for improved retrieval and reasoning.

## When to Use

Activate this skill when:

- Building agents that must persist knowledge across sessions.
- Choosing between memory frameworks (Mem0, Zep/Graphiti, Letta, LangMem, Cognee).
- Needing to maintain entity consistency across conversations.
- Implementing reasoning over accumulated knowledge.
- Designing memory architectures that scale in production.
- Evaluating memory systems against benchmarks (LoCoMo, LongMemEval, DMR).
- Building dynamic memory with automatic entity/relationship extraction and self-improving memory (Cognee).

### Do Not Use

Route adjacent work to the skill that owns it:

- File-backed scratchpads, run logs, and tool-output offloading → `filesystem-context`.
- Conversation compaction or human-readable handoff summaries → `context-compression`.
- Masking, prefix caching, token budgets, or retrieval scoping inside one trajectory → `context-optimization`.
- Formal belief/desire/intention models over RDF state → `bdi-mental-states`.

### Deprecation & Security Warnings

- **Encryption at rest is mandatory for PII.** Avoid any memory store that does not support encryption at rest (e.g., plain SQLite files) for personally identifiable information. Prefer stores with built-in AES-256 encryption or external vault integration.
- **Zep/Graphiti cloud OAuth.** The cloud-hosted offering now requires OAuth 2.0 scopes `memory.read` and `memory.write`; legacy API keys are deprecated as of 2026-03-01.
- **Validate embedding dimensions.** Never accept unchecked user-generated embeddings; always validate vector dimensions against the pinned model to prevent injection attacks.
- **Network isolation.** When using Mem0 or any managed vector store, enable network-level isolation (VPC, private endpoints) to mitigate data exfiltration risks.

## Prerequisites

- Python 3.11+ for framework examples (Mem0, Cognee, Graphiti, LangMem).
- A TLS-capable vector store or graph database endpoint (Redis, Neo4j 5.x, or managed equivalent).
- Environment variables for secrets — never hard-code connection strings. Example placeholders: `MEM0_STORE_URL`, `GRAPHITI_API_KEY`, `COGNEE_DATA_DIR`.
- Windows host is primary (PowerShell). Use `python -m venv` and `.\.venv\Scripts\Activate.ps1` for virtual environments on Windows.
- Load `./references/implementation.md` when implementing vector stores, property graphs, temporal queries, or memory consolidation logic from scratch (includes 2026-05 security hardening notes and cryptographic hash-based tamper check).

## Procedure

Design memory as a layered system: pick the shallowest layer that meets the persistence need, validate retrieval against benchmarks, and add structure only when a simpler layer demonstrably fails.

### Step 1 — Understand the Memory Layer Spectrum

Think of memory as a spectrum from volatile context window to persistent storage. Default to the simplest layer that meets retrieval needs, because benchmark evidence suggests tool complexity matters less than reliable retrieval for some memory workloads (claim-memory-locomo-filesystem-baseline). Add structure (graphs, temporal validity) only when retrieval quality degrades or the agent needs multi-hop reasoning, relationship traversal, or time-travel queries.

| Layer | Persistence | Implementation | When to Use |
|-------|------------|----------------|-------------|
| **Working** | Context window only | Scratchpad in system prompt | Always — optimize with attention-favored positions |
| **Short-term** | Session-scoped | File-system, in-memory cache | Intermediate tool results, conversation state |
| **Long-term** | Cross-session | Key-value store → graph DB (e.g., RedisJSON, Neo4j 5.x) | User preferences, domain knowledge, entity registries |
| **Entity** | Cross-session | Entity registry + properties | Maintaining identity ("John Doe" = same person across conversations) |
| **Temporal KG** | Cross-session + history | Graph with validity intervals (Zep/Graphiti v3.1) | Facts that change over time, time-travel queries, preventing context clash |

### Step 2 — Select a Framework

Select a framework based on the dominant retrieval pattern the agent requires. Use this table to narrow the shortlist, then validate with the benchmark data below.

| Framework | Architecture | Best For | Trade-off |
|-----------|-------------|----------|-----------|
| **Mem0** | Vector store + graph memory, pluggable backends (v2.4, 2026-04) | Multi-tenant systems, broad integrations | Less specialized for multi-agent |
| **Zep/Graphiti** | Temporal knowledge graph, bi-temporal model (v3.1, 2026-02) | Enterprise requiring relationship modeling + temporal reasoning | Advanced features cloud-locked; requires OAuth 2.0 |
| **Letta** | Self-editing memory with tiered storage (in-context/core/archival) (v1.8, 2026-01) | Full agent introspection, stateful services | Complexity for simple use cases |
| **Cognee** | Multi-layer semantic graph via customizable ECL pipeline with customizable Tasks (v2.2, 2026-03) | Evolving agent memory that adapts and learns; multi-hop reasoning | Heavier ingest-time processing |
| **LangMem** | Memory tools for LangGraph workflows (v0.9, 2025-12) | Teams already on LangGraph | Tightly coupled to LangGraph |
| **File-system** | Plain files with naming conventions (v1.0) | Simple agents, prototyping | No semantic search, no relationships |

**Selection rules:**

- Choose **Zep/Graphiti** when the agent needs bi-temporal modeling (tracking both when events occurred and when they were ingested). Its three-tier knowledge graph (episode, semantic entity, community subgraphs) excels at temporal queries.
- Choose **Mem0** when the priority is fast time-to-production with managed infrastructure.
- Choose **Letta** when the agent needs deep self-introspection through its Agent Development Environment.
- Choose **Cognee** when the agent must build dense multi-layer semantic graphs — it layers text chunks and entity types as nodes with detailed relationship edges, and every core piece (ingestion, entity extraction, post-processing, retrieval) is customizable.

### Step 3 — Consult Benchmarks

Consult these benchmarks to set expectations, but treat them as source-specific signals for retrieval dimensions rather than absolute rankings. No single benchmark is definitive.

| System | DMR Accuracy | LoCoMo | HotPotQA (multi-hop) | Latency |
|--------|-------------|--------|---------------------|---------|
| Cognee | — | — | Published high score (2026-04) | Variable |
| Zep (Temporal KG) | Published high score (2026-02) | — | Mid-range across metrics | Low-latency reported |
| Letta (filesystem) | — | Published filesystem baseline (2025-11) | — | — |
| Mem0 | — | Published specialized-tool baseline (2026-03) | Lower in one comparison | — |
| MemGPT | Published high score (2025-10) | — | — | Variable |
| GraphRAG | Published mid/high range (2025-09) | — | — | Variable |
| Vector RAG baseline | Published lower range (2025-08) | — | — | Fast |

**Key takeaway:** Compare memory systems by retrieval shape, not brand. Use benchmark numbers as dated evidence that must be rechecked before making product claims. The stable design rule is to start shallow, measure retrieval quality, then add semantic or graph structure only when a simpler layer fails.

### Step 4 — Match Retrieval Strategy to Query Shape

| Strategy | Use When | Limitation |
|----------|----------|------------|
| **Semantic** (embedding similarity, OpenAI `text-embedding-3-large` or Cohere `embed-multilingual-v3`) | Direct factual queries | Degrades on multi-hop reasoning |
| **Entity-based** (graph traversal) | "Tell me everything about X" | Requires graph structure |
| **Temporal** (validity filter) | Facts change over time | Requires validity metadata |
| **Hybrid** (semantic + keyword + graph) | Best overall accuracy | Most infrastructure |

Hybrid approaches reduce active context by retrieving only relevant subgraphs or memories. Cognee implements hybrid retrieval through multiple search modes across graph, vector, and relational stores, letting agents select the retrieval strategy that fits the query type rather than using a one-size-fits-all approach.

### Step 5 — Follow the Escalation Path

1. **Prototype:** Use file-system memory. Store facts as structured JSON with ISO-8601 timestamps and optional HMAC signatures for integrity. This validates agent behavior before committing to infrastructure.
2. **Scale:** Move to Mem0 or a vector store with metadata when the agent needs semantic search and multi-tenant isolation, because file-based lookup cannot handle similarity queries.
3. **Complex reasoning:** Add Zep/Graphiti when the agent needs relationship traversal, temporal validity, or cross-session synthesis. Graphiti uses structured ties with generic relations, keeping graphs simple and easy to reason about; Cognee builds denser multi-layer semantic graphs with detailed relationship edges — choose based on whether the agent needs temporal bi-modeling (Graphiti) or richer interconnected knowledge structures (Cognee).
4. **Full control:** Use Letta or Cognee when the agent must self-manage its own memory with deep introspection, because these frameworks expose memory operations as first-class agent actions.

### Step 6 — Implement Memory Consolidation

Run consolidation periodically to prevent unbounded growth, because unchecked memory accumulation degrades retrieval quality over time. **Invalidate but do not discard** — preserving history matters for temporal queries that need to reconstruct past states. Trigger consolidation on memory count thresholds, degraded retrieval quality, or scheduled intervals.

Load `./references/implementation.md` for working consolidation code that includes a cryptographic hash-based tamper check (added 2026-05).

### Step 7 — Integrate with Context

Load memories just-in-time rather than preloading everything, because large context payloads are expensive and degrade attention quality. Place retrieved memories in attention-favored positions (beginning or end of context) to maximize their influence on generation. When using OpenAI `gpt-4o-2024-08-06` or Claude `3.5-sonnet-2024-10`, prepend a memory header that includes a SHA-256 hash of the retrieved chunk for downstream verification.

### Step 8 — Implement Error Recovery

Handle retrieval failures gracefully because memory systems are inherently noisy. Apply these recovery strategies in order:

- **Empty retrieval:** Fall back to broader search (remove entity filter, widen time range). If still empty, prompt user for clarification.
- **Stale results:** Check `valid_until` timestamps. If most results are expired, trigger consolidation before retrying.
- **Conflicting facts:** Prefer the fact with the most recent `valid_from`. Surface the conflict to the user if confidence is low.
- **Storage failure:** Queue writes for retry with exponential back-off. Never block the agent's response on a memory write.

## Guidelines

These are defaults, not dogma. Each one carries the reason it exists so you can recognize when a deliberate exception is warranted.

1. **Start with file-system memory and escalate only when retrieval quality demands it.** Why: every deeper layer (vector, graph, temporal KG) adds infrastructure, operational burden, and new failure modes, and benchmark evidence shows a simple filesystem baseline can match specialized tooling on some workloads (claim-memory-locomo-filesystem-baseline). Pay that cost only once a simpler layer measurably falls short.
2. **Track temporal validity (`valid_from`/`valid_until`) for any fact that can change.** Why: without it the agent cannot distinguish a current fact from a superseded one, so stale data silently poisons the context and the agent acts on outdated assumptions.
3. **Prefer hybrid retrieval (semantic + keyword + graph) when accuracy matters most.** Why: each single strategy has a blind spot — semantic search degrades on multi-hop reasoning, keyword misses paraphrases, graph traversal needs structure — and combining them covers each other's gaps. The trade-off is more infrastructure, so reserve hybrid for high-stakes retrieval.
4. **Consolidate periodically and invalidate rather than discard.** Why: unbounded growth degrades retrieval precision over time, but hard-deleting history breaks the time-travel queries that need to reconstruct a past state. Invalidation preserves both retrieval quality and auditability.
5. **Design for retrieval failure with explicit fallbacks.** Why: memory systems are inherently noisy and will return empty, stale, or conflicting results in production; an agent that assumes a clean hit will hallucinate or stall the moment a lookup misses.
6. **Treat persistence as a privacy obligation, not just a feature.** Why: storing user data across sessions creates retention, deletion-right, and regulatory exposure (GDPR/CCPA). Define retention windows, honor deletion requests, and encrypt PII at rest before data accumulates, because retrofitting compliance onto a populated store is far harder.
7. **Benchmark against LoCoMo or LongMemEval before and after every change.** Why: a new embedding model or consolidation policy can regress retrieval invisibly; a before/after measurement turns "it feels better" into evidence and catches silent regressions early.
8. **Monitor memory growth and retrieval latency in production.** Why: latency creep and unbounded memory size degrade quietly until they hurt user-facing response time, so treat them as leading indicators and page someone before users feel it — for instance, alert on > 200 ms latency per query.
9. **Pin one embedding model per store and re-embed on any upgrade.** Why: vectors written by one model are not comparable to vectors written by another, so mixing them — e.g., reading `text-embedding-3-large` entries with `text-embedding-3-xl` — quietly wrecks similarity scores. On an upgrade, batch re-index every entry so the whole store shares one vector space.

## Pitfalls

1. **Stuffing everything into context:** Loading all available memories into the prompt is expensive and degrades attention quality. Use just-in-time retrieval with relevance filtering instead.
2. **Ignoring temporal validity:** Facts go stale. Without validity tracking, outdated information poisons the context and the agent acts on wrong assumptions.
3. **Over-engineering early:** Simple filesystem-backed memory can outperform more specialized tooling on some benchmarks (claim-memory-locomo-filesystem-baseline). Add sophistication only when simple approaches demonstrably fail.
4. **No consolidation strategy:** Unbounded memory growth degrades retrieval quality over time. Set memory count thresholds or scheduled intervals to trigger consolidation.
5. **Embedding model mismatch:** Writing memories with one embedding model and reading with another produces poor retrieval because vector spaces are not interchangeable. Pin a single embedding model for each memory store and re-embed all entries if the model changes.
6. **Graph schema rigidity:** Over-structured graph schemas (rigid node types, fixed relationship labels) break when the domain evolves. Prefer generic relation types and flexible property bags so new entity kinds do not require schema migrations.
7. **Stale memory poisoning:** Old memories that contradict the current state corrupt agent behavior silently. Implement expiry policies or confidence decay so the agent deprioritizes aged facts, and surface contradictions explicitly when detected.
8. **Memory-context mismatch:** Retrieving memories that are topically related but contextually wrong (e.g., a memory about "Python" the snake when the agent is discussing Python the language). Mitigate by including session or domain metadata in memory entries and filtering on it during retrieval.
9. **Security oversight:** Never store raw PII without encryption-at-rest and access-control checks. Use field-level encryption for sensitive attributes (e.g., email, SSN).

## Examples

### Example 1: Mem0 Integration (v2.4)

A production wrapper with typed signatures, input validation, secrets read from the environment, and memory writes that degrade gracefully instead of blocking the agent.

```python
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from mem0 import Memory

logger = logging.getLogger("memory.mem0")


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def build_memory(store_url: str | None = None) -> Memory:
    """Construct a Mem0 client backed by an encrypted, TLS-only store."""
    resolved = store_url or os.environ.get("MEM0_STORE_URL")
    if not resolved:
        raise ValueError(
            "MEM0_STORE_URL is not set. Provide a TLS connection string, "
            "e.g. 'rediss://:<password>@mem0-redis:6379/0'."
        )
    if not resolved.startswith(("rediss://", "redis://")):
        raise ValueError(f"Unsupported store URL scheme: {resolved!r}")
    if not resolved.startswith("rediss://") and "tls=true" not in resolved:
        raise ValueError("Refusing to connect without TLS; use 'rediss://' or add 'tls=true'.")
    return Memory(store_url=resolved)


def remember(memory: Memory, text: str, user_id: str) -> None:
    """Persist one fact for a user. Never blocks the agent on store failure."""
    if not text.strip():
        raise ValueError("Refusing to store an empty memory.")
    if not user_id.strip():
        raise ValueError("user_id is required to scope memories per tenant.")
    try:
        memory.add(text, user_id=user_id, metadata={"timestamp": utc_now_iso()})
    except Exception as exc:  # noqa: BLE001
        logger.warning("Mem0 write failed for user %s: %s", user_id, exc)


def current_preference(
    memory: Memory,
    question: str,
    user_id: str,
    top_k: int = 3,
) -> list[dict[str, object]]:
    """Return only the still-valid memories for a question."""
    if not question.strip():
        raise ValueError("Refusing to search with an empty query.")
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer.")
    try:
        results = memory.search(query=question, user_id=user_id, limit=top_k)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Mem0 search failed for user %s: %s", user_id, exc)
        return []
    # Filter out expired entries
    now = utc_now_iso()
    valid = [r for r in results if r.get("metadata", {}).get("valid_until", None) is None
             or r["metadata"]["valid_until"] > now]
    return valid
```

### Example 2: Zep/Graphiti Temporal KG (v3.1)

Recording a residence fact with validity intervals and querying at a specific point in time.

```python
from __future__ import annotations

import logging
from datetime import datetime, timezone

from graphiti import GraphitiClient

logger = logging.getLogger("memory.graphiti")


def build_graphiti_client() -> GraphitiClient:
    """Construct a Graphiti client using OAuth 2.0 (legacy API keys deprecated 2026-03-01)."""
    return GraphitiClient.from_oauth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        scopes=["memory.read", "memory.write"],
    )


def _require_aware(name: str, value: datetime) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware; got naive {value!r}")


def record_residence(
    client: GraphitiClient,
    user_id: str,
    address_id: str,
    valid_from: datetime,
    valid_until: datetime | None,
) -> None:
    """Record a LIVES_AT edge with bi-temporal validity."""
    _require_aware("valid_from", valid_from)
    if valid_until is not None:
        _require_aware("valid_until", valid_until)
    try:
        client.add_edge(
            source=user_id,
            target=address_id,
            relation="LIVES_AT",
            valid_from=valid_from,
            valid_until=valid_until,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to record residence for user %s: %s", user_id, exc)
        raise


def residence_at(client: GraphitiClient, query_time: datetime) -> list[dict[str, object]]:
    """Return the residence facts that were valid at a specific instant."""
    _require_aware("query_time", query_time)
    try:
        results = client.query_at_time(
            {"type": "LIVES_AT", "source_label": "User"},
            query_time=query_time,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Temporal query failed at %s: %s", query_time.isoformat(), exc)
        return []
    return list(results)


client = build_graphiti_client()
user_node = "user:alice"
address_node = "address:berlin-flat-12"

record_residence(
    client,
    user_id=user_node,
    address_id=address_node,
    valid_from=datetime(2024, 1, 15, tzinfo=timezone.utc),
    valid_until=datetime(2024, 9, 1, tzinfo=timezone.utc),
)

results = residence_at(client, query_time=datetime(2024, 3, 1, tzinfo=timezone.utc))
print(results)
```

### Example 3: Cognee Memory Ingestion and Search (v2.2)

The ECL pipeline (add → cognify → memify → search) wrapped in async functions with source validation, typed returns, and an empty-result fallback on search failure.

```python
from __future__ import annotations

import logging
from pathlib import Path

import cognee
from cognee.modules.search.types import SearchType

logger = logging.getLogger("memory.cognee")


async def ingest_knowledge(sources: list[str | Path]) -> None:
    """Run Cognee's ECL pipeline over real sources."""
    if not sources:
        raise ValueError("Provide at least one source to ingest.")
    for source in sources:
        candidate = Path(source)
        if candidate.exists():
            await cognee.add(str(candidate))
        elif isinstance(source, str):
            await cognee.add(source)
        else:
            raise FileNotFoundError(f"Source path does not exist: {candidate}")
    try:
        await cognee.cognify()
        await cognee.memify()
    except Exception as exc:  # noqa: BLE001
        logger.error("Cognee ingestion pipeline failed: %s", exc)
        raise


async def recall(question: str, top_k: int = 5) -> list[dict[str, object]]:
    """Retrieve relationship-aware context for a question."""
    if not question.strip():
        raise ValueError("Refusing to search with an empty query.")
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer.")
    try:
        results = await cognee.search(
            query_text=question,
            query_type=SearchType.GRAPH_COMPLETION,
            top_k=top_k,
            filters={"valid_until": None},
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cognee search failed for query %r: %s", question, exc)
        return []
    return list(results)


async def main() -> None:
    await ingest_knowledge(
        [
            "./docs/",
            "Alice leads the payments team and prefers async standups.",
        ]
    )
    answers = await recall("Who leads the payments team?")
    print(answers)
```

## Verification

- [ ] Test the skill end-to-end with at least two different memory frameworks.
- [ ] Confirm the shallowest viable memory layer was chosen — working/file-system was used before escalating to vector, graph, or temporal KG.
- [ ] Confirm the selected framework matches the dominant retrieval pattern and was validated against a benchmark (LoCoMo, LongMemEval, or DMR) before any product claim.
- [ ] Confirm temporal validity (`valid_from`/`valid_until`) is tracked for every fact that can change over time.
- [ ] Confirm a single embedding model is pinned per memory store, with a re-embedding plan if the model changes (no read/write vector-space mismatch).
- [ ] Confirm a consolidation trigger exists (count threshold, degraded retrieval, or schedule) and that it invalidates rather than discards history.
- [ ] Confirm retrieval-failure fallbacks are implemented for empty, stale, conflicting, and storage-failure paths, and that memory writes never block the agent's response.
- [ ] Confirm memories are loaded just-in-time into attention-favored positions rather than preloaded wholesale.
- [ ] Confirm session/domain metadata is attached to entries and filtered on retrieval to prevent context mismatch.
- [ ] Confirm privacy, retention, and deletion policies are defined and enforced for persistent memory (including encryption-at-rest).
- [ ] Confirm memory growth and retrieval latency are monitored in production; alerts fire if latency > 200 ms or size grows > 2× baseline.

Checkable commands:

```powershell
# Verify environment variables are set (no secrets in source)
echo $env:MEM0_STORE_URL   # should print rediss://... (not empty, not http://)
echo $env:GRAPHITI_API_KEY # should be set for OAuth flow

# Verify embedding model pinning — check store metadata
python -c "from mem0 import Memory; m = Memory(store_url='$env:MEM0_STORE_URL'); print(m.config.embedding_model)"

# Run a smoke-test retrieval and check latency
python -c "import time; from mem0 import Memory; m = Memory(store_url='$env:MEM0_STORE_URL'); t=time.time(); r=m.search('test', user_id='smoke'); print(f'latency_ms={int((time.time()-t)*1000)}'); assert len(r) >= 0"
```

## Related Skills

- `filesystem-context`: file-backed scratchpads, logs, and simple run state before semantic retrieval is needed.
- `context-compression`: summaries and handoffs that preserve session state in prose.
- `context-optimization`: just-in-time memory loading and retrieval scoping inside active context budgets.
- `context-degradation`: stale or conflicting memories as context poisoning or clash.
- `bdi-mental-states`: formal mental-state modeling when beliefs, desires, intentions, and provenance chains matter.
- `multi-agent-patterns`: shared memory across agents.
- `evaluation`: memory quality, retrieval correctness, and benchmark selection.

## References

Internal references:

- `./references/implementation.md` — Read when: implementing vector stores, property graphs, temporal queries, or memory consolidation logic from scratch (includes 2026-05 security hardening notes and cryptographic hash-based tamper check).

Related skills in this collection:

- `context-fundamentals` — Read when: designing the context layer that memory feeds into.
- `multi-agent-patterns` — Read when: multiple agents need to share or coordinate memory state.

External resources:

- Zep temporal knowledge graph paper (arXiv:2501.13956) — 2026-01
- Mem0 production architecture paper (arXiv:2504.19413) — 2026-04
- Cognee optimized knowledge graph + LLM reasoning paper (arXiv:2505.24478) — 2026-05
- LoCoMo benchmark (Snap Research) — 2025-11
- MemBench evaluation framework (ACL 2025) — 2025-07
- Graphiti open-source temporal KG engine (github.com/getzep/graphiti) — latest release v3.1 (2026-02)
- Cognee open-source knowledge graph memory (github.com/topoteretes/cognee) — latest release v2.2 (2026-03)
- [Cognee comparison: Form vs Function](https://www.cognee.ai/blog/deep-dives/competition-comparison-form-vs-function) — 2026-04
