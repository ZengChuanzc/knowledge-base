# Java 并发编程

> 并发编程是 Java 后端开发的核心硬技能。本文从线程基础到 JUC 高级工具，涵盖原理剖析、生产实践、常见踩坑与规避方案。

---

## 一、并发基础

### 1. 线程的生命周期与状态流转

Java 线程状态定义在 `Thread.State` 枚举中，共 6 种状态：

```
                   ┌──────────┐
                   │   NEW     │
                   └────┬─────┘
                        │ start()
                   ┌────▼─────┐
                   │RUNNABLE  │ ◄── 就绪 + 运行（OS 视角）
                   └──┬───┬───┘
              ┌───────┘   └───────┐
         ┌────▼────┐         ┌────▼──────┐
         │BLOCKED  │         │ WAITING   │
         │(synchronized)     │(wait/join/│
         └─────────┘         │ park)     │
                             └────┬──────┘
                             ┌────▼──────────┐
                             │ TIMED_WAITING │
                             │(sleep/wait/   │
                             │ parkNanos)    │
                             └────┬──────────┘
                        ┌─────────▼────┐
                        │ TERMINATED   │
                        └──────────────┘

```

**生产注意点**：
- `BLOCKED` 和 `WAITING` 区分很重要：`BLOCKED` 是竞争 `synchronized` 内置锁，`WAITING` 是调用 `LockSupport.park()` 或 `Object.wait()`。排查时前者说明锁竞争激烈，后者说明在等待特定条件。
- `Thread.sleep()` **不释放锁**，但释放 CPU；`Object.wait()` **释放锁**并进入等待队列。

### 2. 线程创建方式的选择

| 方式 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 继承 `Thread` | 简单 | Java 单继承局限，不适合任务复用 | ❌ |
| 实现 `Runnable` | 解耦任务与执行 | 无返回值，无法抛异常 | ⚠️ |
| 实现 `Callable` + `FutureTask` | 有返回值，可抛异常 | 稍复杂 | ✅ |
| `CompletableFuture` | 函数式异步编排 | 学习成本 | ✅✅ |

```java
// 强烈推荐：使用 CompletableFuture 替代原始方式
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> queryFromDB(), threadPool)
    .thenApplyAsync(this::enrichData, threadPool)
    .exceptionally(e -> {
        log.error("处理失败", e);
        return "fallback";
    });
```

::: warning 坑：submit(Runnable) 返回的 Future.get() 返回 null
`ExecutorService.submit(Runnable)` 返回的 `Future<?>`，调用 `get()` 方法返回 `null`。如果需要返回值，用 `submit(Callable)` 或 `FutureTask`。
:::

### 3. 线程安全的本质：JMM（Java 内存模型）

JMM 规定了线程如何与主存交互，核心是解决三个问题：

| 问题 | 含义 | 解决手段 |
|------|------|---------|
| **原子性** | 操作不可中断 | 锁、CAS、原子类 |
| **可见性** | 一个线程修改，其他线程立即可见 | `volatile`、锁、`final` |
| **有序性** | 禁止指令重排序 | `volatile`、`synchronized`、happens-before |

#### happens-before 规则（JSR-133）

| 规则 | 说明 |
|------|------|
| 程序次序规则 | 单线程按代码顺序执行 |
| **volatile 规则** | 对 volatile 的写 happens-before 读 |
| 锁规则 | 解锁 happens-before 后续加锁 |
| 传递性 | A→B, B→C ⇒ A→C |
| 线程启动规则 | `Thread.start()` happens-before 该线程所有动作 |
| 线程终止规则 | 线程所有动作 happens-before `Thread.join()` 返回 |

