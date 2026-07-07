---
outline: deep
---

# 🤖 AI / ML 专项学习路线

> 从数学基础到 AI 工程化，系统掌握 AI / LLM 技术栈，具备独立构建 AI 应用的能力。

---

## 路线总览

```
第一阶段：数学基础 ──────────────────────────────┐
    （1-2 个月）                                  │
         ▼                                        │
第二阶段：机器学习基础 ────┐                       │
    （2-3 个月）            │                      │
         ▼                 │                      │
第三阶段：深度学习 ────────┼─── 知识储备 ─────────┤
    （2-3 个月）            │                      │
         ▼                 │                      │
第四阶段：LLM 与大模型 ────┘                      │
    （2-3 个月）                                   │
         ▼                                        │
第五阶段：RAG / AI Agent ──────────────── 应用实践 ─┤
    （2 个月）                                      │
         ▼                                        │
第六阶段：AI 工程化 ───────────────────── 生产落地 ─┘
    （持续）
```

---

## 第一阶段：数学基础（1-2 个月）

**目标**：建立理解 ML 算法所需的数学基础，不需要搞透所有推导，但要理解核心概念。

### 线性代数

| 知识点 | 掌握程度 | 与 ML 的关联 |
|--------|---------|-------------|
| 向量与矩阵运算 | 熟练 | 数据表示、权重矩阵、Embedding |
| 矩阵分解（SVD/特征值分解） | 理解 | 降维（PCA）、推荐系统 |
| 范数与距离度量 | 理解 | L1/L2 正则化、KNN/聚类 |

### 概率论与统计

| 知识点 | 掌握程度 | 与 ML 的关联 |
|--------|---------|-------------|
| 概率分布（正态/伯努利/多项分布） | 理解 | 生成模型、分类器假设 |
| 贝叶斯定理 | **深入** | 朴素贝叶斯、贝叶斯调参 |
| 极大似然估计（MLE） | 理解 | 模型训练的目标函数推导 |
| 期望与方差 | 理解 | 偏差-方差权衡、模型评估 |

### 微积分

| 知识点 | 掌握程度 | 与 ML 的关联 |
|--------|---------|-------------|
| 导数与偏导数 | 理解 | 梯度下降基础 |
| 链式法则 | **深入** | **反向传播的核心** |
| 梯度与优化 | 理解 | SGD、Adam 等优化器 |

