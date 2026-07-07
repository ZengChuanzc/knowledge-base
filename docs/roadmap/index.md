---
outline: deep
---

# 🗺️ 学习路线

> 体系化的学习路径规划。每条路线按阶段划分，标注核心知识点、推荐资源、预期时长和常见踩坑，帮助高效建立知识体系。

---

## ☕ Java 后端学习路线

### 路线总览

```
第一阶段：Java 核心基础 ───→ 第二阶段：JVM 与并发
        │                           │
        ▼                           ▼
第三阶段：Spring 生态 ←──────────────┘
        │
        ▼
第四阶段：微服务与分布式
        │
        ▼
第五阶段：架构与系统设计
        │
        ▼
第六阶段：工程素养与软技能
```

### 第一阶段：Java 核心基础（1-2 个月）

**目标**：掌握 Java 语法、面向对象思想、常用 API，能独立编写中等复杂度程序。

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| Java 语法基础 | 熟练 | 数据类型、控制流程、运算符 |
| 面向对象 | 深入 | 封装/继承/多态、抽象类/接口、内部类 |
| 集合框架 | 深入 | ArrayList/LinkedList、HashMap/ConcurrentHashMap、TreeMap |
| 泛型 | 掌握 | 泛型类/方法/接口、通配符、类型擦除 |
| 异常处理 | 掌握 | try-catch-finally、自定义异常、异常链 |
| IO / NIO | 理解 | 字节流/字符流、Buffer/Channel、Selector |
| 反射与注解 | 理解 | Class 对象、动态代理、APT 处理 |
| Lambda / Stream | 熟练 | 函数式接口、Stream 中间/终止操作、Optional |

**推荐资源**：
- 《Java 核心技术 卷 I》— 入门经典
- 《Thinking in Java》（Java 编程思想）— 进阶理解
- LeetCode 简单~中等难度 50 题（巩固语法）

**踩坑提醒**：
::: warning 常见误区
- 不要过早深入框架（Spring），先打好 Java 基础
- HashMap 原理（put/resize、红黑树转换）是面试高频，一定要看源码
- IO/NIO 理解阻塞/非阻塞模型即可，BIO/NIO/AIO 的差异要理清
- 泛型类型擦除是常见面试题，要理解编译期和运行期的区别
:::

### 第二阶段：JVM 与并发（2-3 个月）

**目标**：理解 JVM 内存管理和垃圾回收机制，掌握 Java 并发编程核心工具。

#### JVM

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| 运行时数据区 | 深入 | 堆/栈/方法区/程序计数器、JDK 8+ 元空间变化 |
| 对象创建与内存布局 | 理解 | TLAB、指针压缩、对象头 Mark Word |
| 类加载机制 | 深入 | 双亲委派模型、破坏双亲委派、Tomcat 类加载 |
| 垃圾回收 | 深入 | GC Roots、引用类型、GC 算法（标记-清除/复制/标记-整理） |
| GC 调优 | 掌握 | G1/ZGC/Parallel 选择、GC 日志分析、常见参数 |
| JVM 调优工具 | 掌握 | jstat/jstack/jmap/jcmd/JMC/Arthas |

**推荐资源**：
- 《深入理解 Java 虚拟机》（周志明）— **必读**
- [JVM 原理](/java/jvm) — 本站笔记
- 实战：用 jstat 和 jconsole 观察自己应用的 GC 情况

#### 并发编程

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| 线程基础 | 掌握 | 线程状态、创建方式、wait/notify、sleep/yield/join |
| synchronized | 深入 | 对象头 Mark Word、锁升级过程、偏向锁/轻量锁/重量锁 |
| JMM | 深入 | 原子性/可见性/有序性、happens-before、volatile 原理 |
| AQS | 深入 | CLH 队列、独占/共享模式、Condition |
| JUC 工具 | 掌握 | ReentrantLock、CountDownLatch、CyclicBarrier、Semaphore |
| 线程池 | 深入 | 核心参数、execute 流程、队列选择、拒绝策略、容量估算 |
| ConcurrentHashMap | 深入 | JDK 7/8 差异、CAS + synchronized、扩容机制 |
| CompletableFuture | 掌握 | 异步编排、thenApply/thenCombine/allOf、异常处理 |

**推荐资源**：
- 《Java 并发编程的艺术》— JMM 和 AQS 讲得最清楚
- 《Java 并发编程实战》— 进阶必读
- [并发编程](/java/concurrent) — 本站笔记
- 实战：用 CompletableFuture 重构一个串行接口为并行请求

