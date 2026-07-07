# RAG 检索增强生成

> RAG（Retrieval-Augmented Generation）是解决 LLM 知识局限和幻觉问题的核心方案。通过检索外部知识库来增强生成质量，已成为企业级 AI 应用的事实标准。

---

## 一、RAG 概述

### 1. 为什么需要 RAG？

LLM 存在三个天然缺陷：

| 问题 | 表现 | RAG 的解决 |
|------|------|-----------|
| **知识截止** | 模型训练后新知识不可知 | 从最新文档中检索 |
| **幻觉（Hallucination）** | 模型编造事实 | 基于检索结果生成，有据可依 |
| **领域知识不足** | 通用模型缺乏垂直领域深度 | 注入企业内部文档/知识库 |

### 2. 核心架构

```
用户提问
    ↓
┌─────────────────────────────────────────────────┐
│                  Query 处理                       │
│  原始查询 → 查询重写/扩展 → 多路检索              │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  检索 (Retrieval)                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ 向量检索  │   │ 关键词检索 │   │ 混合检索  │    │
│  │ (语义)   │   │ (BM25)   │   │ (合并)   │    │
│  └──────────┘   └──────────┘   └──────────┘    │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  增强 (Augmentation)              │
│  检索结果 → 去重/排序 → 重排序(Reranker)         │
│  → 构建 Prompt（含上下文 + 指令）                  │
└─────────────────────┬───────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  生成 (Generation)                │
│  LLM → 基于上下文生成回答 → 引用溯源               │
└─────────────────────────────────────────────────┘
                      ↓
                   回答输出
```

### 3. RAG vs 微调（Fine-tuning）

| 对比维度 | RAG | Fine-tuning | 最佳组合 |
|---------|-----|-------------|---------|
| **知识更新** | 实时更新文档即可 | 需重新训练 | RAG 做实时知识，FT 做指令遵循 |
| **幻觉控制** | 较好（有检索依据） | 仍可能幻觉 | RAG 兜底 + FT 优化输出格式 |
| **实施成本** | 低（无需 GPU 训练） | 高（需要标注数据+算力） | 从 RAG 开始，必要时 FT |
| **推理成本** | 略高（检索+生成） | 同基础模型 | 混合策略 |
| **适用场景** | 知识密集型问答 | 风格/格式/行为对齐 | 企业知识库 = RAG + 少 FT |

::: tip 选型建议
- 知识更新频繁 → **RAG**（如内部知识库、新闻问答）
- 需要特定输出格式/风格 → **Fine-tuning**（如客服角色、代码生成）
- **两者互补**：生产中常 RAG + FT 一起用
:::

---

## 二、文档处理（Ingestion）

### 1. 文档加载与解析

| 文档类型 | 加载工具 | 注意点 |
|---------|---------|-------|
| PDF | PyMuPDF、Unstructured、LlamaParse | 表格/图片/多栏布局、OCR 质量 |
| Word/PPT | python-docx、unstructured | 嵌入图片、复杂表格 |
| HTML | BeautifulSoup、Trafilatura | 去除导航/广告等无用标签 |
| 代码 | 按语言分块 | 保留缩进和注释结构 |
| 数据库 | 结构化查询 | 考虑 Schema 上下文 |

```python
# 文档加载（非结构化文档）
from langchain_community.document_loaders import PyMuPDFLoader
loader = PyMuPDFLoader("report.pdf")
documents = loader.load()  # 每页一个 Document

# 更好的选择：Unstructured（支持更多格式，但更慢）
from langchain_community.document_loaders import UnstructuredFileLoader
loader = UnstructuredFileLoader("report.pdf", mode="elements")
# mode="elements" 会按段落/标题/表格分离，保留元数据
```

### 2. 文档切分（Chunking）

切分是 RAG 中**最容易踩坑也影响最大的环节**之一。

#### 切分策略对比

| 策略 | 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **固定大小** | 按字符/token 数切 | 简单直接 | 断句、丢失语义 | 快速原型 |
| **递归分割** | 按层级分隔符切(段落→句→词) | 语义完整 | 可能过长或过短 | **通用推荐** |
| **语义分割** | 检测主题变化点 | 语义完整、块间独立 | 开销大、边界未必准确 | 长文档（论文、书籍） |
| **LLM 分割** | LLM 识别自然边界 | 质量最高 | 慢、贵 | 高质量知识库 |
| **特定格式** | 按 Markdown 标题/代码函数切 | 结构完整 | 格式依赖 | 技术文档/代码库 |

