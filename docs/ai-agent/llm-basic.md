# LLM 基础

> 大语言模型（LLM）是 AI Agent 时代的核心引擎。理解其原理、训练流程和工程实践，是构建 AI 应用的基础。

---

## 一、LLM 核心原理

### 1. 本质：下一个 Token 预测

LLM 的核心是一个**自回归的概率模型**：

```
给定上文 tokens：[今天，天气，真]
预测下一个 token 的概率分布：P(好) = 0.6, P(不) = 0.2, P(很) = 0.1, ...
```

```python
# 这本质上就是 LLM 在做的事
def llm_generate(prompt: str) -> str:
    output = prompt
    for _ in range(max_tokens):
        next_token = model.predict_next_token(output)  # 预测下一个 token
        output += next_token
        if next_token == "<EOS>":  # 遇到结束符停止
            break
    return output[len(prompt):]
```

### 2. Transformer 架构（核心组件）

```
                   输出序列
                      ↑
                  ┌──────┐
                  │ Linear│  → 映射到词表概率分布
                  └──┬───┘
                     │
               ┌─────▼──────┐
               │ LayerNorm  │
               └─────┬──────┘
                     │
               ┌─────▼──────┐
        ┌─────┤  FeedForward ├─────┐
        │     │  (FFN)      │     │
        │     └─────────────┘     │
        │          ↑              │
   ┌────▼────┐    Add     ┌───────▼──────┐
   │ Multi-  │  + Norm    │ Multi-      │
   │ Head    │◄───────────│ Head        │
   │ Self-   │            │ Cross-      │
   │ Attention│           │ Attention   │
   └────┬────┘            └───────┬──────┘
        │                        │
   Positional Encoding     Positional Encoding
        │                        │
   输入 Embedding           输入 Embedding
        │                        │
   输入 Tokens              输入 Tokens
   (Decoder-only 架构，如 GPT 系列)
```

| 组件 | 作用 | 比喻 |
|------|------|------|
| **Token Embedding** | 将 token 映射到高维向量 | 每个词在一个"语义空间"中的坐标 |
| **Positional Encoding** | 注入位置信息 | 标记每个词在句子中的位置 |
| **Self-Attention** | 每个 token 关注上下文中的其他 token | 阅读时"回看"前文 |
| **Multi-Head Attention** | 多个注意力头并行，捕捉不同关系 | 同时关注语法、语义、指代等不同维度 |
| **Feed-Forward** | 非线性变换，学习复杂模式 | 对注意力结果做深层加工 |
| **LayerNorm** | 稳定训练，加速收敛 | 归一化，防止数值爆炸 |
| **Residual Connection** | 缓解梯度消失 | 跳跃连接，保留原始信息 |

#### Attention 机制（缩放点积注意力）

```
Attention(Q, K, V) = softmax(Q × K^T / √d_k) × V

其中：
  Q (Query)：当前 token 的查询向量
  K (Key)：  所有 token 的键向量
  V (Value)： 所有 token 的值向量
  d_k：       维度（除 √d_k 防止 softmax 梯度消失）
```

```python
# 简化的 Attention 计算
import numpy as np

def attention(Q, K, V):
    d_k = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(d_k)  # 相似度矩阵
    weights = softmax(scores)                # 归一化为概率
    return np.dot(weights, V)                # 加权求和
```

### 3. Tokenizer（分词器）

Tokenizer 是 LLM 的"第一道门"——它将文本转换为数字序列。

| 算法 | 代表模型 | 特点 |
|------|---------|------|
| **BPE**（Byte-Pair Encoding） | GPT 系列 | 从字符开始，逐步合并高频对 |
| **WordPiece** | BERT | 类似 BPE，基于概率合并 |
| **SentencePiece** | LLaMA、Mistral | 不依赖空格分词，原生支持多语言 |
| **Tiktoken** | OpenAI 系列 | 基于 BPE，Rust 实现，速度极快 |

