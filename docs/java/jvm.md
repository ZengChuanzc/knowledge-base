# JVM 原理与实战

> JVM（Java Virtual Machine）是 Java 跨平台的基石。理解 JVM 内存模型、垃圾回收机制和调优手段，是 Java 后端进阶的必经之路。

---

## 一、运行时数据区

### 1. 整体结构（JDK 8+）

```
┌─────────────────────────────────────────────────┐
│                  线程共享区域                      │
├─────────────────────┬───────────────────────────┤
│      堆 (Heap)      │     方法区 (Metaspace)      │
│   - 新生代 (Eden)   │  - 类元信息（Klass）        │
│   - 新生代 (S0/S1)  │  - 运行时常量池             │
│   - 老年代 (Old)    │  - 静态变量                 │
│   字符串常量池       │  - JIT 编译产物             │
├─────────────────────┴───────────────────────────┤
│                  线程私有区域                      │
├──────────────┬──────────────┬───────────────────┤
│ 程序计数器    │ 虚拟机栈      │  本地方法栈        │
│ (PC Register)│ (VM Stack)   │ (Native Stack)    │
│  行号指示器   │ 栈帧：局部变量表 │  native 方法调用 │
│              │ 操作数栈、   │                    │
│              │ 动态链接、    │                    │
│              │ 方法出口      │                    │
└──────────────┴──────────────┴───────────────────┘
```

### 2. 堆（Heap）

JVM 管理的最大一块内存，几乎所有对象实例都在这里分配。

#### 分代结构（JDK 8 默认 G1 之前）

```
    新生代 (Young Gen)         老年代 (Old Gen)
┌──────────┬──────┬──────┐  ┌────────────────────┐
│  Eden    │ S0   │ S1   │  │      Old           │
│  (8/10)  │(1/10)│(1/10)│  │                    │
└──────────┴──────┴──────┘  └────────────────────┘
     Minor GC (复制算法)           Major GC (标记整理)
```

::: tip JDK 8+ 堆内存分区变化
- **JDK 7 → JDK 8**：永久代（PermGen）→ 元空间（Metaspace），字符串常量池移到堆
- **JDK 9**：默认 GC 从 Parallel GC 改为 G1（低延迟优先）
- **JDK 12+**：G1 改进，支持及时归还未用内存
- **JDK 17+ ZGC / JDK 21 分代 ZGC**：堆不再严格分代
:::

#### 常见参数

```bash
# 堆大小
-Xms4g                  # 初始堆大小（启动时分配）
-Xmx4g                  # 最大堆大小（建议与 Xms 相等，避免动态扩容）
-Xmn2g                  # 新生代大小

# 元空间
-XX:MetaspaceSize=256m  # 元空间初始大小
-XX:MaxMetaspaceSize=256m  # 元空间最大大小（不设则无上限）

# OOM 时自动 dump
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/dump.hprof
```

::: warning Xms 和 Xmx 为什么不建议设不同值？
如果 Xms < Xmx，JVM 会在需要时向 OS 申请内存，期间触发 **Full GC** 来整理堆。设相等可以：
1. 避免运行期扩容开销
2. 保证启动时内存就到位，避免高峰时分配失败
3. 对容器环境（K8s）更友好，内存资源提前锁定

但在容器中要注意：Xms 设太大可能启动就 OOMKilled，建议 Xms ≈ 堆的稳定使用水位，略低于容器 limit。
:::

### 3. 方法区（Metaspace）

JDK 8 起，永久代（PermGen）被元空间（Metaspace）取代。

| 对比 | PermGen（JDK 7） | Metaspace（JDK 8+） |
|------|-----------------|-------------------|
| 存储位置 | JVM 堆内 | OS 本地内存（Native Memory） |
| 默认大小 | 有上限（-XX:MaxPermSize） | 无上限（可能耗尽 OS 内存） |
| GC 触发 | Full GC 时回收 | Full GC + CMS 并发收集 |
| **常见问题** | PermGen OOM（类加载过多） | Metaspace 持续增长（类加载泄漏） |

::: danger Metaspace OOM 排查
**问题**：动态类加载的场景（CGLib 代理、热部署、Groovy 脚本）如果代码有泄漏，Metaspace 会持续增长直到 OS 内存耗尽。

**排查**：
```bash
# 监控 Metaspace 使用
jstat -gcmetacapacity <pid> 1000

# 查看加载类数量
jstat -class <pid>

# 转储分析（JDK 8u92+）
-XX:+TraceClassLoading
-XX:+TraceClassUnloading
```
常见元空间泄漏源头：
- CGLib 动态代理每调用一次生成一个新类（未缓存）
- 热部署场景未清理 ClassLoader
- Groovy 脚本引擎每执行一次编译一个新类
:::

