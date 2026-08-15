---
name: pinecone
description: "Operates Pinecone serverless indexes via pinecone-client: batch upsert, metadata filters, namespaces, and dense-plus-sparse hybrid queries. Use when production RAG, semantic search, or recommendations need a managed auto-scaling vector store. Not for local Chroma, FAISS-only kNN, or self-hosted Weaviate."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [pinecone-client]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [RAG, Pinecone, Vector Database, Managed Service, Serverless, Hybrid Search, Production, Auto-Scaling, Low Latency, Recommendations]
---

# Pinecone — Managed Vector Database

Pinecone is a fully managed, auto-scaling vector database with hybrid search (dense + sparse), metadata filtering, and namespaces. p95 latency <100ms. Use for production RAG, recommendation systems, or semantic search at scale.

## When to Use

**Use Pinecone when:**
- You need a managed, serverless vector database without infrastructure overhead
- Building production RAG applications requiring <100ms p95 query latency
- Auto-scaling to billions of vectors is required
- You need hybrid search (dense + sparse vectors) in a single query
- Multi-tenant isolation via namespaces is needed
- 99.9% uptime SLA is a requirement

**Use alternatives instead:**
- **Chroma**: Self-hosted, open-source, local development
- **FAISS**: Offline, pure similarity search, no metadata filtering
- **Weaviate**: Self-hosted with more features (graph relationships, modules)

## Prerequisites

1. Python 3.8+ installed
2. A Pinecone API key — obtain from https://app.pinecone.io
3. Embedding model selected (determines vector dimension)
4. On Windows (primary host), use PowerShell for all CLI commands

### Installation

```bash
pip install pinecone-client
```

For LangChain integration:

```bash
pip install langchain-pinecone langchain-openai
```

For LlamaIndex integration:

```bash
pip install llama-index-vector-stores-pinecone
```

## Procedure

### 1. Initialize the client

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_KEY")
```

### 2. Create an index

**Serverless (recommended for most workloads):**

```python
pc.create_index(
    name="my-index",
    dimension=1536,  # Must match your embedding model's output dimension
    metric="cosine",  # Options: "cosine", "euclidean", "dotproduct"
    spec=ServerlessSpec(
        cloud="aws",       # Options: "aws", "gcp", "azure"
        region="us-east-1"
    )
)
```

**Pod-based (for consistent performance / specific hardware):**

```python
from pinecone import PodSpec

pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-east1-gcp",
        pod_type="p1.x1"
    )
)
```

### 3. Connect to an index

```python
index = pc.Index("my-index")
```

### 4. Upsert vectors

**Single upsert:**

```python
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, 0.3],  # Must match index dimension
        "metadata": {
            "text": "Document content",
            "category": "tutorial",
            "timestamp": "2025-01-01"
        }
    }
])
```

**Batch upsert (recommended — 100–200 vectors per batch):**

```python
vectors = [
    {"id": f"vec{i}", "values": embedding, "metadata": metadata}
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas))
]

index.upsert(vectors=vectors, batch_size=100)
```

### 5. Query vectors

**Basic query:**

```python
results = index.query(
    vector=[0.1, 0.2, 0.3],
    top_k=10,
    include_metadata=True,
    include_values=False
)
```

**With metadata filtering:**

```python
results = index.query(
    vector=[0.1, 0.2, 0.3],
    top_k=5,
    filter={"category": {"$eq": "tutorial"}}
)
```

**Namespace query:**

```python
results = index.query(
    vector=[0.1, 0.2, 0.3],
    top_k=5,
    namespace="production"
)
```

**Access results:**

```python
for match in results["matches"]:
    print(f"ID: {match['id']}")
    print(f"Score: {match['score']}")
    print(f"Metadata: {match['metadata']}")
```

### 6. Metadata filtering operators

```python
# Exact match
filter = {"category": "tutorial"}

# Comparison: $gt, $gte, $lt, $lte, $ne
filter = {"price": {"$gte": 100}}

# Logical: $and, $or
filter = {
    "$and": [
        {"category": "tutorial"},
        {"difficulty": {"$lte": 3}}
    ]
}

# In operator
filter = {"tags": {"$in": ["python", "ml"]}}
```

### 7. Namespaces (multi-tenant isolation)

```python
# Upsert into a namespace
index.upsert(
    vectors=[{"id": "vec1", "values": [0.1, 0.2]}],
    namespace="user-123"
)

# Query a specific namespace
results = index.query(
    vector=[0.1, 0.2],
    namespace="user-123",
    top_k=5
)

# List all namespaces and their stats
stats = index.describe_index_stats()
print(stats['namespaces'])
```

### 8. Hybrid search (dense + sparse)

```python
# Upsert with sparse vectors
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, 0.3],  # Dense vector
        "sparse_values": {
            "indices": [10, 45, 123],  # Token IDs
            "values": [0.5, 0.3, 0.8]   # TF-IDF or BM25 scores
        },
        "metadata": {"text": "..."}
    }
])

