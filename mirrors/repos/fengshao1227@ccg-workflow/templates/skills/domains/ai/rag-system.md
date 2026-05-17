---
name: rag-system
description: RAG 检索增强生成架构。向量数据库、Embedding、检索策略、重排算法、混合检索。当用户提到 RAG、检索增强、向量数据库、Embedding、重排、LangChain、LlamaIndex 时使用。
---

# 🔮 丹鼎秘典 · RAG 系统 (Retrieval-Augmented Generation)

## RAG 架构

```
查询 → Embedding → 向量检索 → 重排 → 上下文注入 → LLM 生成
  │         │           │         │          │            │
  └─ 改写 ──┴─ 混合检索 ─┴─ 相关性 ─┴─ 压缩 ──┴─ 答案 + 引用
```

### 核心流程
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 文档加载与切分
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = TextLoader("docs.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", ".", " "]
)
chunks = splitter.split_documents(documents)

# 2. 向量化与存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# 3. 检索与生成
llm = ChatOpenAI(model="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

result = qa_chain({"query": "什么是 RAG？"})
print(result["result"])
```

## 向量数据库对比

| 数据库 | 类型 | 索引算法 | 适用场景 | 部署 |
|--------|------|----------|----------|------|
| Pinecone | 托管 | HNSW | 生产级、高并发 | 云端 |
| Weaviate | 开源 | HNSW | 多模态、GraphQL | 自托管/云 |
| Qdrant | 开源 | HNSW | 高性能、过滤 | 自托管/云 |
| Chroma | 开源 | HNSW | 快速原型、本地 | 本地/内存 |
| Milvus | 开源 | IVF/HNSW | 大规模、分布式 | 自托管 |
| Faiss | 库 | IVF/PQ | 研究、离线 | 本地 |

### Pinecone 示例
```python
import pinecone
from langchain.vectorstores import Pinecone

pinecone.init(api_key="YOUR_KEY", environment="us-west1-gcp")

index_name = "rag-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI ada-002
        metric="cosine"
    )

vectorstore = Pinecone.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=index_name
)
```

### Qdrant 示例
```python
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant

client = QdrantClient(host="localhost", port=6333)

vectorstore = Qdrant.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="knowledge_base",
    client=client
)

# 带过滤的检索
results = vectorstore.similarity_search(
    query="RAG 架构",
    k=5,
    filter={"source": "technical_docs"}
)
```

## Embedding 模型选择

### 模型对比
| 模型 | 维度 | 性能 | 成本 | 适用场景 |
|------|------|------|------|----------|
| OpenAI ada-002 | 1536 | 高 | 中 | 通用、多语言 |
| Cohere embed-v3 | 1024 | 高 | 中 | 多语言、压缩 |
| BGE-large-zh | 1024 | 高 | 免费 | 中文优化 |
| E5-large-v2 | 1024 | 中 | 免费 | 开源、通用 |
| text2vec-base | 768 | 中 | 免费 | 中文、轻量 |

### 本地 Embedding
```python
from langchain.embeddings import HuggingFaceEmbeddings

# BGE 中文模型
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True}
)

# 批量编码
texts = ["文档1", "文档2", "文档3"]
vectors = embeddings.embed_documents(texts)

# 查询编码（带指令）
query_vector = embeddings.embed_query("为这个句子生成表示")
```

### 多模态 Embedding
```python
from langchain.embeddings import OpenAIEmbeddings

# CLIP 图文联合
class MultiModalEmbedding:
    def __init__(self):
        self.text_model = OpenAIEmbeddings()
        self.image_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

    def embed_image(self, image_path: str):
        image = Image.open(image_path)
        return self.image_model.encode_image(image)

    def embed_text(self, text: str):
        return self.text_model.embed_query(text)
```

## 检索策略

### Dense 检索（向量）
```python
# 余弦相似度检索
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# MMR（最大边际相关性）- 多样性
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
)

# 相似度阈值过滤
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.8, "k": 5}
)
```

### Sparse 检索（BM25）
```python
from langchain.retrievers import BM25Retriever

# BM25 关键词检索
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5

results = bm25_retriever.get_relevant_documents("RAG 系统")
```

### Hybrid 混合检索
```python
from langchain.retrievers import EnsembleRetriever

# 向量 + BM25 混合
ensemble_retriever = EnsembleRetriever(
    retrievers=[vectorstore.as_retriever(), bm25_retriever],
    weights=[0.6, 0.4]  # 向量权重 60%，BM25 权重 40%
)

results = ensemble_retriever.get_relevant_documents("查询")
```

### 多路召回
```python
class MultiRecallRetriever:
    def __init__(self, vector_store, bm25_retriever, graph_retriever):
        self.retrievers = {
            "vector": vector_store.as_retriever(search_kwargs={"k": 10}),
            "bm25": bm25_retriever,
            "graph": graph_retriever
        }

    def retrieve(self, query: str, top_k: int = 5):
        all_docs = []
        for name, retriever in self.retrievers.items():
            docs = retriever.get_relevant_documents(query)
            all_docs.extend([(doc, name) for doc in docs])

        # 去重 + 重排
        unique_docs = self._deduplicate(all_docs)
        return self._rerank(unique_docs, query)[:top_k]
```

## 重排算法

### Cross-Encoder 重排
```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query: str, documents: list, top_k: int = 5):
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.predict(pairs)

        # 按分数排序
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked[:top_k]]

# 使用
reranker = Reranker()
initial_docs = vectorstore.similarity_search(query, k=20)
final_docs = reranker.rerank(query, initial_docs, top_k=5)
```

### Cohere Rerank API
```python
import cohere

co = cohere.Client("YOUR_API_KEY")