**推荐资源**：
- [3Blue1Brown 线性代数的本质](https://www.bilibili.com/video/BV1ib411t7UR) — 可视化理解，最佳入门
- [3Blue1Brown 微积分的本质](https://www.bilibili.com/video/BV1qW411N7nq)
- 可汗学院 — 概率论与统计
- 陈希孺《概率论与数理统计》— 中文经典

::: tip 不需要恐惧数学
不要被数学劝退。**先理解直觉，再深入公式**：
1. 先知道"梯度下降是在下山"
2. 再理解"梯度是导数在多维的推广"
3. 最后才看数学推导

很多从业者数学并不好，但不影响他们用框架训练模型。数学可以边用边补。
:::

---

## 第二阶段：机器学习基础（2-3 个月）

**目标**：理解经典 ML 算法的原理和使用场景，能完成一个完整的 ML 项目流程。

### 监督学习

| 算法 | 掌握程度 | 适用场景 |
|------|---------|---------|
| 线性回归 | 深入 | 连续值预测（房价、温度） |
| 逻辑回归 | **深入** | **二分类基线模型（CTR 预估）** |
| 决策树 | 理解 | 可解释性要求高的场景 |
| SVM | 理解 | 小样本高维分类（文本分类） |
| KNN | 理解 | 推荐、分类（懒学习） |

### 无监督学习

| 算法 | 掌握程度 | 适用场景 |
|------|---------|---------|
| K-Means 聚类 | 掌握 | 用户分群、图像分割 |
| PCA 降维 | 理解 | 高维数据可视化、去噪 |
| t-SNE / UMAP | 了解 | Embedding 可视化 |

### 集成学习

| 算法 | 掌握程度 | 适用场景 |
|------|---------|---------|
| 随机森林 | 掌握 | 表格数据、特征重要性分析 |
| **XGBoost** | **深入** | **Kaggle 竞赛之王，工业界最常用** |
| GBDT | 理解 | 梯度提升树原理 |
| LightGBM | 掌握 | 大规模数据的 XGBoost 替代 |

### 模型评估与调优

| 知识点 | 掌握程度 |
|--------|---------|
| 交叉验证（K-Fold） | 掌握 |
| 过拟合/欠拟合诊断 | **深入** |
| 正则化（L1/L2） | 理解 |
| 混淆矩阵、Precision/Recall/F1、AUC-ROC | **深入** |
| 超参数调优（Grid Search / Random Search） | 掌握 |

**推荐资源**：
- **吴恩达《Machine Learning Specialization》** — 最佳入门，无替代
- 周志华《机器学习》（西瓜书）— 理论参考，不是入门书
- [Kaggle Titanic 入门赛](https://www.kaggle.com/c/titanic) — 第一个 ML 项目

::: warning 常见误区
- **不要一开始就上深度学习**。表格数据上 XGBoost/LightGBM 往往比 NN 效果好
- 特征工程比模型选择更重要。数据质量决定上限，模型只是逼近这个上限
- 过拟合的典型信号：训练集准确率很高但验证集很低
- Kaggle 竞赛可以作为练习，但不要迷信"高分方案就是工程最佳方案"（竞赛方案往往过拟合）
:::

---

## 第三阶段：深度学习（2-3 个月）

**目标**：掌握神经网络原理，能用 PyTorch 实现并训练模型。

### 核心理论

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| 感知机与多层神经网络 | 理解 | 最基本的神经网络结构 |
| **反向传播（Backpropagation）** | **深入** | **深度学习的核心，必须理解链式法则应用** |
| 激活函数（ReLU/Sigmoid/Tanh） | 掌握 | ReLU 解决梯度消失，但可能导致 Dead ReLU |
| 损失函数（Cross-Entropy/MSE） | 掌握 | 分类用 CE，回归用 MSE |
| 优化器（SGD/Momentum/Adam） | 掌握 | Adam 是默认选择，SGD+Momentum 有时泛化更好 |
| 正则化（Dropout/Batch Norm） | 理解 | Dropout 是隐式集成学习，BN 加速收敛 |
| 梯度消失/爆炸 | 理解 | 深层网络的核心难题，ResNet / LayerNorm 缓解 |

### 经典架构

| 架构 | 掌握程度 | 应用 |
|------|---------|------|
| **CNN** 卷积神经网络 | 掌握 | 图像分类、目标检测（ResNet、YOLO） |
| **RNN / LSTM** 循环网络 | 理解 | 序列建模（文本、时间序列），**LLM 时代已被 Transformer 替代** |
| **Transformer** | **深入** | **所有现代 LLM 的基础**（Self-Attention、多头注意力、位置编码） |
| ResNet / Skip Connection | 理解 | 残差连接，解决梯度消失 |

### 框架实践

```python
# PyTorch 训练流程（记住这个模板）
import torch
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(784, 10)
    
    def forward(self, x):
        return self.fc(x)

model = MyModel()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):
    for x, y in dataloader:
        pred = model(x)
        loss = criterion(pred, y)
        
        optimizer.zero_grad()  # 梯度清零（容易遗漏！）
        loss.backward()        # 反向传播
        optimizer.step()       # 更新参数
```

**推荐资源**：
- 吴恩达《Deep Learning Specialization》— 理论
- **李沐《动手学深度学习》**（[d2l.ai](https://d2l.ai/)）— **理论 + PyTorch 代码，最佳组合**
- 李沐的 B 站课程（带读论文系列）
- 实战：用 PyTorch 训练手写数字识别（MNIST）或 CIFAR-10 分类

::: warning 深度学习踩坑
- **梯度清零**：每个 batch 都要 `optimizer.zero_grad()`，这是最常见的 PyTorch bug
- **学习率**：最大的超参数。Adam 默认 lr=1e-3，SGD 需要更小（1e-2~1e-4），可以先找 lr 范围再调优
- **数据归一化**：输入必须归一化到 [0,1] 或标准化为均值为 0、方差为 1
- **GPU OOM**：减小 batch size 或使用 `gradient_accumulation_steps`
- **不要自己造轮子**：数据处理用 Dataset/DataLoader，模型用 torchvision 预训练权重
:::

---

## 第四阶段：LLM 与大模型（2-3 个月）

**目标**：深入理解 Transformer 架构，掌握 LLM 的训练范式和解锁方式。

### Transformer 架构详解

```
注意力机制（Attention）= softmax(Q × K^T / √d_k) × V

其中：
  Q (Query) —— 当前词"想查什么"
  K (Key)   —— 其他词"有什么信息"
  V (Value) —— 其他词"实际内容"
  √d_k      —— 缩放因子，防止 softmax 梯度消失
```

| 组件 | 作用 | 备注 |
|------|------|------|
| Self-Attention | 每个词关注所有词 | O(n²) 复杂度，长文本的瓶颈 |
| Multi-Head Attention | 多个注意力头并行，捕捉不同关系 | "多头" = 多个子空间 |
| Positional Encoding | 注入位置信息 | Transformer 没有 RNN 的天然序 |
| Feed-Forward | 非线性变换 | 每个位置独立的两层 MLP |
| LayerNorm + Residual | 稳定训练 | 连接是深度网络的关键 |
| Decoder-only（GPT） | 自回归生成 | **当前主流 LLM 架构** |

### 预训练与微调

| 阶段 | 数据 | 算力 | 目标 |
|------|------|------|------|
| **预训练** | 海量互联网文本（TB 级） | 数千 GPU × 数月 | 下一个 Token 预测 |
| **SFT** | 高质量问答对 | 单卡~数卡 × 数天 | 指令遵循 |
| **RLHF** | 偏好排序数据 | 数卡 × 数天 | 人类偏好对齐 |

```python
# 在消费级显卡上微调 7B 模型（QLoRA）
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,                     # 低秩矩阵的秩
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    load_in_4bit=True,       # 4bit 量化
    device_map="auto",
)
model = get_peft_model(model, lora_config)
```

### 关键概念

| 概念 | 说明 |
|------|------|
| **In-Context Learning** | 不更新参数，在 Prompt 中给示例（GPT-3 发现的能力） |
| **Chain-of-Thought** | "让我们一步步思考"——显著提升推理准确率 |
| **Temperature** | 控制输出的确定性，0=确定，1=多样 |
| **Top-p / Top-k** | 采样策略，限制候选 token 范围 |
| **Context Window** | 模型能处理的最大输入长度（GPT-4 128K，Claude 200K） |
| **"中间迷失"** | 长上下文中间部分信息容易被忽略 |

**推荐资源**：
- [李沐《LLM 课程》B 站](https://space.bilibili.com/1567748478/channel/seriesdetail?sid=3921380) — **从原理到实现**
- [LLM 基础](/ai-agent/llm-basic) — 本站笔记
- [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course) — Transformers 实践
- 论文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)、[InstructGPT](https://arxiv.org/abs/2203.02155)

---

## 第五阶段：RAG 与 AI Agent（2 个月）

**目标**：掌握 RAG 系统构建和 AI Agent 开发，能搭建生产级的问答系统和智能体应用。

### RAG 系统

```
    用户查询
        │
        ▼
   ┌─────────┐     ┌───────────┐     ┌──────────┐
   │ Query    │────►│ Document  │────►│ Embedding│
   │ Rewrite  │     │ Ingestion │     │ Model    │
   └─────────┘     └───────────┘     └────┬─────┘
                                          │
                                    ┌─────▼─────┐
                                    │ Vector DB │
                                    │ (Milvus/  │
                                    │ Chroma/   │
                                    │ pgvector) │
                                    └─────┬─────┘
                                          │
   ┌──────────┐     ┌──────────┐     ┌─────▼─────┐
   │  Final   │◄────│   LLM    │◄────│  Context  │
   │ Answer   │     │          │     │ + Prompt  │
   └──────────┘     └──────────┘     └───────────┘
```

| 关键决策点 | 方案 | 说明 |
|-----------|------|------|
| **文档切分** | 递归切割 / 语义切分 | chunk_size 256~1024，重叠率 10~20% |
| **Embedding 模型** | BAAI/bge-large-zh / OpenAI | 中文场景选 BGE |
| **向量数据库** | Chroma(原型) / Milvus(生产) / pgvector(业务共存) | 根据规模选 |
| **检索策略** | 混合检索（向量 + BM25）+ RRF 合并 | 工业标准 |
| **重排序** | BGE Reranker / Cohere Rerank | 精排 Top-5 |
| **评估** | RAGAS（Faithfulness / Relevancy） | 离线评估必做 |

### AI Agent

| 能力 | 说明 | 实现方式 |
|------|------|---------|
| **工具调用（Tool Calling）** | Agent 选择并调用外部工具 | Function Calling / Spring AI @Tool / LangChain Tool |
| **记忆管理** | 多轮对话上下文维护 | Conversation Buffer / Window / Summary |
| **多 Agent 协作** | 专业 Agent 分工协作 | LangGraph / CrewAI / AutoGen |
| **MCP 协议** | 标准化工具接入协议 | Anthropic MCP 标准 |

**推荐资源**：
- [RAG 系统](/ai-agent/rag) — 本站笔记
- [MCP 协议](/ai-agent/mcp) — 本站笔记
- [Spring AI](/ai-agent/spring-ai) — 本站笔记
- [LangChain 官方教程](https://python.langchain.com/docs/tutorials/)
- [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [吴恩达《Building Agentic RAG》](https://www.deeplearning.ai/short-courses/)

::: warning RAG 项目踩坑清单
1. **检索不到文档** → 调整 chunk_size 或换 Embedding 模型
2. **检索到不相关文档** → 加 Reranker 精排
3. **LLM 不遵循检索结果** → 加强 System Prompt，设置 "不知道就说不知道"
4. **中文分词不准** → 使用 IK Analyzer（ES 中文分词）
5. **Context Window 超长** → 限制 Top-K + 控制 chunk_size
6. **多轮上下文消解** → 加 Query Rewrite（"它"→ 具体指代）
:::

---

## 第六阶段：AI 工程化（持续）

**目标**：将 AI 能力落地到生产环境，具备完整 AI 应用架构设计和运维能力。

| 领域 | 知识点 | 推荐工具/框架 |
|------|--------|-------------|
| **模型部署** | 模型服务化、量化 | Ollama（本地）、vLLM（高性能）、TGI |
| **AI 框架** | Java 生态集成 | Spring AI（推荐）、LangChain4j |
| **低代码平台** | 可视化 AI 应用构建 | Dify、FastGPT |
| **监控评估** | Token 用量、延迟、质量 | LangSmith、Prompt Flow |
| **安全** | Prompt Injection 防护 | 输入过滤 + 输出校验 |
| **测试** | AI 回归测试 | 自动化评估集（Golden Dataset） |

### Spring AI 生产配置参考

```yaml
# application.yml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini  # 成本优先
    retry:
      max-attempts: 3
      backoff:
        initial-interval: 1000ms
        multiplier: 2
```

### Dify 搭建 RAG 应用

```
Dify 是构建 AI 应用的低代码平台，适合快速验证：

1. 上传文档 → 自动切分 + Embedding
2. 连接 LLM API
3. 配置检索策略（向量/全文/混合）
4. 设置 Prompt + 变量
5. 发布 API 或嵌入 Web 页面
```

**推荐资源**：
- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [Dify 官方文档](https://dify.ai/)
- [Ollama 本地部署](https://ollama.com/)
- [vLLM 高性能推理](https://github.com/vllm-project/vllm)

---

## 🎯 分阶段里程碑

| 阶段 | 里程碑项目 | 验收标准 |
|------|-----------|---------|
| **ML 基础** | Kaggle Titanic / House Price | 提交第一份预测结果 |
| **深度学习** | MNIST / CIFAR-10 分类 | 测试集准确率 > 90% |
| **LLM** | 用 HuggingFace 跑通 Qwen 推理 | 完成一次 LoRA 微调 |
| **RAG** | 搭建个人知识库问答系统 | 能基于 PDF 文档回答 |
| **Agent** | 代码审查 Agent / 客服 Agent | 调用至少 2 个外部工具 |
| **工程化** | Spring AI + Dify 应用上线 | 生产运行 7 天无故障 |

---

## 📚 推荐资源完整列表

### 课程

| 课程 | 平台 | 评级 | 说明 |
|------|------|------|------|
| Machine Learning Specialization | Coursera / 吴恩达 | ⭐⭐⭐⭐⭐ | ML **最佳入门**，没有之一 |
| Deep Learning Specialization | Coursera / 吴恩达 | ⭐⭐⭐⭐⭐ | DL 最佳入门 |
| 动手学深度学习 | Bilibili / 李沐 | ⭐⭐⭐⭐⭐ | 理论 + PyTorch 代码实践 |
| Stanford CS231n | YouTube / 李飞飞 | ⭐⭐⭐⭐ | CV 方向的经典课程 |
| Stanford CS224n | YouTube | ⭐⭐⭐⭐ | NLP 方向的经典课程 |
| HuggingFace NLP Course | HuggingFace | ⭐⭐⭐⭐ | Transformers 库实践 |

### 书籍

| 书名 | 评级 | 说明 |
|------|------|------|
| 周志华《机器学习》（西瓜书） | ⭐⭐⭐⭐ | 中文 ML 理论参考，**不适合入门** |
| 李沐《动手学深度学习》 | ⭐⭐⭐⭐⭐ | 理论与实践结合最佳 |
| PRML（Pattern Recognition and ML） | ⭐⭐⭐ | 进阶数学理论，有志于 AI 研究的再看 |
|《深度学习》（花书）| ⭐⭐⭐ | 综合性强，适合查缺补漏 |
|《机器学习实战：基于 Scikit-Learn》| ⭐⭐⭐⭐ | 实践导向，代码驱动 |

### 论文必读

| 论文 | 重要性 | 说明 |
|------|--------|------|
| Attention Is All You Need | ⭐⭐⭐⭐⭐ | Transformer 奠基之作 |
| GPT-3 / InstructGPT | ⭐⭐⭐⭐⭐ | LLM 范式（预训练 + SFT + RLHF） |
| BERT / RoBERTa | ⭐⭐⭐⭐ | Encoder-only 的巅峰 |
| LLaMA 系列 | ⭐⭐⭐⭐ | 开源 LLM 的里程碑 |
| RAG 论文（Lewis 2020） | ⭐⭐⭐⭐ | 检索增强生成的开山作 |

---

## 常见问题与避坑

### Q1：数学不好能学 AI 吗？

**答**：
能。绝大多数 AI 从业者不需要每天做数学推导。按优先级：
1. **必须理解**：梯度下降是什么（下山）、损失函数（目标）、过拟合（死记硬背）
2. **建议理解**：链式法则（反向传播）、SVD（降维）、贝叶斯定理（朴素贝叶斯）
3. **用到了再补**：信息论、凸优化、泛函分析

先用框架跑通，遇到瓶颈再补数学。

### Q2：学 AI 要不要深度学习框架？

**答**：
要。推荐 PyTorch：
- 先会用：定义模型、前向计算、loss.backward()、optimizer.step()
- 再理解：DataLoader、自动求导、GPU 训练
- 最后进阶：分布式训练、混合精度、torch.compile

学习顺序：**先用框架跑通，再理解底层原理**。

### Q3：RAG 和 Fine-tuning 怎么选？

**答**：

| 场景 | 选 RAG | 选 Fine-tuning |
|------|--------|---------------|
| 知识更新频繁 | ✅ | ❌ |
| 需要特定输出格式/风格 | ❌ | ✅ |
| 需要引用来源 | ✅ | ❌ |
| 实施成本 | 低（无需训练） | 高（需要标注+算力） |
| 幻觉控制 | 更好 | 有限 |

**最佳实践**：两者互补。RAG 做实时知识，Fine-tuning 做格式对齐。

### Q4：学完 ML 要不要打 Kaggle？

**答**：
Kaggle 适合**练习**但不适合**学习**：
- ✅ 好处：完整的 ML 项目流程、社区讨论
- ❌ 问题：高分方案往往过拟合排行榜、工程实践不适用

**建议**：参加 1-2 个入门赛（Titanic / House Price）理解流程，然后转向自己的实际项目。

---

## 参考文章与推荐阅读

- [LLM 基础](/ai-agent/llm-basic) — 本站笔记
- [RAG 系统](/ai-agent/rag) — 本站笔记
- [Spring AI](/ai-agent/spring-ai) — 本站笔记
- [MCP 协议](/ai-agent/mcp) — 本站笔记
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Transformer 论文
- [RLHF 论文 (InstructGPT)](https://arxiv.org/abs/2203.02155)
- [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course)
- [Papers With Code](https://paperswithcode.com/) — 论文 + 代码实现
- [吴恩达 DeepLearning.AI](https://www.deeplearning.ai/short-courses/)
- [动手学深度学习 (d2l.ai)](https://d2l.ai/)

---

## 相关文章

- [Java 后端学习路线](/roadmap/)
- [JVM 原理](/java/jvm)
- [并发编程](/java/concurrent)
- [Spring 生态](/java/spring)
