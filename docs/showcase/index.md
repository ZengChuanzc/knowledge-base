---
outline: deep
---

# 🛠️ 项目展示

> 个人项目与实战案例展示，从需求分析到架构设计再到实现的全过程复盘。

---

## 🚀 项目列表

<div class="project-showcase">

<div class="showcase-card">
  <div class="card-badge">💼 个人项目</div>
  <h3>Knowledge Base — 个人知识库平台</h3>
  <div class="card-meta">
    <span>🔧 VitePress</span>
    <span>📅 2026</span>
  </div>
  <p>基于 VitePress 构建的个人技术知识库，涵盖 Java、AI Agent、机器学习等领域的学习笔记与项目实践。</p>
  <div class="card-features">
    <h4>核心功能：</h4>
    <ul>
      <li>多分类知识体系管理</li>
      <li>学习路线规划与追踪</li>
      <li>技术导航与资源收录</li>
      <li>文章/论文/项目阅读管理</li>
    </ul>
  </div>
  <div class="card-links">
    <a href="/">🔗 访问站点</a>
    <a href="https://github.com/zengchans/knowledge-base" target="_blank">📦 源代码</a>
  </div>
</div>

<!-- 占位：后续添加更多项目 -->
<div class="showcase-card placeholder">
  <div class="card-badge">⏳ 待补充</div>
  <h3>更多项目即将展示...</h3>
  <p>正在整理过往项目的架构文档与复盘笔记，敬请期待！</p>
</div>

</div>

---

## 📊 项目分类

| 类型 | 说明 | 状态 |
|------|------|------|
| 🏗️ 后端项目 | Spring Cloud 微服务项目 | 📝 整理中 |
| 🤖 AI 项目 | LLM + RAG 应用实践 | 📝 整理中 |
| 📱 全栈项目 | 前后端分离项目 | ⏳ 待整理 |
| 🔧 工具/库 | 自研工具与组件 | ⏳ 待整理 |

---

## 📋 项目复盘模板

每个项目展示将包含：

1. **项目背景** — 为什么做这个项目？
2. **技术选型** — 为什么选择这些技术栈？
3. **架构设计** — 整体架构图与模块划分
4. **核心实现** — 关键代码与设计模式
5. **踩坑记录** — 遇到的问题与解决方案
6. **复盘总结** — 收获、不足与改进方向

---

> 💡 持续整理中，每个项目将逐步补充完整的架构文档与复盘笔记。

<style>
.project-showcase {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin: 1.5rem 0;
}
.showcase-card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 1.5rem;
  background: var(--vp-c-bg-soft);
  transition: all 0.2s;
}
.showcase-card:not(.placeholder):hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.showcase-card.placeholder {
  opacity: 0.6;
  border-style: dashed;
}
.card-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.showcase-card h3 {
  margin: 0 0 0.5rem;
}
.card-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.75rem;
}
.showcase-card p {
  color: var(--vp-c-text-2);
  margin: 0 0 1rem;
}
.card-features {
  margin-bottom: 1rem;
}
.card-features h4 {
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
}
.card-features ul {
  margin: 0;
  padding-left: 1.25rem;
}
.card-features li {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}
.card-links {
  display: flex;
  gap: 1rem;
}
.card-links a {
  font-weight: 500;
}
</style>