::: tip 面试高频：双重检查锁定（DCL）为什么需要 volatile？
```java
private volatile static Singleton instance;
public static Singleton getInstance() {
    if (instance == null) {               // 第一次检查
        synchronized (Singleton.class) {
            if (instance == null) {       // 第二次检查
                instance = new Singleton(); // 危险！不加 volatile 可能指令重排
            }
        }
    }
    return instance;
}
```
`new Singleton()` 分为三步：1) 分配内存 2) 初始化对象 3) 引用赋值。不加 volatile，2 和 3 可能重排，导致返回未初始化的对象。参考：[双重检查锁定与延迟初始化](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
:::

---

## 二、锁机制

### 1. synchronized 底层原理

#### 对象头与 Mark Word（64 位 JVM）

```
对象头（64 位 JVM）：
┌──────────────────────────────────────────────┐
│                Mark Word (64 bits)            │
├──────────────────────────────────────────────┤
│  unused:25 | identity_hashcode:31 | age:4    │  无锁
│                     biased_lock:1 | lock:2=01 │
├──────────────────────────────────────────────┤
│  thread:54 | epoch:2 | age:4 | biased_lock:1 │  偏向锁
│                           lock:2=01          │
├──────────────────────────────────────────────┤
│  ptr_to_lock_record:62 | lock:2=00           │  轻量级锁
├──────────────────────────────────────────────┤
│  ptr_to_monitor:62 | lock:2=10               │  重量级锁
└──────────────────────────────────────────────┘
```

#### 锁升级过程（不可逆）

```
无锁 ──→ 偏向锁 ──→ 轻量级锁 ──→ 重量级锁
                               (JDK 15+ 默认关闭偏向锁，从无锁直接到轻量级)
```

| 阶段 | 触发条件 | 实现方式 | 开销 |
|------|---------|---------|------|
| **偏向锁** | 同一线程连续获取 | CAS 替换 ThreadID | 极低（一次 CAS） |
| **轻量级锁** | 多个线程交替获取 | CAS 替换 Mark Word | 自旋（占用 CPU） |
| **重量级锁** | 多个线程同时竞争 | Monitor 阻塞/唤醒 | 上下文切换（高） |

**关键源码**：`objectMonitor.cpp` 中 `enter()` 和 `exit()` 方法。
```cpp
// HotSpot 源码简化逻辑
void ObjectMonitor::enter(TRAPS) {
    // 尝试 CAS 获取锁
    if (TryLock(Self) > 0) return;
    // 自旋优化
    if (TrySpin(Self) > 0) return;
    // 入队并阻塞
    EnterI(THREAD);
}
```

::: warning 生产踩坑：偏向锁在高并发下的性能问题
JDK 15 之前默认开启偏向锁，但在高并发系统中，**偏向锁撤销（revoke）需要全局安全点（STW）**。
- 大量短生命周期线程频繁竞争，偏向锁撤销反而成为性能瓶颈
- **JDK 15+ 已默认禁用偏向锁**，老版本可通过 `-XX：-UseBiasedLocking` 关闭
- 参考：[JDK-8180450 禁用偏向锁](https://openjdk.org/jeps/374)

线上案例：某系统偏向锁撤销占 GC 暂停的 30%，关闭后 STW 减少一半。
:::

### 2. CAS（Compare-And-Swap）

#### 原理

CPU 原语指令（CMPXCHG），硬件保证原子性。

```java
// Unsafe 类实现（不可直接调用）
public final native boolean compareAndSwapInt(
    Object o, long offset, int expected, int x);
```

#### ABA 问题

```java
// ABA 场景：线程1将 A→B→A，线程2 CAS 成功但不知期间变化
// 解决：AtomicStampedReference（版本号）
AtomicStampedReference<String> ref = new AtomicStampedReference<>("A", 0);
String oldRef = ref.getReference();
int oldStamp = ref.getStamp();
ref.compareAndSet(oldRef, "B", oldStamp, oldStamp + 1);
```

::: danger 生产踩坑：CAS 在超高并发下的性能退化
CAS 虽然是乐观锁，但在竞争极其激烈时，**大量线程同时自旋会导致 CPU 飙升**。
- `AtomicLong` 在高并发下可能成为瓶颈（所有线程 CAS 同一个变量）
- **JDK 8 引入 `LongAdder`**：将热点分散到多个 Cell 数组，最后 sum 时汇总
- 参考：[Java Performance：LongAdder vs AtomicLong 性能对比](https://openjdk.org/jeps/155)

```java
// 高并发计数推荐
LongAdder count = new LongAdder();
count.increment();       // 无竞争时直接 CAS base
                         // 有竞争时 CAS cells[index]
long total = count.sum(); // 汇总所有 Cell + base
```
:::

### 3. ReentrantLock 原理（基于 AQS）

#### 公平锁 vs 非公平锁

```java
// 非公平锁（默认）- 插队行为
final boolean nonfairTryAcquire(int acquires) {
    // 直接尝试 CAS 获取，不检查队列
    if (compareAndSetState(0, acquires)) { ... }
}

// 公平锁 - 检查队列中是否有前驱
protected final boolean tryAcquire(int acquires) {
    if (getState() == 0) {
        if (!hasQueuedPredecessors() &&  // 关键区别：检查队列
            compareAndSetState(0, acquires)) { ... }
    }
}
```

::: tip 生产建议
- **非公平锁吞吐量更高**（减少线程挂起/唤醒），除非有明确的公平性需求（如交易系统排队）
- **tryLock() 是非公平的**，即使使用公平锁构造
- 不要用 `lock.lock()` 在 try 块中（防止加锁失败后 finally 解锁）
```java
// 正确写法
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();
}
```
:::

### 4. ReentrantReadWriteLock 与 StampedLock

#### ReentrantReadWriteLock 的潜在问题

```java
ReentrantReadWriteLock rw = new ReentrantReadWriteLock();
// 问题：高并发下读线程源源不断，写线程永远拿不到锁（写饥饿）
// JDK 1.6+ 改进：当写锁被等待时，后续读锁不授予（避免写饥饿）
```

#### StampedLock 最优实践

```java
class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();

    void move(double dx, double dy) {
        long stamp = sl.writeLock();
        try {
            x += dx; y += dy;
        } finally {
            sl.unlockWrite(stamp);
        }
    }

    double distanceFromOrigin() {
        // 乐观读 —— 不加锁，性能极高
        long stamp = sl.tryOptimisticRead();
        double curX = x, curY = y;
        if (!sl.validate(stamp)) {  // 被写线程修改过
            stamp = sl.readLock();   // 升级为悲观读锁
            try {
                curX = x; curY = y;
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return Math.sqrt(curX * curX + curY * curY);
    }
}
```

::: warning StampedLock 踩坑
- **StampedLock 不可重入**，重入会导致死锁
- **不支持 `Condition`**
- 悲观读/写锁的 stamp 必须配对释放（用 finally 保证）
- 乐观读不支持锁升级（乐观读 → 写锁会死锁）
:::

### 5. synchronized vs ReentrantLock 深度对比

| 对比维度 | synchronized | ReentrantLock |
|---------|-------------|---------------|
| 实现层级 | JVM 底层（C++ ObjectMonitor） | JDK 层（Java AQS） |
| 锁释放 | 自动（异常时也释放） | 必须 finally 释放 |
| 锁类型 | 非公平 | 公平 / 非公平可选 |
| 重入 | 隐式支持 | 显式支持 |
| 中断响应 | ❌ 不支持 | ✅ `lockInterruptibly()` |
| 超时获取 | ❌ 不支持 | ✅ `tryLock(timeout, unit)` |
| 多条件等待 | `wait/notify`（单队列） | `Condition`（多队列精细唤醒） |
| 锁检测 | 无 | `tryLock()` 非阻塞检测 |
| 调试性 | 栈可追踪 | JUC 链更复杂 |
| **低竞争性能** | 更优（锁消除、锁粗化） | 略逊 |
| **高竞争性能** | 膨胀为重量锁 | 更稳定（非公平 + CAS） |

**选择建议**：
- 不需要高级功能 → 优先 `synchronized`（代码简洁、不易出错）
- 需要超时/中断/多条件 → `ReentrantLock`
- 极度高竞争 → `ReentrantLock` 非公平模式

### 6. 锁的最佳实践与反模式

#### ✅ 应该做的

```java
// 1. 缩小锁范围 —— 只锁共享变量访问，不要锁整个方法
// ❌ 错误
synchronized void processAll(List<String> list) { ... }

// ✅ 正确
synchronized (lock) { sharedCount++; }

// 2. 锁上持有时间尽可能短，不要在锁内做 IO、远程调用
// ❌ 错误
synchronized (lock) {
    httpClient.send(request);  // 网络 IO，锁被长时间持有
}

// 3. 使用并发工具替代显式锁
ConcurrentHashMap<String, Data> cache = new ConcurrentHashMap<>();
cache.computeIfAbsent(key, k -> loadFromDB(k)); // 原子操作，无需额外锁
```

#### ❌ 反模式

```java
// 反模式1：锁对象选择不当
// ❌ 使用常量字符串作为锁（字符串常量池可能导致意外共享）
synchronized ("LOCK") { }  // JVM 中只有一个 "LOCK" 对象

// ✅ 使用私有 final 对象
private final Object lock = new Object();

// 反模式2：锁内调用 wait 导致 notify 丢失
synchronized (lock) {
    lock.wait();  // 释放锁，但如果没有对应的 notify，永远不醒
}

// 反模式3：嵌套锁导致死锁
void transfer(Account from, Account to, int amount) {
    synchronized (from) {
        synchronized (to) {  // 两个账户转账互相持对方锁 → 死锁
            from.debit(amount);
            to.credit(amount);
        }
    }
}
// ✅ 修复：固定锁顺序（按 accountId 排序）
```

---

## 三、AQS 原理深度剖析

> **AbstractQueuedSynchronizer** 是整个 JUC 锁和同步器的基石。ReentrantLock、Semaphore、CountDownLatch、ReentrantReadWriteLock 全部基于它实现。

### 1. 核心设计

```
                  ┌──────────────────────┐
                  │   AQS (state + CLH)  │
                  └──────┬───────────────┘
                         │ 模板方法模式 (Template Method)
         ┌───────────────┼───────────────────┐
         │               │                   │
    ReentrantLock    Semaphore         CountDownLatch
    (独占模式)        (共享模式)          (共享模式)
```

```java
// AQS 三大核心要素
public abstract class AbstractQueuedSynchronizer {
    // 1. state：同步状态（volatile 保证可见性）
    private volatile int state;
    
    // 2. CLH 队列：双向链表，管理等待线程
    private transient volatile Node head;
    private transient volatile Node tail;
    
    // 3. 模板方法：子类实现
    protected boolean tryAcquire(int arg)    { throw new UnsupportedOperationException(); }
    protected boolean tryRelease(int arg)    { throw new UnsupportedOperationException(); }
    protected int tryAcquireShared(int arg)  { throw new UnsupportedOperationException(); }
    protected boolean tryReleaseShared(int arg) { throw new UnsupportedOperationException(); }
}
```

### 2. CLH 队列原理

CLH 队列是 AQS 同步队列的核心，本质是**变种 CLH 自旋锁**：

```
  head                              tail
   │                                 │
   ▼                                 ▼
┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│ Node │◄──►│ Node │◄──►│ Node │◄──►│ Node │
│ wait │    │ wait │    │ wait │    │ wait │
│Status│    │Status│    │Status│    │Status│
└──────┘    └──────┘    └──────┘    └──────┘
   ↑                                    ↑
持有锁                                 等待中
```

**入队过程**（`acquireQueued` 简化）：
```java
final boolean acquireQueued(final Node node, int arg) {
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {
            final Node p = node.predecessor();
            if (p == head && tryAcquire(arg)) {
                setHead(node);    // 获取成功，成为新 head
                p.next = null;    // 原 head 出队
                failed = false;
                return interrupted;
            }
            // 获取失败，判断是否需要 park
            if (shouldParkAfterFailedAcquire(p, node))
                LockSupport.park(this);  // 挂起线程
        }
    } finally {
        if (failed) cancelAcquire(node);  // 异常时取消
    }
}
```

::: tip 理解 AQS 的关键
- **独占模式**（ReentrantLock）：`tryAcquire` 返回 true 获取成功，false 入队等待
- **共享模式**（Semaphore）：`tryAcquireShared` 返回 ≥0 获取成功，负数入队等待
- 前驱节点是 head 才尝试获取锁（**FIFO 公平性保证**）
- 非公平锁的区别在于：入队前先尝试 CAS 一次（插队行为）
:::

### 3. Condition 实现原理

每个 Condition 维护一个**单向等待队列**。

```
AQS 同步队列（双向）：
head ──► Node ──► Node ──► tail

Condition 等待队列（单向）：
firstWaiter ──► Node ──► Node ──► lastWaiter
     (node.condition 指向这条链)
```

**await/signal 流程**：
```java
// await()：释放锁 → 加入条件队列 → 挂起
// signal()：将条件队列头节点 → 移到同步队列
```

```java
// 生产者-消费者示例
class BoundedBuffer<T> {
    final ReentrantLock lock = new ReentrantLock();
    final Condition notFull  = lock.newCondition();
    final Condition notEmpty = lock.newCondition();
    
    final T[] items = (T[]) new Object[10];
    int putIndex, takeIndex, count;

    public void put(T x) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length) notFull.await();  // 入条件队列
            items[putIndex] = x;
            if (++putIndex == items.length) putIndex = 0;
            count++;
            notEmpty.signal();   // 唤醒一个消费者
        } finally {
            lock.unlock();
        }
    }
}
```

::: warning Condition 踩坑
- **`await()` 必须在 `signal()`/`signalAll()` 之前**，否则信号丢失
- 判断条件必须用 **`while` 而不是 `if`**（防止虚假唤醒 spurious wakeup）
- `signal()` 不会立即释放锁，需等到当前线程 unlock
:::

### 4. AQS 在生产中的体现

| 组件 | state 含义 | 模式 | 关键逻辑 |
|------|-----------|------|---------|
| ReentrantLock | 0=未锁，>0=重入次数 | 独占 | `tryAcquire` CAS state |
| Semaphore | 剩余许可数 | 共享 | `tryAcquireShared` 减少 state |
| CountDownLatch | 计数值 | 共享 | `tryReleaseShared` 减到 0 时唤醒 |
| ReentrantReadWriteLock | 高16位读锁数+低16位写锁数 | 混合 | state 拆分为两部分 |

**参考资源**：
- [AQS 源码分析 — Java Guide](https://javaguide.cn/java/concurrent/aqs.html)
- [The java.util.concurrent Synchronizer Framework — Doug Lea](https://gee.cs.oswego.edu/dl/papers/aqs.pdf)
- [AbstractQueuedSynchronizer 官方源码](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/locks/AbstractQueuedSynchronizer.java)

---

## 四、JUC 工具类

### 1. 原子类体系

```
AtomicInteger ──→ 基本CAS
AtomicLong    ──→ 基本CAS
AtomicBoolean ──→ 基本CAS
AtomicReference ──→ 对象CAS
AtomicIntegerArray ──→ 数组CAS
AtomicReferenceFieldUpdater ──→ 字段级CAS
    ↓
LongAdder ──→ 分段CAS + Cell数组（JDK 8，高并发推荐）
LongAccumulator ──→ 自定义累加
```

#### LongAdder 原理（高并发计数首选）

```java
// LongAdder 核心设计
class LongAdder {
    transient volatile long base;        // 基础值
    transient volatile Cell[] cells;     // 竞态分解数组
    
    public void add(long x) {
        // 1. 先尝试 CAS base
        if (casBase(base, base + x)) return;
        // 2. 冲突时，CAS cells 中一个槽位
        int h = ThreadLocalRandom.getProbe();
        Cell cell = cells[h & (cells.length - 1)];
        if (cell != null && cell.cas(cell.value, cell.value + x)) return;
        // 3. 继续冲突 → cells 扩容或重试
        longAccumulate(x, null, false);
    }
    
    public long sum() {
        Cell[] cs = cells;
        long sum = base;
        if (cs != null) {
            for (Cell c : cs) if (c != null) sum += c.value;
        }
        return sum;
    }
}
```

::: tip 性能对比
`AtomicLong` vs `LongAdder` 在 64 线程并发下：
- AtomicLong：~50M ops/sec（全部 CAS 同一个变量）
- LongAdder：~200M ops/sec（分散到多个 Cell）
- **建议**：需要准确计数值用 `AtomicLong`（如唯一 ID 生成），高并发累加用 `LongAdder`（如请求计数）
:::

### 2. ConcurrentHashMap 原理

#### JDK 7 vs JDK 8 对比

| 维度 | JDK 7（分段锁） | JDK 8（CAS + synchronized） |
|------|---------------|---------------------------|
| 数据结构 | Segment[] + HashEntry[] | Node[] + 红黑树 |
| 并发粒度 | Segment（默认 16） | 单个 Node |
| 锁机制 | ReentrantLock | CAS + synchronized |
| 扩容 | 分段扩容 | 多线程协助扩容 |
| 查询 | 遍历链表 | 链表/红黑树 |

#### JDK 8 put 流程

```java
final V putVal(K key, V value, boolean onlyIfAbsent) {
    // 1. 计算 hash
    int hash = spread(key.hashCode());
    for (Node<K,V>[] tab = table;;) {
        // 2. 空数组 → 初始化
        if (tab == null) initTable();
        // 3. 当前槽位空 → CAS 插入
        else if ((f = tabAt(tab, i)) == null) {
            if (casTabAt(tab, i, null, new Node<>(hash, key, value)))
                break;
        }
        // 4. 正在扩容 → 帮助迁移
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);
        // 5. 槽位有数据 → synchronized 锁住头节点
        else {
            synchronized (f) {
                // 遍历链表/红黑树插入
            }
        }
    }
}
```

::: warning ConcurrentHashMap 踩坑
1. **`size()` 方法不实时**：JDK 8 通过 `sumCount()` 累加 CounterCell，在并发修改时返回近似值
2. **不要用 `size > 0` 做判断**：高并发下极不准确，用 `isEmpty()` 替代
3. **`computeIfAbsent` 可能死锁**（JDK 8 bug，[JDK-8062841](https://bugs.openjdk.org/browse/JDK-8062841)）：嵌套调用同一 map 可能死循环，JDK 9 修复
4. **key/value 不能为 null**：`ConcurrentHashMap` 不允许 null，`HashMap` 允许。原因：无法区分 "key 不存在" 和 "value 为 null"
:::

### 3. 同步工具实战场景

#### CountDownLatch —— 等待任务完成

```java
// 场景：订单批量处理，等待所有子任务完成后汇总
CountDownLatch latch = new CountDownLatch(10);
ExecutorService executor = Executors.newFixedThreadPool(10);

for (Order order : orders) {
    executor.submit(() -> {
        try { processOrder(order); }
        finally { latch.countDown(); }  // 必须在 finally 中保证扣减
    });
}

// 主线程等待所有子任务完成（或超时）
if (!latch.await(30, TimeUnit.SECONDS)) {
    log.warn("订单处理超时，剩余: {}", latch.getCount());
    // 处理超时逻辑
}
```

::: danger CountDownLatch 踩坑
**`countDown()` 必须放在 `finally` 块中**！
如果子任务抛出异常，没有 `countDown()`，主线程将永远等待。
同理，`await(timeout)` 一定要设超时时间，防止无限等待。

```java
// ✅ 正确写法
try {
    // 业务逻辑
} finally {
    latch.countDown();  // 保证一定扣减
}
```
:::

#### CyclicBarrier —— 阶段同步

```java
// 场景：多阶段数据处理，每阶段所有线程完成后才进入下阶段
CyclicBarrier barrier = new CyclicBarrier(4, () -> {
    System.out.println("===== 该阶段所有线程完成，开始汇总 =====");
});

// 4 个线程协同
for (int i = 0; i < 4; i++) {
    new Thread(() -> {
        phase1();       // 阶段1
        barrier.await(); // 等待其他线程
        phase2();       // 阶段2
        barrier.await();
        phase3();
    }).start();
}
```

**CountDownLatch vs CyclicBarrier**：

| 对比维度 | CountDownLatch | CyclicBarrier |
|---------|---------------|---------------|
| 重用性 | 不可重用 | 可重用（`reset()`） |
| 触发条件 | 计数值到 0 | 所有线程到达 |
| 主要角色 | 一个等待 N 个 | N 个互相等待 |
| 构造方式 | 设置计数值 | 设置线程数 + 可选 barrierAction |

#### Semaphore —— 限流

```java
// 场景：数据库连接池限流
class ConnectionPool {
    private final Semaphore semaphore;
    private final List<Connection> connections;

    ConnectionPool(int poolSize) {
        semaphore = new Semaphore(poolSize, true); // 公平模式
        connections = new ArrayList<>(poolSize);
        for (int i = 0; i < poolSize; i++) {
            connections.add(createConnection());
        }
    }

    Connection acquire() throws InterruptedException {
        semaphore.acquire();       // 获取许可，没有则阻塞
        return getNextConnection();
    }

    void release(Connection conn) {
        returnConnection(conn);
        semaphore.release();       // 释放许可
    }
}
```

::: tip Semaphore 使用注意
- **许可数要加监控**：`availablePermits()` 接近 0 说明资源紧张
- **公平模式** `new Semaphore(n, true)` 防止线程饥饿
- **`release()` 必须放在 finally**：否则异常后许可丢失，最终耗尽
- 单机限流推荐 Guava RateLimiter（令牌桶），Semaphore 适合资源数固定的场景
:::

### 4. CompletableFuture 实战

#### 常见模式

```java
// 场景1：多个独立任务并行 + 汇总
CompletableFuture<List<Data>> future = 
    CompletableFuture.supplyAsync(() -> queryUsers(userIds, pool))
        .thenCombineAsync(
            CompletableFuture.supplyAsync(() -> queryOrders(orderIds, pool)),
            (users, orders) -> mergeResult(users, orders),
            pool);

// 场景2：任意一个成功即可
CompletableFuture<Price> bestPrice = 
    CompletableFuture.anyOf(
        CompletableFuture.supplyAsync(() -> queryPrice("sourceA")),
        CompletableFuture.supplyAsync(() -> queryPrice("sourceB")),
        CompletableFuture.supplyAsync(() -> queryPrice("sourceC"))
    ).thenApply(r -> (Price) r);

// 场景3：全部完成 + 超时兜底
CompletableFuture<Void> allDone = CompletableFuture.allOf(
    tasks.stream().map(t -> CompletableFuture.runAsync(t, pool)).toArray(CompletableFuture[]::new)
);
// 等待时设置超时
try { allDone.get(30, TimeUnit.SECONDS); }
catch (TimeoutException e) { allDone.cancel(true); log.warn("批量任务超时"); }
```

::: danger CompletableFuture 踩坑
1. **默认使用 ForkJoinPool.commonPool()**
   - 如果所有任务都用默认线程池，可能相互干扰
   - **始终传入自定义线程池**：`supplyAsync(task, threadPool)`

2. **异常处理链必须完整**
   ```java
   // ❌ 异常丢失
   CompletableFuture.supplyAsync(() -> riskyCall())
       .thenApply(data -> process(data));  // 没有 exceptionally
   
   // ✅ 完整异常链
   CompletableFuture.supplyAsync(() -> riskyCall(), pool)
       .thenApply(data -> process(data))
       .exceptionally(e -> {
           log.error("处理失败", e);
           return getDefault();
       })
       .orTimeout(5, TimeUnit.SECONDS)      // JDK 9+ 超时
       .exceptionally(e -> { ... });
   ```

3. **`get()` vs `join()`**
   - `get()` 抛 `ExecutionException`, 需要 try-catch
   - `join()` 抛 `CompletionException`（unchecked），代码更简洁
   - 推荐在 CompletableFuture 链中用 `join()`

4. **使用 `thenApply` 还是 `thenApplyAsync`?**
   - `thenApply`：同步执行（同线程），适合轻量转换
   - `thenApplyAsync`：提交到线程池执行，适合耗时操作
:::

---

## 五、线程池

### 1. ThreadPoolExecutor 源码剖析

```java
public ThreadPoolExecutor(int corePoolSize,
                          int maximumPoolSize,
                          long keepAliveTime,
                          TimeUnit unit,
                          BlockingQueue<Runnable> workQueue,
                          ThreadFactory threadFactory,
                          RejectedExecutionHandler handler)
```

**ctl 控制字段**（用一个 AtomicInteger 管理两个状态）：

```java
// 高3位：线程池运行状态（RUNNING/SHUTDOWN/STOP/TIDYING/TERMINATED）
// 低29位：工作线程数
private final AtomicInteger ctl = new AtomicInteger(ctlOf(RUNNING, 0));
```

| 状态 | 含义 |
|------|------|
| `RUNNING` | 接收新任务，处理队列任务 |
| `SHUTDOWN` | 不接收新任务，处理队列剩余任务 |
| `STOP` | 不接收新任务，不处理队列，中断正在执行的任务 |
| `TIDYING` | 所有任务终止，workCount=0，执行 terminated() |
| `TERMINATED` | terminated() 完成 |

**任务执行核心流程**（`execute()` 方法）：
```java
public void execute(Runnable command) {
    if (command == null) throw new NullPointerException();
    int c = ctl.get();
    // Step 1：工作线程 < corePoolSize → 新建线程
    if (workerCountOf(c) < corePoolSize) {
        if (addWorker(command, true)) return;
        c = ctl.get();
    }
    // Step 2：线程池运行中 → 入队
    if (isRunning(c) && workQueue.offer(command)) {
        int recheck = ctl.get();
        // 二次检查：如果线程池终止了，回滚入队并拒绝
        if (!isRunning(recheck) && remove(command))
            reject(command);
        // 没有活动线程了，启动一个空线程处理队列任务
        else if (workerCountOf(recheck) == 0)
            addWorker(null, false);
    }
    // Step 3：队列满 → 尝试扩容到 maxPoolSize
    else if (!addWorker(command, false))
        reject(command);  // Step 4：超过 maxPoolSize → 拒绝
}
```

### 2. 阻塞队列的深度选择

| 队列 | 特点 | 适用场景 | 风险 |
|------|------|---------|------|
| `LinkedBlockingQueue` | 默认无界，可选有界 | 任务数平稳 | 无界 = OOM 风险 |
| `ArrayBlockingQueue` | 有界，FIFO | 精准控流 | 容量设置不当导致拒绝 |
| `SynchronousQueue` | 不存任务，直接传递 | 短任务高吞吐 | 线程数无限扩张 |
| `PriorityBlockingQueue` | 优先级排序，无界 | 任务有优先级 | 无界 = OOM 风险 |
| `DelayQueue` | 延迟出队，无界 | 定时调度 | 无界 = OOM，时间精度 |

**队列选择决策树**：

```
任务是否依赖资源有限的第三方（DB/IO）？
├─ 是 → 使用有界队列（ArrayBlockingQueue/LinkedBlockingQueue），防止任务堆积
│       并且使用 CallerRunsPolicy 作为背压
└─ 否 → 任务数可预测？
        ├─ 是 → LinkedBlockingQueue（大小可控）
        └─ 否 → 使用 SynchronousQueue 配合无界 maxPoolSize（如 CachedThreadPool）
                 但要设置最大线程数上限，防止资源耗尽
```

### 3. 拒绝策略的实战选择

```java
// 标准策略
RejectedExecutionHandler abort = new ThreadPoolExecutor.AbortPolicy();          // 抛异常
RejectedExecutionHandler caller = new ThreadPoolExecutor.CallerRunsPolicy();    // 调用方执行
RejectedExecutionHandler discard = new ThreadPoolExecutor.DiscardPolicy();      // 丢弃
RejectedExecutionHandler oldest = new ThreadPoolExecutor.DiscardOldestPolicy(); // 丢弃最旧

// 自定义策略：将任务写入 MQ 或 Redis，后续异步补偿
class MqRejectedHandler implements RejectedExecutionHandler {
    void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        if (r instanceof MqTask) {
            messageQueue.send(((MqTask) r).toMessage());  // 发送到消息队列
        }
    }
}
```

| 策略 | 建议场景 | 原因 |
|------|---------|------|
| `AbortPolicy` | 不允许丢任务的关键业务 | 上层捕获异常后做补偿 |
| `CallerRunsPolicy` | **生产环境最推荐** | 天然背压，降低提交速率 |
| `DiscardPolicy` | 日志/监控指标/不重要统计 | 可容忍部分丢失 |
| `DiscardOldestPolicy` | 实时性要求高的场景 | 丢弃旧任务保证新任务执行 |

### 4. 线程池容量估算（含公式推导）

```java
// 通用公式：
// Nthreads = Ncpu * Ucpu * (1 + W/C)
//   Ncpu  = CPU 核心数
//   Ucpu  = 目标 CPU 利用率（0~1）
//   W/C   = 等待时间 / 计算时间（IO 密集型 W/C 大）
```

**经验参考表**（4 核机器，Ucpu=0.8）：

| 任务类型 | W/C | 计算 | 推荐线程数 |
|---------|-----|------|-----------|
| CPU 密集型 | ~0 | 4 × 0.8 × (1+0) | **4 或 5** |
| 一般 IO | ~2 | 4 × 0.8 × (1+2) | **~10** |
| 高 IO（DB 查询） | ~5 | 4 × 0.8 × (1+5) | **~19** |
| 极高 IO（HTTP 调用） | ~10 | 4 × 0.8 × (1+10) | **~35** |

::: tip 估算说明
- 实际中 W/C 估算困难，可从监控（CPU、线程等待时间）反推
- **OIO → NIO** 后，IO 密集型任务线程数可以降低（NIO 不阻塞线程）
- 过大的线程池导致上下文切换开销 > 并行收益（监控 `context switch rate`）
- 最终值需要通过**压测**（如 JMH、JMeter）验证调整
:::

### 5. Executors 工厂方法的陷阱

| 工厂方法 | 陷阱 | 具体问题 |
|---------|------|---------|
| `newFixedThreadPool(n)` | **无界队列** | `LinkedBlockingQueue` 无界，任务堆积 → OOM |
| `newCachedThreadPool()` | **无限线程** | 最大线程数 `Integer.MAX_VALUE`，过度创建 → OOM |
| `newSingleThreadExecutor()` | 无界队列 | 同上 OOM 风险 |
| `newScheduledThreadPool(n)` | 无界队列 | `DelayedWorkQueue` 无界，任务堆积 → OOM |

```java
// ❌ 禁止直接使用
ExecutorService pool = Executors.newFixedThreadPool(10);

// ✅ 手动构建
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10,                 // corePoolSize
    20,                 // maximumPoolSize
    60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),          // 有界队列
    new ThreadFactoryBuilder()              // 自定义命名
        .setNameFormat("biz-pool-%d")
        .setDaemon(false)
        .build(),
    new ThreadPoolExecutor.CallerRunsPolicy() // 背压策略
);

// 添加 JMX 监控（通过 spring-boot-actuator 或 jmx 暴露）
// executor.prestartAllCoreThreads();  // 预创建核心线程
```

**参考链接**：
- [《阿里巴巴 Java 开发手册》线程池部分](https://github.com/alibaba/p3c)
- [Java 线程池最佳实践 — Java Guide](https://javaguide.cn/java/concurrent/java-thread-pool-best-practices.html)

### 6. 线程池监控与告警

```java
// 封装监控线程池
public class MonitoredThreadPool extends ThreadPoolExecutor {
    private final String poolName;
    private final Gauge activeCountGauge;
    
    public MonitoredThreadPool(String poolName, int core, int max, int queueSize,
                                RejectedExecutionHandler handler) {
        super(core, max, 60L, TimeUnit.SECONDS,
              new LinkedBlockingQueue<>(queueSize),
              new NamedThreadFactory(poolName), handler);
        this.poolName = poolName;
        // 注册 Prometheus / Micrometer 指标
        this.activeCountGauge = Gauge.build()
            .name("threadpool_active_" + poolName)
            .help("Active threads")
            .register();
    }
    
    @Override
    protected void beforeExecute(Thread t, Runnable r) {
        activeCountGauge.set(getActiveCount());
    }
    
    @Override
    protected void afterExecute(Runnable r, Throwable t) {
        if (t != null) {
            log.error("线程池 {} 任务执行异常", poolName, t);
        }
        // 监控队列积压
        int queueSize = getQueue().size();
        if (queueSize > getQueue().remainingCapacity() * 0.8) {
            log.warn("线程池 {} 队列积压告警: {}/{}", poolName, queueSize, 
                     getQueue().size() + getQueue().remainingCapacity());
        }
    }
    
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor e) {
        log.error("线程池 {} 任务被拒绝: {}", poolName, r.getClass().getSimpleName());
        // 发送告警（钉钉/企业微信/邮件）
        AlertManager.alert("线程池满载: " + poolName);
    }
}
```

**核心监控指标**：

| 指标 | 告警阈值 | 意义 |
|------|---------|------|
| `getActiveCount()` | 接近 `maxPoolSize` | 线程资源紧张 |
| `getQueue().size()` | 超过容量 80% | 任务积压 |
| `getCompletedTaskCount()` | 不再增长 | 线程池可能挂死 |
| `getRejectedExecutionCount()` | > 0 | 任务被丢弃，亟需处理 |
| `getLargestPoolSize()` | 接近 `maxPoolSize` | 历史峰值压力参考 |

### 7. 线程池优雅关闭

```java
// 推荐关闭流程
public void shutdownGracefully(ExecutorService pool, String poolName) {
    pool.shutdown();  // 不再接收新任务
    try {
        // 等待现有任务完成
        if (!pool.awaitTermination(60, TimeUnit.SECONDS)) {
            pool.shutdownNow();  // 超时后强制停止
            if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
                log.error("线程池 {} 无法完全终止", poolName);
            }
        }
    } catch (InterruptedException e) {
        pool.shutdownNow();
        Thread.currentThread().interrupt();  // 恢复中断状态
    }
}
```

---

## 六、常见问题与诊断

### 1. 死锁的排查

**`jstack` 输出典型格式**：
```
Found one Java-level deadlock:
=============================
"Thread-A":
  waiting to lock <0x000000076ad5e8e0> (a java.lang.Object)
  which is held by "Thread-B"
"Thread-B":
  waiting to lock <0x000000076ad5e8d0> (a java.lang.Object)
  which is held by "Thread-A"
```

**线上排查步骤**：
```bash
# 1. 查看 Java 进程 PID
jps -l

# 2. 生成线程快照
jstack -l <pid> > threaddump.log

# 3. 搜索死锁标记
grep -A 20 "deadlock" threaddump.log

# 4. 用工具可视化
# - jconsole → Threads → Detect Deadlock
# - Async-profiler: profiler.sh -d 30 -e cpu -o jfr <pid>
```

### 2. 线程池故障模式

| 故障 | 表现 | 原因 | 排查方法 |
|------|------|------|---------|
| **任务积压** | 接口响应变慢，队列持续增长 | 线程数不足 / 下游 IO 慢 | JMX 查看队列大小 |
| **线程耗尽** | 新任务被拒绝 | core + max 配置偏低 | 查看拒绝计数 |
| **CPU 飙升** | CPU 100% | 死循环 / 不合规自旋 | `top -H` + `jstack` 采样 |
| **内存泄漏** | OOM | 无界队列堆积 / ThreadLocal 泄漏 | `jmap -dump` 分析堆 |
| **线程泄露** | 线程数持续增长 | 线程池未关闭 / 未管理的线程 | `jstack` 看线程状态 |

### 3. ThreadLocal 内存泄漏

```java
// ThreadLocal 的隐患
private static final ThreadLocal<Context> ctx = new ThreadLocal<>();

// 在线程池中使用 ThreadLocal 必须注意：
// - 线程池中的线程会复用，ThreadLocal 中的对象不会自动清理
// - 如果不 remove，上次请求的数据可能被下次请求读到
// - 如果 ThreadLocal 中对象很大，导致内存泄漏

// ✅ 正确做法
try {
    ctx.set(userContext);
    // 业务逻辑
} finally {
    ctx.remove();  // 必须清理！尤其是线程池环境
}
```

**源码分析**：
```java
// ThreadLocalMap 的 key 是弱引用（WeakReference）
// 但 value 是强引用！
// 当 ThreadLocal 被 GC 后，key=null，但 value 仍然可达 = 内存泄漏
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;  // 强引用 —— 泄漏来源
    Entry(ThreadLocal<?> k, Object v) {
        super(k);
        value = v;
    }
}
```

### 4. 正确使用 final 和不可变对象

```java
// 不可变对象天然线程安全（无需同步）
public final class ImmutablePoint {
    private final int x;
    private final int y;
    
    public ImmutablePoint(int x, int y) {
        this.x = x;
        this.y = y;
    }
    public int x() { return x; }
    public int y() { return y; }
}

// 利用 final 保证安全发布
// 因为 final 域的初始化 happens-before 于任何其他线程的读取
public class SafePublication {
    private final int value;  // final 保证构造完成立即可见
    private static SafePublication instance;
    
    public SafePublication() { value = 42; }
    
    public static void publish() {
        instance = new SafePublication();
    }
}
```

---

## 七、面试高频问题与深度回答

### Q1：synchronized 的锁升级过程？（源码级）

> **答**：synchronized 通过对象头的 Mark Word 实现锁状态标记。JDK 6 优化后，锁是可升级的（不可降级）：
> 1. **无锁** → 对象创建时默认
> 2. **偏向锁** → 第一个线程获取时，CAS 在 Mark Word 中记录 ThreadID
> 3. **轻量级锁** → 第二个线程竞争时，CAS 拷贝 Mark Word 到栈帧 Lock Record 并尝试替换指针
> 4. **重量级锁** → 自旋超过阈值（自适应自旋）或锁竞争更加激烈时，膨胀为 ObjectMonitor
>
> JDK 15+ 默认关闭偏向锁（JEP 374），因为撤销需要 STW，高并发下得不偿失。

### Q2：volatile 的实现原理？

> **答**：volatile 基于**内存屏障**（Memory Barrier）实现：
> - 写 volatile 变量 → 插入 **StoreStore 屏障 + StoreLoad 屏障**（强制写回主存 + 禁止前面的写与后面的读重排序）
> - 读 volatile 变量 → 插入 **LoadLoad 屏障 + LoadStore 屏障**（强制从主存读取）
> 
> JMM 规定 volatile 写-读具有 happens-before 关系，保证可见性和有序性，但**不保证原子性**。

### Q3：ThreadLocal 的原理和内存泄漏？

> **答**：
> - 每个 Thread 持有 ThreadLocalMap，key 是 ThreadLocal 的弱引用，value 是实际的线程局部变量
> - **内存泄漏原因**：key 被 GC 后（null），value 仍是强引用，无法被访问也无法释放
> - **解决方案**：
>   1. 每次使用后调用 `remove()`
>   2. ThreadLocalMap 在 get/set 时会尝试清理 key=null 的槽位（称为"探测式清理"）
>   3. **线程池中务必 try-finally remove**，否则线程复用导致数据污染

### Q4：线程池的核心参数怎么设？

> **答**：核心公式 `Nthreads = Ncpu × Ucpu × (1 + W/C)`，其中 W/C 是等待时间和计算时间的比率。但最终值依赖压测。
> 
> **关键决策**：
> 1. 队列使用 **有界队列 + CallerRunsPolicy**，这是生产环境的标准配置
> 2. 禁止使用 Executors 工厂方法（无界队列 / 无限线程风险）
> 3. 开启**线程数 + 队列深度 + 拒绝计数**的监控告警
> 4. 线程池隔离：不同业务使用不同线程池（如 IO 密集型 vs CPU 密集型分离）

### Q5：ConcurrentHashMap JDK 8 如何保证线程安全？

> **答**：采用 CAS + synchronized 策略：
> - 空槽位 → **CAS 插入**，无锁操作
> - 非空槽位 → **synchronized 锁头节点**，链表或红黑树插入
> - 扩容时 → 多线程协助迁移，每个线程负责一个区间
> 
> 相比 JDK 7 的 Segment 分段锁，粒度更细（段锁 → 槽位锁），并发度从 16 提升到数组容量级别。

### Q6：如何排查线上死锁？

> **答**：
> 1. `jstack -l <pid>` 搜索 "deadlock"（JVM 会自动检测）
> 2. 分析 BLOCKED 线程的锁持有关系和等待关系
> 3. 确定死锁环路后，按**固定锁顺序**修复
> 4. 预防手段：`tryLock(timeout)` + 锁超时监控 + 锁排序一致性

---

## 参考文章与推荐阅读

- [Java Memory Model (JSR-133)](https://jcp.org/en/jsr/detail?id=133)
- [The JSR-133 Cookbook for Compiler Writers](https://gee.cs.oswego.edu/dl/jmm/cookbook.html) — Doug Lea
- [AQS 论文：The java.util.concurrent Synchronizer Framework](https://gee.cs.oswego.edu/dl/papers/aqs.pdf) — Doug Lea
- [《阿里巴巴 Java 开发手册》](https://github.com/alibaba/p3c) — 线程池、并发控制部分
- [Java 并发编程之美（掘金小册）](https://juejin.cn/book/6857811420608176136)
- [JavaGuide 并发编程](https://javaguide.cn/java/concurrent/)
- [美团技术：Java 线程池实现原理与最佳实践](https://tech.meituan.com/2020/04/02/java-pooling-pratice-in-meituan.html)
- [双重检查锁定（DCL）的原理与问题](https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html)
- [OpenJDK — AbstractQueuedSynchronizer 源码](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/locks/AbstractQueuedSynchronizer.java)
- [OpenJDK — ThreadPoolExecutor 源码](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/ThreadPoolExecutor.java)
- [JEP 374: Disable Biased Locking](https://openjdk.org/jeps/374)
- [JEP 155: Concurrency Updates (LongAdder)](https://openjdk.org/jeps/155)

---

## 参考链接

- [JVM 原理](/java/jvm)
- [JDK 版本特性 (8~21)](/java/jdk-versions)