```python
# 不同 tokenizer 对同一段文本的编码差异
text = "人工智能 AI Agent 正在改变世界"

# GPT-4 (tiktoken) → ~15 tokens (每个中文约 1-2 tokens)
# LLaMA (SentencePiece) → ~18 tokens
# Claude (自己的 tokenizer) → ~14 tokens

# token 计数经验（约估）：
# 英文：1 token ≈ 0.75 词 ≈ 4 字符
# 中文：1 token ≈ 1.5 字 ≈ 3 字节
# 2000 tokens ≈ 1500 英文词 ≈ 1300 中文字
```

::: tip Token 数估算
| 文本类型 | tokens 估算 |
|---------|------------|
| 1 个英文单词 | ~1.3 tokens |
| 1 个中文字 | ~1.5 tokens |
| 1 页英文书（~500 词）| ~650 tokens |
| 1 页中文书（~500 字）| ~750 tokens |
:::

---

## 二、LLM 训练流程

```
                    预训练 (Pre-training)
    ┌──────────────────────────────────────────────┐
    │  数据：海量互联网文本（TB 级别）                │
    │  目标：下一个 Token 预测（自监督学习）           │
    │  算力：数千~数万 GPU 卡 × 数月                 │
    │  产出：Base Model（如 LLaMA、GPT-3）           │
    └─────────────────────┬────────────────────────┘
                          ▼
                    SFT (Supervised Fine-Tuning)
    ┌──────────────────────────────────────────────┐
    │  数据：人工标注的高质量问答对                    │
    │  目标：指令遵循（Instruction Following）        │
    │  产出：SFT Model（能听懂指令）                 │
    └─────────────────────┬────────────────────────┘
                          ▼
                        RLHF
    ┌──────────────────────────────────────────────┐
    │  阶段1：训练 Reward Model（偏好打分）           │
    │  阶段2：PPO 强化学习（对齐人类偏好）             │
    │  产出：Chat Model（如 ChatGPT、Claude）        │
    └──────────────────────────────────────────────┘
```

### 1. 预训练（Pre-training）

- **数据量**：GPT-3 ~45TB（570GB 去重后），LLaMA 2 ~2T tokens
- **参数规模**：70M → 7B → 70B → 180B → 405B（参数越多，能力越强但成本越高）
- **计算成本**：训练 LLaMA 65B ~2048 A100 GPU × 21 天

```bash
# 预训练的超参数
batch_size: ~4M tokens
learning_rate: ~3e-4
warmup_steps: ~2000
weight_decay: ~0.1
gradient_clip: ~1.0
```

### 2. SFT（有监督微调）

用**人工标注的指令-回答对**微调，教会模型遵循指令。

```
输入："用 Python 写一个计算斐波那契数列的函数"
输出：高质量代码 + 解释
```

SFT 数据质量 >>>> 数量。几百条高质量 SFT 数据有时比几万条低质量数据效果更好。

### 3. RLHF（基于人类反馈的强化学习）

```
Step 1：训练 Reward Model
  指令 "写一首诗"
  ├── 回答 A (4.5分) ──→ RM 训练
  └── 回答 B (3.0分)

Step 2：PPO 强化学习
  SFT Model → 生成回答 → Reward Model 打分 → 更新 SFT Model
  + KL Penalty（防止模型偏移太远）
```

::: tip SFT vs RLHF 对比
| 维度 | SFT | RLHF |
|------|-----|------|
| 目的 | 学会格式和风格 | 学会偏好和对齐 |
| 数据要求 | 高质量问答对 | 偏好排序数据 |
| 效果边界 | 只能模仿 | 可以超越训练数据 |
| 实现复杂度 | 低 | 高 |
:::

### 4. 参数高效微调（PEFT）

全量微调成本极高，PEFT 技术可以在消费级 GPU 上微调大模型。

| 方法 | 原理 | 参数量 | 效果 |
|------|------|--------|------|
| **LoRA** | 低秩适配矩阵 `A×B` | ~0.1%~1% | ⭐⭐⭐⭐⭐ |
| **QLoRA** | LoRA + 4bit 量化 | ~0.1% | ⭐⭐⭐⭐ |
| **Adapter** | 插入小网络层 | ~3%~6% | ⭐⭐⭐ |
| **Prefix Tuning** | 学习虚拟 token | ~0.1% | ⭐⭐⭐ |

