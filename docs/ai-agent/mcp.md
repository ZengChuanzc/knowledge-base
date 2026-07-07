# MCP 协议

> MCP（Model Context Protocol）是 Anthropic 提出的开放协议，用于标准化 AI 模型与外部工具/数据源之间的交互。它相当于"AI 应用的 USB-C 接口"——让 LLM 以统一方式访问任何工具和数据。

---

## 一、MCP 概述

### 1. 为什么需要 MCP？

在 MCP 之前，让 LLM 使用工具的模式是**碎片化**的：

```
传统方式（每个工具一种集成方式）：
LLM ──→ LangChain Tool ──→ API A
    └──→ Semantic Kernel Plugin ──→ API B
    └──→ 自研 Adapter ──→ API C
    └──→ Spring AI Tool ──→ API D

MCP 方式（统一标准）：
LLM ──→ MCP Client ──→ MCP Server A
                     └──→ MCP Server B
                     └──→ MCP Server C
                     └──→ MCP Server D (全部统一协议)
```

| 问题 | 传统方案 | MCP 方案 |
|------|---------|---------|
| **集成成本** | 每个工具单独开发适配器 | 一次 MCP Server 开发，所有 Client 通用 |
| **协议多样性** | REST/gRPC/WebSocket/CLI/…… | 统一 JSON-RPC 协议 |
| **工具发现** | 文档/硬编码 | `listTools` 动态发现 |
| **多框架支持** | 每个框架各自实现 | Claude/LangChain/Spring AI 均可接入 |

### 2. 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                    Host（宿主应用）                           │
│  Claude Desktop / VS Code / IntelliJ / 自研应用              │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Protocol (JSON-RPC)
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐     ┌─────────────────────────┐
│   MCP Client        │     │   MCP Client (进程内)    │
│   (SDK 实现)        │     │   (SDK 实现)             │
└─────────┬───────────┘     └───────────┬─────────────┘
          │                             │
          ▼                             ▼
┌─────────────────────┐     ┌─────────────────────────┐
│    MCP Server A     │     │    MCP Server B          │
│  (文件系统访问)      │     │  (数据库查询)             │
└─────────────────────┘     └─────────────────────────┘
```

| 角色 | 说明 | 示例 |
|------|------|------|
| **Host** | 用户直接使用的应用 | Claude Desktop、VS Code、IDE |
| **Client** | 与 MCP Server 建立连接的 SDK | `@modelcontextprotocol/sdk` |
| **Server** | 暴露工具/资源的服务 | `mcp-server-filesystem`、`mcp-server-sqlite` |

---

## 二、MCP 协议核心

### 1. 通信方式

MCP 使用 **JSON-RPC 2.0** 协议，支持两种传输层：

| 传输方式 | 适用场景 | 特点 |
|---------|---------|------|
| **stdio** | 本地进程启动 | 零配置，通过标准输入输出通信 |
| **SSE** (Server-Sent Events) | 远程服务 | 通过 HTTP 通信，支持远程部署 |

```
// stdio 模式（最简单）
Host ←→ Client(进程内) ←→ stdio ←→ MCP Server(子进程)

// SSE 模式（远程）
Host ←→ Client(进程内) ←→ HTTP ←→ MCP Server(远程服务)
```

### 2. 核心方法

```
Client → Server 的请求：

// 初始化
initialize → 协商协议版本和能力

// 工具相关
tools/list     → 获取可用工具列表
tools/call     → 调用指定工具

// 资源相关
resources/list   → 获取可用资源列表
resources/read   → 读取指定资源

// 提示（Prompt）相关
prompts/list     → 获取可用提示模板列表
prompts/get      → 获取指定提示模板
```

### 3. 协议能力

MCP 定义了三种核心**原语（Primitives）**：

| 原语 | 作用 | 类比 | 示例 |
|------|------|------|------|
| **Tools**（工具） | LLM 可以调用的函数 | API Endpoint | 查询天气、计算器、发邮件 |
| **Resources**（资源） | 可供读取的数据 | 文件/API 数据 | 数据库记录、日志文件、API 响应 |
| **Prompts**（提示模板） | 可复用的 Prompt 模板 | 代码片段 | 代码审查模板、翻译模板 |

#### Tools（工具）——提供给 LLM 调用的函数

```json
// tools/list 响应
{
  "tools": [
    {
      "name": "get_weather",
      "description": "获取指定城市的天气信息",
      "inputSchema": {
        "type": "object",
        "properties": {
          "city": { "type": "string", "description": "城市名" }
        },
        "required": ["city"]
      }
    }
  ]
}

// tools/call 请求
{
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": { "city": "北京" }
  }
}

// tools/call 响应
{
  "content": [
    { "type": "text", "text": "北京：25°C，晴" }
  ]
}
```

#### Resources（资源）——供 LLM 读取的数据

```json
// resources/list 响应
{
  "resources": [
    {
      "uri": "file:///logs/app.log",
      "name": "应用日志",
      "mimeType": "text/plain"
    }
  ]
}

