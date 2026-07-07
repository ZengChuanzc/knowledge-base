---
outline: deep
---

# JDK 版本特性 (8~21)

> 从 JDK 8 到 JDK 21，Java 以每半年一个版本的节奏快速演进。本文梳理各版本的核心新特性，帮助快速了解 Java 语言的现代化进程。

::: tip 版本发布节奏
JDK 8 之后 Java 采用**每半年发布一个版本**的节奏（3月、9月），每 3 年发布一个 **LTS（长期支持）** 版本。
当前主要 LTS 版本：**8、11、17、21**。
:::

---

## JDK 8 (LTS) — 2014.03

> 里程碑式版本，开启了 Java 函数式编程时代。

### 核心特性

| 特性 | 说明 |
|------|------|
| **Lambda 表达式** | `(params) -> expression` 语法，简化匿名内部类 |
| **函数式接口** | `@FunctionalInterface`，如 `Predicate`、`Consumer`、`Function` |
| **Stream API** | 集合的函数式操作：`filter`、`map`、`reduce`、`collect` |
| **Optional 类** | 优雅处理 NullPointerException |
| **新的日期时间 API** | `java.time` 包：`LocalDate`、`LocalDateTime`、`Instant` |
| **接口默认方法** | `default` 和 `static` 方法 |
| **方法引用** | `::` 操作符：`Class::staticMethod`、`object::instanceMethod` |
| **CompletableFuture** | 异步编程组合式 API |
| **Nashorn 引擎** | JavaScript 运行时引擎 |
| **PermGen 移除** | 元空间（Metaspace）取代永久代 |

### 示例

```java
// Lambda + Stream
list.stream()
    .filter(s -> s.startsWith("A"))
    .map(String::toUpperCase)
    .forEach(System.out::println);
```

---

## JDK 9 — 2017.09

### 核心特性

| 特性 | 说明 |
|------|------|
| **模块化系统 (JPMS)** | `module-info.java`，实现 JDK 自身模块化 |
| **JShell** | 交互式 REPL 工具 |
| **集合工厂方法** | `List.of()`、`Set.of()`、`Map.of()` |
| **私有接口方法** | 接口中支持 `private` 方法 |
| **改进的 Stream API** | `takeWhile`、`dropWhile`、`ofNullable` |
| **Optional 增强** | `ifPresentOrElse`、`stream`、`or` |
| **进程 API** | `ProcessHandle` 获取进程信息 |
| **HTTP Client (孵化)** | `java.net.http` 模块 |
| **多版本 JAR** | 同一 JAR 支持不同 JDK 版本运行 |

---

## JDK 10 — 2018.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **局部变量类型推断** | `var` 关键字：`var list = new ArrayList<String>();` |
| **不可变集合改进** | `List.copyOf()`、`Collectors.toUnmodifiableList()` |
| **并行全 GC (G1)** | G1 垃圾收集器并行 Full GC |
| **应用类数据共享** | CDS 扩展到应用类 |
| **线程本地握手** | 无需全局安全点即可执行线程回调 |

---

## JDK 11 (LTS) — 2018.09

> 从 Oracle 迁移到 OpenJDK 的里程碑，Long Term Support 版本。

### 核心特性

| 特性 | 说明 |
|------|------|
| **HTTP Client 标准化** | `java.net.http.HttpClient` 正式可用 |
| **String 增强** | `isBlank`、`lines`、`strip`、`repeat` |
| **Files 增强** | `readString`、`writeString` |
| **Lambda 参数局部变量语法** | lambda 表达式中使用 `var` |
| **嵌套访问控制** | 反射支持嵌套类私有成员访问 |
| **飞行记录器 (JFR)** | 低开销的事件监控框架 |
| **Epsilon GC** | 无操作垃圾收集器（性能测试用） |
| **ZGC (实验性)** | 低延迟可伸缩垃圾收集器 |
| **移除 Java EE 模块** | CORBA、JAX-WS 等移除 |

### 示例

```java
// HTTP Client
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .build();
client.sendAsync(request, BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .thenAccept(System.out::println);

// String 增强
"  hello  ".strip();             // "hello"
"abc".repeat(3);                 // "abcabc"
"a\nb\nc".lines().count();       // 3
```

---