```python
# LoRA 微调（HuggingFace PEFT）
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,                    # 秩（rank），越大能力越强但参数越多
    lora_alpha=32,           # 缩放系数
    target_modules=["q_proj", "v_proj"],  # 通常只 Q/V 矩阵
    lora_dropout=0.1,
    bias="none",
)

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b")
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 只训练 ~0.1% 的参数
```

---

## 三、Prompt Engineering

### 1. 核心原则

```markdown
# 好的 Prompt 模板
## 1. 角色设定
你是一个资深 Java 工程师，擅长并发编程。

## 2. 任务描述
请分析这段代码的线程安全问题。

## 3. 上下文
{code_snippet}

## 4. 输出约束
1. 指出所有线程安全问题
2. 给出修复后的代码
3. 用列表形式输出

## 5. 示例（few-shot）
输入：...
输出：...
```

| 技巧 | 说明 | 效果 |
|------|------|------|
| **角色设定** | "你是一个资深架构师" | 显著提升输出质量 |
| **明确约束** | 格式、长度、风格 | 控制输出一致性 |
| **Few-shot** | 给 2-3 个示例 | 降低理解偏差 |
| **思维链（CoT）** | "让我们一步步思考" | 提升推理准确率 |
| **分隔符** | 用 ``` 或 `---` 分隔不同部分 | 减少混淆 |
| **任务分步** | 复杂任务拆解为子任务 | 提升效果 |

### 2. 温度（Temperature）与采样

```python
# Temperature 控制输出的"创造性"
# 低 temperature → 确定性高，适合事实问答
# 高 temperature → 多样性高，适合创意写作

temperature_guide = {
    0.0:  "代码生成、事实性问答",
    0.3:  "翻译、摘要、分类",
    0.7:  "日常对话、通用任务",
    0.9:  "创意写作、头脑风暴",
    1.2+: "诗歌、极富创意（可能不可控）",
}

# Top-p (nucleus sampling)：只从累积概率 p 的 token 中采样
# top_p=0.9 → 只保留概率和 90% 的 token
# 通常 temperature 和 top_p 只调一个
```

```python
# 推荐组合
api_params = {
    "事实问答":  {"temperature": 0.0, "top_p": 1.0},
    "创意写作":  {"temperature": 0.8, "top_p": 0.9},
    "代码生成":  {"temperature": 0.1, "top_p": 0.9},
    "对话":     {"temperature": 0.7, "top_p": 0.95},
}
```

### 3. System Prompt vs User Prompt

| 角色 | 作用 | 示例 |
|------|------|------|
| **System** | 设定全局行为、角色、规则 | `你是银行客服，回答必须基于知识库，不得编造` |
| **User** | 用户的具体问题或指令 | `定期存款利率是多少？` |
| **Assistant** | 模型的回复（可用于 few-shot） | `定期存款一年的利率为 2.1%（范例回复）` |

::: warning System Prompt 容易被覆盖
不要将安全规则仅放在 System Prompt 中——用户消息可以通过"忽略前面的指令"覆盖。
关键约束应在应用层（输入过滤、输出校验）而不是仅靠 Prompt。
:::

---

## 四、LLM 的关键参数与能力边界

### 1. 上下文窗口（Context Window）

| 模型 | 上下文长度 | 说明 |
|------|-----------|------|
| GPT-3.5 | 4K ~ 16K | 早期限制明显 |
| GPT-4 | 8K ~ 128K | 128K = ~300 页书 |
| Claude 3 | 200K | 可处理大部头书籍 |
| Gemini 1.5 Pro | 1M ~ 2M | 最大上下文窗口 |
| LLaMA 3 | 8K ~ 128K | 开源最长 |

#### 长上下文的"中间迷失"问题

```
                          回答准确率
   ┃
   ┃
   ┃    ██████████
   ┃    ████████████████████
   ┃    ██████████████████████████
   ┃    ████████████████████████████████
   ┃    ████████████████████████████████████
   ┃    ████████████████████████████████████████
   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        开头                   中间          结尾