```python
# 递归分割（生产中最常用）
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,          # 每块大小（按字符或 token）
    chunk_overlap=50,        # 重叠窗口（跨块上下文）
    separators=["\n\n", "\n", "。", ".", " ", ""],  # 分隔符优先级
    length_function=len,
)
chunks = text_splitter.split_documents(documents)
```

```python
# 语义分割（基于嵌入相似度变化）
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

semantic_splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # 相似度百分位断点
)
chunks = semantic_splitter.split_documents(documents)
```

#### 切分大小的选择

```python
# 根据检索场景选择 chunk_size
# 经验法则：
#  - 问答/事实查询：256~512 tokens（精确匹配）
#  - 摘要/归纳：1024~2048 tokens（需要全貌）
#  - 代码检索：按函数/类分割（500~1500 tokens）

chunk_size_guidelines = {
    "精确问答（Q&A）":      "256-512 tokens",
    "摘要生成":             "1024-2048 tokens",
    "代码检索":             "500-1500 tokens（按函数）",
    "论文/长文档问答":      "512-1024 tokens + 层级摘要",
}
```

::: warning 切分踩坑

**1. chunk_size 设太小 → 上下文碎片**
- 检索到的片段信息不全，LLM 无法回答
- 调大 chunk_size 或设合理的 chunk_overlap（10~20%）

**2. chunk_size 设太大 → 噪声引入**
- 大量无关内容进入 context window，稀释关键信息
- LLM 注意力被分散，答案质量下降

**3. 无差别的切分策略**
- Markdown 文档应按标题层级分割（保留文档结构）
- 代码文件应按函数/类分割（保留语法结构）
- 表格应整表作为一块（不要跨行切）

**4. 忽略元数据**
- 未保留来源页码、文件名、章节标题
- 导致 LLM 无法引用（无法回答"这个结论来自哪里"）
:::

### 3. 向量化（Embedding）

#### 主流 Embedding 模型

| 模型 | 维度 | 最大长度 | 特点 | 适用场景 |
|------|------|---------|------|---------|
| `text-embedding-3-small` (OpenAI) | 1536 | 8191 tokens | 价格低、性能好 | **通用推荐** |
| `text-embedding-3-large` (OpenAI) | 3072 | 8191 tokens | 精度更高 | 高精度需求 |
| `bge-large-zh-v1.5` (BAAI) | 1024 | 512 tokens | **中文优化** | **中文场景推荐** |
| `mulit-qa-mpnet-base-dot-v1` | 768 | 512 tokens | 句子嵌入强 | 英文问答 |
| `text2vec-large-chinese` | 1024 | 512 tokens | 国产开源 | 中文场景 |
| `m3e-base` | 768 | 512 tokens | 轻量中文 | 中文、部署受限 |
| `gte-Qwen2-1.5B-instruct` | 1536 | 8192 tokens | 多语言强 | 最新推荐 |

```python
# LangChain 中使用 Embedding
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# OpenAI（云端）
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,  # 可通过 dimensions 降维，减少存储（性能略降）
)

# 本地部署（推荐中文场景用 BGE）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True},  # 归一化后可直接用内积
)
```

::: tip Embedding 选择建议
- 中文文档优先选 **BGE** 或 **m3e**（对中文语义理解更好）
- 多语言场景（中英混合）选 **gte-Qwen2** 或 **text-embedding-3**
- 向量维度越高，检索精度一般越高，但存储和计算成本也上升
- 很多模型支持**降维输出**（如 text-embedding-3 可以设 `dimensions=256`）
- **一定要归一化**（normalize），否则余弦相似度结果不稳定
:::

---

## 三、向量数据库

### 1. 向量数据库选型

