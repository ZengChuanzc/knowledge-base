---
outline: deep
---

# 赫兹运力平台系统

> 赫兹运力系统是面向**电力物资运输**场景的企业级运力管理平台，覆盖 App、PC 管理端及小程序，支持运营、司机、承运商等多角色协同。系统作为能源物流运输数字化核心平台之一，**累计服务 400 万+ 运单**。

---

## 一、项目概述

### 基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 赫兹运力平台系统 |
| 项目周期 | 2026.04 - 2026.06 |
| 业务领域 | 电力物资运输、能源物流 |
| 服务规模 | 累计 400 万+ 运单 |
| 终端覆盖 | `App` `PC 管理端` `小程序` |
| 角色体系 | 运营、司机、承运商等多角色协同 |
| 技术栈 | `Spring Boot` `Spring Cloud` `MySQL` `Redis` `RocketMQ` `Nacos` `Docker` |

### 核心能力

- **运单管理**：运单创建、调度、跟踪、签收全流程
- **运力调度**：智能匹配运力资源与运输需求
- **轨迹监控**：实时位置追踪与异常告警
- **统计报表**：多维度报表中心，支撑运营决策

### 工作职责

1. 参与系统**重构及新旧系统切换**，负责核心业务模块改造与接口联调，保障系统平滑迁移与稳定上线
2. 主导**报表中心模块重构**，基于 `RocketMQ` 异步化 + 策略模式统一报表生成流程
3. 针对高频报表查询接口进行 **SQL 重写、索引优化及聚合查询优化**，平均响应由 `1.2s` 优化至 `200ms` 以内
4. 参与线上问题排查、接口联调及版本发布

---

## 二、报表中心：RocketMQ 异步化 + 策略模式

### 1. 业务背景与痛点

报表中心需要支撑多种报表类型：**运力报表、运单统计、费用分析、司机绩效、客户对账单**等。每种报表的生成逻辑不同，数据量大，生成耗时久。

原有方案是**同步生成**：

```
用户请求生成报表
    ↓
后端接收请求 → 查询数据库 → 聚合计算 → 填充模板 → 返回结果
    ↓
用户等待（平均 1.5s，部分复杂报表 > 5s）
```

**问题分析**：

| 问题 | 具体表现 | 影响 |
|------|---------|------|
| 接口长时间阻塞 | 复杂报表生成需要 3-5s，HTTP 连接长时间占用 | 前端超时、连接池耗尽 |
| 耦合严重 | 报表生成逻辑与业务请求在同一事务中 | 报表生成失败导致业务异常 |
| 扩展性差 | 新增报表类型需要修改现有代码 | 每次改动都要全量回归 |
| 用户体验差 | 用户点击"生成报表"后页面白等 | 多次点击加重系统负担 |

### 2. 方案选型对比

针对"报表生成慢、阻塞接口"的问题，评估了三种方案：

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：同步优化** | 继续同步，优化 SQL 和计算逻辑 | 架构不变，改动最小 | 复杂报表仍可能超时，治标不治本 | ❌ |
| **方案B：RocketMQ 异步化** | 请求先返回，MQ 异步处理，前端轮询结果 | 彻底解耦，用户体验好 | 引入消息队列复杂度，需要处理消息丢失/重复消费 | ✅ **选择** |
| **方案C：线程池异步** | 用线程池异步执行，Future 轮询结果 | 不需要额外中间件 | 服务重启丢失任务、无法跨节点追踪、无重试机制 | ❌ |

**为什么选 RocketMQ 而不是线程池？**

```
场景：报表生成任务可能在执行过程中，服务重启了怎么办？

方案C（线程池）：内存中的任务全部丢失 → 用户永远等不到报表
方案B（RocketMQ）：消息已持久化到磁盘 → 服务重启后继续消费 → 最终完成
```

另一个关键因素：RocketMQ 提供了**消息持久化、重试机制、死信队列**等能力，线程池全部需要自实现。而项目中已经引入了 RocketMQ，没有额外的运维成本。

### 3. 最终方案架构