## JDK 12 — 2019.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **Switch 表达式 (预览)** | 箭头语法：`case "A" -> 1` |
| **Shenandoah GC (实验性)** | 低暂停时间垃圾收集器 |
| **G1 改进** | 可中止的混合收集、及时返回未用内存 |
| **微基准测试套件** | JMH 基准测试 |

---

## JDK 13 — 2019.09

### 核心特性

| 特性 | 说明 |
|------|------|
| **文本块 (预览)** | `"""` 多行字符串 |
| **Switch 表达式增强** | `yield` 返回值 |
| **ZGC 增强** | 未用内存返回操作系统 |
| **Socket API 重构** | 新的底层实现 |

### 示例

```java
// 文本块
String html = """
    <html>
        <body>
            <h1>Hello, World!</h1>
        </body>
    </html>
    """;
```

---

## JDK 14 — 2020.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **Switch 表达式 (正式)** | 标准化的 Switch 表达式 |
| **Records (预览)** | `record Point(int x, int y) { }` |
| **Pattern Matching for instanceof (预览)** | `if (obj instanceof String s)` |
| **NPE 消息改进** | 精准提示哪个变量为 null |
| **打包工具 (Incubating)** | `jpackage` 打包为原生安装包 |
| **G1 改进** | 优化大对象的分配与回收 |

### 示例

```java
// Switch 表达式
int num = switch (day) {
    case MONDAY, FRIDAY -> 6;
    case TUESDAY         -> 7;
    default -> {
        int len = day.toString().length();
        yield len;
    }
};

// instanceof 模式匹配
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.length());
}
```

---

## JDK 15 — 2020.09

### 核心特性

| 特性 | 说明 |
|------|------|
| **文本块 (正式)** | 多行字符串标准化 |
| **密封类 (预览)** | `sealed`、`permits` 关键字 |
| **Pattern Matching 二次预览** | instanceof 模式匹配改进 |
| **Records 二次预览** | 支持局部 record 等增强 |
| **ZGC (正式)** | 生产可用 |
| **Shenandoah GC (正式)** | 生产可用 |
| **禁用偏向锁** | 默认禁用偏向锁 |
| **Edwards-Curve 数字签名** | EdDSA 签名算法 |

---

## JDK 16 — 2021.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **Records (正式)** | `record` 类标准化 |
| **Pattern Matching for instanceof (正式)** | 正式可用 |
| **密封类二次预览** | 增强的密封类 |
| **Stream API 增强** | `Stream.toList()` 便捷方法 |
| **Vector API (孵化)** | 向量计算 API |
| **Unix 域套接字** | 支持 Unix Domain Socket |
| **日期的时段支持** | `DayPeriod` 支持 |
| **弹性元空间** | 可归还未用内存给操作系统 |

### 示例

```java
// Record
public record Point(int x, int y) { }

// 使用
var p = new Point(3, 4);
System.out.println(p.x());  // 自动生成访问器

// Stream.toList()
var result = stream.filter(s -> s.length() > 3).toList();
```

---

## JDK 17 (LTS) — 2021.09

> 下一个重要 LTS 版本，也是 Spring Boot 3.x 的基线版本。

### 核心特性

| 特性 | 说明 |
|------|------|
| **密封类 (正式)** | `sealed` 类层次结构控制 |
| **Pattern Matching for switch (预览)** | Switch 中的模式匹配 |
| **伪随机数生成器** | 新的随机数 API |
| **恢复始终严格的浮点语义** | `strictfp` 不再需要 |
| **Context-Specific 反序列化过滤器** | `JEP 415` |
| **增强的伪随机数** | `RandomGenerator` 接口 |
| **Applet API 弃用** | Applet 标记为弃用 |
| **Vector API (二次孵化)** | 向量计算 API |
| **外部函数与内存 API (孵化)** | `Foreign Function & Memory API` |
| **移除实验性 AOT/JIT 编译器** | Graal JIT 实验特性移除 |

### 示例

```java
// 密封类
public sealed class Shape
    permits Circle, Rectangle, Triangle { }

final class Circle extends Shape { }
final class Rectangle extends Shape { }
final class Triangle extends Shape { }
```

---