| 数据库 | 部署方式 | 索引算法 | 规模上限 | 特点 |
|--------|---------|---------|---------|------|
| **Milvus** | 分布式 | IVF/IVF-PQ/HNSW | 百亿级 | 功能最强，运维复杂 |
| **Qdrant** | 分布式/单机 | HNSW | 十亿级 | Rust 实现，性能好 |
| **Weaviate** | 单机/云 | HNSW | 千万级 | 内置模块（向量化/重排序） |
| **Pinecone** | 云服务 | 自动 | 十亿级 | 全托管，免运维 |
| **Chroma** | 嵌入式 | HNSW | 百万级 | **开发友好，推荐原型** |
| **FAISS** | 嵌入式 | IVF/HNSW | 十亿级 | 内存索引，无服务端 |
| **pgvector** | PostgreSQL 插件 | IVFFlat/HNSW | 千万级 | 与业务数据共存 |
| **Elasticsearch** | 分布式 | HNSW | 十亿级 | 天然支持关键词+向量混合 |

```python
# 快速原型：Chroma（零配置，嵌入运行）
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db",  # 持久化到磁盘
)

# 生产环境：pgvector（与业务数据共存，支持 SQL 过滤）
from langchain_postgres import PGVector

vector_store = PGVector.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    connection="postgresql+psycopg://user:pass@host:5432/db",
    collection_name="knowledge_base",
    pre_delete_collection=False,
)

# 高性能场景：Milvus
from langchain_milvus import Milvus

vector_store = Milvus.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(),
    connection_args={"host": "localhost", "port": "19530"},
)
```

### 2. 向量索引算法

| 算法 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **FLAT（暴力搜索）** | 全量比对 | 100% 准确 | 极慢（十万级以上不可用） | 小数据集(<1w) |
| **IVF** | 聚类+倒排 | 快，内存友好 | 召回率略低 | 百万级，追求速度 |
| **HNSW** | 分层可导航小世界图 | 快+准，业界最强 | 内存占用大 | **通用推荐** |
| **IVF-PQ** | 聚类+量化压缩 | 极省内存 | 精度损失 | 十亿级，内存受限 |

```python
# FAISS 索引类型选择
import faiss

# 百万级以下：HNSW（精度高）
index = faiss.IndexHNSWFlat(dimension, 32)  # 32 = 邻居数

# 百万级以上：IVF（速度快）
index = faiss.IndexIVFFlat(quantizer, dimension, 100)  # 100 = 聚类数
index.train(vectors)
```

::: warning 索引选择经验
- 数据量 < 10 万 → 不需要复杂索引，FLAT 即可
- 数据量 10 万~1000 万 → **HNSW** 是首选
- 数据量 > 1000 万 → IVF 系列，或 Milvus/Qdrant 分布式方案
- **HNSW 参数调优**：
  - `M`（邻居数，默认 16）：越大召回越高，内存越大
  - `efConstruction`（构建搜索范围，默认 200）：越大索引质量越高，构建越慢
  - `efSearch`（检索搜索范围）：越大召回越高，查询越慢
:::

### 3. 混合检索（Hybrid Search）

单纯向量检索在关键词精确匹配上不如 BM25。**混合检索 = 向量检索 + 关键词检索** 是目前工业界的最佳实践。

```
            ┌──────────────┐
            │  用户查询 QA   │
            └──────┬───────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌──────────┐         ┌──────────┐
   │ 向量检索  │         │ BM25     │
   │ (语义)   │         │ (关键词)  │
   └────┬─────┘         └────┬─────┘
        │                    │
   ┌────▼────────────────────▼────┐
   │      RRF 合并 (Reciprocal    │
   │      Rank Fusion)            │
   └────────────┬─────────────────┘
                ▼
         ┌──────────────┐
         │   重排序器    │
         │  (Reranker)  │
         └──────┬───────┘
                ▼
           Top-K 结果
```

```python
# Elasticsearch 混合检索（推荐生产方案）
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# 创建索引：配置 dense_vector + 关键词字段
es.indices.create(index="knowledge", body={
    "mappings": {
        "properties": {
            "content": {"type": "text", "analyzer": "ik_max_word"},
            "content_vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
})

# Lucene 版 HNSW + BM25 原生混合（ES 8.12+）
query_vector = embedding_model.encode(query)

# 混合检索：kNN + BM25（RRF 合并）
response = es.search(index="knowledge", body={
    "query": {
        "bool": {
            "should": [
                {"match": {"content": {"query": query, "boost": 0.3}}},   # BM25
                {"knn": {"content_vector": {                              # 向量
                    "vector": query_vector.tolist(),
                    "k": 10
                }}}
            ]
        }
    },
    "size": 10,
    "rank": {"rrf": {"rank_constant": 60}}  # RRF 融合
})
```

