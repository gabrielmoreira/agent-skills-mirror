---
name: memory-systems
description: "Design short-term, long-term, and graph-based memory architectures"
risk: safe
source: "https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/memory-systems"
date_added: "2026-02-27"
---

## When to Use This Skill

Design short-term, long-term, and graph-based memory architectures

Use this skill when working with design short-term, long-term, and graph-based memory architectures.
# Memory System Design

Memory provides the persistence layer that allows agents to maintain continuity across sessions and reason over accumulated knowledge. Simple agents rely entirely on context for memory, losing all state when sessions end. Sophisticated agents implement layered memory architectures that balance immediate context needs with long-term knowledge retention. The evolution from vector stores to knowledge graphs to temporal knowledge graphs represents increasing investment in structured memory for improved retrieval and reasoning.

## When to Activate

Activate this skill when:
- Building agents that must persist across sessions
- Needing to maintain entity consistency across conversations
- Implementing reasoning over accumulated knowledge
- Designing systems that learn from past interactions
- Creating knowledge bases that grow over time
- Building temporal-aware systems that track state changes

## Core Concepts

Memory exists on a spectrum from immediate context to permanent storage. At one extreme, working memory in the context window provides zero-latency access but vanishes when sessions end. At the other extreme, permanent storage persists indefinitely but requires retrieval to enter context.

Simple vector stores lack relationship and temporal structure. Knowledge graphs preserve relationships for reasoning. Temporal knowledge graphs add validity periods for time-aware queries. Implementation choices depend on query complexity, infrastructure constraints, and accuracy requirements.

## Detailed Topics

### Memory Architecture Fundamentals

**The Context-Memory Spectrum**
Memory exists on a spectrum from immediate context to permanent storage. At one extreme, working memory in the context window provides zero-latency access but vanishes when sessions end. At the other extreme, permanent storage persists indefinitely but requires retrieval to enter context. Effective architectures use multiple layers along this spectrum.

The spectrum includes working memory (context window, zero latency, volatile), short-term memory (session-persistent, searchable, volatile), long-term memory (cross-session persistent, structured, semi-permanent), and permanent memory (archival, queryable, permanent). Each layer has different latency, capacity, and persistence characteristics.

**Why Simple Vector Stores Fall Short**
Vector RAG provides semantic retrieval by embedding queries and documents in a shared embedding space. Similarity search retrieves the most semantically similar documents. This works well for document retrieval but lacks structure for agent memory.

Vector stores lose relationship information. If an agent learns that "Customer X purchased Product Y on Date Z," a vector store can retrieve this fact if asked directly. But it cannot answer "What products did customers who purchased Product Y also buy?" because relationship structure is not preserved.

Vector stores also struggle with temporal validity. Facts change over time, but vector stores provide no mechanism to distinguish "current fact" from "outdated fact" except through explicit metadata and filtering.

**The Move to Graph-Based Memory**
Knowledge graphs preserve relationships between entities. Instead of isolated document chunks, graphs encode that Entity A has Relationship R to Entity B. This enables queries that traverse relationships rather than just similarity.

Temporal knowledge graphs add validity periods to facts. Each fact has a "valid from" and optionally "valid until" timestamp. This enables time-travel queries that reconstruct knowledge at specific points in time.

**Benchmark Performance Comparison**
The Deep Memory Retrieval (DMR) benchmark provides concrete performance data across memory architectures:

| Memory System | DMR Accuracy | Retrieval Latency | Notes |
|---------------|--------------|-------------------|-------|
| Zep (Temporal KG) | 94.8% | 2.58s | Best accuracy, fast retrieval |
| MemGPT | 93.4% | Variable | Good general performance |
| GraphRAG | ~75-85% | Variable | 20-35% gains over baseline RAG |
| Vector RAG | ~60-70% | Fast | Loses relationship structure |
| Recursive Summarization | 35.3% | Low | Severe information loss |

Zep demonstrated 90% reduction in retrieval latency compared to full-context baselines (2.58s vs 28.9s for GPT-5.2). This efficiency comes from retrieving only relevant subgraphs rather than entire context history.

GraphRAG achieves approximately 20-35% accuracy gains over baseline RAG in complex reasoning tasks and reduces hallucination by up to 30% through community-based summarization.

### Memory Layer Architecture

**Layer 1: Working Memory**
Working memory is the context window itself. It provides immediate access to information currently being processed but has limited capacity and vanishes when sessions end.