```

- 模型在长上下文中对**开头和结尾**的信息检索效果好
- **中间部分**容易被"迷失"（Lost in the Middle）
- **解决方案**：关键信息放在 Prompt 的开头或结尾；使用 RAG 精确检索而不是全量投放

### 2. 幻觉（Hallucination）

| 类型 | 表现 | 原因 | 缓解 |
|------|------|------|------|
| **事实性幻觉** | 编造不存在的事实 | 知识不足/压缩损失 | RAG + 外部知识库 |
| **忠实性幻觉** | 偏离用户指令 | Prompt 歧义 | 更清晰的 Prompt + 约束 |
| **逻辑幻觉** | 推理链条断裂 | 模型推理能力不足 | CoT + 分步验证 |

**缓解策略**（按 ROE 排序）：

1. **RAG 检索增强**：让模型基于检索结果回答（ROE 最高）
2. **引用要求**：要求模型标注信息出处
3. **Prompt 约束**：明确的"不知道就说不知道"
4. **温度调低**：`temperature=0.0` 减少发散
5. **多轮验证**：让模型自检（"上一步推理是否有误？"）

### 3. 推理能力

```markdown
# 思维链（Chain-of-Thought, CoT）显著提升推理
问：一个池塘里的睡莲每天翻倍，48 天覆盖整个池塘。
    覆盖一半需要多少天？

直接回答 → ❌ 模型可能答错
"让我们一步步思考：" → ✅ 正确率大幅提升

一步步思考：
- 第 48 天：覆盖整个池塘
- 每天翻倍 → 第 47 天覆盖一半
- 答案：47 天
```

| 推理增强技术 | 说明 | 适用 |
|-------------|------|------|
| **Zero-shot CoT** | Prompt 加"让我们一步步思考" | 通用推理 |
| **Few-shot CoT** | 给示例 + 推理过程 | 数学/逻辑问题 |
| **Self-Consistency** | 多次采样 + 投票选择 | 需要高准确率 |
| **ToT（Tree of Thoughts）** | 探索多条推理路径 | 复杂规划问题 |

---

## 五、生产实践中的 LLM

### 1. 模型选择

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 中文对话 | Claude / GPT-4o / Qwen | 中文支持好 |
| 代码生成 | Claude / GPT-4o / DeepSeek | 代码能力领先 |
| 推理/数学 | GPT-4o / Claude Sonnet / DeepSeek-R1 | 推理能力强 |
| 长文档处理 | Gemini 1.5 / Claude（200K+） | 超大上下文 |
| 成本敏感 | GPT-4o-mini / DeepSeek-V3 | 性价比高 |
| 私有化部署 | Qwen / LLaMA / DeepSeek | 数据安全 |

### 2. API 调用最佳实践

```python
# 稳健的 API 调用模式
import time
from openai import OpenAI

client = OpenAI()

