---
outline: deep
---

# 📄 技术论文阅读

> 经典论文与前沿论文的阅读笔记，包含摘要、核心思想与技术要点梳理。

---

## 📑 论文列表

<div class="paper-list">

<div class="paper-item">
  <div class="paper-tag">📌 LLM</div>
  <h3>Attention Is All You Need</h3>
  <p class="paper-meta">Vaswani et al. | NeurIPS 2017</p>
  <p>Transformer 架构的奠基之作，提出了自注意力机制（Self-Attention）并彻底改变了 NLP 领域。</p>
  <div class="paper-status">
    <span class="status-badge done">✅ 已读</span>
  </div>
</div>

<div class="paper-item">
  <div class="paper-tag">📌 RAG</div>
  <h3>Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks</h3>
  <p class="paper-meta">Lewis et al. | NeurIPS 2020</p>
  <p>RAG 范式开创性论文，将检索模块与生成模型结合，显著提升了知识密集型任务的性能。</p>
  <div class="paper-status">
    <span class="status-badge done">✅ 已读</span>
  </div>
</div>

<div class="paper-item">
  <div class="paper-tag">📌 LLM</div>
  <h3>Training Language Models to Follow Instructions with Human Feedback (InstructGPT)</h3>
  <p class="paper-meta">Ouyang et al. | OpenAI 2022</p>
  <p>RLHF 技术的核心论文，展示了如何通过人类反馈微调语言模型以更好地遵循指令。</p>
  <div class="paper-status">
    <span class="status-badge progress">📖 阅读中</span>
  </div>
</div>

</div>

---

## 📋 待读论文

| 论文 | 领域 | 优先级 |
|------|------|--------|
| Deep Residual Learning for Image Recognition (ResNet) | CV | ⭐⭐⭐ |
| BERT: Pre-training of Deep Bidirectional Transformers | NLP | ⭐⭐⭐ |
| Chain-of-Thought Prompting Elicits Reasoning in LLMs | LLM | ⭐⭐⭐ |
| Graph Attention Networks | GNN | ⭐⭐ |
| LoRA: Low-Rank Adaptation of Large Language Models | LLM | ⭐⭐⭐ |

---

## 📚 经典论文清单

### NLP / LLM
- [x] Attention Is All You Need (2017)
- [x] BERT (2019)
- [x] GPT-3 (2020)
- [x] RAG (2020)
- [ ] InstructGPT / RLHF (2022)
- [ ] Chain-of-Thought (2022)
- [ ] Llama (2023)

### 机器学习
- [ ] ResNet (2015)
- [ ] Generative Adversarial Nets (2014)
- [ ] Variational Autoencoders (2013)
- [ ] Dropout (2014)
- [ ] Batch Normalization (2015)

### 系统 / 分布式
- [ ] MapReduce (2004)
- [ ] Bigtable (2006)
- [ ] Dynamo (2007)
- [ ] Spanner (2012)

---

> 💡 每篇论文将逐步补充详细的阅读笔记、核心公式推导与实践启发。

<style>
.paper-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1.5rem 0;
}
.paper-item {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 1.25rem;
  background: var(--vp-c-bg-soft);
  transition: all 0.2s;
}
.paper-item:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-1px);
}
.paper-item h3 {
  margin: 0.25rem 0 0.5rem;
  font-size: 1.05rem;
}
.paper-meta {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  margin: 0 0 0.5rem;
  font-style: italic;
}
.paper-item p {
  margin: 0 0 0.75rem;
  color: var(--vp-c-text-2);
}
.paper-tag {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 500;
}
.status-badge {
  font-size: 0.8rem;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
}
.status-badge.done {
  background: #ecfdf5;
  color: #059669;
}
.status-badge.progress {
  background: #fffbeb;
  color: #d97706;
}
</style>