Working memory usage patterns include scratchpad calculations where agents track intermediate results, conversation history that preserves dialogue for current task, current task state that tracks progress on active objectives, and active retrieved documents that hold information currently being used.

Optimize working memory by keeping only active information, summarizing completed work before it falls out of attention, and using attention-favored positions for critical information.

**Layer 2: Short-Term Memory**
Short-term memory persists across the current session but not across sessions. It provides search and retrieval capabilities without the latency of permanent storage.

Common implementations include session-scoped databases that persist until session end, file-system storage in designated session directories, and in-memory caches keyed by session ID.

Short-term memory use cases include tracking conversation state across turns without stuffing context, storing intermediate results from tool calls that may be needed later, maintaining task checklists and progress tracking, and caching retrieved information within sessions.

**Layer 3: Long-Term Memory**
Long-term memory persists across sessions indefinitely. It enables agents to learn from past interactions and build knowledge over time.

Long-term memory implementations range from simple key-value stores to sophisticated graph databases. The choice depends on complexity of relationships to model, query patterns required, and acceptable infrastructure complexity.

Long-term memory use cases include learning user preferences across sessions, building domain knowledge bases that grow over time, maintaining entity registries with relationship history, and storing successful patterns that can be reused.

**Layer 4: Entity Memory**
Entity memory specifically tracks information about entities (people, places, concepts, objects) to maintain consistency. This creates a rudimentary knowledge graph where entities are recognized across multiple interactions.

Entity memory maintains entity identity by tracking that "John Doe" mentioned in one conversation is the same person in another. It maintains entity properties by storing facts discovered about entities over time. It maintains entity relationships by tracking relationships between entities as they are discovered.

**Layer 5: Temporal Knowledge Graphs**
Temporal knowledge graphs extend entity memory with explicit validity periods. Facts are not just true or false but true during specific time ranges.

This enables queries like "What was the user's address on Date X?" by retrieving facts valid during that date range. It prevents context clash when outdated information contradicts new data. It enables temporal reasoning about how entities changed over time.

### Memory Implementation Patterns

**Pattern 1: File-System-as-Memory**
The file system itself can serve as a memory layer. This pattern is simple, requires no additional infrastructure, and enables the same just-in-time loading that makes file-system-based context effective.

Implementation uses the file system hierarchy for organization. Use naming conventions that convey meaning. Store facts in structured formats (JSON, YAML). Use timestamps in filenames or metadata for temporal tracking.

Advantages: Simplicity, transparency, portability.
Disadvantages: No semantic search, no relationship tracking, manual organization required.

**Pattern 2: Vector RAG with Metadata**
Vector stores enhanced with rich metadata provide semantic search with filtering capabilities.

Implementation embeds facts or documents and stores with metadata including entity tags, temporal validity, source attribution, and confidence scores. Query includes metadata filters alongside semantic search.

**Pattern 3: Knowledge Graph**
Knowledge graphs explicitly model entities and relationships. Implementation defines entity types and relationship types, uses graph database or property graph storage, and maintains indexes for common query patterns.

**Pattern 4: Temporal Knowledge Graph**
Temporal knowledge graphs add validity periods to facts, enabling time-travel queries and preventing context clash from outdated information.

### Memory Retrieval Patterns

**Semantic Retrieval**
Retrieve memories semantically similar to current query using embedding similarity search.

**Entity-Based Retrieval**
Retrieve all memories related to specific entities by traversing graph relationships.

**Temporal Retrieval**
Retrieve memories valid at specific time or within time range using validity period filters.

### Memory Consolidation

Memories accumulate over time and require consolidation to prevent unbounded growth and remove outdated information.

**Consolidation Triggers**
Trigger consolidation after significant memory accumulation, when retrieval returns too many outdated results, periodically on a schedule, or when explicit consolidation is requested.

**Consolidation Process**
Identify outdated facts, merge related facts, update validity periods, archive or delete obsolete facts, and rebuild indexes.

## Practical Guidance

### Integration with Context

Memories must integrate with context systems to be useful. Use just-in-time memory loading to retrieve relevant memories when needed. Use strategic injection to place memories in attention-favored positions.

### Memory System Selection

Choose memory architecture based on requirements:
- Simple persistence needs: File-system memory
- Semantic search needs: Vector RAG with metadata
- Relationship reasoning needs: Knowledge graph
- Temporal validity needs: Temporal knowledge graph

## Examples