### 4. 虚拟机栈

每个线程私有，生命周期与线程相同。每个方法调用创建一个**栈帧**。

```
栈帧 (Stack Frame)：
┌──────────────────────────┐
│ 局部变量表 (Local Variables)  │  32bit slot，long/double 占 2 slot
│ 操作数栈 (Operand Stack)      │  字节码指令的工作区
│ 动态链接 (Dynamic Linking)    │  指向运行时常量池的方法引用
│ 方法出口 (Return Address)     │  方法返回后恢复调用者状态
└──────────────────────────┘
```

#### 栈大小配置

```bash
-Xss256k    # 默认 1M（Linux x64），建议 256k~512k
```

::: warning 栈溢出场景
```java
// 场景1：递归过深（StackOverflowError）
void recurse() { recurse(); }

// 场景2：线程数过多（OutOfMemoryError: unable to create new native thread）
// 每个线程分配独立栈，如果栈太大（1M），2G 用户空间最多 ~2000 线程
// Xss 设为 256k，同样内存可以支持 ~8000 线程
```
生产注意：**大量线程的应用（Netty IO 线程 + 业务线程）一定要调小 Xss**，否则很容易达到线程数上限。
:::

### 5. 程序计数器

- 当前线程执行的字节码行号指示器
- **唯一不会 OutOfMemoryError 的区域**
- 线程私有，Native 方法执行时为 undefined

### 6. 直接内存（Direct Memory）

NIO（`DirectByteBuffer`）通过 native 方法直接分配 OS 内存。

```bash
-XX:MaxDirectMemorySize=1g   # 默认等于 Xmx
```

::: warning 直接内存泄漏排查
`ByteBuffer.allocateDirect()` 分配的内存不在堆上，`-Xmx` 不管用。
泄漏后表现为进程 RSS 持续增长，但堆内存正常。

排查手段：
```bash
# NMT (Native Memory Tracking) 开启
-XX:NativeMemoryTracking=summary

# 查看 native 内存分布
jcmd <pid> VM.native_memory summary

# pmap 查看 OS 级别内存映射
pmap -x <pid> | grep anon
```
:::

---

## 二、对象创建与内存布局

### 1. 对象创建流程

```
        加载类 ──→ 分配内存 ──→ 初始化零值 ──→ 设置对象头 ──→ 执行构造方法
           ↑           ↑            ↑              ↑              ↑
      类加载检查   指针碰撞/    实例字段       Mark Word       <init>
       已完成     空闲列表    置默认值      + Klass指针      (字节码)
 ```

#### 内存分配方式

| 方式 | 条件 | 说明 |
|------|------|------|
| **指针碰撞**（Bump-the-Pointer） | 堆内存规整（Serial/ParNew 带 Compact） | 已用/未用分界指针，分配后移动指针 |
| **空闲列表**（Free List） | 堆内存不规整（CMS） | 维护空闲块列表，分配时查找合适块 |

#### TLAB（Thread Local Allocation Buffer）

```bash
# 每个线程在 Eden 区预分配一块缓冲区，避免多线程竞争
-XX:+UseTLAB                        # 默认开启
-XX:TLABSize=512k                   # TLAB 大小
-XX:TLABRefillWasteFraction=64      # 填充浪费比例（默认 1/64）
-XX:ResizeTLAB                      # 允许动态调整
```

TLAB 不够时，对象直接在 Eden 分配（需要同步）。**大对象（> TLAB 大小）直接在老年代分配**：
```bash
-XX:PretenureSizeThreshold=1m  # 超过此大小的对象直接在老年代分配
```

### 2. 对象内存布局（HotSpot）

```
普通对象（以 32 位为参考，实际 64 位 + 压缩指针）：
┌──────────────────────────────────────┐
│           Mark Word (8 bytes)        │  ← 哈希码、GC 分代年龄、锁状态
├──────────────────────────────────────┤
│        Klass Pointer (4/8 bytes)     │  ← 指向方法区的类元数据
├──────────────────────────────────────┤
│        实例数据 (Instance Data)       │  ← 各字段按分配顺序排列
├──────────────────────────────────────┤
│       对齐填充 (Padding)              │  ← 保证 8 字节对齐
└──────────────────────────────────────┘

数组对象：
┌──────────────────────────────────────┐
│           Mark Word (8 bytes)        │
├──────────────────────────────────────┤
│        Klass Pointer (4/8 bytes)     │
├──────────────────────────────────────┤
│         数组长度 (4 bytes)            │  ← 数组特有
├──────────────────────────────────────┤
│        数组元素数据 (N bytes)         │
├──────────────────────────────────────┤
│           Padding                    │
└──────────────────────────────────────┘
```

