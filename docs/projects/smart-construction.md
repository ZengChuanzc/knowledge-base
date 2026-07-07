---
outline: deep
---

# 基建智慧工程管控项目

> 面向大型企业数字化转型需求，搭建服务 **30-40 万用户**的企业级基建工程管控平台。融合微服务、大数据及现场感知系统，涵盖工程中心、进度中心、安全中心三大核心模块，支撑工程建设全流程管理、实时监控与海量数据采集。

---

## 一、项目概述

### 基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 基建智慧工程管控项目 |
| 项目周期 | 2022.10 - 2025.10 |
| 用户规模 | 30-40 万用户 |
| 架构模式 | 微服务架构 + 多节点负载均衡 |
| 数据量级 | 千万级数据统计 + 多省份设备监控 |
| 技术栈 | `Spring Boot` `Spring Cloud` `MySQL` `Redis` `MyBatis` `Kafka` `RocketMQ` `Docker` `Jenkins` |

### 三大核心模块

| 模块 | 说明 |
|------|------|
| **工程中心** | 工程基础信息管理、资料归档、流程审批 |
| **进度中心** | 一二三级进度编制、里程碑管理、进度跟踪 |
| **安全中心** | 安全教育、安全检查、质量评估 |

### 工作职责

1. 负责**进度中心、工程中心核心模块开发**
2. 基于 **Redis + Caffeine 多级缓存**优化高频接口，5 个接口日均 120 万次调用，平均响应 **700ms → 100ms**，P99 **2.1s → 210ms**
3. 自研**分库分表组件**，设备 ID 哈希路由至 32 张分表 + 按月 Range 分区混合架构，解决五省天气设备数据日增量 1200 万条、单表 2.8 亿行的写入及查询瓶颈
4. 采用 **RocketMQ 异步消息驱动**改造一二三级进度编制流程，接口响应 **1.5s → 80ms**
5. 针对千万级年度数据统计，通过 **SQL 重写 + 索引优化 + 多线程并行计算**，处理性能提升 **70%**

---

## 二、Redis + Caffeine 多级缓存

### 1. 业务背景与痛点

进度中心、工程中心的核心查询接口面临严重性能瓶颈——5 个高频接口日均调用约 **120 万次**，但每次请求都直接查询数据库。

| 问题 | 表现 |
|------|------|
| 响应缓慢 | 平均 **700ms**，P99 高达 **2.1s** |
| 数据库压力大 | 120 万次/天的读请求全部打到 MySQL |
| 用户体验差 | 页面加载慢，高频操作场景下等待感明显 |

### 2. 方案对比

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：只加 Redis** | 分布式缓存，所有实例共享 | 数据一致性好 | 每次请求仍需网络 IO（~1ms） | ⚠️ 可接受 |
| **方案B：Redis + Caffeine 多级** | L1 本地缓存（纳秒级）+ L2 Redis（~1ms） | L1 命中时无网络开销 | L1 多实例不一致，需要广播失效 | ✅ **选择** |
| **方案C：只做本地缓存** | Caffeine 本地缓存 | 速度最快 | 多实例不一致，容量有限 | ❌ |

**为什么选多级缓存？** 单纯加 Redis 在高并发下依然有网络 IO 开销（~1ms/次 × 120 万次 ≈ 20 分钟/天的网络延迟）。Caffeine 本地缓存命中时是纳秒级，完全不需要网络，适合高频读取、低频更新的数据。

### 3. 架构设计

```
请求到达
    ↓
┌──────────────┐
│  Caffeine    │  ← L1：进程内缓存（纳秒级）
│  (L1)        │     最大 10,000 条，过期 60s
└──────┬───────┘
       │ miss
       ▼
┌──────────────┐
│   Redis      │  ← L2：分布式缓存（~1ms）
│  (L2)        │     过期 3600s，AOF 持久化
└──────┬───────┘
       │ miss
       ▼
┌──────────────┐
│   MySQL      │  ← 回源数据库，回填 L1+L2
└──────────────┘
```

### 4. 缓存一致性处理