```
用户请求生成报表
    ↓
┌────────────────────────────────────────┐
│           报表服务 (API)                 │
│  1. 创建报表任务记录（状态：初始化）       │
│  2. 发送 MQ 消息（topic: report-gen）    │
│  3. 立即返回 taskId                      │
└────────────────┬───────────────────────┘
                 │
                 ▼  RocketMQ
        ┌────────────────┐
        │   report-gen   │
        │     Topic      │
        └────────┬───────┘
                 │
                 ▼ 消费
┌────────────────────────────────────────┐
│           报表服务 (Consumer)            │
│  根据报表类型路由到对应策略               │
│       ↓                                │
│  运力报表策略 → 查询运力数据 → 生成报表    │
│  运单统计策略 → 查询运单数据 → 生成报表   │
│  费用分析策略 → 查询费用数据 → 生成报表   │
│       ↓                                │
│  更新任务状态（完成/失败）                │
└────────────────────────────────────────┘
                 │
                 ▼
用户前端轮询 → 获取报表URL → 展示
```

### 4. 策略模式实现

不同报表的生成逻辑差异很大，用策略模式替代 if-else 分支：

```java
// 策略接口
public interface ReportGenerator {
    String getReportType();
    Report generate(ReportRequest request);
}

// 运力报表策略
@Component
public class TransportCapacityReport implements ReportGenerator {
    @Override
    public String getReportType() { return "运力报表"; }

    @Override
    public Report generate(ReportRequest request) {
        // 查询运力数据 → 聚合计算 → 填充模板
        List<TransportData> data = transportMapper.queryByDate(request.getDateRange());
        return ReportBuilder.build(data, ReportTemplate.CAPACITY);
    }
}

// 运单统计策略
@Component
public class WaybillStatisticsReport implements ReportGenerator {
    @Override
    public String getReportType() { return "运单统计"; }

    @Override
    public Report generate(ReportRequest request) {
        // 查询运单数据 → 聚合计算 → 填充模板
        List<WaybillData> data = waybillMapper.statisticsByCondition(request.getParams());
        return ReportBuilder.build(data, ReportTemplate.WAYBILL);
    }
}

// 策略上下文：自动收集所有策略
@Component
public class ReportGeneratorContext {
    private final Map<String, ReportGenerator> generatorMap;

    public ReportGeneratorContext(List<ReportGenerator> generators) {
        this.generatorMap = generators.stream()
            .collect(Collectors.toMap(ReportGenerator::getReportType, Function.identity()));
    }

    public Report generate(String reportType, ReportRequest request) {
        ReportGenerator generator = generatorMap.get(reportType);
        if (generator == null) {
            throw new BizException("不支持的报表类型: " + reportType);
        }
        return generator.generate(request);
    }
}
```

### 5. 最终一致性保障

| 问题 | 风险 | 解决方案 |
|------|------|---------|
| 消息丢失 | 报表永远无法生成 | RocketMQ 同步刷盘（`FlushDiskType=SYNC_FLUSH`） |
| 消息重复 | 同��报表生成两次 | 报表任务表唯一索引 + 幂等性校验 |
| 消费失败 | 报表生成异常 | 16 级阶梯重试（间隔递增）→ 死信队列 → 人工处理 |
| 极端情况漏处理 | 任务状态一直为"处理中" | 定时补偿任务（每 5 分钟扫描超时未完成的任务重新投递） |

---

## 三、SQL 优化实战：高频报表查询 1.2s → 200ms

### 1. 问题发现

报表中心是系统核心模块之一，运营人员每天高频使用。线上监控发现部分高频报表查询接口响应缓慢，平均 **1.2s**，最慢的超过 **3s**，影响运营侧使用体验。

在 **腾讯云** 控制台查看慢查询日志，定位到最耗时的查询——一条 **7 表 JOIN** 的报表数据查询：

```sql
-- 报表数据查询（JOIN 7 张表，平均耗时 1.2s，最慢 > 3s）
SELECT
    oh.id, oh.order_no, oh.status, oh.create_time, oh.total_amount,
    oi.org_name, oi.org_code,
    ci.customer_name, ci.customer_code,
    di.driver_name, di.driver_phone,
    vi.vehicle_no, vi.vehicle_type,
    ri.route_name,
    pi.product_name,
    si.supplier_name
FROM order_header oh
LEFT JOIN org_info oi ON oh.org_id = oi.id
LEFT JOIN customer_info ci ON oh.customer_id = ci.id
LEFT JOIN driver_info di ON oh.driver_id = di.id
LEFT JOIN vehicle_info vi ON oh.vehicle_id = vi.id
LEFT JOIN route_info ri ON oh.route_id = ri.id
LEFT JOIN product_info pi ON oh.product_id = pi.id
LEFT JOIN supplier_info si ON oh.supplier_id = si.id
WHERE oh.status IN (10, 20, 30, 40, 50, 60)
  AND oh.deleted = 0
  AND oi.org_name LIKE '%项目部%'
  AND ci.customer_code = 'CUS001'
  AND oh.create_time >= '2026-01-01'
ORDER BY oh.create_time DESC
LIMIT 20;
```