#### 指针压缩（Compressed OOPs）

```bash
-XX:+UseCompressedOops   # JDK 8+ 默认开启（堆 < 32GB 时）
```

| 堆大小 | OOP 压缩 | 最大寻址 |
|-------|---------|---------|
| < 32GB | 开启（4 字节） | 2^32 × 8 = 35GB |
| ≥ 32GB | 关闭（8 字节） | 2^64 |

::: danger 指针压缩的陷阱
**对象引用从 8 字节压缩到 4 字节**，但前提是对象地址 8 字节对齐（低 3 位为 0）。因此：
1. **堆 > 32GB 时压缩失效**，引用变成 8 字节，实际可用对象数反而比 31GB 时少
2. 这是为什么很多生产环境配置 **-Xmx31g** 而不是 32g 的原因——多用 1GB 但每个引用多占 4 字节，得不偿失
3. **超过 32GB 的堆建议用 ZGC**（JEP 364 支持压缩指针），而非 G1
:::

### 3. 对象访问定位

```
句柄访问（HotSpot 不用）：
   栈 ──→ 句柄池 ──→ 对象实例
                  └──→ 对象类型数据

直接指针（HotSpot 默认）：
   栈 ──→ 堆中对象 ──→ 方法区类型信息
          (包含 Klass 指针)
```

直接指针优势：**少一次指针寻址**，性能更好。GC 移动对象时只需修改栈中引用，无需更新句柄池。

---

## 三、类加载机制

### 1. 类生命周期

```
加载 ──→ 验证 ──→ 准备 ──→ 解析 ──→ 初始化 ──→ 使用 ──→ 卸载
   (Loading) (Verification) (Preparation) (Resolution) (Initialization)
                                                   ↓
                                  部分 JIT 在运行时进行 (延迟解析)
```

| 阶段 | 操作 | 说明 |
|------|------|------|
| **加载** | 通过全限定名获取二进制字节流 | 可通过自定义类加载器覆盖 |
| **验证** | 文件格式/元数据/字节码/符号引用验证 | 可关闭 `-Xverify：none`（JDK 13 弃用） |
| **准备** | 为静态变量分配内存并赋零值 | 不是赋用户指定值（那是初始化阶段） |
| **解析** | 符号引用替换为直接引用 | 常量池解析 |
| **初始化** | 执行 `<clinit>()` 方法 | 静态变量赋值 + 静态代码块 |

### 2. 双亲委派模型

```
                    Bootstrap ClassLoader
                    (C++ 实现, jre/lib/rt.jar)
                           ↑
                    Extension ClassLoader
                    (JDK 9+ → Platform ClassLoader)
                    (jre/lib/ext/*.jar)
                           ↑
                    Application ClassLoader
                    (classpath 指定的类)
                           ↑
                    自定义 ClassLoader
```

#### 双亲委派源码

```java
protected Class<?> loadClass(String name, boolean resolve)
    throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // 1. 检查是否已加载
        Class<?> c = findLoadedClass(name);
        if (c == null) {
            try {
                // 2. 父加载器加载
                if (parent != null) {
                    c = parent.loadClass(name, false);
                } else {
                    c = findBootstrapClassOrNull(name);
                }
            } catch (ClassNotFoundException e) {
                // 父加载器找不到
            }
            if (c == null) {
                // 3. 自己加载
                c = findClass(name);
            }
        }
        return c;
    }
}
```

#### 为什么要双亲委派？

1. **沙箱安全**：防止核心 API 被篡改（如自定义 `java.lang.String`）
2. **类唯一性**：保证同一个类在 JVM 中只加载一次（全限定名 + ClassLoader 决定）

#### 破坏双亲委派的场景

| 场景 | 破坏方式 | 说明 |
|------|---------|------|
| **JDBC SPI** | 线程上下文类加载器（ThreadContextClassLoader） | 核心类（rt.jar 中的 DriverManager）需要调用应用类（各数据库驱动） |
| **Tomcat** | 优先加载 WEB-INF/classes 的类 | 不同 WebApp 可以部署不同版本的类库 |
| **热部署** | 自定义 ClassLoader，每次加载新版本类 | OSGi、Spring Boot DevTools |

```java
// JDBC 驱动加载（SPI 经典案例）
// DriverManager 在 rt.jar 中（Bootstrap ClassLoader）
// MySQL 驱动在 classpath 中（App ClassLoader）
// 核心类无法加载应用类，于是使用 ThreadContextClassLoader
ServiceLoader<Driver> drivers = ServiceLoader.load(Driver.class);
// Thread.currentThread().getContextClassLoader() 负责加载
```