# Hybrid query — alpha controls the blend
results = index.query(
    vector=[0.1, 0.2, 0.3],
    sparse_vector={
        "indices": [10, 45],
        "values": [0.5, 0.3]
    },
    top_k=5,
    alpha=0.5  # 0 = sparse only, 1 = dense only, 0.5 = hybrid
)
```

### 9. Delete vectors

```python
# Delete by ID
index.delete(ids=["vec1", "vec2"])

# Delete by filter
index.delete(filter={"category": "old"})

# Delete all vectors in a namespace
index.delete(delete_all=True, namespace="test")

# Delete all vectors in the index
index.delete(delete_all=True)
```

### 10. Index management

```python
# List all indices
indexes = pc.list_indexes()

# Describe a specific index
index_info = pc.describe_index("my-index")
print(index_info)

# Get index statistics
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")

# Delete an index (irreversible)
pc.delete_index("my-index")
```

### 11. LangChain integration

```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# Create vector store from documents
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index_name="my-index"
)

# Similarity search
results = vectorstore.similarity_search("query", k=5)

# With metadata filter
results = vectorstore.similarity_search(
    "query",
    k=5,
    filter={"category": "tutorial"}
)

# As a retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
```

### 12. LlamaIndex integration

```python
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

# Connect to Pinecone
pc = Pinecone(api_key="YOUR_KEY")
pinecone_index = pc.Index("my-index")

# Create vector store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Use in LlamaIndex
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

## Examples

### Full RAG pipeline (minimal)

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_KEY")

# Create index if it doesn't exist
if "rag-index" not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name="rag-index",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index("rag-index")

# Upsert documents
index.upsert(vectors=[
    {"id": "doc1", "values": [0.1]*1536, "metadata": {"text": "Hello world", "source": "intro"}},
    {"id": "doc2", "values": [0.2]*1536, "metadata": {"text": "Goodbye world", "source": "outro"}},
])

# Query
results = index.query(
    vector=[0.15]*1536,
    top_k=2,
    include_metadata=True,
    filter={"source": {"$in": ["intro", "outro"]}}
)

for match in results["matches"]:
    print(f"{match['id']}: {match['metadata']['text']} (score: {match['score']:.4f})")
```

## Pitfalls

1. **Dimension mismatch** — The `dimension` parameter at index creation MUST match your embedding model's output. OpenAI `text-embedding-ada-002` and `text-embedding-3-small` produce 1536 dimensions. `text-embedding-3-large` produces 3072. You cannot change dimension after creation — you must delete and recreate the index.

2. **Metric is immutable** — Once an index is created with `cosine`, `euclidean`, or `dotproduct`, you cannot change it without deleting the index. Choose carefully based on your embedding model's training.

3. **Batch size limits** — Upserting more than ~200 vectors per batch can cause timeouts. Stick to 100–200 per batch for reliability.

4. **Namespace deletion is irreversible** — `index.delete(delete_all=True, namespace="test")` removes all vectors in that namespace. There is no undo.

5. **`delete_index` is permanent** — `pc.delete_index("my-index")` destroys the index and all data. Always export/backup important data before deletion.

6. **Free tier limits** — The free tier allows only 1 serverless index and 100K vectors (at 1536 dimensions). Exceeding this requires a paid plan.

7. **Metadata filter overhead** — Metadata filtering adds ~10–20ms to query latency. Index frequently filtered fields for better performance.

8. **Sparse vector indices must be unique** — In `sparse_values`, the `indices` array must contain unique integers. Duplicates will cause errors.

9. **API key exposure** — Never hardcode API keys in source files. Use environment variables (`PINECONE_API_KEY`) or a secrets manager.

10. **Serverless vs Pod-based** — Serverless auto-scales but may have cold start variability. Pod-based provides consistent performance but requires capacity planning. Choose based on your latency requirements.

## Verification

### Verify installation

```bash
pip show pinecone-client
```

Expected output includes the package name and version.

### Verify client connection

```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_KEY")
print(pc.list_indexes())
```

Should return a list of index names (empty list if none created).

### Verify index exists and has data

```python
index = pc.Index("my-index")
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")
```

### Verify query returns results

```python
results = index.query(
    vector=[0.1]*1536,
    top_k=1,
    include_metadata=True
)
assert len(results["matches"]) > 0, "No matches returned"
print(f"Top match: {results['matches'][0]['id']} (score: {results['matches'][0]['score']:.4f})")
```

### Performance check

| Operation | Expected Latency | Notes |
|-----------|-----------------|-------|
| Upsert | ~50–100ms | Per batch of 100 |
| Query (p50) | ~50ms | Depends on index size |
| Query (p95) | ~100ms | SLA target |
| Metadata filter | +10–20ms | Additional overhead on top of base query |

## Related skills

- **chroma** — Self-hosted, open-source vector database for local development
- **faiss** — Offline similarity search library, no metadata filtering
- **weaviate** — Self-hosted vector database with graph relationships and modules

## Resources

- **Website**: https://www.pinecone.io
- **Docs**: https://docs.pinecone.io
- **Console**: https://app.pinecone.io
- **Pricing**: https://www.pinecone.io/pricing
- **Free tier**: 1 serverless index, 100K vectors (1536 dimensions)