| 方法 | 原理 | 推荐度 |
|------|------|--------|
| **RRF（Reciprocal Rank Fusion）** | `score = Σ 1/(k + rank)` 简单有效 | ⭐⭐⭐⭐⭐ |
| **加权平均** | `score = α·vector_score + (1-α)·keyword_score` | ⭐⭐⭐ |
| **学习排序（LTR）** | 用训练数据学加权 | ⭐⭐⭐⭐ |
| **Cascaded** | 先用向量检索 Top-N，再用关键词精排 | ⭐⭐⭐ |

---

## 四、检索优化策略

### 1. 查询重写（Query Rewriting）

用户原始查询往往简短、模糊，直接检索效果差。

```python
# 查询重写：让 LLM 优化原始查询
query_rewrite_prompt = """
你是一个搜索专家。请将用户的原始问题改写成更适合检索的多个子问题。
要求：
1. 分解复杂问题为多个简单子问题
2. 补充缺失的关键上下文
3. 使用专业术语替代口语化表达

原始问题：{original_query}
改写后的检索查询（每行一个，不要编号）：
"""

# 示例
# 原始问题："Spring Boot 事务怎么不管用了？"
# 改写后：
#   Spring @Transactional 注解失效原因
#   Spring AOP 同类方法调用事务不生效
#   Transaction rollbackFor 配置
```

### 2. 查询扩展（HyDE）

HyDE（Hypothetical Document Embeddings）：先生成假设性答案，再用答案检索。

```
用户查询 → LLM 生成假设答案 → 用假设答案做 Embedding → 检索相似文档
    
原理：假设答案的语义空间更接近目标文档（因为都是"陈述"而非"提问"）
适用场景：查询语言与文档语言差异大（如口语提问 vs 技术文档）
```

```python
from langchain.chains import HypotheticalDocumentEmbedder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# HyDE：先生成假设文档，再用文档的嵌入检索
base_embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(temperature=0)

hyde_embeddings = HypotheticalDocumentEmbedder.from_llm(
    llm=llm,
    base_embeddings=base_embeddings,
    prompt_key="web_search",  # 预定义的假设文档生成模板
)

# 与普通 Embedding 对比
query = "Spring 事务不生效的常见原因"
vector_embedding = base_embeddings.embed_query(query)   # 直接用查询嵌入
hyde_embedding = hyde_embeddings.embed_query(query)      # 先生成假设文档再嵌入
```

### 3. 重排序（Reranking）

向量检索的 Top-K 结果中，前几个不一定最相关。用一个**交叉编码器（Cross-Encoder）** 对结果重新排序，显著提升精度。

```
向量检索: Top-50 → Reranker 重新打分 → Top-5
```

| 模型 | 特点 | 语言 | 速度 |
|------|------|------|------|
| `BAAI/bge-reranker-v2-m3` | 精度高、支持多语言 | 中/英/多语言 | 中 |
| `BAAI/bge-reranker-large` | 高精度 | 中/英 | 慢 |
| `cohere rerank` | 云服务，免部署 | 多语言 | 快 |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | 轻量 | 英文 | 极快 |

```python
# LangChain 集成 Reranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker

# 初始化 reranker
reranker = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")

# 压缩检索器：先检索再重排序
compressor = CrossEncoderReranker(
    model=reranker,
    top_n=5  # 只保留 Top-5
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever(search_kwargs={"k": 20})
)

# 检索：先取 Top-20，reranker 精排后保留 Top-5
docs = compression_retriever.invoke("Spring 事务隔离级别有哪些？")
```

::: tip 为什么需要 Reranker？
- 向量检索是粗排（双编码器）：文档和查询独立编码 → 余弦相似度
- Reranker 是精排（交叉编码器）：文档和查询一起编码 → 深度交互
- 后者精度高但慢：向量检索可处理百万级，Reranker 只处理 Top-50~100
- **典型策略：粗排（向量）取 Top-50 → 精排（交叉编码器）取 Top-5**
:::

### 4. 多路召回

不同检索方式各有优劣，多路召回后合并结果。