多级缓存的核心问题——L1 缓存多实例间数据不一致。更新时通过 RocketMQ 广播失效消息：

```
更新 DB → 删除 Redis → 广播 MQ → 所有实例删除 Caffeine → 下次请求重新加载
```

对于工程基础信息这类**读多写少、对一致性不敏感**的数据，秒级延迟在可接受范围内。

### 5. 收益

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 平均响应 | **700ms** | **100ms 以内** | **86%** |
| P99 响应 | **2.1s** | **~210ms** | **90%** |
| 日均调用量 | 120 万次 | 120 万次 | 缓存命中率 99%+ |

---

## 三、自研分库分表组件：Kafka 多线程消费 + 设备 ID 哈希路由

### 1. 业务背景与痛点

项目接入**五省天气监控设备数据**，设备实时上报温度、湿度、风速、气压等监测数据。数据量增长迅猛：

| 指标 | 数据 |
|------|------|
| 覆盖省份 | 5 省 |
| 日增量 | **约 1200 万条** |
| 单表数据量 | **突破 2.8 亿行** |
| 写入平均耗时 | **180ms**（持续恶化） |
| 范围查询耗时 | **2.3s**（按时间范围查整月数据时超时） |

#### 关键链路：Kafka 消费 + 批量写入

数据通过 **Kafka** 接入，消费者拉取消息后批量写入数据库：

```
五省设备 → Kafka Topic → 消费者拉取 → 批量 INSERT → MySQL
```

随着数据量增长，出现了两个瓶颈：

| 瓶颈 | 分析 |
|------|------|
| **单表写入性能下降** | 2.8 亿行数据的 B+ 树索引高度增加，每次 INSERT 维护索引的成本越来越高，平均写入耗时从 ~30ms 退化到 **180ms** |
| **范围查询超时** | 按时间范围的聚合查询需要扫描海量数据，即使走索引也要回表大量行，**2.3s** 已无法满足监控看板的需求 |

### 2. 方案对比

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：单表硬扛** | 加索引、加硬件 | 不动代码 | 治标不治本，2.8 亿行继续增长迟早扛不住 | ❌ |
| **方案B：MyBatis 插件动态分表** | 自研插件按设备 ID 哈希路由到 32 张物理分表 | 业务代码零侵入，灵活可控 | 需要自研路由组件 | ✅ **选择** |
| **方案C：ShardingSphere** | 引入中间件分库分表 | 功能全面 | 引入额外组件，调优成本高 | ❌ 暂不需要 |
| **方案D：分表 + 分区混合** | 分表（设备ID哈希）+ 分区（按月 Range） | 既分散写入压力，又优化范围查询 | 需同时维护分表和分区策略 | ✅ **组合方案B** |

**为什么自研而不是 ShardingSphere？** 项目的路由规则相对简单——按设备 ID 哈希取模即可，不需要跨分片 JOIN、分布式事务等 ShardingSphere 的高级能力。自研组件代码量不大（核心路由逻辑 ~200 行），避免了引入 ShardingSphere 后的配置复杂度和排障成本。

### 3. 核心架构

```
五省设备 → Kafka Topic（3 分区）
                │
        ┌───────┴───────┐
        │  多线程消费     │  ← 关键：多线程并行拉取，提高吞吐
        │  (thread pool) │
        └───────┬───────┘
                │ 批量写入
        ┌───────┴───────┐
        │  自研路由组件   │
        │  设备ID哈希取模 │
        └───────┬───────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌────────┐ ┌────────┐   ┌────────┐
│ tb_0   │ │ tb_1   │ … │ tb_31  │  ← 32 张物理分表
│ 分区P1  │ │ 分区P1  │   │ 分区P1  │
│ 分区P2  │ │ 分区P2  │   │ 分区P2  │  ← 按月 Range 分区
│ 分区P3  │ │ 分区P3  │   │ 分区P3  │
└────────┘ └────────┘   └────────┘
```

### 4. 实现方案

#### 多线程 Kafka 消费（重要）

