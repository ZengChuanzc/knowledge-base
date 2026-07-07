# Spring AI

> Spring AI 是 Spring 生态下的 AI 应用开发框架，提供统一的 LLM 调用、RAG 支持、Tool Calling 等能力，让 Java 开发者像使用数据库一样使用 AI 模型。

---

## 一、Spring AI 概述

### 1. 定位与设计哲学

```
传统 Spring 应用：
  Controller → Service → DAO → Database

Spring AI 应用：
  Controller → Service → Spring AI → LLM API / VectorStore
```

Spring AI 并非像 LangChain 那样追求大而全，而是**延续 Spring 的核心理念**：
- **可移植性**：切换 AI 模型只需改配置（类似切换数据库）
- **声明式**：`@Retryable`、`@RateLimiter` 等注解
- **统一抽象**：`ChatClient`、`EmbeddingModel`、`VectorStore` 接口

### 2. 核心模块

```
spring-ai-core        ← 核心抽象（ChatClient, ToolCalling 等）
spring-ai-openai      ← OpenAI 模型适配
spring-ai-ollama      ← Ollama 本地模型适配
spring-ai-azure       ← Azure OpenAI 适配
spring-ai-anthropic   ← Claude 模型适配
spring-ai-mcp         ← MCP 协议支持
spring-ai-transformers ← HuggingFace Transformers 支持
spring-ai-pgvector    ← PostgreSQL pgvector 支持
spring-ai-milvus      ← Milvus 向量库支持
spring-ai-pinecone    ← Pinecone 向量库支持
spring-ai-chroma      ← Chroma 向量库支持
```

---

## 二、ChatClient —— 统一 LLM 调用

### 1. 基本使用

```java
@RestController
public class ChatController {
    
    private final ChatClient chatClient;
    
    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }
    
    @GetMapping("/chat")
    public String chat(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .call()
            .content();  // 获取文本回复
    }
}
```

### 2. Prompt 模板

```java
// 使用模板（类似 Spring 的 MessageSource）
@Service
public class AIService {
    private final ChatClient chatClient;
    
    @Value("classpath:/prompts/analysis.st")
    private Resource analysisPrompt;
    
    public String analyze(String code) {
        return chatClient.prompt()
            .user(u -> u
                .text("""
                    你是一个资深代码审查专家。
                    
                    请分析以下代码的问题：
                    
                    {code}
                    
                    请从以下维度分析：
                    1. 安全性
                    2. 性能
                    3. 可维护性
                    """)
                .param("code", code)
            )
            .call()
            .content();
    }
}
```

### 3. 流式输出（Streaming）

```java
@GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> chatStream(@RequestParam String message) {
    return chatClient.prompt()
        .user(message)
        .stream()  // 流式调用
        .content();  // 返回 Flux<String>
}
```

### 4. 结构化输出

```java
// 定义输出结构
public record AnalysisResult(
    @JsonProperty("issues") List<Issue> issues,
    @JsonProperty("score") int score
) {
    public record Issue(String type, String description, String severity) {}
}

// 使用结构化输出
@GetMapping("/analyze")
public AnalysisResult analyze(@RequestParam String code) {
    return chatClient.prompt()
        .user(u -> u.text("分析代码:\n{code}").param("code", code))
        .call()
        .entity(AnalysisResult.class);  // 自动解析 LLM 输出为 POJO
}
```

### 5. 多模态支持

```java
// Spring AI 支持图片+文本的多模态输入
@PostMapping("/analyze-image")
public String analyzeImage(@RequestParam String imageUrl, @RequestParam String question) {
    return chatClient.prompt()
        .user(u -> u
            .text(question)
            .media(MediaType.IMAGE_PNG, imageUrl)  // 附加图片
        )
        .call()
        .content();
}
```

---

## 三、Tool Calling（函数调用）

### 1. 定义工具

```java
@Component
@Description("获取天气信息")  // 工具描述（重要！LLM 靠描述理解工具用途）
public class WeatherFunction implements ToolCallback {
    
    @Override
    @Description("根据城市名查询当前天气")
    public String call(String cityName) {
        return weatherService.getWeather(cityName);
    }
    
    @Override
    public String getDescription() {
        return "获取指定城市的当前天气信息，输入城市名称";
    }
    
    @Override
    public String getName() {
        return "getWeather";
    }
    
    @Override
    public String getInputTypeSchema() {
        return """
            {
                "type": "object",
                "properties": {
                    "cityName": {
                        "type": "string",
                        "description": "城市名称，如北京、上海"
                    }
                },
                "required": ["cityName"]
            }
            """;
    }
}
```