// resources/read 请求
{
  "method": "resources/read",
  "params": {
    "uri": "file:///logs/app.log"
  }
}
```

#### Prompts（提示模板）——可复用的 Prompt 模板

```json
// prompts/list 响应
{
  "prompts": [
    {
      "name": "code_review",
      "description": "代码审查模板",
      "arguments": [
        { "name": "code", "description": "代码内容", "required": true }
      ]
    }
  ]
}
```

---

## 三、开发 MCP Server

### 1. Python SDK

```python
# mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("weather-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="获取指定城市的天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                },
                "required": ["city"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments["city"]
        weather = await weather_service.query(city)
        return [TextContent(type="text", text=str(weather))]
    raise ValueError(f"Unknown tool: {name}")

# 启动（stdio 模式）
if __name__ == "__main__":
    app.run(stdio_server())
```

### 2. TypeScript SDK

```typescript
// mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "weather-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "get_weather",
    description: "获取指定城市的天气信息",
    inputSchema: {
      type: "object",
      properties: {
        city: { type: "string", description: "城市名称" },
      },
      required: ["city"],
    },
  }],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_weather") {
    const { city } = request.params.arguments;
    const weather = await getWeather(city);
    return { content: [{ type: "text", text: JSON.stringify(weather) }] };
  }
  throw new Error("Unknown tool");
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3. Java SDK（基于 Spring AI MCP）

```java
// Spring Boot MCP Server 示例
@SpringBootApplication
@EnableMcpServer  // 启用 MCP Server
public class McpServerApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(McpServerApplication.class, args);
    }
    
    @Bean
    public ToolCallback weatherTool(WeatherService weatherService) {
        return new ToolCallback() {
            @Override
            public String getName() { return "get_weather"; }
            
            @Override
            public String getDescription() { return "获取天气信息"; }
            
            @Override
            public String call(String arguments) {
                // arguments 是 JSON 字符串，包含 city 参数
                String city = extractCity(arguments);
                return weatherService.getWeather(city);
            }
        };
    }
}
```

### 4. 用配置文件注册 MCP Server

```json
// Claude Desktop 配置（~/.claude/claude_desktop_config.json）
{
  "mcpServers": {
    "file-system": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/path/to/data.db"]
    },
    "custom-server": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

---

## 四、MCP Server 最佳实践

### 1. 工具设计原则

```python
# ✅ 好的工具设计
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_jira_ticket",      # 命名：动词+名词，清晰
            description="创建 Jira 工单"，    # 描述：说明做什么
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "项目 KEY (如 PROJ)"},
                    "summary": {"type": "string", "description": "工单标题"},
                    "priority": {"type": "string", "enum": ["高", "中", "低"]},
                },
                "required": ["project", "summary"],
            },
        )
    ]