**踩坑提醒**：
::: warning 常见误区
- `Thread.sleep()` 不会释放锁，`Object.wait()` 才会 —— 面试高频
- 线程池**禁止使用 `Executors` 工厂方法**，务必手动构建有界队列
- `@Async` 注解同类调用失效（本质是 AOP 代理问题）
- `ConcurrentHashMap` 的 `size()` 不精确，`key/value` 不能为 null
- ThreadLocal 务必在 finally 中 `remove()`，否则内存泄漏
:::

### 第三阶段：Spring 生态（2-3 个月）

**目标**：掌握 Spring Boot 开发框架，能独立构建 RESTful API 和 Web 应用。

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| Spring IoC | 深入 | 容器体系、Bean 生命周期、循环依赖（三级缓存）、注入方式选择 |
| Spring AOP | 深入 | JDK/CGLib 代理、通知类型、@Transactional 失效场景 |
| Spring Boot 自动配置 | 理解 | @EnableAutoConfiguration、@Conditional、spring.factories |
| Spring MVC | 掌握 | DispatcherServlet 流程、拦截器 vs 过滤器、统一异常处理 |
| 数据访问 | 掌握 | MyBatis/MyBatis-Plus、Spring Data JPA、事务传播与隔离 |
| Spring Security | 理解 | 认证授权流程、JWT 集成、常见漏洞防护 |
| 单元测试 | 掌握 | JUnit 5、Mockito、Spring Boot Test、MockMvc |

**推荐资源**：
- [Spring 生态](/java/spring) — 本站笔记
- 官方文档：spring.io/docs
- 实战：搭建一个完整的 CRUD 项目（含多数据源、事务、单元测试）

**踩坑提醒**：
::: warning 常见误区
- `@Transactional` 同类调用失效、异常被 catch 后不回滚——这是线上最常见的问题
- **构造器注入优于字段注入**（Spring 官方推荐）
- Controller 层不要塞业务逻辑，只做参数校验和路由转发
- Spring Boot 2.6+ 默认禁止循环依赖，设计上应避免
- 配置项不要硬编码，用 `@ConfigurationProperties` 集中管理
:::

### 第四阶段：微服务与分布式（2-3 个月）

**目标**：理解微服务架构设计理念，掌握常用分布式中间件。

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| Spring Cloud 生态 | 掌握 | 服务注册/发现（Nacos/Eureka）、配置中心、网关（Gateway） |
| 远程调用 | 掌握 | OpenFeign、gRPC、Dubbo |
| 分布式事务 | 理解 | Seata AT/TCC/Saga 模式、最终一致性 |
| 消息队列 | 掌握 | RabbitMQ / RocketMQ：消息模型、可靠投递、顺序消息 |
| 分布式缓存 | 掌握 | Redis：数据结构、持久化、集群、缓存穿透/击穿/雪崩 |
| 分布式锁 | 掌握 | Redis Redisson、ZooKeeper 实现 |
| 容器化 | 掌握 | Docker 基础 + Docker Compose |
| 服务网格 | 了解 | Istio 基本概念 |

**推荐资源**：
- 《微服务架构设计模式》（Chris Richardson）— 圣经
- 《凤凰架构》（周志明）— 中文最佳
- 实战：搭建 Spring Cloud Alibaba 微服务 Demo（含 Gateway + Nacos + Sentinel）

### 第五阶段：架构与系统设计（持续）

**目标**：具备中大型系统架构设计能力，能评估和优化系统性能。

| 知识点 | 掌握程度 | 说明 |
|--------|---------|------|
| 设计模式 | 掌握 | 常用 8-10 种（单例/工厂/策略/模板/观察者/代理等） |
| DDD 领域驱动设计 | 理解 | 限界上下文、聚合根、领域事件、六边形架构 |
| 系统设计 | 掌握 | 高可用/高并发设计、读写分离、分库分表（ShardingSphere） |
| 性能优化 | 理解 | SQL 调优、JVM 调优、接口优化（批处理、异步、缓存） |
| 可观测性 | 掌握 | 日志（ELK）、指标（Prometheus + Grafana）、链路追踪（SkyWalking） |
| CI/CD | 掌握 | Jenkins / GitHub Actions、Docker 镜像构建、K8s 部署 |

**推荐资源**：
- 《系统设计面试》（Alex Xu）— 面试专项
- 《数据密集型应用系统设计》（DDIA）— 进阶必读
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

### 第六阶段：工程素养（贯穿始终）