```
                   ┌──────────┐
                   │ 用户查询  │
                   └────┬─────┘
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌───────────┐ ┌───────────┐ ┌───────────┐
   │  向量检索  │ │  BM25     │ │  SQL 查询 │
   │ (语义)    │ │ (关键词)  │ │ (结构化) │
   └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
         └──────────────┴──────────────┘
                        ▼
                 ┌──────────────┐
                 │   RRF 合并   │
                 │  + Reranker  │
                 └──────┬───────┘
                        ▼
                   Top-K 结果
```

---

## 五、高级 RAG 模式

### 1. 多轮对话 RAG

```python
# 对话式 RAG（带历史上下文）
prompt_template = """
你是一个基于知识库的问答助手。

历史对话：
{chat_history}

检索到的相关文档：
{context}

请基于上述文档回答用户的问题。如果文档中没有相关信息，请直接说不知道，不要编造。
用户问题：{question}
"""
```

**挑战**：
- 用户的引用（"上面提到的那个方案"）需要消解
- 对话历史过长超过 context window
- 解决方案：**对话压缩**（LLM 总结历史）或 **Sliding Window**

### 2. Agentic RAG

RAG 与 Agent 结合，让 LLM 自主决定何时检索、检索什么。

```python
# LangGraph Agent + RAG 示例
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List
    documents: List
    need_retrieval: bool

def should_retrieve(state):
    """Agent 自主判断是否需要检索"""
    messages = state["messages"]
    last_msg = messages[-1].content
    
    # 使用 LLM 判断是否需要查询知识库
    response = judge_llm.invoke(
        f"用户说：{last_msg}\n是否需要查询知识库来回答？回答 YES 或 NO"
    )
    return "retrieve" if "YES" in response else "generate"

# 高级模式：Agent 可以自主
# 1. 重写查询 → 2. 选择检索源 → 3. 阅读结果 → 4. 如果需要再检索 → 5. 生成回答
```

**Agentic RAG 常见模式**：

| 模式 | 流程 | 适用场景 |
|------|------|---------|
| **Corrective RAG** | 检索 → 评估相关性 → 不相关则重写查询 → 重试 | 检索结果不稳定时 |
| **Self-RAG** | 检索 → 生成 → 自检 → 是否需要更多检索 | 需要高可靠性 |
| **Adaptive RAG** | 判断问题难度 → 简单=直接生成, 中等=单次检索, 复杂=多步检索 | 混合问题类型 |
| **CRAG (Corrective RAG)** | 检索 → 评分 → 好→生成, 差→Web搜索 | 知识库覆盖不足时 |

### 3. Graph RAG

微软推出的基于知识图谱的 RAG 方案。

```
传统 RAG：                               Graph RAG：
分块 → Embedding → 检索                  分块 → Entity/Relation 提取 → 知识图谱 → 社区总结 → 检索

适用：事实型问答（"XX 公司的 CEO 是谁？"）    适用：关系推理（"XX 公司与 YY 公司有哪些合作？"）
                                         全局性问题（"报告中讨论了哪些主要风险？"）
```

```python
# Graph RAG 思路（简化）
# 1. 提取实体和关系
entities = llm.extract("报告中提到的所有实体（人名、公司、产品）及其关系")

# 2. 构建知识图谱
graph.add_entity("DeepMind")
graph.add_entity("AlphaFold")
graph.add_relation("DeepMind", "开发", "AlphaFold")

# 3. 检索时：向量检索 + 图遍历
relevant_chunks = vector_search(query)
graph_context = graph.query_traversal(entities_in_query)
combined_context = merge(relevant_chunks, graph_context)
```

---

## 六、生产化实践

### 1. RAG 评估体系

| 评估维度 | 指标 | 说明 |
|---------|------|------|
| **检索精度** | Recall@K、MRR、NDCG | 检索到的文档是否包含正确答案 |
| **生成质量** | 忠实度（Faithfulness）、答案相关度（Answer Relevance） | 回答是否基于检索结果 |
| **系统性能** | P50/P99 延迟、QPS | 检索+生成的端到端耗时 |
| **覆盖率** | 未回答率（无法回答问题的比例） | 知识库覆盖是否全面 |