```java
@Component
public class WeatherDataConsumer {

    // 多线程消费 Kafka 消息，提高吞吐量
    @KafkaListener(topics = "weather-device-data", concurrency = "3")
    public void consume(List<ConsumerRecord<String, String>> records, Acknowledgment ack) {
        // 批量处理，按设备 ID 分组后路由写入对应分表
        List<WeatherData> batch = records.stream()
            .map(r -> JSON.parseObject(r.value(), WeatherData.class))
            .collect(Collectors.toList());

        // 批量写入（通过自研路由组件自动路由到目标分表）
        weatherDataService.batchInsert(batch);
        ack.acknowledge();
    }
}
```

**为什么多线程消费很重要？** 单线程消费 Kafka 消息，处理速度受限于单条写入时间（~180ms）。使用多线程并发消费（`concurrency = "3"`，配合 Kafka 分区数），并行处理多批消息，整体吞吐量提升 3 倍。

#### 自研路由组件：设备 ID 哈希取模

```java
@Component
public class TableRouter {

    /** 32 张物理分表 */
    private static final int TABLE_COUNT = 32;

    /** 根据设备 ID 哈希取模，路由到目标物理分表 */
    public String route(String deviceId, LocalDateTime time) {
        // 1. 设备 ID 哈希取模 → 确定物理分表
        int tableIndex = Math.abs(deviceId.hashCode() % TABLE_COUNT);

        // 2. 按月分区 → 确定分区
        String partitionName = String.format("p_%04d%02d", time.getYear(), time.getMonthValue());

        // 返回物理表名：weather_data_08
        return String.format("weather_data_%02d", tableIndex);
    }
}
```

**为什么按设备 ID 哈希而不是按时间？**
- 设备 ID 哈希取模 → **同一设备的数据集中在同一张分表**，方便按设备维度的查询（如查某个设备的历史趋势）
- 按月 Range 分区 → **按时间维度的查询可以分区裁剪**，只扫描目标月份的数据

#### 分表 + 分区混合架构

```sql
-- 建表示例：每张物理分表下按月建立 Range 分区
CREATE TABLE weather_data_00 (
    id BIGINT AUTO_INCREMENT,
    device_id VARCHAR(64),
    province VARCHAR(32),
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    wind_speed DECIMAL(5,2),
    collect_time DATETIME,
    create_time DATETIME,
    PRIMARY KEY (id, collect_time),
    INDEX idx_device_id (device_id),
    INDEX idx_collect_time (collect_time)
) PARTITION BY RANGE (TO_DAYS(collect_time)) (
    PARTITION p_202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
    PARTITION p_202602 VALUES LESS THAN (TO_DAYS('2026-03-01')),
    PARTITION p_202603 VALUES LESS THAN (TO_DAYS('2026-04-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

**分表 vs 分区的定位**：

| 维度 | 分表（设备 ID 哈希） | 分区（按月 Range） |
|------|-------------------|-------------------|
| 解决什么问题 | 分散写入压力，避免单表过大 | 优化范围查询，分区裁剪 |
| 路由依据 | 设备 ID 哈希取模 | collect_time 时间范围 |
| 写入影响 | 32 张表并行写入，分散 IO | 写入时自动路由到对应分区 |
| 查询（按设备） | 直接定位到目标分表 | — |
| 查询（按时间范围） | 需查询所有分表 | 分区裁剪，只扫目标分区 |

### 5. 收益

| 指标 | 优化前（单表 2.8 亿行） | 优化后（32 分表 + 月分区） |
|------|---------------------|------------------------|
| 单表数据量 | **2.8 亿行** | < 1000 万行/分表（月分区后更少） |
| 写入耗时 | **180ms** | **~15ms**（↓92%） |
| 范围查询 | **2.3s**（超时） | **~120ms**（分区裁剪后） |
| 数据倾斜 | — | 设备 ID 哈希均匀分布，无热点 |
| 业务代码侵入 | — | **0**（路由组件自动处理） |

---

## 四、RocketMQ 异步化进度编制

### 1. 业务背景与痛点

一二三级进度编制流程涉及多级计划联动——一级计划调整后，二级、三级计划需要联动更新。原来的同步调用导致：

```
用户保存一级进度 → 计算二级计划 → 计算三级计划 → 返回结果
                 ↓
           接口响应 1.5s，用户等待