- **代码质量**：遵循阿里巴巴开发手册，使用 SonarQube / Checkstyle
- **版本管理**：Git 分支模型（GitFlow / Trunk-Based）、Commit Message 规范
- **文档能力**：API 文档（OpenAPI）、架构文档、README 规范
- **技术视野**：关注 InfoQ、掘金、V2EX、GitHub Trending

---

## 🤖 AI / LLM 学习路线

> 详情请参见 [AI / ML 专项学习路线](/roadmap/ai-ml-roadmap)，以下是核心脉络。

```
第一阶段：数学基础 ───→ 第二阶段：机器学习 ───→ 第三阶段：深度学习
                                                    │
                                                    ▼
                             第五阶段：AI 工程化 ←─── 第四阶段：LLM / RAG / Agent
```

| 阶段 | 核心内容 | 预计时长 | 里程碑 |
|------|---------|---------|--------|
| **一：数学基础** | 线性代数 + 概率论 + 微积分 | 1-2 个月 | 理解梯度下降、贝叶斯公式、矩阵运算 |
| **二：机器学习** | 监督/无监督学习、集成学习 | 2-3 个月 | 完成 Kaggle Titanic 入门赛 |
| **三：深度学习** | CNN/RNN/Transformer、PyTorch 实践 | 2-3 个月 | 训练一个自定义分类模型 |
| **四：LLM 应用** | RAG、Prompt Engineering、Agent | 2-3 个月 | 搭建一个完整 RAG 问答系统 |
| **五：AI 工程化** | 模型部署、监控、Spring AI 集成 | 持续 | 生产级 AI 应用上线 |

---

## 📚 学习资源推荐

### Java 后端

| 类型 | 资源 | 评级 | 说明 |
|------|------|------|------|
| **入门** | 《Java 核心技术 卷 I》 | ⭐⭐⭐⭐⭐ | Java 自学最佳入门书 |
| **进阶** | 《深入理解 Java 虚拟机》 | ⭐⭐⭐⭐⭐ | JVM 必读 |
| **进阶** | 《Java 并发编程的艺术》 | ⭐⭐⭐⭐⭐ | AQS 和 JMM 最透彻 |
| **框架** | 《Spring 实战》 | ⭐⭐⭐⭐ | Spring 基础入门 |
| **微服务** | 《凤凰架构》 | ⭐⭐⭐⭐⭐ | 中文分布式系统最佳 |
| **系统设计** | 《数据密集型应用系统设计》 | ⭐⭐⭐⭐⭐ | 终局之战 |
| **面试** | 《Java Guide》 | ⭐⭐⭐⭐⭐ | online：javaguide.cn |

### AI / ML

| 类型 | 资源 | 评级 | 说明 |
|------|------|------|------|
| **ML 入门** | 吴恩达《Machine Learning Specialization》 | ⭐⭐⭐⭐⭐ | 最佳入门课 |
| **ML 理论** | 周志华《机器学习》（西瓜书） | ⭐⭐⭐⭐⭐ | 中文经典 |
| **DL 实践** | 李沐《动手学深度学习》 | ⭐⭐⭐⭐⭐ | 理论+PyTorch 代码 |
| **LLM** | 吴恩达《ChatGPT Prompt Engineering for Developers》 | ⭐⭐⭐⭐ | 提示工程入门 |
| **LLM 进阶** | 李沐《LLM 课程》bilibili | ⭐⭐⭐⭐⭐ | 从原理到应用 |
| **RAG** | LangChain 官方教程 | ⭐⭐⭐⭐ | 实践 RAG 系统搭建 |

---

## 🎯 学习建议

1. **先广后深**：先快速了解全貌（每个阶段 2 周通识），再深挖感兴趣的领域
2. **项目驱动**：每学完一个阶段，做一个项目来巩固，不要光看不练
3. **输出倒逼输入**：用自己的话整理笔记、写博客、教别人
4. **面试导向**：知识体系 vs 面试八股要平衡，有些原理（如 AQS、ConcurrentHashMap）是面试必考也是理解深度的试金石
5. **不要"等学完再开始"**：学到 60% 就可以开始做项目，在实战中查漏补缺

---

## 参考文章与推荐阅读

- [JavaGuide — Java 学习路线](https://javaguide.cn/home.html#java)
- [美团技术博客](https://tech.meituan.com/)
- [阿里云开发者社区](https://developer.aliyun.com/)
- [吴恩达 DeepLearning.AI](https://www.deeplearning.ai/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Papers With Code](https://paperswithcode.com/)

---

## 相关文章

- [JVM 原理](/java/jvm)
- [并发编程](/java/concurrent)
- [Spring 生态](/java/spring)
- [AI / ML 专项路线](/roadmap/ai-ml-roadmap)