### 2. 使用 @Tool 注解（Spring AI 1.0+）

```java
@Service
public class OrderAgent {
    
    @Tool("根据订单号查询订单状态")
    public String queryOrderStatus(String orderId) {
        return orderRepository.findStatusById(orderId);
    }
    
    @Tool("取消指定订单（需要用户确认）")
    public String cancelOrder(String orderId) {
        orderRepository.cancel(orderId);
        return "订单 " + orderId + " 已取消";
    }
}
```

### 3. 将 Tool 注入 ChatClient

```java
@Bean
public ChatClient chatClient(ChatClient.Builder builder, List<ToolCallback> tools) {
    return builder
        .defaultTools(tools)  // 注册所有可用的 Tool
        .defaultSystem("你是一个智能助手，调用工具回答用户问题")
        .build();
}
```

::: warning @Tool 方法注意事项
- 方法签名不能太复杂（建议 `String → String`，让框架做 JSON 序列化/反序列化）
- 方法名即工具名，确保语义清晰
- **@Description 注解至关重要**——LLM 靠此判断何时调用哪个工具
- 工具调用是**有副作用**的操作，确保幂等性或添加确认步骤
:::

---

## 四、RAG 支持

### 1. 文档读取（DocumentReader）

```java
// 支持多种文档格式
@Bean
public DocumentReader pdfReader() {
    return new PagePdfDocumentReader("classpath:/docs/manual.pdf");
    // 也支持：JsonDocumentReader, TextDocumentReader, 
    //         MarkdownDocumentReader, HtmlDocumentReader
}
```

### 2. 文档切分（DocumentTransformer）

```java
@Bean
public DocumentTransformer textSplitter() {
    return TokenTextSplitter.builder()
        .withChunkSize(500)          // 每块 token 数
        .withChunkOverlap(50)        // 重叠 token 数
        .withSeparators("\n\n", "\n", ".", " ", "")
        .build();
}
```

### 3. VectorStore 配置

```java
@Configuration
public class RAGConfig {
    
    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel, DataSource dataSource) {
        return new PgVectorStore(
            dataSource,
            embeddingModel,
            PgVectorStore.PgIndexType.HNSW  // 使用 HNSW 索引
        );
    }
    
    @Bean
    public EmbeddingModel embeddingModel() {
        // OpenAI Embedding
        return new OpenAiEmbeddingModel();
        // 或本地部署：new OllamaEmbeddingModel().withModel("bge-large-zh-v1.5");
    }
}
```

### 4. RAG 完整链路

```java
@Service
public class RAGService {
    
    private final ChatClient chatClient;
    
    public RAGService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
            .defaultAdvisors(new QuestionAnswerAdvisor(vectorStore))  // RAG Advisor
            .build();
    }
    
    public String ask(String question) {
        return chatClient.prompt()
            .user(question)
            .advisors(a -> a
                .param("retrievalTopK", 5)      // 检索 Top-K
                .param("retrievalThreshold", 0.5)  // 相似度阈值
            )
            .call()
            .content();
    }
}
```

### 5. RAG 相关的 Advisors

| Advisor | 作用 | 说明 |
|---------|------|------|
| `QuestionAnswerAdvisor` | 向量检索 + 上下文注入 | 最常用，自动执行 RAG |
| `VectorStoreChatMemoryAdvisor` | 对话历史管理 | 多轮对话中的历史管理 |
| `PromptChatMemoryAdvisor` | Prompt 级记忆 | 在 Prompt 中注入历史 |
| `RetrievalAugmentationAdvisor` | 高级检索增强 | 可定制检索流程 |

---

## 五、Advisors（拦截器）

Advisor 是 Spring AI 的**洋葱式拦截器链**，类似 Spring MVC 的 Interceptor。

```
User → Advisor 1 → Advisor 2 → LLM → Advisor 2 → Advisor 1 → Response
           ↑                                          ↓
        鉴权/日志/限流                             结果增强/格式化
```

### 自定义 Advisor

