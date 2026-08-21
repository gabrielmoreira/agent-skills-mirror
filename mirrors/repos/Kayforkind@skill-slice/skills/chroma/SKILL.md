---
name: chroma
description: "Runs Chroma (chromadb) locally or as a server: PersistentClient, create_collection/add/query/get, metadata where filters, and LangChain or LlamaIndex vector stores. Use when building self-hosted RAG, notebook semantic search, or embedding documents with metadata. Not for managed Pinecone indexes, FAISS-only kNN without metadata, or Weaviate GraphQL clusters."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [chromadb, sentence-transformers]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [RAG, Chroma, Vector Database, Embeddings, Semantic Search, Open Source, Self-Hosted, Document Retrieval, Metadata Filtering]
---

# Chroma — Open-Source Embedding Database

The AI-native database for building LLM applications with memory. Simple 4-function API: `create_collection`, `add`, `query`, `get`. Scales from notebooks to production clusters.

## When to Use

**Use Chroma when:**
- Building RAG (retrieval-augmented generation) applications
- Need local or self-hosted vector database
- Want open-source solution (Apache 2.0)
- Prototyping in notebooks with semantic search
- Storing embeddings with metadata and filtering by that metadata
- Need document retrieval with vector + full-text search

**Use alternatives instead:**
- **Pinecone**: Managed cloud, auto-scaling, no infrastructure management
- **FAISS**: Pure similarity search, no metadata support
- **Weaviate**: Production ML-native database with GraphQL API
- **Qdrant**: High performance, Rust-based, production filtering

**Metrics:**
- 24,300+ GitHub stars, 1,900+ forks
- v1.3.3+ (stable, weekly releases)
- Apache 2.0 license

## Prerequisites

1. **Python 3.8+** (or Node.js 18+ for JS/TS client)
2. Install Chroma and default embedding dependencies:

```bash
# Python
pip install chromadb

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

3. For LangChain integration: `pip install langchain-chroma langchain-openai`
4. For LlamaIndex integration: `pip install llama-index-vector-stores-chroma`
5. For OpenAI embeddings: `pip install openai` and set `OPENAI_API_KEY` environment variable
6. For HuggingFace embeddings: `pip install huggingface_hub` and set `HF_TOKEN` environment variable

## Procedure

### 1. Create a Client and Collection

```python
import chromadb

# In-memory client (data lost on restart)
client = chromadb.Client()

# Persistent client (data saved to disk)
client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection
collection = client.create_collection(name="my_collection")

# Get existing collection
collection = client.get_collection("my_docs")

# Get or create (safe if collection may not exist)
collection = client.get_or_create_collection("my_docs")

# Delete collection
client.delete_collection("my_docs")
```

### 2. Add Documents

```python
# Add documents with auto-generated embeddings (default: all-MiniLM-L6-v2)
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)