```python
# RAGAS 评估框架
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)

# 构建测试集
test_dataset = {
    "question": ["Spring 事务隔离级别有哪些？"],
    "answer": ["READ_UNCOMMITTED, READ_COMMITTED, ..."],
    "contexts": [["Spring 支持四种隔离级别..."]],
    "ground_truth": ["四种：READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE"]
}

# 评估
result = evaluate(test_dataset, metrics=[
    faithfulness,      # 答案忠���于上下文
    answer_relevancy,  # 答案相关度
    context_recall,    # 上下文召回率
    context_precision, # 上下文精确率
])
```

### 2. 延迟优化

```
RAG 请求耗时分解（典型值）：

┌──────────────────────┐
│   查询 Embedding     │ ~50ms  (调用一次 Embedding 模型)
├──────────────────────┤
│   向量检索 Top-K     │ ~10ms  (HNSW 索引, 百万级)
├──────────────────────┤
│   Reranker 重排序    │ ~200ms (交叉编码器 Top-50 推理)
├──────────────────────┤
│   LLM 生成           │ ~1-3s  (取决于输出长度和模型)
├──────────────────────┤
│   端到端              │ ~1.3-3.5s
└──────────────────────┘
```

| 优化手段 | 效果 | 代价 |
|---------|------|------|
| **嵌入缓存**（query 级别的 cache） | 减少 Embedding 调用 | 命中率依赖查询分布 |
| **Batch 检索** | 多条查询合并一次检索 | 批处理延迟折中 |
| **减少 Reranker Top-N** | 降低 Reranker 耗时 | 召回率略降 |
| **LLM 流式输出** | 首 token 延迟大幅降低 | 用户体验提升 |
| **文档摘要缓存** | 减少 LLM 上下文处理 | 额外存储 |
| **异步 ingestion** | 文档更新不影响检索 | 一致性窗口 |

### 3. 生产架构

```
                    ┌──────────┐
                    │  用户请求  │
                    └─────┬────┘
                          │
               ┌──────────▼──────────┐
               │   API Gateway       │
               │  (认证/限流/路由)    │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │   RAG Orchestrator   │
               │  - Query Rewrite    │
               │  - Retrieval Logic  │
               │  - Prompt Builder   │
               └──────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Embedding   │  │  向量数据库   │  │  重排序器    │
│  Service     │  │  (Milvus)    │  │  (Reranker)  │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
               ┌─────────▼──────────┐
               │    LLM Service     │
               │  (OpenAI/本地模型)  │
               └────────────────────┘
```

### 4. 常见踩坑清单

::: danger RAG 生产踩坑

| # | 问题 | 现象 | 原因 | 解决方案 |
|---|------|------|------|---------|
| 1 | **检索不到相关文档** | LLM 说"不知道"或编造 | chunk_size 不合适/Embedding 模型差 | 调大 chunk/重叠/换 Embedding |
| 2 | **检索到不相关文档** | 答案偏离 | 向量检索语义漂移 | 加 Reranker / 混合检索 |
| 3 | **LLM 不遵循检索结果** | 仍然幻觉 | Prompt 指令不够强 | 加强 System Prompt，few-shot |
| 4 | **Context Window 超长** | LLM 报错 | 检索片段太多/太长 | 限制 Top-K + chunk_size |
| 5 | **更新文档后查询没变** | 知识库不一致 | 向量库未重新索引 | 触发异步重建索引 |
| 6 | **中文分词不准** | 关键词检索效果差 | 未用中文分词器 | 使用 IK Analyzer 等 |
| 7 | **高并发后检索变慢** | 查询超时 | 索引未优化/资源不足 | 加索引缓存/扩容 |
| 8 | **多轮对话上下文消解** | 用户说"它"无法理解 | 未做历史 query 重写 | 加 Query Rewrite 步骤 |

**关键教训**：
- **RAG 的瓶颈通常在检索，不在生成**。优化检索效果（chunking、reranker、混合检索）是 ROE 最高的投入
- **先建立离线评估，再上线优化**。没有评估指标，优化方向就是盲目的
- **embedding 模型选择远比你想象的重要**。中文场景用 BGE 比用 text-embedding-ada-002 好很多
- **始终加引用溯源**：让 LLM 在每个回答后标注来源文档、页码，便于排查
:::

---

## 七、面试高频问题

### Q1：RAG 是什么？核心流程是怎样的？

