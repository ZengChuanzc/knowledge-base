---
title: 🎯 深入 Spring MVC：如何在 HandlerInterceptor 中优雅获取 RequestBody 与 ResponseBody？
date: "2026-07-13"
tags: [Java, Spring Boot, Spring MVC, HandlerInterceptor, 日志, RequestBody, ResponseBody, 技术热点]
category: 技术热点
source: Baeldung
description: 本文揭秘如何利用 Spring MVC 的 HandlerInterceptor 拦截器，在不侵入业务代码的前提下，优雅地捕获并记录 HTTP 请求与响应体，为日志审计、调试与性能监控提供最佳实践。
author: Harpal Singh
---

# 🎯 深入 Spring MVC：如何在 HandlerInterceptor 中优雅获取 RequestBody 与 ResponseBody？

## 📝 一句话总结

本文揭秘如何利用 Spring MVC 的 HandlerInterceptor 拦截器，在不侵入业务代码的前提下，优雅地捕获并记录 HTTP 请求与响应体，为日志审计、调试与性能监控提供最佳实践。

---

## 📌 核心内容

- **问题背景**：HandlerInterceptor 默认只能获取请求头与参数，无法直接读取 RequestBody 和 ResponseBody，因为流只能被读取一次。
- **解决方案**：
  - **获取 RequestBody**：使用 `ContentCachingRequestWrapper` 包装原始请求，将输入流缓存，以便多次读取。
  - **获取 ResponseBody**：使用 `ContentCachingResponseWrapper` 包装原始响应，将输出流缓存，拦截响应内容。
- **具体实现步骤**：
  1. 在 `preHandle` 方法中，将 `HttpServletRequest` 包装为 `ContentCachingRequestWrapper`。
  2. 在 `afterCompletion` 方法中，从包装器中读取缓存的请求体。
  3. 在 `postHandle` 或 `afterCompletion` 方法中，从 `ContentCachingResponseWrapper` 读取缓存的响应体。
- **注意事项**：
  - 必须确保包装器在 Filter 链的最外层，否则流可能已被消费。
  - 对于大请求体，需考虑内存消耗，可结合限制大小或异步处理。
- **代码示例**：
  ```java
  public class LoggingInterceptor extends HandlerInterceptorAdapter {
      @Override
      public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
          HttpServletRequest wrappedRequest = new ContentCachingRequestWrapper(request);
          // 将包装后的 request 设置到当前线程
          request.setAttribute("cachedRequest", wrappedRequest);
          return true;
      }

      @Override
      public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
          ContentCachingRequestWrapper wrappedRequest = (ContentCachingRequestWrapper) request.getAttribute("cachedRequest");
          if (wrappedRequest != null) {
              String requestBody = new String(wrappedRequest.getContentAsByteArray(), request.getCharacterEncoding());
              // 记录日志
          }
      }
  }
  ```

## 🎯 为什么值得关注

- 🚀 **解决实际痛点**：许多开发者需要记录请求/响应日志用于调试或审计，但常因流不可重复读取而束手无策，本文给出了简洁有效的官方推荐方案。
- 🧩 **无侵入式设计**：利用 Spring MVC 的拦截器机制，无需修改 Controller 代码，完美契合 AOP 思想。
- 📚 **Baeldung 出品**：作为 Java 技术圈的权威教程平台，其内容可靠且经过社区验证，适合直接应用于生产。
- 🔧 **可扩展性强**：基于此思路，可轻松扩展为请求/响应的加密、脱敏、压缩等中间件。

## ✨ 技术亮点

- **新增功能**：
  - 利用 `ContentCachingRequestWrapper` 和 `ContentCachingResponseWrapper` 实现流的缓存与重复读取。
- **架构变化**：
  - 在拦截器层面引入包装器，不改变原有请求/响应处理流程，但增强了拦截器的能力。
- **性能优化**：
  - 缓存仅在需要时读取，避免不必要的内存占用；可结合 `@Profile` 或开关配置，在生产环境按需启用。
- **最佳实践**：
  - 推荐在 Filter 中尽早包装请求/响应，确保拦截器能正确获取完整内容。
  - 建议对敏感字段（如密码、Token）进行脱敏处理，防止日志泄露。
- **API 变化**：
  - 依赖 Spring 自带的 `ContentCachingRequestWrapper`（位于 `org.springframework.web.util`），无需引入第三方库。
- **兼容性**：
  - 支持 Spring MVC 4.x 及以上版本，与 Spring Boot 2.x/3.x 完全兼容。

## 💭 我的思考

作为 Java 后端工程师，我认为这篇文章非常值得学习。它解决了一个常见但容易被忽视的问题：在拦截器中读取请求/响应体。许多新手会直接尝试 `request.getInputStream()` 然后发现流为空，而本文给出了标准且优雅的解决方案。

**适用场景**：
- 统一日志记录：用于审计、调试和监控。
- 请求/响应校验：比如对请求体进行格式验证或脱敏。
- API 网关或中间件：在微服务架构中，可用于统一的请求/响应处理。

**未来趋势**：
- 随着 Observability（可观测性）的普及，这种拦截器方案会越来越重要，因为它能提供颗粒度更细的追踪数据。
- 结合 Spring Cloud Gateway 或 Zuul，可以实现更强大的网关级日志记录。

**生产环境使用建议**：
- 值得使用，但需注意：
  - 对大型请求体（如文件上传）要谨慎，避免大量内存消耗。可以设置最大缓存大小或使用异步处理。
  - 在 high-throughput 系统中，建议仅在调试模式或按需开启，避免性能损耗。
  - 注意线程安全：`ContentCachingRequestWrapper` 不是线程安全的，需确保在单个线程内使用。

**与 Spring AI / RAG 的结合**：
- 目前 Spring AI 还在早期阶段，但未来若需要记录 AI 模型的请求/响应（例如 LLM 的 prompt 和 completion），这种拦截器可以轻松扩展为 AI 服务的日志中间件。
- 结合 RAG（检索增强生成），可以记录用户查询和检索到的上下文，用于后续的调试或模型优化。

**是否值得后续写专题**：
- 非常值得！可以进一步探讨：
  - 如何结合 Spring Boot Actuator 实现动态开启/关闭日志？
  - 如何将日志输出到 ELK 或 Grafana Loki？
  - 如何对敏感数据自动脱敏？
  - 如何在 WebFlux 中实现类似功能？

总之，这是一个小而美的技巧，值得每个 Spring MVC 开发者掌握。

---

> 📎 **原文链接**: [https://feeds.feedblitz.com/~/960269651/0/baeldung~How-to-Get-The-RequestBody-and-ResponseBody-in-HandlerInterceptor](https://feeds.feedblitz.com/~/960269651/0/baeldung~How-to-Get-The-RequestBody-and-ResponseBody-in-HandlerInterceptor)

> 📅 **文章日期**: 2026-07-20
> 🏷️ **标签**: Java, Spring Boot, Spring MVC, HandlerInterceptor, 日志, RequestBody, ResponseBody, 技术热点
> 📂 **分类**: 技术热点