`EXPLAIN` 分析：

| id | select_type | table | type | key | rows | Extra |
|----|------------|-------|------|-----|------|-------|
| 1 | SIMPLE | oh | **ALL** | (null) | 3,872,456 | Using where; Using filesort |
| 1 | SIMPLE | oi | **ALL** | (null) | 12,541 | Using where |
| 1 | SIMPLE | ci | eq_ref | PRIMARY | 1 | — |
| 1 | SIMPLE | di | **ALL** | (null) | 23,478 | Using where |
| 1 | SIMPLE | vi | **ALL** | (null) | 15,632 | Using where |
| 1 | SIMPLE | ri | **ALL** | (null) | 8,451 | Using where |
| 1 | SIMPLE | si | **ALL** | (null) | 5,327 | Using where |

**问题**：

| 问题 | 分析 |
|------|------|
| **order_header 全表扫描** | `type=ALL`，扫描 **387 万行** |
| **6 张 JOIN 表全表扫描** | oi、di、vi、ri、si 全部 `type=ALL` |
| **文件排序** | `ORDER BY create_time` 无索引支持 |
| **WHERE 条件多且杂** | 多个 LIKE 模糊查询 + 范围条件 |

### 3. 方案评估

#### 为什么已有的联合索引没生效？

之前 DBA 已经为 `order_header` 建了联合索引 `(status, create_time, org_id)`。按理说应该能加速 `WHERE status IN (...)` 和 `ORDER BY create_time`。

但问题是**前端页面没有传递时间范围参数**，用户不习惯选时间直接点查询，导致 `WHERE` 中缺失 `create_time` 条件，联合索引退化：

```
联合索引 (status, create_time, org_id)

场景：WHERE status IN (...)   （create_time 缺失）
     → status IN (6个值) 本身是范围查询，
       MySQL 评估索引扫描 ≈ 全表扫描，
       最终选择全表扫描 + filesort ❌

场景：WHERE status IN (...) AND create_time >= ?  （有时间条件）
     → 先 status 定位，再 create_time 范围扫描 ✅
```

**根本原因**：前端不传时间，`create_time` 条件缺失，387 万行全表扫描 + 文件排序，查询缓慢。

#### 方案对比

| 方案 | 做法 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案A：强制前端传时间** | 时间选择器改为必填 | 索引能正常工作 | 改变用户习惯 | ❌ 产品否了 |
| **方案B：拆分索引 + 覆盖索引** | `status` 和 `create_time` 拆单列索引，Index Merge 优化；高频字段覆盖索引 | 不强制前端也能走索引 | 索引数量增加 | ✅ **选择** |
| **方案C：FORCE INDEX + 兜底** | 强制索引 + DAO 层配置时间范围 | 性能稳定 | 不够灵活 | ❌ |
| **方案D：JOIN 拆分 + 代码组装** | 基础表不 JOIN，走缓存代码组装 | 降低 JOIN 复杂度 | 代码量增加 | ⚠️ 补充 |

### 4. 最终优化方案

#### 索引重构

```sql
-- 1. status 单列索引（IN 过滤）
ALTER TABLE order_header ADD INDEX idx_status (status);
-- 2. create_time 单列索引（ORDER BY 排序）
ALTER TABLE order_header ADD INDEX idx_create_time (create_time);
-- 3. 覆盖索引：高频查询字段一次索引返回
ALTER TABLE order_header ADD INDEX idx_cover (status, create_time, id, order_no, total_amount);
-- 4. JOIN 表加索引
ALTER TABLE org_info ADD INDEX idx_org_name (org_name);
ALTER TABLE driver_info ADD INDEX idx_driver_name (driver_name);
ALTER TABLE vehicle_info ADD INDEX idx_vehicle_no (vehicle_no);
```

#### MyBatis 动态 SQL + 时间兜底

DAO 层兜底，前端不传时间时按配置的时间范围（半年）默认过滤：

```xml
<if test="startTime == null">
    AND oh.create_time >= #{defaultStartTime}
</if>
```

#### JOIN 拆分 + 缓存代码组装

`org_info`、`driver_info`、`vehicle_info` 等基础资料表——数据量小、变更少、可缓存——改为代码层查缓存组装：

```java
// Step 1：只查 order_header 主表
List<WaybillDO> waybills = waybillMapper.queryMain(params);
// Step 2：取关联 ID，缓存批量补全
Map<Long, String> orgMap = cache.batchGet(orgIds);
Map<Long, String> driverMap = cache.batchGet(driverIds);
// Step 3：代码层组装
waybills.forEach(w -> vo.setOrgName(orgMap.get(w.getOrgId())));
```