```java
@Component
public class LoggingAdvisor implements CallAroundAdvisor {
    
    @Override
    public String getName() {
        return "LoggingAdvisor";
    }
    
    @Override
    public int getOrder() {
        return 1;
    }
    
    @Override
    public AdvisorResponse aroundCall(AdvisorSpec advisorSpec) {
        String userText = advisorSpec.getUserText();
        log.info("用户输入: {}", userText);
        
        long start = System.currentTimeMillis();
        AdvisorResponse response = advisorSpec.next();  // 继续调用链
        long cost = System.currentTimeMillis() - start;
        
        log.info("LLM 耗时: {}ms, 输出长度: {}", cost, 
                 response.content().length());
        return response;
    }
}
```

---

## 六、生产配置与踩坑

### 1. application.yml 配置

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.7
          max-tokens: 2048
      embedding:
        options:
          model: text-embedding-3-small
    
    retry:
      max-attempts: 3
      backoff:
        initial-interval: 1000ms
        multiplier: 2
        max-interval: 10000ms
    
    vectorstore:
      pgvector:
        index-type: HNSW
        distance-type: COSINE_DISTANCE
        dimensions: 1536
```

### 2. 重试与降级

```java
@Configuration
public class AIConfig {
    
    @Bean
    public ChatClient chatClient(ChatClient.Builder builder) {
        return builder
            .defaultSystem("你是一个 AI 助手")
            // 自动重试
            .defaultAdvisors(new RetryAdvisor(3, Duration.ofSeconds(30)))
            // 限流保护
            .defaultAdvisors(new RateLimiterAdvisor(10, Duration.ofSeconds(1)))
            .build();
    }
}
```

### 3. 常见踩坑

::: danger Spring AI 生产踩坑

| # | 问题 | 原因 | 解决方案 |
|---|------|------|---------|
| 1 | **Tool 方法未被调用** | @Description 缺失或不清晰 | 检查工具描述是否准确，LLM 需要靠描述理解工具用途 |
| 2 | **结构化输出解析失败** | LLM 输出格式不符合预期 | 降低 temperature 到 0；检查 @JsonProperty 映射 |
| 3 | **流式输出中断** | 网络超时或 API 限制 | 增加 timeout；实现重试逻辑 |
| 4 | **Token 超限** | 输入 + 输出超过模型限制 | 设置 maxTokens；使用 TokenTextSplitter 截断 |
| 5 | **向量检索结果为空** | Embedding 维度不匹配 | 确保 VectorStore 维度与 Embedding 模型一致 |
| 6 | **@Tool 方法线程安全问题** | 单例 Bean 中有状态字段 | 确保 Tool 实现是无状态的 |
| 7 | **Spring AI 版本兼容问题** | 框架迭代快，API 变化大 | 固定版本，参考 Migration Guide |
| 8 | **LLM API 密钥泄露** | 代码仓库中硬编码 | 使用环境变量 + 密钥管理服务 |

```java
// ✅ 安全的 Tool 实现（无状态）
@Component
public class SafeTool implements ToolCallback {
    // 不要在这里放有状态字段！
    
    @Override
    public String call(String input) {
        // 每次调用都是独立的
        return externalService.query(input);
    }
}

// ❌ 不安全的 Tool 实现
@Component
public class UnsafeTool implements ToolCallback {
    private int callCount = 0;  // 多个请求共享，线程不安全
    
    @Override
    public String call(String input) {
        callCount++;  // 并发问题！
        return "调用 #" + callCount;
    }
}
```
:::

### 4. 监控与指标

```java
@Configuration
public class AIMonitoringConfig {
    
