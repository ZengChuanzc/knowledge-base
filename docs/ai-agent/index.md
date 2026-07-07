---
outline: deep
---

# 🤖 AI Agent

> 从 LLM 基础到 AI Agent 应用开发的学习笔记与实践总结。

---

## 📖 内容导航

<div class="knowledge-grid">

<div class="knowledge-card">
  <h3>📝 LLM 基础</h3>
  <p>大语言模型核心概念：Transformer、预训练、微调、Prompt Engineering 等基础知识。</p>
  <a href="../ai-agent/llm-basic">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>🔍 RAG 系统</h3>
  <p>检索增强生成（Retrieval-Augmented Generation）原理、架构与最佳实践。</p>
  <a href="../ai-agent/rag">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>🌱 Spring AI</h3>
  <p>Spring AI 框架学习笔记，AI 模型集成、向量数据库、Agent 开发实践。</p>
  <a href="../ai-agent/spring-ai">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>🔌 MCP 协议</h3>
  <p>Model Context Protocol：AI 模型与外部工具/数据源的标准化交互协议。</p>
  <a href="../ai-agent/mcp">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>🧩 Agent Skills</h3>
  <p>AI Agent 技能（Skills）的设计、开发与编排，从原子工具到组合工作流的完整实践。</p>
  <a href="../ai-agent/skills">阅读 →</a>
</div>

</div>

---

## 📊 学习进度

- [x] LLM 基础概念
- [x] RAG 原理与实现
- [x] Spring AI 入门
- [x] MCP 协议
- [x] Agent 技能设计
- [x] LangChain 实践
- [ ] AI Agent 多工具编排
- [ ] 模型微调（Fine-tuning）
- [ ] 多模态模型应用

---

## 🔗 相关资源

- [吴恩达《ChatGPT Prompt Engineering for Developers》](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
- [LangChain 官方文档](https://python.langchain.com/)
- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)

<style>
.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}
.knowledge-card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 1.25rem;
  background: var(--vp-c-bg-soft);
  transition: all 0.2s;
}
.knowledge-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.knowledge-card h3 {
  margin-top: 0;
}
.knowledge-card a {
  font-weight: 500;
}
</style>