# Add with custom pre-computed embeddings
collection.add(
    embeddings=[[0.1, 0.2, 0.3], [0.3, 0.4, 0.5]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

### 3. Query (Similarity Search)

```python
# Basic query
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# Query with metadata filter (exact match)
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# Query with comparison operators
results = collection.query(
    query_texts=["advanced topics"],
    n_results=3,
    where={"page": {"$gt": 10}}  # Operators: $gt, $gte, $lt, $lte, $ne
)

# Query with logical operators
results = collection.query(
    query_texts=["advanced topics"],
    n_results=3,
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }  # Also supports: $or
)

# Query with $in (contains)
results = collection.query(
    query_texts=["query"],
    where={"tags": {"$in": ["python", "ml"]}}
)

# Access results
print(results["documents"])   # List of matching documents
print(results["metadatas"])    # Metadata for each doc
print(results["distances"])   # Similarity scores
print(results["ids"])         # Document IDs
```

### 4. Get Documents (Without Query)

```python
# Get by IDs
docs = collection.get(ids=["id1", "id2"])

# Get with filters
docs = collection.get(
    where={"category": "tutorial"},
    limit=10
)

# Get all documents
docs = collection.get()
```

### 5. Update Documents

```python
# Update document content and metadata
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)
```

### 6. Delete Documents

```python
# Delete by IDs
collection.delete(ids=["id1", "id2"])

# Delete with filter
collection.delete(where={"source": "outdated"})
```

### 7. Persistent Storage

```python
# Persist to disk — data saved automatically
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection("my_docs")
collection.add(documents=["Doc 1"], ids=["id1"])

# Reload later with same path
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
```

### 8. Custom Embedding Functions

**Default (Sentence Transformers — no API key needed):**
```python
# Uses sentence-transformers all-MiniLM-L6-v2 by default
collection = client.create_collection("my_docs")
```

**OpenAI:**
```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_KEY",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

**HuggingFace:**
```python
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key="YOUR_KEY",
    model_name="sentence-transformers/all-mpnet-base-v2"
)

collection = client.create_collection(
    name="hf_docs",
    embedding_function=huggingface_ef
)
```

**Custom embedding function:**
```python
from chromadb import Documents, EmbeddingFunction, Embeddings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Your embedding logic here
        return embeddings

my_ef = MyEmbeddingFunction()
collection = client.create_collection(
    name="custom_docs",
    embedding_function=my_ef
)
```

### 9. Server Mode (Production)

```bash
# Start Chroma server (terminal)
chroma run --path ./chroma_db --port 8000
```

```python
# Connect to running server
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

# Use as normal
collection = client.get_or_create_collection("my_docs")
```

### 10. LangChain Integration

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# Create Chroma vector store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# Query
results = vectorstore.similarity_search("machine learning", k=3)

# As retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

### 11. LlamaIndex Integration

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import chromadb

# Initialize Chroma
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is machine learning?")
```

## Pitfalls

1. **In-memory client loses data on restart** — Always use `PersistentClient(path=...)` for any data you need to keep. The default `chromadb.Client()` is in-memory only.
2. **Embedding function mismatch** — You cannot query a collection with a different embedding function than the one used to create it. Embeddings from different models are not comparable.
3. **Duplicate IDs silently overwrite** — Adding documents with existing IDs will overwrite the previous content without warning. Use unique IDs to avoid data loss.
4. **Metadata values must be primitives** — Chroma metadata supports `str`, `int`, `float`, and `bool` values only. Lists, dicts, or nested objects are not supported as metadata values.
5. **`$in` operator requires list values** — The `where_document` filter does not support `$in`; only `where` metadata filters support `$in` with a list of values.
6. **Server mode port conflicts** — Ensure port 8000 (or your chosen port) is free before starting `chroma run`. Check with `netstat -ano | findstr :8000` on Windows or `lsof -i :8000` on Linux/macOS.
7. **Telemetry enabled by default** — Set `anonymized_telemetry=False` in Settings to disable telemetry if required.
8. **Large batch adds can timeout** — For collections with 10,000+ documents, add in batches of 1,000-5,000 to avoid memory issues.
9. **No built-in authentication in server mode** — Chroma server does not include authentication. Do not expose it to the public internet without a reverse proxy with auth.
10. **Collection name restrictions** — Collection names must be 3-63 characters, start/end with alphanumeric, and contain only alphanumeric, underscores, or hyphens.

## Verification

1. **Verify installation:**
```bash
python -c "import chromadb; print(chromadb.__version__)"
# Expected output: 1.3.3 or higher
```

2. **Verify basic CRUD operations:**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("test_verify")
collection.add(
    documents=["test document"],
    metadatas=[{"source": "verify"}],
    ids=["id1"]
)
results = collection.query(query_texts=["test"], n_results=1)
assert results["ids"][0][0] == "id1"
assert results["documents"][0][0] == "test document"
print("CRUD verification passed")
```

3. **Verify persistent storage:**
```python
import chromadb

# Write
client = chromadb.PersistentClient(path="./chroma_verify")
collection = client.get_or_create_collection("verify_persist")
collection.add(documents=["persisted doc"], ids=["id1"])

# Read in new client
client2 = chromadb.PersistentClient(path="./chroma_verify")
collection2 = client2.get_collection("verify_persist")
docs = collection2.get(ids=["id1"])
assert docs["documents"][0] == "persisted doc"
print("Persistence verification passed")
```

4. **Verify server mode:**
```bash
# Terminal 1: start server
chroma run --path ./chroma_db --port 8000

# Terminal 2: verify connection
python -c "import chromadb; c = chromadb.HttpClient(host='localhost', port=8000); print(c.heartbeat())"
# Expected output: a nanosecond timestamp integer
```

5. **Verify metadata filtering:**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("filter_verify")
collection.add(
    documents=["doc1", "doc2", "doc3"],
    metadatas=[{"cat": "a"}, {"cat": "b"}, {"cat": "a"}],
    ids=["id1", "id2", "id3"]
)
results = collection.query(query_texts=["doc"], n_results=10, where={"cat": "a"})
assert len(results["ids"][0]) == 2
print("Filter verification passed")
```

## Performance Reference

| Operation | Latency | Notes |
|-----------|---------|-------|
| Add 100 docs | ~1-3s | With default embedding (all-MiniLM-L6-v2) |
| Query (top 10) | ~50-200ms | Depends on collection size |
| Metadata filter | ~10-50ms | Fast with proper indexing |

## Best Practices

1. Use `PersistentClient` — don't lose data on restart
2. Add metadata to every document — enables filtering and tracking
3. Batch operations — add multiple docs at once (1,000-5,000 per batch)
4. Choose the right embedding model — balance speed vs quality
5. Use `where` filters to narrow search space before vector search
6. Use unique, deterministic IDs — avoid collisions and silent overwrites
7. Regular backups — copy the `chroma_db` directory
8. Monitor collection size — scale to server mode for multi-user production
9. Test embedding functions on your domain data — ensure quality
10. Use server mode for production — better for concurrent access

## Resources

- **GitHub**: https://github.com/chroma-core/chroma
- **Docs**: https://docs.trychroma.com
- **Discord**: https://discord.gg/MMeYNTmh3x
- **Version**: 1.3.3+
- **License**: Apache 2.0