```

| 问题 | 影响 |
|------|------|
| 接口响应慢 | 平均 1.5s，用户体验差 |
| 耦合紧密 | 一级编制失败导致后续全部回滚 |
| 无法削峰 | 多用户同时编制时，数据库连接飙升 |

### 2. 方案对比

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：同步优化** | 优化联计算逻辑 | 改动小 | 治标不治本，仍有超时风险 | ❌ |
| **方案B：RocketMQ 异步消息驱动** | 保存后发 MQ，异步联动计算 | 接口快速返回，削峰填谷 | 需要处理消息一致性 | ✅ **选择** |
| **方案C：线程池异步** | 线程池异步执行联动计算 | 不需要中间件 | 服务重启丢失任务 | ❌ |

**为什么异步化？** 进度编制的联动计算不是用户需要实时等待的结果——用户保存一级进度后，二级三级的联动计算可以在后台完成。利用 RocketMQ 的延迟消息 + 重试机制，既能快速响应用户，又能保障最终一致性。

### 3. 实现方案

```java
// 同步改异步
public void saveProgress(ProgressRequest request) {
    // 1. 保存一级进度（核心逻辑，同步执行）
    progressService.saveLevel1(request);
    // 2. 联动计算发 MQ 异步处理
    rocketMqTemplate.send("progress-linkage-topic", request);
    // 返回：80ms
}
```

### 4. 最终一致性保障

```
正常流程：MQ 消费 → 二级编制 → 三级编制 → 更新状态
异常流程：消费失败 → 16 级阶梯重试 → 死信队列 → 人工处理
补偿任务：定时扫描超时未完成的编制 → 重新投递消息
```

### 5. 收益

| 指标 | 优化前（同步） | 优化后（异步） |
|------|-------------|--------------|
| 接口响应 | **1.5s** | **~80ms**（↓95%） |
| 业务耦合 | 紧耦合，一级失败全部回滚 | 解耦，互不影响 |
| 削峰能力 | 无 | 消息队列削峰填谷 |

---

## 五、年度工程统计优化：单线程→多线程并行 + 缓存预热

### 1. 业务背景与痛点

系统需要统计全年工程数据，数据量达到**千万级**。原来的实现是单线程 + SQL 聚合方式：

```
用户点击"年度统计"
    ↓
单线程执行 → 复杂 SQL 聚合 → 返回结果
    ↓
统计时间超过 1 分钟，页面长时间等待，严重影响体验
```

**瓶颈分析**：

| 瓶颈 | 分析 |
|------|------|
| **单线程处理** | 千万级数据的聚合计算全部在一个线程中串行执行，CPU 利用率低 |
| **SQL 复杂聚合** | 嵌套子查询 + 多表 JOIN，数据库侧计算压力大 |
| **数据量过大** | 全年数据全量扫描，即使走索引 IO 开销也很大 |

### 2. 方案对比

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：SQL 硬扛** | 继续优化 SQL，单线程执行 | 不用改代码 | 数据量继续增长还是会慢，无扩展性 | ❌ |
| **方案B：多线程并行统计** | 按月拆分任务，`CompletableFuture` 并行执行，合并结果 | 充分利用多核 CPU，时间大幅缩短 | 需要处理线程池参数、结果合并逻辑 | ✅ **选择** |
| **方案C：离线预计算** | 定时任务提前统计，结果缓存到 Redis | 用户查询时毫秒级返回 | 数据不是实时，需要预热策略 | ✅ **组合方案B** |

### 3. 最终方案：并行统计 + 缓存预热

```
年度统计请求
    │
    ├── 缓存命中 → 直接从 Redis 返回（毫秒级）
    │
    └── 缓存未命中 → 多线程并行计算
            │
        ┌───┴───┐
        │ 按月拆分 12 个子任务
        │ CompletableFuture 并行执行
        └───┬───┘
            │
        ┌───┴───┐
        │ 合并结果 → 写入 Redis 缓存
        │ 设置过期时间（与定时任务刷新频率对齐）
        └───┬───┘
            │
            ▼
        返回统计结果