::: tip 热部署原理
Spring Boot DevTools 使用两个 ClassLoader：
- **Base ClassLoader**：加载不常变的第三方 jar
- **Restart ClassLoader**：加载应用自己的类

当检测到文件变化时，**丢弃 Restart ClassLoader 并创建新的**，旧类被 GC。因为新 ClassLoader 加载的类是全新的 Class 对象，所以重新执行 `static` 块和初始化，实现"重启"效果。
:::

### 3. 常见类加载问题排查

```bash
# 排查类加载冲突（项目中存在多个版本的同一 jar）
# 现象：NoSuchMethodError / ClassNotFoundException / LinkageError

# 查看类加载来源
-XX:+TraceClassLoading         # 打印类加载信息
-XX:+TraceClassUnloading       # 打印类卸载信息

# 运行时查看类来源
System.out.println(SomeClass.class.getClassLoader());
System.out.println(SomeClass.getProtectionDomain().getCodeSource().getLocation());

# 诊断：maven 依赖树分析
mvn dependency:tree -Dincludes=groupId:artifactId
```

**常见冲突案例**：
```xml
<!-- maven 依赖冲突 → 两个不同版本的 netty 在 classpath 中 -->
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-all</artifactId>
</dependency>
<!-- 排除传递依赖 -->
<dependency>
    <groupId>xxx</groupId>
    <artifactId>yyy</artifactId>
    <exclusions>
        <exclusion>
            <groupId>io.netty</groupId>
            <artifactId>netty-all</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

---

## 四、垃圾回收（GC）

### 1. 判断对象是否存活

#### 引用计数法（主流 JVM 不用）

循环引用问题：A 引用 B，B 引用 A，外部不可达但引用计数不为 0。

#### 可达性分析（HotSpot 使用）

```
GC Roots 集合：
┌───────────────────────────────────────────────┐
│  - 虚拟机栈引用的对象（局部变量表）                │
│  - 本地方法栈引用的对象                          │
│  - 方法区中类静态属性引用的对象                    │
│  - 方法区中常量引用的对象                         │
│  - JNI（Native 方法）引用的对象                  │
│  - 活跃线程（Thread）                            │
│  - 内部引用（JVM 系统类、基本数据类型对应的 Class）  │
└───────────────────────────────────────────────┘
```

### 2. 引用类型

| 类型 | 回收时机 | 使用场景 |
|------|---------|---------|
| **强引用**（Strong） | 永不回收 | `new Object()`，普通对象 |
| **软引用**（Soft） | OOM 前回收 | 缓存（内存敏感场景） |
| **弱引用**（Weak） | 下次 GC 必回收 | ThreadLocalMap Entry、WeakHashMap |
| **虚引用**（Phantom） | 随时可回收 | 对象回收跟踪（NIO DirectByteBuffer 清理） |

```java
// 软引用缓存示例
SoftReference<Bitmap> cache = new SoftReference<>(bitmap);
Bitmap b = cache.get();
if (b == null) {
    b = loadBitmap();
    cache = new SoftReference<>(b);
}
```

::: tip 弱引用在 ThreadLocal 中的应用
```java
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;
    Entry(ThreadLocal<?> k, Object v) {
        super(k);  // key 是弱引用
        value = v; // value 是强引用 —— 内存泄漏来源
    }
}
```
key 被 GC 后变为 null，但 value 不会被回收，直到 `get()/set()/remove()` 触发探测式清理。
**务必在 finally 中调用 `remove()`**。
:::

### 3. 垃圾收集算法

| 算法 | 原理 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **标记-清除** | Mark → Sweep | 简单，不移动对象 | 内存碎片 | CMS |
| **标记-复制** | 将存活对象复制到另一块 | 无碎片，分配快 | 内存浪费（保留区） | 新生代 |
| **标记-整理** | Mark → Compact（滑动整理） | 无碎片，内存利用率高 | 停顿时间长 | 老年代（G1 Mixed GC） |

### 4. JVM GC 演进历史

```
JDK 7 及之前：
  Serial  ←── 单线程，STW
  ParNew  ←── Serial 的多线程版
  Parallel Scavenge  ←── 吞吐量优先
  CMS     ←── 低延迟（并发标记清除）
  Serial Old / Parallel Old ←── 老年代配套

JDK 9：
  G1 成为默认 GC（替代 Parallel GC）
  CMS 标记为废弃（JDK 14 正式移除）

JDK 11：
  ZGC 实验性引入（低延迟 < 10ms）
  Epsilon GC（无操作 GC）

JDK 12：
  Shenandoah GC（低延迟，RedHat 贡献）

JDK 15：
  ZGC 正式可用
  Shenandoah 正式可用

JDK 17 (LTS)：
  ZGC 从实验性转为生产特性
  CMS 正式移除

