---
outline: deep
---

# ☕ Java 体系

> Java 后端开发的核心知识沉淀，从 JVM 原理到企业级框架的系统学习笔记。

---

## 📖 内容导航

<div class="knowledge-grid">

<div class="knowledge-card">
  <h3>🔧 JVM 原理</h3>
  <p>Java 虚拟机内存模型、垃圾回收机制、类加载机制、性能调优等核心知识。</p>
  <a href="/java/jvm">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>⚡ 并发编程</h3>
  <p>Java 并发基础、JUC 工具类、锁机制、线程池、AQS 原理等并发编程知识体系。</p>
  <a href="/java/concurrent">阅读 →</a>
</div>

<div class="knowledge-card">
  <h3>🌱 Spring 生态</h3>
  <p>Spring Boot、Spring MVC、Spring Cloud 等框架的核心原理与最佳实践。</p>
  <a href="/java/spring">阅读 →</a>
</div>

</div>

---

## 📊 学习进度

- [x] JVM 内存模型
- [x] 垃圾回收机制
- [x] 并发编程基础
- [x] Spring Boot 核心
- [ ] Spring Cloud 微服务
- [ ] 分布式系统设计
- [ ] DDD 领域驱动设计

---

## 📚 推荐资源

- 《深入理解 Java 虚拟机》— 周志明
- 《Java 并发编程的艺术》
- 《Spring 实战》
- 《系统设计面试》— Alex Xu

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