### 5. 优化成果

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 报表查询平均响应 | **1.2s** | **~200ms 以内** | **83%+** |
| 扫描行数 | 387 万行（全表） | ~15,000 行（索引范围扫描） | 99%+ |
| JOIN 表访问 | 7 张表，6 张全表扫描 | 全部走索引或缓存 | — |
| 前端改动 | — | **0 行** | — |

> 整体达到预期优化目标，高频报表接口平均响应从 **约 1.2s 降低至 200ms 以内**。

---

## 四、思考：是否还有更合适的方案

每个技术方案都是在特定约束下的选择。回顾一下，有些决策如果换一个场景，可能会有不同的答案。

### 4.1 RocketMQ 异步化，能不能不用 MQ？

报表异步生成用 RocketMQ 是因为项目里已经引入了 MQ，复用成本低。但如果是一个没有 MQ 的项目呢？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **线程池 + Future** | 不需要额外中间件 | 服务重启任务丢失，无法跨节点追踪 |
| **数据库任务表 + 定时任务** | 可靠持久化，实现简单 | 频繁轮询对 DB 有压力 |
| **RocketMQ** | 持久化、重试、死信队列、完备 | 增加中间件依赖 |

**结论**：如果团队运维能力有限或不想引入 MQ，**数据库任务表 + 定时任务**是一个可行的轻量替代方案——任务持久化到数据库，定时任务扫描未处理的任务执行，配合重试次数和状态管理。缺点是实时性不如 MQ，对 DB 有一定压力。选择哪条路取决于团队的基础设施现状。

### 4.2 策略模式，会不会过度设计？

策略模式在处理多种报表类型时很合适，但如果只有两三种报表而且基本不会新增，用 `if-else` 或 `switch` 反而更简洁。

```
报表类型 < 3 种且稳定 → if-else 足够，无需策略模式
报表类型 > 5 种且频繁新增 → 策略模式，值得
```

这个项目中报表类型多、业务变化快，策略模式是正确的选择，但不等于所有场景都适用。

### 4.3 SQL 优化，索引拆分是最优解吗？

将联合索引拆成单列索引，利用 MySQL Index Merge 来解决前端不传时间的问题，当前场景下方案是合理的。

但换个角度看——如果前端能传时间，联合索引 `(status, create_time, org_id)` 一次索引扫描就能搞定，效率比两个单列索引 Merge 更高。**本质上这是产品和技术的权衡**：

| 方向 | 成本 | 收益 |
|------|------|------|
| **说服产品改前端** | 沟通成本、用户习惯改变 | 索引效率最优 |
| **不改前端，后端兜底** | 0 沟通成本，0 前端改动 | 多建几个索引 |

最终选择了后者，不是因为它技术上更优，而是因为在当时的项目节奏下，**不改前端是最快解决问题的方式**——这本身也是一种工程决策。

### 4.4 JOIN 拆单表，有没有 N+1 问题？

JOIN 拆成单表查询 + 代码组装，如果实现不当，容易出现 N+1 问题——查了主表 20 条记录后，循环逐条去查关联表，反而更慢。

解决方案也很直接：**批量查询**。一次性取出所有关联 ID，用 `IN` 查询批量返回，再做内存映射。上面的实现中 `cache.batchGet(orgIds)` 就是这个目的——一次 IO 获取所有需要的 org 名称。

### 4.5 如果数据量继续增长（千万级 → 亿级）怎么办？

目前的优化手段在千万级数据量下效果显著，但如果数据量继续增长到亿级，可能需要考虑：

| 手段 | 适用阶段 |
|------|---------|
| 索引优化 + SQL 重写 | 千万级 |
| 分库分表（ShardingSphere） | 亿级 |
| 异构数据（ES 用于查询，MySQL 用于存储） | 亿级 + 复杂搜索 |
| 冷热数据分离 | 亿级 + 历史数据不常查 |

这个项目目前处于千万级阶段，索引优化和缓存已经能解决问题，但了解后续的演进路径是有必要的——**技术方案的选择从来不是一劳永逸的**。

---

## 参考链接

- [RocketMQ 官方文档](https://rocketmq.apache.org/docs/)
- [MySQL EXPLAIN 解读——美团技术博客](https://tech.meituan.com/2014/06/30/mysql-index.html)
- [策略模式——Spring 笔记](/java/spring)