## JDK 18 — 2022.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **默认 UTF-8 编码** | 文件 I/O 默认 UTF-8 |
| **简易 Web 服务器** | `jwebserver` 静态文件服务器 |
| **简单 Javadoc 片段** | `@snippet` 注解 |
| **方法句柄反射优化** | `MethodHandle` 性能提升 |
| **Vector API (三次孵化)** | 向量计算 API |
| **外部函数与内存 API (二次孵化)** | FFI API |
| **Pattern Matching for switch (二次预览)** | 改进 |

---

## JDK 19 — 2022.09

### 核心特性

| 特性 | 说明 |
|------|------|
| **虚拟线程 (预览)** | Project Loom：轻量级虚拟线程 |
| **结构化并发 (孵化)** | `StructuredTaskScope` |
| **Record Pattern (预览)** | Record 解构模式匹配 |
| **Pattern Matching for switch (三次预览)** | 进一步改进 |
| **外部函数与内存 API (预览)** | 接近正式 |
| **Vector API (四次孵化)** | 向量计算 API |
| **Linux/RISC-V 移植** | 支持 RISC-V 指令集 |

---

## JDK 20 — 2023.03

### 核心特性

| 特性 | 说明 |
|------|------|
| **虚拟线程 (二次预览)** | 进一步完善 |
| **结构化并发 (二次孵化)** | 增强的 StructuredTaskScope |
| **作用域值 (孵化)** | `ScopedValue` 替代 ThreadLocal |
| **Record Pattern (二次预览)** | 增强 |
| **Pattern Matching for switch (四次预览)** | 进一步优化 |
| **外部函数与内存 API (二次预览)** | 接近完成 |
| **Vector API (五次孵化)** | 向量 API |

---

## JDK 21 (LTS) — 2023.09

> 最新的 LTS 版本，引入了虚拟线程等划时代特性。

### 核心特性

| 特性 | 说明 |
|------|------|
| **虚拟线程 (正式)** | 轻量级线程，数百万级并发能力 |
| **Record Pattern (正式)** | Record 解构能力 |
| **Pattern Matching for switch (正式)** | 极致简洁的类型匹配 |
| **结构化并发 (预览)** | 结构化并发编程模型 |
| **作用域值 (预览)** | `ScopedValue` 继承上下文 |
| **有序集合** | `SequencedCollection`、`SequencedSet`、`SequencedMap` |
| **字符串模板 (预览)** | `STR."Hello \{name}"` |
| **未命名模式和变量 (预览)** | `case _ ->`、`try (\_) ` |
| **未命名类 (预览)** | 简化的小程序入口 |
| **弃用 Windows 32 位** | 最终弃用 |
| **分代 ZGC** | ZGC 支持分代收集 |
| **记录模式匹配增强** | 嵌套解构 |

### 示例

```java
// 虚拟线程
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        System.out.println("虚拟线程: " + Thread.currentThread());
    });
}

// Pattern Matching for switch
String formatted = switch (obj) {
    case Integer i -> String.format("int %d", i);
    case Long l    -> String.format("long %d", l);
    case Double d  -> String.format("double %f", d);
    case String s  -> String.format("String %s", s);
    default        -> obj.toString();
};

// Record Pattern
if (obj instanceof Point(int x, int y)) {
    System.out.println(x + ", " + y);
}

// 有序集合
SequencedCollection<String> seq = new ArrayList<>();
seq.addFirst("first");
seq.addLast("last");
seq.getFirst();  // "first"
seq.getLast();   // "last"
seq.reversed();  // 逆序视图
```

---

## 版本选用建议

| 用途 | 推荐版本 | 说明 |
|------|---------|------|
| **新项目** | **JDK 21** (LTS) | 最新 LTS，虚拟线程 + 模式匹配 |
| **主流生产** | **JDK 17** (LTS) | Spring Boot 3.x 基线版本 |
| **遗留系统** | **JDK 11** (LTS) | 过渡 LTS，已有广泛生态 |
| **老项目** | **JDK 8** (LTS) | 仍在维护，建议升级 |
| **尝鲜** | 最新非 LTS | 体验新特性，不要用于生产 |

---

## 参考链接

- [OpenJDK 官方发布说明](https://openjdk.org/projects/jdk/)
- [Java 版本特性索引 (Oracle)](https://www.oracle.com/java/technologies/java-se-version-history.html)
- [[concurrent|Java 并发编程]]
- [[jvm|JVM 内存模型]]