**Example 1: Entity Tracking**
```python
# Track entity across conversations
def remember_entity(entity_id, properties):
    memory.store({
        "type": "entity",
        "id": entity_id,
        "properties": properties,
        "last_updated": now()
    })

def get_entity(entity_id):
    return memory.retrieve_entity(entity_id)
```

**Example 2: Temporal Query**
```python
# What was the user's address on January 15, 2024?
def query_address_at_time(user_id, query_time):
    return temporal_graph.query("""
        MATCH (user)-[r:LIVES_AT]->(address)
        WHERE user.id = $user_id
        AND r.valid_from <= $query_time
        AND (r.valid_until IS NULL OR r.valid_until > $query_time)
        RETURN address
    """, {"user_id": user_id, "query_time": query_time})
```

## Guidelines

1. Match memory architecture to query requirements
2. Implement progressive disclosure for memory access
3. Use temporal validity to prevent outdated information conflicts
4. Consolidate memories periodically to prevent unbounded growth
5. Design for memory retrieval failures gracefully
6. Consider privacy implications of persistent memory
7. Implement backup and recovery for critical memories
8. Monitor memory growth and performance over time

## Integration

This skill builds on context-fundamentals. It connects to:

- multi-agent-patterns - Shared memory across agents
- context-optimization - Memory-based context loading
- evaluation - Evaluating memory quality

## References

Internal reference:
- Implementation Reference - Detailed implementation patterns

Related skills in this collection:
- context-fundamentals - Context basics
- multi-agent-patterns - Cross-agent memory

External resources:
- Graph database documentation (Neo4j, etc.)
- Vector store documentation (Pinecone, Weaviate, etc.)
- Research on knowledge graphs and reasoning

---

## Skill Metadata

**Created**: 2025-12-20
**Last Updated**: 2025-12-20
**Author**: Agent Skills for Context Engineering Contributors
**Version**: 1.0.0

### Production Framework Landscape

| Framework | Architecture | Best For | Trade-off |
|-----------|-------------|----------|-----------|
| **Mem0** | Vector store + graph memory, pluggable backends | Multi-tenant systems, broad integrations | Less specialized for multi-agent |
| **Zep/Graphiti** | Temporal knowledge graph, bi-temporal model | Enterprise requiring relationship modeling + temporal reasoning | Advanced features cloud-locked |
| **Letta** | Self-editing memory with tiered storage (in-context/core/archival) | Full agent introspection, stateful services | Complexity for simple use cases |
| **Cognee** | Multi-layer semantic graph via customizable ECL pipeline with customizable Tasks | Evolving agent memory that adapts and learns; multi-hop reasoning | Heavier ingest-time processing |
| **LangMem** | Memory tools for LangGraph workflows | Teams already on LangGraph | Tightly coupled to LangGraph |
| **File-system** | Plain files with naming conventions | Simple agents, prototyping | No semantic search, no relationships |

Zep's Graphiti engine builds a three-tier knowledge graph (episode, semantic entity, community subgraphs) with a bi-temporal model tracking both when events occurred and when they were ingested. Mem0 offers the fastest path to production with managed infrastructure. Letta provides the deepest agent control through its Agent Development Environment. Cognee produces multi-layer semantic graphs — it layers text chunks and entity types as nodes with detailed relationship edges, building interconnected knowledge engine. Every core piece (ingestion, entity extraction, post-processing, retrieval) is customizable.

**Benchmark Performance Comparison**

| System | DMR Accuracy | LoCoMo | HotPotQA (multi-hop) | Latency |
|--------|-------------|--------|---------------------|---------|
| Cognee | — | — | Highest on EM, F1, Correctness | Variable |
| Zep (Temporal KG) | 94.8% | — | Mid-range across metrics | 2.58s |
| Letta (filesystem) | — | 74.0% | — | — |
| Mem0 | — | 68.5% | Lowest across metrics | — |
| MemGPT | 93.4% | — | — | Variable |
| GraphRAG | ~75-85% | — | — | Variable |
| Vector RAG baseline | ~60-70% | — | — | Fast |

Zep achieves up to 18.5% accuracy improvement on LongMemEval while reducing latency by 90%. Cognee outperformed Mem0, Graphiti, and LightRAG on HotPotQA multi-hop reasoning benchmarks across Exact Match, F1, and human-like correctness metrics. Letta's filesystem-based agents achieved 74% on LoCoMo using basic file operations, outperforming specialized memory tools — tool complexity matters less than reliable retrieval. No single benchmark is definitive; treat these as signals for specific retrieval dimensions rather than rankings.