**答**：
RAG（检索增强生成）是一种通过检索外部知识库来增强 LLM 生成质量的架构。核心流程：

1. **Ingestion**：文档 → 切分 → Embedding → 存入向量库
2. **Retrieval**：用户查询 → Embedding → 向量检索 → 重排序
3. **Generation**：查询 + 检索结果 → Prompt → LLM → 回答

相比纯 LLM 方案，RAG 解决了知识截止、幻觉、领域知识不足三大问题。

### Q2：如何选择 chunk_size？过大或过小有什么问题？

**答**：
chunk_size 的选择取决于检索场景：
- 精确事实问答：256~512 tokens（精确命中）
- 摘要归纳：1024~2048 tokens（需要全貌）
- 代码检索：按函数/类分割

**chunk_size 太小** → 上下文碎片，信息不完整 → LLM 无法回答
**chunk_size 太大** → 噪声稀释关键信息 → 回答不精确

建议设 **10~20% 的 chunk_overlap** 保证跨块上下文连续，并优先使用 **语义分割** 而非固定字符分割。

### Q3：混合检索为什么比纯向量检索好？

**答**：
向量检索（语义搜索）对同义词、近义表达效果好，但在精确关键词匹配上不如 BM25。混合检索 = 向量检索 + 关键词检索 + RRF 融合，同时获得语义理解和精确匹配的能力。

典型场景：用户搜"Spring 事务隔离级别"，向量检索找到"事务隔离性级别"，BM25 精确匹配"隔离级别"，两者互补，用 RRF 融合排名。

### Q4：什么是 Reranker？为什么需要它？

**答**：
Reranker 是一个交叉编码器（Cross-Encoder），将查询和文档一起输入模型计算相关性分数。向量检索是"粗排"（双编码器，适合大规模过滤），Reranker 是"精排"（交叉编码器，精度高但慢）。

工业标准实践：向量检索取 Top-50（粗排）→ Reranker 精排取 Top-5（精排），兼顾精度和速度。

### Q5：如何评估 RAG 系统的质量？

**答**：
从四个维度评估：
1. **检索质量**：Recall@K、MRR、NDCG
2. **生成质量**：Faithfulness（忠实度）、Answer Relevancy（答案相关度）
3. **系统性能**：P50/P99 延迟、QPS
4. **覆盖率**：未回答率

推荐使用 **RAGAS** 框架做自动化评估，配合人工抽检。

### Q6：RAG 相比 Fine-tuning 的优势和劣势？

**答**：
RAG 优势：
- 知识实时更新（只需更新文档库）
- 控制幻觉（回答基于检索结果）
- 实施成本低（无需训练）

Fine-tuning 优势：
- 学习特定输出格式和风格
- 推理时无检索延迟
- 不依赖外部知识库

**最佳实践是两者结合**：RAG 提供实时知识 → Fine-tuning 优化指令遵循。

### Q7：如何处理 RAG 中检索不到相关文档的情况？

**答**：
三步策略：
1. **优化检索**：换更好的 Embedding 模型、调整 chunk_size 和 overlap、加 Reranker、混合检索
2. **查询增强**：Query Rewrite（LLM 改写）、HyDE（假设文档）、多查询扩展
3. **兜底策略**：检索不到时 LLM 说"不知道"（不要编造）、触发 Web 搜索、转人工

---

## 参考文章与推荐阅读

- [Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)](https://arxiv.org/abs/2005.11401) — RAG 开山之作
- [Gao et al. "Retrieval-Augmented Generation for Large Language Models: A Survey" (2023)](https://arxiv.org/abs/2312.10997) — RAG 全面综述
- [LangChain RAG 文档](https://python.langchain.com/docs/tutorials/rag/)
- [RAGAS 评估框架](https://github.com/explodinggradients/ragas)
- [BAAI/bge-reranker-v2-m3 — Reranker 模型](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Elasticsearch 混合检索文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [Pinecone 学习中心 — RAG 最佳实践](https://www.pinecone.io/learn/rag/)
- [Anthropic — 构建有效 RAG 的指南](https://docs.anthropic.com/en/docs/build-with-claude/retrieval-augmented-generation)
- [LangGraph Agentic RAG 示例](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)

---

## 相关文章

- [LLM 基础](/ai-agent/llm-basic)
- [Spring AI](/ai-agent/spring-ai)