```

| 原则 | 说明 |
|------|------|
| **单一职责** | 一个工具只做一件事 |
| **命名清晰** | `动词_名词` 格式，一看就知道做什么 |
| **描述准确** | LLM 通过描述判断何时调用，描述质量>工具实现 |
| **参数简洁** | 必要参数设 required，可选参数有 defaults |
| **错误处理** | 返回友好错误信息而非异常 |
| **幂等考虑** | 写操作尽量幂等，或需要确认步骤 |

### 2. 安全考虑

::: danger MCP Server 安全要点

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| **命令注入** | 参数中嵌入恶意命令 | 参数校验 + 白名单机制 |
| **路径遍历** | 通过 `../` 访问未授权文件 | 路径规范化 + 根目录限制 |
| **数据泄露** | 返回敏感数据给 LLM | 输出过滤 + 脱敏处理 |
| **资源耗尽** | 大量消耗计算/存储 | 限流 + 超时限制 |
| **权限滥用** | 工具执行超过必要权限 | 最小权限原则 |

```python
# ✅ 安全的文件系统工具
@app.call_tool()
async def read_file(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_file":
        filepath = arguments["path"]
        # 安全措施：路径规范化 + 限制在允许目录内
        normalized = os.path.normpath(os.path.join(ALLOWED_DIR, filepath))
        if not normalized.startswith(ALLOWED_DIR):
            return [TextContent(type="text", text="错误：不允许访问此路径")]
        # ... 读取文件
```
:::

### 3. 测试 MCP Server

```bash
# 用 MCP Inspector 调试（可视化测试）
npx @modelcontextprotocol/inspector python mcp_server.py

# 用命令行测试
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py

# 或不用 Host 直接集成测试
from mcp import ClientSession, StdioServerParameters

async def test_server():
    async with ClientSession(stdio_server()) as session:
        tools = await session.list_tools()
        assert len(tools) > 0
        
        result = await session.call_tool("get_weather", {"city": "北京"})
        assert "北京" in result.content[0].text
```

---

## 五、MCP 生态与对比

### 1. 官方 MCP Servers

Anthropic 提供了一系列官方预构建 MCP Server：

| Server | 用途 | 安装 |
|--------|------|------|
| `server-filesystem` | 文件系统访问 | `npx @modelcontextprotocol/server-filesystem <dir>` |
| `server-github` | GitHub API | `npx @modelcontextprotocol/server-github` |
| `server-postgres` | PostgreSQL 查询 | `npx @modelcontextprotocol/server-postgres <conn-str>` |
| `server-sqlite` | SQLite 查询 | `uvx mcp-server-sqlite --db-path <path>` |
| `server-puppeteer` | 浏览器自动化 | `npx @modelcontextprotocol/server-puppeteer` |
| `server-slack` | Slack 消息 | `npx @modelcontextprotocol/server-slack` |
| `server-google-maps` | 地图服务 | `npx @modelcontextprotocol/server-google-maps` |

### 2. MCP vs 其他协议

| 维度 | MCP | OpenAI Function Calling | LangChain Tool |
|------|-----|----------------------|---------------|
| **开放性** | 开放协议（开源） | 供应商锁定 | 开源框架 |
| **协议标准** | 统一（JSON-RPC） | 供应商特定 | 框架特定 |
| **传输层** | stdio / SSE | HTTP | 内存调用 |
| **工具发现** | `tools/list` | 需预定义 | 代码注册 |
| **Host 无关** | 任何 LLM 应用可用 | 仅 OpenAI | 仅 LangChain |
| **资源/Prompt** | 支持 | 不支持 | 不支持 |
| **适用场景** | 跨框架工具复用 | OpenAI 生态 | LangChain 生态 |

### 3. 框架支持情况

| 框架 | MCP 支持状态 | 说明 |
|------|------------|------|
| **Claude Desktop** | ✅ 原生支持 | 通过 `claude_desktop_config.json` 配置 |
| **VS Code** | ✅ 内置（VS Code 1.99+） | Cline / Continue 等插件支持 |
| **LangChain** | ✅ `mcp` 集成包 | `langchain-mcp-adapters` |
| **Spring AI** | ✅ 支持 | `spring-ai-mcp` 模块 |
| **OpenAI Agents SDK** | ✅ 支持 | 社区适配 |
| **IntelliJ IDEA** | ✅ 支持 | IDE 插件集成 |

---

## 六、面试高频问题

### Q1：MCP 是什么？解决了什么问题？

**答**：
MCP（Model Context Protocol）是 Anthropic 提出的开放协议，**标准化 AI 模型与外部工具/数据源的交互方式**。它解决了"AI 工具集成的碎片化问题"——在此之前，每个框架（LangChain、Spring AI、Semantic Kernel）都有自己的工具定义方式，每个工具都要做多次适配。

MCP 让工具开发者**一次开发 Server，所有 AI 应用通用**，类似 USB-C 接口的标准化作用。

### Q2：MCP 的核心原语有哪些？

**答**：
三种原语：
1. **Tools（工具）**：LLM 可调用的函数，有输入 Schema 约束
2. **Resources（资源）**：LLM 可读取的数据（类似 REST 的 GET）
3. **Prompts（提示模板）**：可复用的 Prompt 模板

其中 Tools 是最常用的原语，也是 MCP 最大的价值所在。

### Q3：MCP 与 OpenAI Function Calling 的区别？

**答**：
- **OpenAI Function Calling** 是供应商特定的工具调用方式，只能用于 OpenAI 模型
- **MCP 是开放协议**，不依赖任何模型供应商。Claude、GPT、开源模型都可以使用
- MCP 还支持 Resources 和 Prompts 等 Function Calling 没有的原语
- Function Calling 是 OpenAI API 的一部分，MCP 是独立于模型的工具层

### Q4：如何开发一个 MCP Server？

**答**：
1. 选择 SDK（Python/TypeScript/Java）
2. 实现 `list_tools` 返回工具列表（含名称、描述、输入 Schema）
3. 实现 `call_tool` 处理工具调用逻辑
4. 通过 stdio 或 SSE 启动
5. 在 Host（如 Claude Desktop）的配置文件中注册即可

### Q5：MCP 的典型应用场景？

**答**：
- **文件系统操作**：LLM 读取/编辑本地文件（VS Code Cline 用此实现代码修改）
- **数据库查询**：LLM 通过 Postgres/SQLite Server 查询数据库
- **API 集成**：LLM 调用 GitHub、Slack、Jira 等外部服务
- **浏览器自动化**：LLM 控制浏览器做页面操作
- **自定义内部工具**：企业内部系统的 AI 访问（权限审批、工单查询等）

---

## 参考文章与推荐阅读

- [MCP 官方文档 — Anthropic](https://modelcontextprotocol.io/)
- [MCP 规范 (GitHub)](https://github.com/modelcontextprotocol/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Anthropic 博客 — Introducing MCP](https://www.anthropic.com/news/model-context-protocol)
- [MCP 官方 Server 列表](https://github.com/modelcontextprotocol/servers)
- [Spring AI MCP 支持](https://docs.spring.io/spring-ai/reference/api/mcp.html)
- [MCP Inspector — 调试工具](https://github.com/modelcontextprotocol/inspector)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

---

## 相关文章

- [LLM 基础](/ai-agent/llm-basic)
- [RAG 系统](/ai-agent/rag)
- [Spring AI](/ai-agent/spring-ai)
