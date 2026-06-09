---
outline: deep
---

# ⭐ GitHub 开源项目

> 精选优质开源项目，包含项目分析、架构解读与实践心得。

---

## 🔥 重点关注

<div class="project-list">

<div class="project-item">
  <div class="project-header">
    <h3><a href="https://github.com/langchain4j/langchain4j" target="_blank">langchain4j / langchain4j</a></h3>
    <span class="project-stars">⭐ 5k+</span>
  </div>
  <p class="project-desc">Java 版本的 LangChain，简化 Java 应用中大语言模型的集成。支持 OpenAI、HuggingFace 等多种模型提供商。</p>
  <div class="project-tags">
    <span>Java</span>
    <span>LLM</span>
    <span>AI Agent</span>
  </div>
</div>

<div class="project-item">
  <div class="project-header">
    <h3><a href="https://github.com/spring-projects/spring-ai" target="_blank">spring-projects / spring-ai</a></h3>
    <span class="project-stars">⭐ 3k+</span>
  </div>
  <p class="project-desc">Spring 官方出品的 AI 框架，提供了一套统一的 API 来集成 AI 模型、向量数据库等 AI 基础设施。</p>
  <div class="project-tags">
    <span>Java</span>
    <span>Spring</span>
    <span>AI</span>
  </div>
</div>

<div class="project-item">
  <div class="project-header">
    <h3><a href="https://github.com/langgenius/dify" target="_blank">langgenius / dify</a></h3>
    <span class="project-stars">⭐ 60k+</span>
  </div>
  <p class="project-desc">开源的 LLM 应用开发平台，提供可视化的 AI 应用编排、RAG 管道、Agent 能力等。</p>
  <div class="project-tags">
    <span>Python</span>
    <span>LLM</span>
    <span>RAG</span>
    <span>Agent</span>
  </div>
</div>

<div class="project-item">
  <div class="project-header">
    <h3><a href="https://github.com/alibaba/nacos" target="_blank">alibaba / nacos</a></h3>
    <span class="project-stars">⭐ 31k+</span>
  </div>
  <p class="project-desc">阿里巴巴开源的动态服务发现、配置管理和服务管理平台，是微服务架构的核心组件。</p>
  <div class="project-tags">
    <span>Java</span>
    <span>微服务</span>
    <span>云原生</span>
  </div>
</div>

</div>

---

## 📂 分类收集

### ☕ Java 生态
| 项目 | 说明 | Stars |
|------|------|-------|
| [Spring Boot](https://github.com/spring-projects/spring-boot) | Spring 应用快速开发框架 | 76k+ |
| [Spring Cloud Alibaba](https://github.com/alibaba/spring-cloud-alibaba) | 阿里微服务解决方案 | 28k+ |
| [MyBatis-Plus](https://github.com/baomidou/mybatis-plus) | MyBatis 增强工具 | 16k+ |
| [Sentinel](https://github.com/alibaba/Sentinel) | 流量控制与熔断降级 | 23k+ |
| [Seata](https://github.com/seata/seata) | 分布式事务解决方案 | 25k+ |

### 🤖 AI / ML
| 项目 | 说明 | Stars |
|------|------|-------|
| [LangChain](https://github.com/langchain-ai/langchain) | LLM 应用开发框架 | 100k+ |
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | AI Agent 实验项目 | 170k+ |
| [ollama](https://github.com/ollama/ollama) | 本地运行大模型 | 110k+ |
| [ChatGPT-Next-Web](https://github.com/ChatGPTNextWeb/NextChat) | 跨平台 ChatGPT 客户端 | 80k+ |

### 🐳 DevOps / 云原生
| 项目 | 说明 | Stars |
|------|------|-------|
| [Kubernetes](https://github.com/kubernetes/kubernetes) | 容器编排平台 | 112k+ |
| [Docker](https://github.com/moby/moby) | 容器引擎 | 69k+ |
| [Prometheus](https://github.com/prometheus/prometheus) | 监控系统 | 56k+ |

---

## 📋 待探索

- [ ] dubbo / dubbo — 阿里 RPC 框架
- [ ] apache / skywalking — APM 监控
- [ ] b3log / solo — 博客系统
- [ ] chatting / chatgpt-on-java — Java AI 应用

---

> 💡 持续追踪优质开源项目，深入研究其架构设计与实现原理。
<style>
.project-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1.5rem 0;
}
.project-item {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 1.25rem;
  background: var(--vp-c-bg-soft);
  transition: all 0.2s;
}
.project-item:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-1px);
}
.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.project-header h3 {
  margin: 0;
  font-size: 1.05rem;
}
.project-header h3 a {
  color: var(--vp-c-brand-1);
}
.project-stars {
  font-size: 0.85rem;
  color: #d97706;
  white-space: nowrap;
}
.project-desc {
  margin: 0 0 0.75rem;
  color: var(--vp-c-text-2);
}
.project-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.project-tags span {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: #4f46e5;
}
</style>