    @Bean
    public CallAroundAdvisor metricsAdvisor(MeterRegistry meterRegistry) {
        return new CallAroundAdvisor() {
            @Override
            public String getName() { return "MetricsAdvisor"; }
            
            @Override
            public AdvisorResponse aroundCall(AdvisorSpec advisorSpec) {
                Timer.Sample sample = Timer.start(meterRegistry);
                try {
                    AdvisorResponse response = advisorSpec.next();
                    sample.stop(Timer.builder("ai.chat.duration")
                        .tag("model", advisorSpec.getModel())
                        .register(meterRegistry));
                    return response;
                } catch (Exception e) {
                    meterRegistry.counter("ai.chat.errors").increment();
                    throw e;
                }
            }
        };
    }
}
```

---

## 七、与 LangChain 对比

| 维度 | Spring AI | LangChain (Python) |
|------|-----------|-------------------|
| 语言 | Java | Python |
| 生态整合 | Spring 生态（JPA、Security、Cloud） | Python ML 生态（PyTorch、HuggingFace） |
| 学习曲线 | 低（Spring 开发者友好） | 中（Python 开发者友好） |
| 可移植性 | 强（换模型只需改配置） | 中（不同模型适配器有差异） |
| Agent 能力 | 基础（Tool Calling） | 丰富（Support Agent、Plan-and-Execute） |
| 社区规模 | 较小（但增长快） | 巨大 |
| 适用场景 | 企业 Java 项目集成 AI | 快速原型、复杂 AI 逻辑 |

**选型建议**：
- 已有 Spring Boot 项目 → **Spring AI**（集成成本最低）
- 需要复杂 Agent 编排 → LangChain（更成熟）
- 两者可以互补：Spring AI 处理 Java 侧，LangChain 处理复杂 AI 逻辑

---

## 八、面试高频问题

### Q1：Spring AI 的核心设计理念是什么？

**答**：
Spring AI 延续 Spring 生态的核心理念——**统一抽象 + 可移植性**。通过 `ChatClient`、`EmbeddingModel`、`VectorStore` 等接口，让开发者可以像切换数据库一样切换 AI 模型。底层 LLM API 的差异被框架封装，业务代码只需面向接口编程。

### Q2：Spring AI 中 Tool Calling 的工作原理？

**答**：
1. 开发者用 `@Tool` 或 `ToolCallback` 定义工具（包括名称、描述、输入 Schema）
2. LLM 在生成回复时，判断需要调用某个工具并输出函数调用请求（JSON 格式）
3. Spring AI 框架解析请求，调用对应的 Java 方法
4. 工具返回结果被注入到对话上下文中
5. LLM 基于工具结果生成最终回复

**关键点**：工具的描述（`@Description`）质量直接影响 LLM 是否正确地调用工具。

### Q3：Spring AI 如何实现 RAG？

**答**：
通过 `QuestionAnswerAdvisor`（一种 Advisor）实现。流程：
1. 用户查询 → Advisor 拦截
2. Advisor 调用 VectorStore 做向量检索，获取相关文档片段
3. 检索结果注入到 Prompt 的 System Message 中
4. LLM 基于注入的上下文生成回答

开发者只需配置 VectorStore + EmbeddingModel，Advisor 自动管理整个检索-增强-生成流程。

### Q4：Advisors 的作用是什么？

**答**：
Advisors 是 Spring AI 的拦截器链，类似 Spring MVC 的 Interceptor 或 Java 的 Filter。它们可以**在调用 LLM 前后**执行自定义逻辑，如：
- `QuestionAnswerAdvisor`：注入 RAG 检索结果
- `RetryAdvisor`：自动重试
- `RateLimiterAdvisor`：限流保护
- 自定义：日志、监控、鉴权、输入校验、输出过滤

### Q5：Spring AI 相比直接调用 LLM API 的优势？

**答**：
1. **统一抽象**：切换模型（OpenAI → Ollama）只需改配置，不改业务代码
2. **结构化输出**：`chatClient.call().entity(RecordClass.class)` 自动解析
3. **Tool 管理**：声明式工具定义 + 自动注册
4. **RAG 集成**：`QuestionAnswerAdvisor` 零配置 RAG
5. **Spring 生态整合**：事务、安全、监控、配置等开箱即用
6. **重试/降级**：内置的重试、限流、熔断机制

---

## 参考文章与推荐阅读

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [Spring AI GitHub](https://github.com/spring-projects/spring-ai)
- [Spring AI 1.0.0 发布说明](https://spring.io/blog/2025/01/16/spring-ai-1-0-0)
- [Spring AI Reference — Tool Calling](https://docs.spring.io/spring-ai/reference/api/tool-calling.html)
- [Spring AI Reference — ChatClient](https://docs.spring.io/spring-ai/reference/api/chatclient.html)
- [Baeldung — Spring AI 入门教程](https://www.baeldung.com/spring-ai)
- [Spring AI — Vector Store 支持](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)

---

## 相关文章

- [LLM 基础](/ai-agent/llm-basic)
- [RAG 系统](/ai-agent/rag)
- [MCP 协议](/ai-agent/mcp)