```

#### CompletableFuture 并行编排

```java
@Service
public class AnnualStatisticsService {

    private final ThreadPoolExecutor statsExecutor;
    private final StatisticsMapper statsMapper;
    private final RedisTemplate redisTemplate;

    public AnnualStatisticsResult calculate(int year) {
        // 1. 查缓存
        String cacheKey = "stats:annual:" + year;
        AnnualStatisticsResult cached = (AnnualStatisticsResult) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) return cached;

        // 2. 按月拆分 12 个任务，CompletableFuture 并行
        List<CompletableFuture<MonthStatistics>> futures = new ArrayList<>();
        for (int month = 1; month <= 12; month++) {
            int finalMonth = month;
            CompletableFuture<MonthStatistics> future = CompletableFuture.supplyAsync(
                () -> statsMapper.statisticsByMonth(year, finalMonth),
                statsExecutor
            );
            futures.add(future);
        }

        // 3. 合并 12 个月的结果
        List<MonthStatistics> monthData = futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());

        AnnualStatisticsResult result = mergeResult(monthData);

        // 4. 结果写入缓存
        redisTemplate.opsForValue().set(cacheKey, result, 2, TimeUnit.HOURS);

        return result;
    }
}
```

**CompletableFuture 的核心特性**：任务提交后不阻塞当前线程，先注册回调；等前序任务完成后自动触发后续任务执行。全程基于**状态机 + 链表回调 + CAS 无锁设计**，避免了传统线程池 `submit().get()` 的阻塞等待。

#### 线程池配置

考虑到统计任务是**IO 密集型**（主要是数据库查询和网络 IO），线程数需要比 CPU 密集型更多：

```java
@Bean("statisticsExecutor")
public ThreadPoolExecutor statisticsExecutor() {
    int cpuCores = Runtime.getRuntime().availableProcessors();
    return new ThreadPoolExecutor(
        cpuCores * 3,                  // corePoolSize
        cpuCores * 6,                  // maximumPoolSize
        60L, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(2000), // 有界队列
        new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略：调用方执行
    );
}
```

| 参数 | 值 | 理由 |
|------|-----|------|
| `corePoolSize` | CPU × 3 | IO 密集型任务，线程等待 IO 时可让出 CPU |
| `maximumPoolSize` | CPU × 6 | 高峰期可临时扩容 |
| `workQueue` | `ArrayBlockingQueue`(2000) | 有界队列，防止任务无限堆积导致 OOM |
| 拒绝策略 | `CallerRunsPolicy` | 队列满时由调用线程执行，作为天然背压 |

#### 定时任务缓存预热

```java
@Component
public class StatisticsPreheatJob {

