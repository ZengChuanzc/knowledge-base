---
title: Google and Industry Partners Announce Agentic Resource Discovery Specification for AI Agents
date: "2026-07-14"
tags: [技术热点]
category: 技术热点
source: InfoQ
author: Leela Kumili
---

# Google and Industry Partners Announce Agentic Resource Discovery Specification for AI Agents

## 📝 一句话总结

（暂无）

---

## 📌 核心内容

```json
{
  "title": "🔥 Google 联手行业巨头发布 Agentic Resource Discovery (ARD) 规范：AI Agent 时代的“服务发现”新标准？",
  "tags": ["Java", "AI Agent", "MCP", "OpenAPI", "Google", "ARD", "服务发现", "微服务", "Spring AI"],
  "category": "技术热点",
  "one_sentence": "Google 联合行业伙伴推出 Agentic Resource Discovery (ARD) 规范，旨在为 AI Agent 提供一套基于目录和注册表的标准化资源发现与验证机制，有望成为连接 AI 能力与现有微服务生态的“服务发现”新基石。",
  "core_content": "## 核心内容\n\n- **背景**：随着 AI Agent 的兴起，Agent 需要动态发现并调用各种外部工具、API 和其他 Agent。现有的 MCP (Model Context Protocol) 和 OpenAPI 解决了“如何调用”的问题，但缺乏“如何发现”和“如何验证”的标准化机制。\n- **ARD 是什么**：Agentic Resource Discovery (ARD) 是一个开放的规范，专注于**发布、发现和验证** AI 工具、API 和 Agent 的标准化层。\n- **核心组件**：\n  - **Catalogs (目录)**：用于组织和分类可用的资源（工具、API、Agent），提供元数据描述。\n  - **Registries (注册表)**：动态注册和注销资源实例，支持实时发现和状态管理。\n- **关键特性**：\n  - **动态发现**：Agent 可以在运行时查询 Catalog 和 Registry，找到所需的能力，无需硬编码。\n  - **信任与互操作性**：规范定义了验证机制，确保发现的资源是可信的、可用的，并遵循统一标准。\n  - **与现有协议兼容**：ARD 不是要替代 MCP 或 OpenAPI，而是在它们之上构建发现层。Agent 通过 ARD 发现资源，然后使用 MCP 或 OpenAPI 执行调用。\n- **生态影响**：Google 与行业伙伴（如 Anthropic、Microsoft、OpenAI 等）共同推动，有望成为行业事实标准。",
  "why_worth": "## 为什么值得关注\n\n- **解决实际痛点**：Java 开发者在使用 Spring AI、LangChain4j 等框架开发 AI Agent 时，常常需要手动配置或硬编码 API 端点。ARD 提供了类似“Eureka + Spring Cloud Gateway”的体验，让 Agent 自动发现和调用服务。\n- **与现有微服务架构融合**：如果你的团队已经使用 Spring Boot 构建微服务，并依赖 Nacos、Consul 等做服务发现，ARD 可以看作是将这套模式扩展到 AI Agent 领域。\n- **降低开发门槛**：无需为每个 Agent 编写复杂的 API 路由和认证逻辑，ARD 的 Catalog 和 Registry 可以统一管理。\n- **提升系统鲁棒性**：动态发现机制使得 Agent 能够优雅地处理 API 的增删改，无需重启或重新部署。\n- **抢占技术先机**：AI Agent 是未来趋势，掌握 ARD 规范有助于你在团队中成为 AI 与后端融合的专家。",
  "tech_highlights": "## 技术亮点\n\n- **新增功能**：\n  - **标准化发现层**：定义了 Catalog 和 Registry 的 API 规范，包括资源的元数据格式、查询接口、注册/注销接口。\n  - **信任验证**：支持基于签名、证书或 OAuth 2.0 的资源验证，确保 Agent 不会调用恶意或伪造的 API。\n  - **动态能力协商**：Agent 可以通过 ARD 查询资源的输入/输出模式、速率限制、可用性等，实现智能路由。\n- **架构变化**：\n  - **从静态配置到动态发现**：传统 Agent 需要硬编码 API 地址，ARD 引入运行时查询机制。\n  - **分层架构**：ARD 作为发现层，MCP/OpenAPI 作为执行层，两者解耦，便于独立演进。\n- **性能优化**：\n  - **缓存与本地索引**：规范建议 Registry 支持缓存和本地索引，减少 Agent 启动时的查询延迟。\n  - **异步注册**：支持异步注册和心跳检测，避免阻塞 Agent 的初始化流程。\n- **最佳实践**：\n  - **版本管理**：Catalog 支持多版本资源，Agent 可以指定版本范围或选择最新稳定版。\n  - **健康检查**：Registry 需要集成健康检查机制，自动下线路由不可用的资源。\n- **API 变化**：\n  - **新的 API 端点**：例如 `POST /catalogs/{catalogId}/resources`、`GET /registries/{registryId}/resources?query=...`。\n  - **元数据格式**：定义了 JSON Schema 格式的资源描述，包含 `name`、`description`、`endpoint`、`authentication`、`inputSchema`、`outputSchema` 等字段。\n- **兼容性**：\n  - **与 MCP 兼容**：ARD 发现的资源可以通过 MCP 协议执行调用，MCP 的 Tool 定义可以作为 ARD 资源的一种。\n  - **与 OpenAPI 兼容**：ARD 可以包装 OpenAPI 规范，将 REST API 暴露为 Agent 可发现的资源。",
  "my_thoughts": "## 我的思考\n\n作为一名 Java 后端工程师，看到 ARD 规范发布，我的第一反应是：**这不就是 AI 时代的“Spring Cloud Netflix”吗？** 我们曾经在微服务领域用 Eureka、Consul、Nacos 解决了服务注册与发现的问题，现在 AI Agent 遇到了同样的痛点——如何让 Agent 知道有哪些工具可用、在哪里可用、是否可信。\n\n### 是否值得学习？\n**非常值得。** 即使你现在不直接开发 AI Agent，理解 ARD 也能帮助你设计更灵活、更可扩展的 API 生态。未来，你的 Spring Boot 服务大概率会被 Agent 调用，而 ARD 就是那个“Agent 访问你的 API 的门户”。\n\n### 适用于哪些场景？\n- **企业内部 AI 助手**：企业有多个内部系统（CRM、ERP、BI），通过 ARD 统一注册，让 Agent 动态发现并调用。\n- **开放平台**：像 OpenAI

## 💭 我的思考

 Plugin 那样，但更加开放和标准化。\n- **IoT 与边缘计算**：设备 Agent 需要动态发现附近的传感器或服务。\n- **MCP Server 集群**：如果你的团队维护了多个 MCP Server，ARD 可以帮你做负载均衡和故障转移。\n\n### 未来趋势？\nARD 有可能成为 AI Agent 领域的“HTTP”。就像 HTTP 定义了如何传输数据，ARD 定义了如何发现和验证资源。结合 MCP（执行层）和 OpenAPI（描述层），三剑客将构成完整的 AI 资源交互体系。\n\n### 是否值得生产环境使用？\n目前 ARD 还处于规范阶段，Google 尚未发布官方实现。但考虑到背后有 Google、Anthropic、Microsoft 等巨头支持，它很有可能成为事实标准。建议先在非关键业务或 PoC 项目中尝试，等待生态成熟后再大规模采用。\n\n### 与 Spring AI 是否有关？\n**关系密切。** Spring AI 的 `ToolCallback` 机制目前需要开发者手动配置。如果 Spring AI 未来集成 ARD，我们可以这样写：\n\n```java\n@Bean\npublic ToolCallbackProvider toolCallbackProvider(ArdRegistryClient registryClient) {\n    return () -> registryClient.queryTools(\"catalog:finance\")\n            .stream()\n            .map(ArdToolCallback::new)\n            .toList();\n}\n```\n\n这样一来，新增一个金融 API 只需在 ARD Registry 注册，Agent 自动获得调用能力，无需修改代码。\n\n### 是否可以结合 RAG？\n**绝配！** RAG 解决了“知识检索”问题，ARD 解决了“能力发现”问题。可以这样架构：\n1. 用户提问 → Agent 解析意图。\n2. Agent 通过 ARD 查询可用的工具（如“查天气”、“订机票”）。\n3. Agent 通过 RAG 从知识库中检索调用这些工具的参数（如“北京”的英文是“Beijing”）。\n4. Agent 调用工具并生成最终回答。\n\n### 是否值得后续写专题？\n**非常值得。** 我计划写一个系列：\n- 《ARD 规范深度解读：从服务发现到 AI Agent》\n- 《Spring Boot 集成 ARD：让你的 API 被 Agent 自动发现》\n- 《实战：用 ARD + Spring AI 构建智能客服系统》\n- 《ARD vs MCP vs OpenAPI：三者的关系与选择》\n\n**总结：** ARD 是 AI Agent 生态中缺失的关键拼图。作为 Java 开发者，我们拥有微服务领域丰富的服务发现经验，这恰恰是 ARD 的核心思想。抓住这个机会，将你的微服务架构经验迁移到 AI 领域，你会成为团队中不可或缺的“AI 架构师”。"
}
```

---

> 📎 **原文链接**: [https://www.infoq.com/news/2026/07/agentic-resource-discovery-spec/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global](https://www.infoq.com/news/2026/07/agentic-resource-discovery-spec/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global)

> 📅 **文章日期**: 2026-07-15
> 🏷️ **标签**: 技术热点
> 📂 **分类**: 技术热点