JDK 21 (LTS)：
  分代 ZGC 正式可用
```

### 5. 常用 GC 详解

#### 如何选择 GC？

```
延迟 (Latency) < 10ms ──→ ZGC / Shenandoah
延迟 10~100ms    ──→ G1
吞吐量优先        ──→ Parallel GC
堆 < 4GB         ──→ G1 或 Parallel
堆 4~100GB       ──→ G1
堆 > 100GB       ──→ ZGC（分代模式）
```

#### G1 —— JDK 9+ 默认 GC

G1 将堆划分为多个 **Region**（1~32MB），不再严格分代，而是每个 Region 标记角色（Eden/Survivor/Old/Humongous）。

```
Heap (2048 个 Region，每个 1MB)：
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ E  │ E  │ S  │ O  │ H  │ O  │ O  │ E  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│ O  │ E  │ E  │ S  │ O  │ O  │ O  │ O  │
├────┼────┼────┼────┼────┼────┼────┼────┤
│ O  │ O  │ O  │ E  │ E  │ S  │ H  │ H  │
└────┴────┴────┴────┴────┴────┴────┴────┘
```

**G1 核心参数**：

```bash
# 目标暂停时间（默认 200ms，调优关键参数）
-XX:MaxGCPauseMillis=100

# Region 大小（自动计算：堆 / 2048，1~32MB）
-XX:G1HeapRegionSize=4m

# 启动 Mixed GC 的堆占用比例（默认 45%）
-XX:InitiatingHeapOccupancyPercent=45

# 新生代最小/最大值（G1 自动调整）
-XX:G1NewSizePercent=5
-XX:G1MaxNewSizePercent=60
```

::: warning G1 调优实战经验
1. **`MaxGCPauseMillis` 不是越小越好**
   - 设 50ms 意味着每次只回收很少 Region → GC 频率升高 → 吞吐量下降
   - 推荐设 100~200ms，观察 GC 日志再微调

2. **`InitiatingHeapOccupancyPercent` 调低可能触发频繁 Mixed GC**
   - 调高（50~60%）可能 Full GC 提前到来
   - 推荐默认 45%，结合 GC 日志调整

3. **G1 的 Full GC 是单线程串行的**（标记-整理）
   - 出现 Full GC 说明 G1 赶不上对象分配速率
   - 解决方向：增大堆 / 调大 Region / 优化业务代码减少对象分配

4. **大对象（Humongous）直接分配到 H Region**
   - 超过 Region 大小 50% 的对象为大对象
   - 连续多个 H Region 可能造成提前触发 GC
   - 可调大 Region 大小避免过多 H Region
:::

#### ZGC —— JDK 21 分代 ZGC

```bash
# JDK 21 启用分代 ZGC（推荐）
-XX:+UseZGC -XX:+ZGenerational

# JDK 17 启用 ZGC（非分代）
-XX:+UseZGC
```

| 特性 | ZGC | G1 |
|------|-----|-----|
| 暂停时间 | < 1ms（与堆大小无关） | 目标 ~100ms |
| 最大堆 | 16TB | ~512GB 最佳 |
| 指针压缩 | ✅ 支持（ZGC 使用 64 位地址的 42 位做压缩） | ✅ 32GB 以内 |
| 分代 | JDK 21+ 支持 | ✅ 天生分代 |
| 吞吐量 | 略低于 G1（~5-15%） | 基准 |

### 6. GC 日志解读

```bash
# JDK 8 格式
-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc：gc.log

# JDK 9+ 统一日志（推荐）
-Xlog：gc*=info：file=gc.log：time,uptimemillis
-Xlog：gc*=info：file=gc.log：time,uptimemillis：filecount=5,filesize=10m

# 开启 GC 耗时 + 停顿时间
-Xlog：safepoint=info
```

**典型 GC 日志解读**（G1）：
```
[2026-06-15T10：30：00.123+0800] GC pause (G1 Evacuation Pause) 
  (young)  young->initial-mark— 100M(->100M) 50M(->10M) 2000M(->2000M) 
  50.123ms  User=0.10s Sys=0.05s Real=0.05s
```
- `young` = Young GC
- `100M->100M` = Region 数不变
- `50M->10M` = 存活对象大小 + 复制后大小
- `50.123ms` = STW 暂停时间
- `Real=0.05s` = 实际墙钟时间

```
[2026-06-15T10：35：00.456+0800] GC pause (G1 Humongous Allocation) 
  (young) (initial-mark)— 250M->10M(300M) 3000M->3200M 120.456ms