    @Scheduled(cron = "0 0 3 1 1 ?") // 每年 1 月 1 日凌晨 3 点执行
    public void preheatAnnualStatistics() {
        int lastYear = LocalDate.now().getYear() - 1;
        log.info("开始预热 {} 年统计数据", lastYear);
        annualStatisticsService.calculate(lastYear);
        log.info("{} 年统计缓存已预热完成", lastYear);
    }
}
```

### 4. SQL 方面也做了优化

除了并行计算，对原始 SQL 也进行了针对性的优化：

| 优化项 | 原 SQL 问题 | 优化后 |
|--------|------------|--------|
| **嵌套子查询** | `WHERE id IN (SELECT ... FROM ... WHERE ...)` | 改为 JOIN 或 EXISTS，减少扫描次数 |
| **大表驱动小表** | 大表作为驱动表，小表作为被驱动表，循环次数多 | 改为**小表驱动大表**，减少循环次数 |
| **IN 和 EXISTS 选择** | 根据数据分布选择了更合适的写法 | 小表用 IN，大表用 EXISTS |
| **复合索引** | 索引不够合理，部分查询回表 | 针对统计查询建立覆盖索引 |
| **大事务** | 单次统计查询在长事务中执行 | 拆分后每个子任务独立事务，避免大事务 |

### 5. 收益

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 统计耗时 | **> 1 分钟** | **~15s**（首次，12 线程并行） | **↓75%** |
| 缓存命中后 | — | **毫秒级** | 几乎无等待 |
| SQL 扫描行数 | 全表扫描 | 索引覆盖 + 分区裁剪 | 大幅降低 |
| 事务粒度 | 单一大事务 | 按月拆分独立事务 | 避免锁冲突 |

---

## 六、思考：是否还有更合适的方案

### 6.1 多级缓存，如果数据一致性要求更高怎么办？

当前方案是 Caffeine 60s 过期 + Redis 3600s 过期 + 更新时广播失效，接受秒级不一致。

如果业务要求**强一致性**，多级缓存就不适用了——只能放弃 L1 缓存，所有请求走 Redis。但代价是响应时间从 100ms 上升到 ~1ms 的网络延迟。这是一个 trade-off：**一致性越强，性能越差**。项目选择的度对工程基础信息这种读多写少的场景来说是合理的。

### 6.2 分表 + 分区混合架构，是不是最优解？

当前按设备 ID 哈希取模分 32 张表 + 按月 Range 分区，日增量 1200 万条的场景下表现良好。

但如果设备数量进一步增长（比如从 5 省扩展到 10 省），有几种演进路径：

| 方案 | 适用阶段 | 说明 |
|------|---------|------|
| **增加分表数**（32→64/128） | 当前阶段 | 只需要改 `TABLE_COUNT` 配置，对存量数据需要迁移 |
| **分库 + 分表** | 数据量再翻 10 倍 | 32 张表还不够的话，先按省份分库，再按设备 ID 分表 |
| **ShardingSphere** | 需要跨分片聚合查询时 | 比如查全国某时段平均温度，自研方案需要遍历所有分表 |

另外，多线程消费 Kafka 消息的 `concurrency` 参数需要和 **Kafka 分区数**匹配——分区数是 3，`concurrency = 3` 才能充分利用。如果后续需要提高消费吞吐，需要同时增加分区数，否则多余的消费者会被闲置。

### 6.3 RocketMQ 异步化，补偿任务会不会太复杂？

补偿任务是最终一致性的兜底手段：定时扫描状态为"处理中"但超过阈值的记录，重新投递 MQ。逻辑简单但需要在设计时考虑进去，否则上线后出现消息丢失才发现没有兜底。

一个更简单的替代方案是**不引入补偿任务，直接用 RocketMQ 的重试机制**——消费失败后 16 级阶梯重试（间隔 10s → 30s → 1min → ... → 2h），16 次都失败后进入死信队列人工介入。大多数场景下重试就够了，补偿任务是"万一"的保障。

### 6.4 年度统计优化，多线程并行有没有风险？

有。多线程并行计算需要关注几个问题：

| 风险 | 解决 |
|------|------|
| 线程数过多耗尽连接池 | 控制并行度（CPU × 3），`ArrayBlockingQueue` 有界队列 |
| 结果合并时 OOM | 按月拆分后数据量可控，12 个 `MonthStatistics` 对象不会很大 |
| 子任务依赖关系 | 月份之间无依赖，天然适合并行 |
| **数据倾斜** | 如果某个月的数据量远超其他月（如年底集中验收），该月的子任务会成为"慢任务"，拖慢整体合并时间 |

对于**数据倾斜**问题，当前按月拆分已经是最自然的拆分维度。如果某个月的数据量确实特别大，可以进一步对该月按省份或工程类型二次拆分。

另外，SQL 方面的 `IN` 和 `EXISTS` 选择需要结合具体数据分布——`IN` 适合子查询结果集小的情况，`EXISTS` 适合外层表小的情况。当时针对不同统计场景分别做了测试，没有一概而论。**