### Memory Layers (Decision Points)

| Layer | Persistence | Implementation | When to Use |
|-------|------------|----------------|-------------|
| **Working** | Context window only | Scratchpad in system prompt | Always — optimize with attention-favored positions |
| **Short-term** | Session-scoped | File-system, in-memory cache | Intermediate tool results, conversation state |
| **Long-term** | Cross-session | Key-value store → graph DB | User preferences, domain knowledge, entity registries |
| **Entity** | Cross-session | Entity registry + properties | Maintaining identity ("John Doe" = same person across conversations) |
| **Temporal KG** | Cross-session + history | Graph with validity intervals | Facts that change over time, time-travel queries, preventing context clash |


### Retrieval Strategies

| Strategy | Use When | Limitation |
|----------|----------|------------|
| **Semantic** (embedding similarity) | Direct factual queries | Degrades on multi-hop reasoning |
| **Entity-based** (graph traversal) | "Tell me everything about X" | Requires graph structure |
| **Temporal** (validity filter) | Facts change over time | Requires validity metadata |
| **Hybrid** (semantic + keyword + graph) | Best overall accuracy | Most infrastructure |

Zep's hybrid approach achieves 90% latency reduction (2.58s vs 28.9s) by retrieving only relevant subgraphs. Cognee implements hybrid retrieval through its 14 search modes — each mode combines different strategies from its three-store architecture (graph, vector, relational), letting agents select the retrieval strategy that fits the query type rather than using a one-size-fits-all approach.


### Choosing a Memory Architecture

**Start simple, add complexity only when retrieval fails.** Most agents don't need a temporal knowledge graph on day one.

1. **Prototype**: File-system memory. Store facts as structured JSON with timestamps. Good enough to validate agent behavior.
2. **Scale**: Move to Mem0 or vector store with metadata when you need semantic search and multi-tenant isolation.
3. **Complex reasoning**: Add Zep/Graphiti when you need relationship traversal, temporal validity, or cross-session synthesis. Graphiti uses structured ties with generic relations, keeping graphs simple and easy to reason about; Cognee builds denser multi-layer semantic graphs with detailed relationship edges — choose based on whether you need temporal bi-modeling (Graphiti) or richer interconnected knowledge structures (Cognee).
4. **Full control**: Use Letta or Cognee when you need agent self-management of memory with deep introspection.


### Error Recovery

- **Empty retrieval**: Fall back to broader search (remove entity filter, widen time range). If still empty, prompt user for clarification.
- **Stale results**: Check `valid_until` timestamps. If most results are expired, trigger consolidation before retrying.
- **Conflicting facts**: Prefer the fact with the most recent `valid_from`. Surface the conflict to the user if confidence is low.
- **Storage failure**: Queue writes for retry. Never block the agent's response on a memory write.


### Anti-Patterns

- **Stuffing everything into context**: Long inputs are expensive and degrade performance. Use just-in-time retrieval.
- **Ignoring temporal validity**: Facts go stale. Without validity tracking, outdated information poisons context.
- **Over-engineering early**: A filesystem agent can outperform complex memory tooling. Add sophistication when simple approaches fail.
- **No consolidation strategy**: Unbounded memory growth degrades retrieval quality over time.


# Retrieves current preference (light mode), not outdated one
results = m.search("What theme does the user prefer?", user_id="alice")
```

**Example 2: Temporal Query**
```python

# Track entity with validity periods
graph.create_temporal_relationship(
    source_id=user_node,
    rel_type="LIVES_AT",
    target_id=address_node,
    valid_from=datetime(2024, 1, 15),
    valid_until=datetime(2024, 9, 1),  # moved out
)


# Query: Where did user live on March 1, 2024?
results = graph.query_at_time(
    {"type": "LIVES_AT", "source_label": "User"},
    query_time=datetime(2024, 3, 1)
)
```

**Example 3: Cognee Memory Ingestion and Search**
```python
import cognee
from cognee.modules.search.types import SearchType


# Ingest and build knowledge graph
await cognee.add("./docs/")
await cognee.add("any data")
await cognee.cognify()


# Enrich memory 
await cognee.memify()


# Agent retrieves relationship-aware context
results = await cognee.search(
    query_text="Any query for your memory",
    query_type=SearchType.GRAPH_COMPLETION,
)
```