```
- Humongous Allocation pause = 分配大对象触发的 GC
- 频繁出现说明大对象过多，考虑 `-XX:G1HeapRegionSize` 或代码优化

### 7. GC 调优实战

#### 常见问题与解决

| 现象 | 可能原因 | 排查方向 | 解决方案 |
|------|---------|---------|---------|
| **频繁 Full GC** | 老年代空间不足 | `jstat -gcutil` 查看 FGC 频率 | 增大堆 / 降低 `IHOP` / 优化代码 |
| **GC 停顿过长** | G1 回收效率低 | `-Xlog：gc*` 看 GC 阶段耗时 | 调大 Region / 用 ZGC |
| **CPU 高但 GC 不频繁** | 对象分配速率过高 | `async-profiler` 采样分配热点 | 减少对象创建 / 对象池化 |
| **OOM：Java heap space** | 堆不够或内存泄漏 | `jmap -dump` 分析堆 | 增大堆 / 修复泄漏 |
| **OOM：GC overhead limit** | GC 回收 < 2% | `jstat -gc` 看 GC 效率 | 增大堆 / 调整 GC 策略 |
| **Metaspace OOM** | 类加载泄漏 | `-XX:+TraceClassLoading` | 修复类加载泄漏 / 加大 Metaspace |

#### 调优决策树

```
应用 GC 停顿过长？
├─ 大堆 (> 100GB) → ZGC (分代模式)
├─ 中等堆 (4~100GB) → G1
│   └─ MaxGCPauseMillis 调优：
│       调小 → 停顿更短，GC 更频繁
│       调大 → 停顿变长，吞吐量更高
├─ 小堆 (< 4GB) → Parallel GC（吞吐量优先）
└─ 极低延迟要求 (< 10ms) → ZGC / Shenandoah

Full GC 频繁？
├─ 堆太小 → 增大 Xmx
├─ IHOP 太大 → 调低 InitiatingHeapOccupancyPercent
├─ 对象分配速率过高 → 优化代码（减少对象创建）
└─ 晋升过快 → 调大新生代（检查 -Xmn 和 -XX:MaxTenuringThreshold）
```

```bash
# 典型 4C8G 容器 G1 配置（Spring Boot 应用）
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:InitiatingHeapOccupancyPercent=60
-XX:G1HeapRegionSize=4m
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/dump.hprof
-XX:+UseStringDeduplication
-Xlog:gc*=info:file=/tmp/gc.log:time,uptimemillis:filecount=5,filesize=10m
```

---

## 五、性能监控与调优工具

### 1. 命令行工具

| 工具 | 用途 | 常用命令 |
|------|------|---------|
| **jps** | 查看 Java 进程 | `jps -lvm` |
| **jstat** | GC 统计 | `jstat -gcutil <pid> 1000` |
| **jstack** | 线程栈 | `jstack -l <pid>` |
| **jmap** | 堆信息/Dump | `jmap -dump：format=b,file=heap.hprof <pid>` |
| **jcmd** | 综合诊断 | `jcmd <pid> VM.command` |
| **jinfo** | JVM 参数 | `jinfo -flags <pid>` |
| **jhsdb** | JDK 9+ 替代 jmap/jstack | `jhsdb jmap --heap --pid <pid>` |

```bash
# GC 实时监控
jstat -gcutil <pid> 1000 10
# 输出：
# S0  S1  E   O   M  CCS  YGC  YGCT  FGC  FGCT  GCT
# 0.00 0.00 45.2 30.5 92.3 88.5 120  3.456   2  1.234  4.690
# YGC=Young GC 次数, YGCT=Young GC 总耗时
# FGC=Full GC 次数, FGCT=Full GC 总耗时
```

```bash
# 线程分析
jstack -l <pid> > threaddump.txt

# 定位 CPU 最高的线程
top -H -p <pid>                    # 找到 CPU 最高的线程 PID
printf "%x\n" <thread-pid>          # 转为 16 进制
jstack <pid> | grep -A 50 "<nid=0xHEX>"  # 查看该线程栈
```

### 2. 可视化工具

| 工具 | 特点 | 适用场景 |
|------|------|---------|
| **JConsole** | JDK 自带，轻量 | 快速查看线程/内存/GC |
| **VisualVM** | 插件丰富，可视化 | 堆转储分析、GC 趋势 |
| **JMC (Java Mission Control)** | JDK 11+ 自带 | JFR 分析、飞行记录器 |
| **Async-profiler** | 低开销采样，火焰图 | CPU/内存热点分析 |
| **MAT (Memory Analyzer)** | 堆转储分析神器 | 内存泄漏定位 |
| **GCEasy** | 在线 GC 日志分析 | GC 日志一键解读 |

### 3. 内存泄漏排查实战

```java
// 经典内存泄漏：HashMap 缓存未清理
public class CacheService {
    private static final Map<String, Data> cache = new HashMap<>();
    