def cohere_rerank(query: str, documents: list, top_k: int = 5):
    results = co.rerank(
        query=query,
        documents=[doc.page_content for doc in documents],
        top_n=top_k,
        model="rerank-multilingual-v2.0"
    )

    return [documents[r.index] for r in results]
```

### LLM 重排
```python
from langchain.chat_models import ChatOpenAI

def llm_rerank(query: str, documents: list, top_k: int = 3):
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = f"""给定查询和文档列表，按相关性排序（1最相关）。

查询: {query}

文档:
{chr(10).join([f"{i+1}. {doc.page_content[:200]}" for i, doc in enumerate(documents)])}

输出格式: 1,3,2,5,4（仅数字和逗号）"""

    ranking = llm.predict(prompt).strip().split(',')
    return [documents[int(i)-1] for i in ranking[:top_k]]
```

## 文档切分策略

### 递归切分
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", "。", ".", " ", ""]
)
```

### 语义切分
```python
from langchain.text_splitter import SemanticChunker

semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # 或 "standard_deviation"
    breakpoint_threshold_amount=95
)

chunks = semantic_splitter.split_text(long_text)
```

### Markdown 结构化切分
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
chunks = markdown_splitter.split_text(markdown_text)
```

## 查询优化

### 查询改写
```python
from langchain.prompts import ChatPromptTemplate

query_rewrite_prompt = ChatPromptTemplate.from_template("""
将用户查询改写为更适合检索的形式。

原始查询: {query}

改写要求:
1. 补全省略信息
2. 扩展同义词
3. 拆分复合问题

改写后查询:""")

def rewrite_query(query: str):
    chain = query_rewrite_prompt | llm
    return chain.invoke({"query": query}).content
```

### 多查询生成
```python
from langchain.retrievers.multi_query import MultiQueryRetriever

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# 自动生成 3-5 个变体查询
results = multi_query_retriever.get_relevant_documents("RAG 是什么？")
```

### HyDE（假设文档嵌入）
```python
def hyde_retrieval(query: str):
    # 1. 让 LLM 生成假设答案
    hyde_prompt = f"请详细回答: {query}"
    hypothetical_doc = llm.predict(hyde_prompt)

    # 2. 用假设答案检索
    results = vectorstore.similarity_search(hypothetical_doc, k=5)
    return results
```

## 上下文压缩

### LLM 压缩器
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 10})
)

# 检索 10 个文档，压缩后返回最相关片段
compressed_docs = compression_retriever.get_relevant_documents(query)
```

### Embedding 过滤
```python
from langchain.retrievers.document_compressors import EmbeddingsFilter

embeddings_filter = EmbeddingsFilter(
    embeddings=embeddings,
    similarity_threshold=0.76
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20})
)
```

## 完整 RAG Pipeline

### LangChain 实现
```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# 对话式 RAG
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory=memory,
    return_source_documents=True,
    verbose=True
)

# 多轮对话
result1 = qa_chain({"question": "什么是 RAG？"})
result2 = qa_chain({"question": "它有什么优势？"})  # 自动引用上下文
```

### LlamaIndex 实现
```python
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding

# 服务上下文
service_context = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-4", temperature=0),
    embed_model=OpenAIEmbedding()
)

# 构建索引
index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

# 查询引擎
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"  # 或 "tree_summarize", "refine"
)

response = query_engine.query("什么是 RAG？")
print(response.response)
print(response.source_nodes)  # 引用来源
```

## 高级 RAG 模式

### Self-RAG（自我反思）
```python
class SelfRAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def query(self, question: str):
        # 1. 判断是否需要检索
        need_retrieval = self._check_retrieval_need(question)

        if not need_retrieval:
            return self.llm.predict(question)

        # 2. 检索
        docs = self.retriever.get_relevant_documents(question)

        # 3. 生成答案
        answer = self._generate_with_docs(question, docs)

        # 4. 自我评估
        if self._verify_answer(question, answer, docs):
            return answer
        else:
            # 重新检索或生成
            return self._fallback_generate(question)
```

### RAPTOR（递归摘要）
```python
from langchain.chains.summarize import load_summarize_chain

def raptor_indexing(documents, levels=3):
    current_docs = documents
    all_summaries = []

    for level in range(levels):
        # 聚类
        clusters = cluster_documents(current_docs, n_clusters=10)

        # 每个簇生成摘要
        summaries = []
        for cluster in clusters:
            summary = summarize_chain.run(cluster)
            summaries.append(summary)

        all_summaries.extend(summaries)
        current_docs = summaries

    # 索引原文档 + 各层摘要
    vectorstore.add_documents(documents + all_summaries)
```

## 工具与框架

| 工具 | 类型 | 特点 |
|------|------|------|
| LangChain | 框架 | 生态丰富、组件化 |
| LlamaIndex | 框架 | 索引优化、查询引擎 |
| Haystack | 框架 | 生产级、Pipeline |
| Pinecone | 向量库 | 托管、高性能 |
| Qdrant | 向量库 | 开源、过滤强 |
| Weaviate | 向量库 | 多模态、GraphQL |
| Cohere | API | Embedding + Rerank |

## 最佳实践

- ✅ 文档切分：chunk_size 500-1500，overlap 10-20%
- ✅ 检索数量：初召回 10-20，重排后 3-5
- ✅ 混合检索：向量 + BM25 权重 6:4 或 7:3
- ✅ 元数据过滤：时间、来源、类型
- ✅ 引用来源：返回 source_documents
- ✅ 缓存：相同查询缓存结果
- ✅ 监控：检索延迟、相关性、答案质量
- ❌ 避免：chunk 过大/过小、无重排、无压缩

---