def llm_call(prompt: str, max_retries: int = 3) -> str:
    """带重试和降级的 LLM 调用"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个 AI 助手"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=1024,
                timeout=30,           # 超时防止 hang
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt == max_retries - 1:
                return "服务暂时不可用，请稍后重试"  # 友好降级
            time.sleep(2 ** attempt)  # 指数退避
```

### 3. 常见踩坑

::: danger LLM 生产踩坑

| # | 问题 | 原因 | 解决方案 |
|---|------|------|---------|
| 1 | **输出不稳定** | 未设置 temperature=0 | 事实性任务设 0，测试时固定 seed |
| 2 | **Token 超限报错** | 输入超过模型限制 | 截断/摘要/滑动窗口 |
| 3 | **API 超时** | 长输出 LLM 耗时过长 | 流式输出(stream=True) |
| 4 | **JSON 解析失败** | 模型输出不是合法 JSON | response_format={"type": "json_object"} |
| 5 | **速率限制** | 并发 QPS 超过 API 限制 | 加本地延迟/退避/多 API Key 轮换 |
| 6 | **成本失控** | 无效的 Token 消耗 | 设置 max_tokens 上限 + 监控 Token 用量 |
| 7 | **Prompt Injection** | 用户输入注入恶意指令 | 输入过滤 + 输出校验 + Prompt 边界 |
| 8 | **停机降级** | LLM API 不可用 | 缓存 + 模型降级（高→低） |

```python
# JSON 输出模式（OpenAI 支持原生 JSON）
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "输出 JSON 格式的配置"}],
    response_format={"type": "json_object"},  # ✅ 强制输出 JSON
)

# 流式输出（首 token 延迟从 ~2s 降到 ~200ms）
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "讲一个故事"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```
:::

---

## 六、面试高频问题

### Q1：LLM 的工作原理是什么？

**答**：
LLM 基于 Transformer 架构中的 Decoder-only 模型。核心是**自回归下一个 Token 预测**——给定上文 tokens，预测下一个 token 的概率分布。训练分为三个阶段：

1. **预训练**：海量无标注文本上的自监督学习
2. **SFT**：人工标注指令数据上的有监督微调
3. **RLHF**：基于人类偏好反馈的强化学习对齐

推理时，通过温度/top-p 采样策略控制输出的确定性和多样性。

### Q2：什么是幻觉？如何缓解？

**答**：
幻觉指 LLM 生成不基于事实的内容。分为事实性幻觉（编造知识）、忠实性幻觉（偏离指令）、逻辑幻觉（推理断裂）。

**缓解策略按 ROE 排序**：
1. RAG 检索增强（引用外部知识）
2. 要求输出标注引用来源
3. 降低 temperature 减少发散
4. 约束 Prompt（"不知道就说不知道"）
5. 模型自检多次验证

没有万全之策，RAG + 约束是当前最有效方案。

### Q3：Context Window 越长越好吗？

**答**：
不是。虽然长上下文可以处理更多信息，但存在"中间迷失"（Lost in the Middle）问题——模型对长上下文中间部分的信息检索效果远差于开头和结尾。并且长上下文意味着更多的 Token 消耗（成本↑）和更长的推理延迟。最佳实践是将精确检索（如 RAG）与上下文配合：只将关键信息放在开头和结尾。

### Q4：SFT 和 RLHF 的区别是什么？

**答**：
- **SFT**："教模型说话"——用问答对训练，学习指令遵循的格式和风格。上限是训练数据的质量。
- **RLHF**："教模型什么好"——通过 Reward Model 打分 + PPO 强化学习，让模型学会人类偏好。可以超越训练数据。

SFT 学的是"怎么说"，RLHF 学的是"说什么好"。两者是递进关系：SFT 是 RLHF 的起点。

### Q5：如何使用 LoRA 微调大模型？

**答**：
LoRA（Low-Rank Adaptation）在预训练权重旁插入低秩矩阵 `A×B`（r=8~64），训练时**只更新这些小矩阵**，冻结原权重。QLoRA 进一步将原权重 4bit 量化，使单卡 24GB 显存可微调 7B 模型。LoRA 适用于特定格式对齐（如客服角色、代码风格），但对注入新知识的提升有限——新知识仍依赖 RAG。

---

## 参考文章与推荐阅读

- [Attention Is All You Need (Vaswani et al. 2017)](https://arxiv.org/abs/1706.03762) — Transformer 奠基之作
- [LLaMA 论文](https://arxiv.org/abs/2302.13971) — 开源 LLM 的里程碑
- [RLHF 论文 (InstructGPT)](https://arxiv.org/abs/2203.02155) — ChatGPT 背后的技术
- [吴恩达 ChatGPT Prompt Engineering 课程](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
- [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course) — Transformer 全教程
- [PEFT (Parameter-Efficient Fine-Tuning)](https://huggingface.co/docs/peft) — LoRA/QLoRA 官方文档
- [OpenAI Tokenizer Visualization](https://platform.openai.com/tokenizer)
- [Lost in the Middle (Liu et al. 2023)](https://arxiv.org/abs/2307.03172) — 上下文"中间迷失"研究
- [OpenAI API 文档](https://platform.openai.com/docs/guides/text-generation) — 最佳实践
- [Anthropic 文档 — Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## 相关文章

- [RAG 系统](/ai-agent/rag)
- [Spring AI](/ai-agent/spring-ai)
- [MCP 协议](/ai-agent/mcp)