    public Data getData(String key) {
        Data data = cache.get(key);
        if (data == null) {
            data = loadFromDB(key);
            cache.put(key, data);  // 只增不减 → 持续增长 → OOM
        }
        return data;
    }
}
```

**排查步骤**：

```bash
# Step 1：发现 OOM
# 看到 OutOfMemoryError: Java heap space

# Step 2：配置自动 dump（如果之前没配，等下次 OOM 或用 jmap 手动 dump）
jmap -dump:live,format=b,file=heap.hprof <pid>

# Step 3：用 MAT 分析
# - 打开 heap.hprof
# - 查看 Leak Suspects Report → 找到最大的 retained size
# - 查看 GC Roots path → 定位到 HashMap/ConcurrentHashMap
# - 查看 Dominator Tree → 找到持有对象最多的线程

# Step 4：修复
# 选项1：使用 WeakHashMap 或 Guava Cache 设置过期
# 选项2：使用 Caffeine 缓存（推荐）
LoadingCache<String, Data> cache = Caffeine.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(1, TimeUnit.HOURS)
    .build(key -> loadFromDB(key));
```

---

## 六、JVM 调优参数速查

### 1. 内存参数

```bash
# 堆
-Xms4g -Xmx4g                      # 堆大小（建议相等）
-Xmn2g                             # 新生代大小
-XX:SurvivorRatio=8                # Eden：Survivor = 8：1：1
-XX:NewRatio=2                     # 新生代：老年代 = 1：2

# 元空间
-XX:MetaspaceSize=256m             # 初始元空间
-XX:MaxMetaspaceSize=256m          # 最大元空间

# 直接内存
-XX:MaxDirectMemorySize=512m

# 大对象
-XX:PretenureSizeThreshold=1m      # 超过此大小的对象直接进入老年代

# 堆外内存
-XX:NativeMemoryTracking=summary   # NMT 开启
```

### 2. GC 参数

```bash
# GC 选择
-XX:+UseG1GC                       # JDK 9+ 默认
-XX:+UseParallelGC                 # 吞吐量优先（JDK 8 默认）
-XX:+UseZGC                        # 低延迟（JDK 15+ 可用）
-XX:+UseZGC -XX:+ZGenerational     # 分代 ZGC（JDK 21+）

# G1 调优
-XX:MaxGCPauseMillis=100           # 目标暂停时间
-XX:InitiatingHeapOccupancyPercent=45  # 触发 Mixed GC 阈值
-XX:G1HeapRegionSize=4m            # Region 大小
-XX:G1MixedGCCountTarget=8         # Mixed GC 阶段数

# GC 日志（JDK 9+）
-Xlog:gc*=info:file=gc.log:time,uptimemillis:filecount=5,filesize=10m
-Xlog:safepoint=info               # 安全点日志
```

### 3. 诊断参数

```bash
# OOM 时自动 dump 堆
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/dump.hprof

# 类加载跟踪
-XX:+TraceClassLoading
-XX:+TraceClassUnloading

# 线程栈
-XX:+PrintConcurrentLocks          # 打印并发锁

# JFR 飞行记录器（生产可用，低开销）
-XX:StartFlightRecording=filename=recording.jfr,maxsize=500m
```

### 4. 容器环境特殊参数

```bash
# K8s / Docker 环境（JDK 8u191+）
-XX:+UseContainerSupport           # 自动识别容器资源限制
-XX:InitialRAMPercentage=50.0      # 初始堆占容器内存 50%
-XX:MaxRAMPercentage=70.0          # 最大堆占容器内存 70%
-XX:MinRAMPercentage=50.0          # 最小堆占容器内存 50%

# 注意：JDK 8u191 之前不识别 cgroup，需要手动设置
-XX:ActiveProcessorCount=4         # 手动指定 CPU 数
```

---

## 七、面试高频问题

### Q1：JDK 8 的 JVM 内存区域有哪些变化？

**答**：
1. **永久代（PermGen）→ 元空间（Metaspace）**：类的元数据从 JVM 堆内移到 OS 本地内存
2. 字符串常量池从方法区移到堆中
3. 默认 GC 从 Parallel Old 改为 G1（JDK 9 起）
4. 变更原因：
   - PermGen 大小固定，容易 OOM（-XX:MaxPermSize）
   - Metaspace 使用 OS 内存，默认无上限
   - 合并 JRockit 代码后的 HotSpot 整合

### Q2：对象在堆中的创建过程（结合 TLAB）？

**答**：
1. 类加载检查 → 检查类是否加载、解析、初始化
2. **TLAB** 分配：尝试在 Thread Local Allocation Buffer 中分配（线程私有，无需同步）
3. TLAB 空间不足：JVM 尝试在 Eden 区分配
4. Eden 区同步分配（需要 CAS 或加锁）
5. **大对象**（超过 PretenureSizeThreshold）：直接进入老年代
6. 分配内存后初始化零值、设置对象头、执行 `<init>`

### Q3：如何判断一个对象可以被回收？

**答**：通过 **GC Roots 可达性分析**。从 GC Roots 对象出发向下搜索引用链，不可达的对象被视为可回收。
GC Roots 包括：栈帧局部变量表引用的对象、静态属性引用的对象、JNI 引用、活跃线程等。

但这并非"必死"——对象可以在 `finalize()` 中逃脱（**不推荐依赖**），实际生产中 `finalize()` 被标记为弃用（JDK 18+）。

### Q4：G1 和 ZGC 有什么区别？如何选择？

**答**：

| 维度 | G1 | ZGC |
|------|-----|-----|
| 原理 | Region 分代，并发标记+复制 | Region 着色指针，并发标记+重映射 |
| 停顿时间 | 100~200ms | < 1ms（与堆大小无关） |
| 吞吐量 | 基准 | 低 ~5-10% |
| 最大堆 | 约 512GB 最佳 | 16TB |
| JDK 版本 | JDK 9+ 默认 | JDK 15+ 生产可用 |

**选择建议**：
- 堆 < 100GB，延迟要求 100ms→ G1
- 堆 > 100GB 或延迟要求 < 10ms → ZGC
- 吞吐量优先 → Parallel GC

### Q5：内存泄漏如何排查？

**答**：
1. 使用 `jstat -gcutil <pid> 1000` 观察 GC 趋势，确认 O 区持续增长
2. 配置 `-XX:+HeapDumpOnOutOfMemoryError` 自动 dump
3. 使用 **MAT (Memory Analyzer)** 分析 hprof 文件：
   - Leak Suspects Report → 快速定位泄漏点
   - Dominator Tree → 查看最大对象持有路径
   - GC Roots path → 追踪对象引用链
4. 常见泄漏类型：未关闭流、ThreadLocal 未 remove、无界缓存、类加载泄漏

### Q6：什么情况下会发生 Full GC？如何避免？

**答**：

**Full GC 触发条件**（以 G1 为例）：
1. **并发标记失败**：标记阶段对象分配过快，堆满
2. **晋升失败**：Young GC 存活对象 > Survivor 空间，直接进入老年代但老年代不够
3. **大对象分配失败**：H Region 无法连续分配
4. **System.gc() 调用**（不推荐）
5. **元空间不足**：Metaspace 满了

**避免方案**：
1. 调大 `-XX:G1ReservePercent` 预留空间（默认 10%）
2. 调低 `-XX:InitiatingHeapOccupancyPercent`（提前触发 Mixed GC）
3. 增大堆或优化代码减少对象分配
4. **禁止使用 `System.gc()`**（可用 `-XX:+DisableExplicitGC` 禁用）

### Q7：类加载的双亲委派机制及其破坏？

**答**：见上文 [类加载机制](#三类加载机制) 章节。

---

## 参考链接

- [JVM 官方文档 — Oracle](https://docs.oracle.com/javase/specs/jvms/se21/html/)
- [Java Memory Model (JSR-133)](https://jcp.org/en/jsr/detail?id=133)
- [美团技术博客 — Java Hotspot G1 GC 原理与调优](https://tech.meituan.com/2016/09/23/g1.html)
- [美团技术博客 — JVM 内存区域详解](https://tech.meituan.com/2020/11/12/java-object-header.html)
- [阿里巴巴 Java 开发手册](https://github.com/alibaba/p3c) — OOM 规范
- [ZGC 官方文档 — OpenJDK](https://wiki.openjdk.org/display/zgc/Main)
- [JEP 364: ZGC on macOS and Windows](https://openjdk.org/jeps/364)
- [JEP 377: ZGC: A Scalable Low-Latency Garbage Collector (Production)](https://openjdk.org/jeps/377)
- [JEP 439: Generational ZGC](https://openjdk.org/jeps/439)
- [Java Object Layout (JOL)](https://openjdk.org/projects/code-tools/jol/) — 查看对象布局
- [GCEasy — GC 日志在线分析](https://gceasy.io/)
- [《深入理解 Java 虚拟机》— 周志明](https://book.douban.com/subject/34907497/)
- [Eclipse MAT — 内存分析工具](https://eclipse.dev/mat/)
- [Async-profiler](https://github.com/async-profiler/async-profiler)

---

## 相关文章

- [并发编程](/java/concurrent)
- [JDK 版本特性 (8~21)](/java/jdk-versions)
