# Spring 生态原理与实战

> Spring 是 Java 企业级开发的事实标准。从 IoC 容器到 AOP、从事务管理到 Spring Boot 自动配置，本文深入核心原理，涵盖生产实践与常见踩坑。

---

## 一、Spring IoC 容器

### 1. 容器体系结构

```
                    BeanFactory (接口)
                         ↑
                    ApplicationContext (接口)
           ┌──────────────┼──────────────┐
           │              │              │
   ClassPathXml      AnnotationConfig   WebApplication
   ApplicationContext  ApplicationContext  Context

- BeanFactory：最基础的容器，延迟加载
- ApplicationContext：扩展了事件发布、国际化、AOP 等能力，预加载单例
```

### 2. BeanFactory 与 ApplicationContext 的区别

| 维度 | BeanFactory | ApplicationContext |
|------|-------------|-------------------|
| 实例化策略 | **懒加载**（调用 `getBean()` 时创建） | **预加载**（启动时创建所有单例） |
| 事件机制 | ❌ 不支持 | ✅ 支持事件发布-监听 |
| 国际化 | ❌ 不支持 | ✅ 支持 MessageSource |
| AOP 支持 | 基础支持 | 完整支持 |
| 常用实现 | `DefaultListableBeanFactory` | `AnnotationConfigApplicationContext` |

```java
// BeanFactory —— 按需获取
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();
// ... 注册 BeanDefinition ...
UserService userService = factory.getBean(UserService.class);  // 此时才创建

// ApplicationContext —— 启动即加载
AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
// 启动时所有单例 Bean 已经创建完成
```

### 3. Bean 的生命周期（核心）

```
实例化 ──→ 属性注入 ──→ Aware 接口 ──→ BeanPostProcessor#postProcessBeforeInitialization
  ↑                                                                         │
  │                                                                         ▼
  │                                                    InitializingBean#afterPropertiesSet
  │                                                          / @PostConstruct / init-method
  │                                                                         │
  │                                                                         ▼
  │                                                    BeanPostProcessor#postProcessAfterInitialization
  │                                                                         │
  │                                                                         ▼
  │                                                              Bean 就绪（可用了）
  │                                                                         │
  │                                                                         ▼
  │                                                          容器关闭 → @PreDestroy
  │                                                          / DisposableBean#destroy
  │                                                          / destroy-method
  └────────────────────────── 销毁 ─────────────────────────←───────────────┘
```

#### 完整阶段详解

| 阶段 | 触发时机 | 常见用途 |
|------|---------|---------|
| **实例化** | 调用构造器 | `new` 对象，默认使用无参构造 |
| **属性注入** | 依赖注入（Setter/Field） | `@Autowired`、`@Resource` |
| **Aware 接口** | 注入 Spring 容器组件 | `BeanNameAware`、`ApplicationContextAware`、`EnvironmentAware` |
| **BeanPostProcessor before** | 初始化前调用 | 代理创建、包装对象 |
| **@PostConstruct** | 初始化回调 | 资源初始化、数据校验 |
| **InitializingBean** | `afterPropertiesSet()` | 属性注入后的初始化逻辑 |
| **init-method** | XML/注解指定的初始化 | 类似 `@PostConstruct` |
| **BeanPostProcessor after** | 初始化后调用 | AOP 代理返回（关键！） |
| **Bean 就绪** | 放入容器 | 对外提供服务 |
| **@PreDestroy** | 容器关闭前 | 资源清理、连接关闭 |
| **DisposableBean** | `destroy()` | 释放资源 |

#### 关键源码：AbstractAutowireCapableBeanFactory

```java
// Spring 5.x 源码（核心方法）
protected Object doCreateBean(String beanName, RootBeanDefinition mbd, @Nullable Object[] args) {
    // 1. 实例化
    BeanWrapper instanceWrapper = createBeanInstance(beanName, mbd, args);
    
    // 2. 属性注入
    populateBean(beanName, mbd, instanceWrapper);
    
    // 3. 初始化
    Object exposedObject = bean;
    try {
        // 3.1 BeanPostProcessor before
        exposedObject = applyBeanPostProcessorsBeforeInitialization(exposedObject, beanName);
        // 3.2 初始化方法（@PostConstruct / afterPropertiesSet / init-method）
        invokeInitMethods(beanName, exposedObject, mbd);
        // 3.3 BeanPostProcessor after ← AOP 代理在这里返回
        exposedObject = applyBeanPostProcessorsAfterInitialization(exposedObject, beanName);
    } catch (Throwable ex) {
        // ...
    }
    return exposedObject;
}
```

::: tip 记住关键点
AOP 代理是在 **BeanPostProcessor#postProcessAfterInitialization** 阶段创建的。
这意味着：`@PostConstruct` 方法中 `this` 是原始对象，不是 AOP 代理对象。
:::

### 4. 依赖注入方式

| 方式 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **构造器注入**（推荐） | `public A(B b) { this.b = b; }` | 不可变、可测试、非空保证 | 参数过多时代码冗长 |
| **Setter 注入** | `@Autowired public void setB(B b) {}` | 可选依赖 | 可变性 |
| **字段注入** | `@Autowired private B b;` | 代码简洁 | 无法测试、循环依赖隐患 |

```java
// ✅ Spring 官方推荐：构造器注入
@RestController
public class UserController {
    private final UserService userService;
    private final OrderService orderService;
    
    public UserController(UserService userService, OrderService orderService) {
        this.userService = userService;
        this.orderService = orderService;
    }
}
```

### 5. 循环依赖与三级缓存

Spring 使用**三级缓存**解决单例 Bean 的循环依赖问题。

```java
// DefaultSingletonBeanRegistry 三级缓存
public class DefaultSingletonBeanRegistry {
    // 一级缓存：成品对象（完全初始化）
    private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);
    
    // 二级缓存：半成品对象（已实例化但未完成属性注入）
    private final Map<String, Object> earlySingletonObjects = new ConcurrentHashMap<>(16);
    
    // 三级缓存：对象工厂（提前暴露，生成代理对象）
    private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);
}
```

**循环依赖处理流程**（A 依赖 B，B 依赖 A）：

```
1. Spring 开始创建 A
2. A 实例化（半成品）→ 放入三级缓存（singletonFactories）
3. A 属性注入 → 发现依赖 B
4. Spring 开始创建 B
5. B 实例化 → 放入三级缓存
6. B 属性注入 → 发现依赖 A
7. B 从三级缓存获取 A 的提前引用（ObjectFactory.get()）
   └─ 这步可能触发 AOP，返回代理对象 → 放入二级缓存
8. B 继续完成初始化 → B 成为成品 → 放入一级缓存
9. A 继续完成属性注入 → 获取到 B
10. A 完成初始化 → 成为成品 → 放入一级缓存

对象引用流转：
   三级缓存 (early reference)  ──→ 二级缓存 (提前暴露的代理)  ──→ 一级缓存 (成品)
   singletonFactories          earlySingletonObjects           singletonObjects
```

#### 哪些场景不能解决？

```java
// 场景1：构造器注入循环依赖（无法解决 ❌）
@Component
public class A {
    public A(B b) { }  // 构造器阶段就需 B，此时 A 还没实例化，三级缓存无记录
}

// 场景2：多例（prototype）循环依赖（无法解决 ❌）
// prototype 不缓存，三级缓存中找不到

// 场景3：@Async 注解导致循环依赖（容易踩坑）
// @Async 会生成代理，且代理对象在 BeanPostProcessor after 阶段才生成
// 这时候三级缓存已经用过了，拿到的是原始对象而非代理
// 解决方案：@Lazy 延迟加载一个
@Component
public class A {
    @Lazy  // 懒加载打破循环
    @Autowired
    private B b;
}
```

::: warning 循环依赖最佳实践
虽然 Spring 支持循环依赖，但**应该避免在设计层面引入循环依赖**。它往往是代码设计不合理的信号：
- 将相互依赖的逻辑拆分为三个 Bean（A → C → B）
- 使用事件驱动替代循环调用
- 使用 `@Lazy` 延迟加载

从 Spring Boot 2.6+ 开始，**默认禁止循环依赖**：
```properties
# application.properties
spring.main.allow-circular-references=false   # 默认值
```
:::

---

## 二、Spring AOP 原理

### 1. 代理方式

Spring AOP 基于**动态代理**实现，支持两种方式：

| 代理方式 | 条件 | 实现 | 特点 |
|---------|------|------|------|
| **JDK 动态代理** | Bean 实现了接口 | `java.lang.reflect.Proxy` | 只能代理接口方法 |
| **CGLib 代理** | Bean 未实现接口 | `net.sf.cglib.proxy.Enhancer` | 通过继承实现，可代理类方法 |

```java
// Spring Boot 2.x+ 默认行为：
// - 如果 Bean 有接口 → JDK 动态代理（可通过 proxy-target-class 强制 CGLib）
// - 如果 Bean 无接口 → CGLib
// Spring Boot 2.0+ 默认 proxy-target-class=true（统一 CGLib）

// 强制使用 CGLib（Spring Boot 默认）
@EnableAspectJAutoProxy(proxyTargetClass = true)
```

### 2. 代理失效场景（高频踩坑）

```java
@Service
public class UserService {
    
    // 场景1：同类方法调用（方法内部调用），AOP 失效 ❌
    @Transactional
    public void methodA() {
        methodB();  // 直接调用 this.methodB()，不是代理对象
    }
    
    @Transactional
    public void methodB() {  // 事务不生效！
        // 因为 this 是原始对象，不是代理对象
    }
    
    // ✅ 解决方案1：注入自身代理（循环依赖风险）
    @Autowired
    private UserService self;
    
    @Transactional
    public void methodA() {
        self.methodB();  // 通过代理对象调用
    }
    
    // ✅ 解决方案2：提取到另一个 Service
    // ✅ 解决方案3：使用 AopContext.currentProxy()
    @Transactional
    public void methodA() {
        ((UserService) AopContext.currentProxy()).methodB();
    }
    
    // 场景2：private/protected 方法（CGLib 基于继承，private 不可见）
    // 场景3：final 方法（CGLib 不能覆写 final 方法）
    // 场景4：内部 static 类中的方法
}
```

::: warning 常见代理失效一览
| 场景 | 原因 | 解决 |
|------|------|------|
| 同类方法调用 | `this` 是原始对象 | 注入自身 / `AopContext.currentProxy()` |
| private 方法 | CGLib 无法覆写 private | 改为 public/protected |
| final 方法 | CGLib 无法覆写 final | 去掉 final |
| 静态方法 | 代理不拦截 static | 改为实例方法 |
| 构造方法中调用 | AOP 代理未生成完毕 | 使用 `@PostConstruct` |
| `@Async` + 同类调用 | 同步执行 | 注入自身代理 |
| 缺少 `@EnableAspectJAutoProxy` | 未开启 AOP | 添加注解 |
:::

### 3. AOP 核心概念

```java
@Aspect
@Component
public class LogAspect {
    
    // 切点：匹配 Controller 所有方法
    @Pointcut("execution(* com.example.controller.*.*(..))")
    public void controllerPointcut() {}
    
    // 前置通知
    @Before("controllerPointcut()")
    public void before(JoinPoint point) {
        log.info("调用方法：{}", point.getSignature().getName());
    }
    
    // 环绕通知
    @Around("@annotation(io.micrometer.core.annotation.Timed)")
    public Object measureTime(ProceedingJoinPoint point) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return point.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            if (cost > 1000) {
                log.warn("慢调用 [{}] 耗时：{}ms", point.getSignature(), cost);
            }
        }
    }
    
    // 异常通知
    @AfterThrowing(pointcut = "controllerPointcut()", throwing = "ex")
    public void handleException(JoinPoint point, Exception ex) {
        log.error("方法异常 [{}]: {}", point.getSignature(), ex.getMessage());
    }
}
```

| 通知类型 | 注解 | 执行时机 |
|---------|------|---------|
| 前置通知 | `@Before` | 目标方法执行前 |
| 后置通知 | `@After` | 目标方法执行后（无论是否异常） |
| 返回通知 | `@AfterReturning` | 目标方法正常返回后 |
| 异常通知 | `@AfterThrowing` | 目标方法抛出异常后 |
| 环绕通知 | `@Around` | 包裹目标方法（最强控制） |

### 4. 通知执行顺序

```
Spring 5.x + AOP 执行顺序：

         @Around (proceed 前)
              ↓
         @Before
              ↓
        目标方法执行
              ↓
         @AfterReturning / @AfterThrowing
              ↓
         @After
              ↓
         @Around (proceed 后)
```

当有多个通知时：
- **前置通知**：`@Order` 值小的先执行
- **后置通知**：`@Order` 值大的先执行（反转）

```java
@Aspect
@Component
@Order(1)  // 控制多个切面的执行顺序
public class TransactionAspect { }
```

---

## 三、Spring 事务机制

### 1. @Transactional 原理

```
@Transactional 标注的方法或类
        ↓
Spring AOP 生成代理对象
        ↓
代理对象拦截方法调用
        ↓
TransactionInterceptor.invoke()
        ↓
根据 @Transactional 参数获取 TransactionAttribute
        ↓
PlatformTransactionManager.getTransaction()
        ↓
   ┌─ 存在事务 → 根据 propagation 决定：挂起/加入/新事务
   └─ 不存在事务 → 创建新事务
        ↓
invokeWithinTransaction() → 执行目标方法
        ↓
正常返回 → commit()   |   异常 → rollback()
```

```java
@Transactional
public void businessMethod() {
    // 1. 事务管理器获取/创建事务
    // 2. 执行业务逻辑
    // 3. 正常 → 提交   异常 → 回滚
}
```

### 2. 传播行为（Propagation）

| 传播行为 | 含义 | 适用场景 |
|---------|------|---------|
| `REQUIRED`（默认） | 有事务用当前，没有则新建 | 大部分业务方法 |
| `REQUIRES_NEW` | 挂起当前事务，新建一个 | 日志记录、审计（不受主事务回滚影响） |
| `NESTED` | 嵌套事务，回滚到保存点 | 批量处理中单条失败不影响整体 |
| `SUPPORTS` | 有则参与，没有也无所谓 | 查询方法 |
| `NOT_SUPPORTED` | 挂起当前事务，以非事务方式运行 | 发送通知 |
| `MANDATORY` | 强制有事务，没有则抛异常 | 必须被事务调用的方法 |
| `NEVER` | 强制无事务，有则抛异常 | 不允许事务中执行 |

```java
@Service
public class OrderService {
    
    // 主事务
    @Transactional(rollbackFor = Exception.class)
    public void createOrder(Order order) {
        saveOrder(order);
        
        // 要求：即使主事务回滚，日志也必须记录
        logService.saveLog(order);  // REQUIRES_NEW
    }
}

@Service
public class LogService {
    
    // ⚠️ REQUIRES_NEW：独立事务，主事务回滚不影响
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveLog(Order order) {
        // 写入日志表
    }
}
```

### 3. 事务失效的 8 种场景

::: danger @Transactional 失效排查清单

| # | 场景 | 原因 | 解决方案 |
|---|------|------|---------|
| 1 | **同类方法调用** | `this.method()` 绕过代理 | 注入自身 / 提取到其他 Service |
| 2 | **private 方法** | AOP 代理不可见 private | 改成 public |
| 3 | **异常被 catch** | 未抛出事务管理器可见的异常 | catch 中手动回滚：`TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` |
| 4 | **异常类型不对** | 默认只回滚 `RuntimeException` | `@Transactional(rollbackFor = Exception.class)` |
| 5 | **非 public 方法** | CGLib 代理限制 | 用 public |
| 6 | **数据库引擎不支持事务** | MySQL MyISAM | 改用 InnoDB |
| 7 | **@Transactional 在父类/接口上** | 接口注解被忽略（JDK 代理时） | 注解写在实现类上 |
| 8 | **方法内部直接 new 线程** | 事务绑定当前线程 | 使用 `@Async` 或手动管理事务 |

```java
// ❌ 错误：异常被 catch，事务不会回滚
@Transactional
public void createUser(User user) {
    try {
        userDao.insert(user);
        throw new RuntimeException("模拟失败");
    } catch (Exception e) {
        log.error("发生异常", e);
        // ❌ 异常被捕获，事务管理器无法感知
    }
}

// ✅ 正确：手动回滚
@Transactional
public void createUser(User user) {
    try {
        userDao.insert(user);
        throw new RuntimeException("模拟失败");
    } catch (Exception e) {
        log.error("发生异常", e);
        TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}

// ✅ 正确：直接抛出异常
@Transactional(rollbackFor = Exception.class)
public void createUser(User user) {
    userDao.insert(user);
    throw new RuntimeException("模拟失败");  // 让事务管理器处理
}
```
:::

### 4. 事务隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|---------|------|-----------|------|------|
| `READ_UNCOMMITTED` | ✅ 可能 | ✅ 可能 | ✅ 可能 | 最低级别，很少用 |
| `READ_COMMITTED` | ❌ | ✅ 可能 | ✅ 可能 | **Oracle 默认，PostgreSQL 默认** |
| `REPEATABLE_READ` | ❌ | ❌ | ✅ 可能 | **MySQL InnoDB 默认** |
| `SERIALIZABLE` | ❌ | ❌ | ❌ | 性能最低 |

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void queryWithReadCommitted() { }
```

::: tip 隔离级别选择建议
- **默认使用数据库的默认隔离级别**（MySQL RR、Oracle RC），不要随便改
- 大多数场景 `READ_COMMITTED` 已经足够
- 如果有严格的不可重复读需求，用 `REPEATABLE_READ`，但要关注间隙锁带来的死锁风险
- `SERIALIZABLE` 性能极差，生产基本不用
:::

### 5. 事务超时与只读优化

```java
// 查询方法建议标注 readOnly
@Transactional(readOnly = true, timeout = 30)
public List<User> findAll() {
    return userMapper.selectAll();
}
```

| 参数 | 作用 | 底层实现 |
|------|------|---------|
| `readOnly = true` | 提示数据库进行只读优化 | MySQL 会取消行锁；JPA 会刷新 FlushMode 为 NEVER |
| `timeout = 30` | 超时自动回滚 | `TransactionManager` 定时检测 |

::: warning 注意
`readOnly = true` **不能保证没有写操作**——它只是提示（给 JDBC driver 和 ORM 框架）。如果没有写权限，数据库层面要配置只读用户。
:::

---

## 四、Spring Boot 自动配置

### 1. @SpringBootApplication 三板斧

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootConfiguration   // = @Configuration
@EnableAutoConfiguration  // 自动配置核心
@ComponentScan            // 包扫描（当前包及其子包）
public @interface SpringBootApplication { }
```

### 2. 自动配置原理

```
@EnableAutoConfiguration
        ↓
@Import(AutoConfigurationImportSelector.class)
        ↓
selectImports() 方法
        ↓
加载 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
（JDK 9+，以前是 spring.factories）
        ↓
读取 130+ AutoConfiguration 类
        ↓
根据 @Conditional 条件判断是否生效
        ↓
生效 → 创建对应的 Bean
```

#### 常用 @Conditional

| 条件注解 | 生效条件 |
|---------|---------|
| `@ConditionalOnClass` | 类路径存在指定类 |
| `@ConditionalOnMissingBean` | 容器中不存在指定 Bean |
| `@ConditionalOnProperty` | 配置项是否为指定值 |
| `@ConditionalOnWebApplication` | 当前是否为 Web 环境 |
| `@ConditionalOnExpression` | SpEL 表达式为 true |

```java
// RedisAutoConfiguration 简版源码
@AutoConfiguration
@ConditionalOnClass(RedisOperations.class)  // 有 Redis 依赖才生效
@EnableConfigurationProperties(RedisProperties.class)
public class RedisAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean(name = "redisTemplate")  // 用户没自定义才自动配置
    @ConditionalOnSingleCandidate(RedisConnectionFactory.class)
    public RedisTemplate<Object, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<Object, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        return template;
    }
}
```

### 3. 自定义 Starter

```java
// 1. 自动配置类
@AutoConfiguration
@ConditionalOnClass(MailService.class)
@EnableConfigurationProperties(MailProperties.class)
public class MailAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public MailService mailService(MailProperties properties) {
        return new MailService(properties.getHost(), properties.getPort());
    }
}

// 2. 配置类
@ConfigurationProperties(prefix = "app.mail")
public class MailProperties {
    private String host;
    private int port = 25;
    // getter & setter
}

// 3. spring.factories（Spring Boot 2.x）
// META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
// com.example.starter.MailAutoConfiguration
```

#### 自定义 Starter 命名规范

```yaml
# Spring Boot 官方 starter
spring-boot-starter-{module}    # 如 spring-boot-starter-web

# 第三方（非 Spring 官方）
{module}-spring-boot-starter    # 如 mybatis-spring-boot-starter
{module}-spring-boot-autoconfigure  # 自动配置模块（推荐分离）
```

### 4. Spring Boot 配置加载优先级

```
1. @TestPropertySource 注解          ← 最高优先级
2. 命令行参数 (--server.port=8080)
3. JNDI 属性 (java:comp/env)
4. 系统属性 (-Dkey=value)
5. OS 环境变量
6. application-{profile}.properties
7. application.properties / application.yml
8. @PropertySource 注解
                                         ← 最低优先级
```

---

## 五、Spring MVC

### 1. DispatcherServlet 处理流程

```
请求到达
    ↓
DispatcherServlet（前端控制器）
    ↓ 查询 HandlerMapping
HandlerExecutionChain（Handler + Interceptors）
    ↓
HandlerAdapter.handle()
    ↓
执行 Controller 方法（进入拦截器链 → 目标方法 → 拦截器链后退）
    ↓ 返回 ModelAndView
ViewResolver 解析视图
    ↓
View 渲染响应
    ↓
返回给客户端
```

### 2. 拦截器 vs 过滤器

| 维度 | Filter（Servlet） | Interceptor（Spring） |
|------|-------------------|----------------------|
| 规范 | Servlet 规范 | Spring 框架 |
| 生效范围 | 所有 URL（包括静态资源） | 仅 Controller 请求 |
| 访问资源 | 不能访问 Spring Bean | 可访问 IoC 容器中的 Bean |
| 粒度 | 粗粒度 | 细粒度（可匹配 Ant 路径） |
| 典型应用 | 字符编码、跨域、鉴权 Token | 权限校验、日志、性能监控 |

```java
// 拦截器示例：接口耗时监控
@Component
public class TimeInterceptor implements HandlerInterceptor {
    
    private static final ThreadLocal<Long> startTime = new ThreadLocal<>();
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, 
                             Object handler) {
        startTime.set(System.currentTimeMillis());
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        long cost = System.currentTimeMillis() - startTime.get();
        startTime.remove();  // 清理 ThreadLocal！
        if (cost > 1000) {
            log.warn("慢接口 [{} {}] 耗时：{}ms", request.getMethod(), 
                     request.getRequestURI(), cost);
        }
    }
}
```

### 3. 统一异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    // 业务异常
    @ExceptionHandler(BizException.class)
    public Result<Void> handleBizException(BizException e) {
        log.warn("业务异常: code={}, msg={}", e.getCode(), e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }
    
    // 参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return Result.error(400, msg);
    }
    
    // 兜底异常
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e, HttpServletRequest request) {
        log.error("系统异常: {}", request.getRequestURI(), e);
        return Result.error(500, "系统繁忙，请稍后重试");
    }
}
```

---

## 六、Spring 常见踩坑与生产问题

### 1. @Autowired 字段注入的隐患

```java
// ❌ 字段注入——无法单元测试，循环依赖难以发现
@Autowired
private UserService userService;

// ✅ 构造器注入——单一职责、不可变、可测试
private final UserService userService;
public UserController(UserService userService) {
    this.userService = userService;
}
```

### 2. Spring Bean 的作用域问题

```java
@Component
@Scope("singleton")  // 默认：单例（一个应用仅一个实例）
public class SingletonBean {
    // ✅ 无状态 Bean（Service、Controller）
    // ❌ 有状态字段（如 int count）并发不安全
}

@Component
@Scope("prototype")  // 每次 getBean 创建新实例
public class PrototypeBean {
}

@Scope("request")    // 一次 HTTP 请求一个实例
@Scope("session")    // 一次 Session 一个实例
```

::: danger 单例 Bean 注入原型 Bean 的陷阱
```java
@Component
@Scope("singleton")
public class SingletonService {
    
    @Autowired
    private PrototypeBean prototypeBean;  // ❌ 只注入一次，永远是同一个对象
    
    public void doSomething() {
        prototypeBean.doSomething();  // 每次调用都是同一个 PrototypeBean！
    }
}

// ✅ 方案1：方法注入（@Lookup）
@Component
public abstract class SingletonService {
    public void doSomething() {
        PrototypeBean bean = createPrototypeBean();  // 每次获取新的
        bean.doSomething();
    }
    
    @Lookup
    protected abstract PrototypeBean createPrototypeBean();
}

// ✅ 方案2：ObjectFactory（推荐）
@Component
public class SingletonService {
    @Autowired
    private ObjectFactory<PrototypeBean> prototypeBeanFactory;
    
    public void doSomething() {
        PrototypeBean bean = prototypeBeanFactory.getObject();  // 每次新的
    }
}

// ✅ 方案3：ScopedProxy（不推荐，性能差）
@Component
@Scope(value = "prototype", proxyMode = ScopedProxyMode.TARGET_CLASS)
public class PrototypeBean { }
```
:::

### 3. Spring 事件机制使用不当

```java
// 事件发布
@Component
public class OrderEventPublisher {
    @Autowired
    private ApplicationEventPublisher publisher;
    
    public void publish(Order order) {
        publisher.publishEvent(new OrderCreatedEvent(order));
    }
}

// 事件监听
@Component
public class OrderEventListener {
    
    @Async  // ⚠️ 默认同步执行，建议异步
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)  
    // AFTER_COMMIT：事务提交后才触发，避免事件处理异常导致主事务回滚
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 发送短信、推送通知
    }
}
```

### 4. @Value 注入踩坑

```java
// ❌ 错误：null
@Value("${app.name}")       // 配置缺失导致启动失败（默认值：无）
private String appName;

// ✅ 正确：设默认值
@Value("${app.name:default}")
private String appName;

// ❌ 错误：静态变量注入
@Value("${app.name}")
private static String APP_NAME;  // null！Spring 不能注入静态字段

// ✅ 正确：静态变量通过 setter 注入
private static String APP_NAME;
@Value("${app.name}")
public void setAppName(String name) {
    APP_NAME = name;
}
```

### 5. Spring 事务 + 多数据源

```java
// 多数据源时需指定事务管理器
@Transactional(transactionManager = "orderTransactionManager")
public void createOrder(Order order) {
    orderDao.insert(order);
}
```

---

## 七、面试高频问题

### Q1：Spring IoC 容器的启动流程？

**答**（重点）：
1. **加载配置**：读取 XML / 注解 / Java Config，解析成 `BeanDefinition`
2. **BeanDefinition 注册**：注册到 `BeanDefinitionRegistry`
3. **BeanFactoryPostProcessor**：修改 BeanDefinition（如 `PropertySourcesPlaceholderConfigurer` 解析 `${}`）
4. **实例化所有单例 Bean**：按依赖关系依次创建
5. **BeanPostProcessor 注册**：为后续 Bean 增强做准备
6. **预实例化**：创建所有非懒加载的单例 Bean（经历完整 Bean 生命周期）
7. **Context 刷新完成**：发布 `ContextRefreshedEvent`

### Q2：Spring 如何解决循环依赖？

**答**：
Spring 通过**三级缓存**解决单例 Bean 的 Setter 注入循环依赖：
- 一级缓存（`singletonObjects`）：完全初始化好的 Bean
- 二级缓存（`earlySingletonObjects`）：提前暴露的半成品（未完成属性注入）
- 三级缓存（`singletonFactories`）：对象工厂，用于生成提前引用的 AOP 代理

流程：A 实例化 → 放入三级缓存 → 属性注入发现依赖 B → 创建 B → B 属性注入发现依赖 A → 从三级缓存获取 A 的提前引用 → B 完成初始化 → A 完成属性注入。

**不能解决**：构造器注入循环依赖、prototype 作用域循环依赖、`@Async` 循环依赖。

### Q3：@Transactional 注解失效的场景？

**答**：（详见上文"事务失效的 8 种场景"）常见的有：同类方法调用（最常见）、异常被 catch、异常类型不是 RuntimeException、private 方法、数据库引擎不支持事务等。

### Q4：Spring AOP 的 JDK 动态代理和 CGLib 有什么区别？

**答**：
- **JDK 动态代理**：基于接口，实现 `InvocationHandler`，运行时通过 `Proxy.newProxyInstance()` 生成代理对象
- **CGLib**：基于继承，通过 `Enhancer` 生成子类，`private` 和 `final` 方法不可代理
- Spring Boot 2.0+ 默认使用 CGLib（`spring.aop.proxy-target-class=true`），因为大多数 Bean 没有实现接口
- 性能上，JDK 8+ JDK 动态代理性能已经接近甚至超过 CGLib

### Q5：Spring Boot 自动配置的原理？

**答**：
`@SpringBootApplication` 包含 `@EnableAutoConfiguration`，后者通过 `@Import(AutoConfigurationImportSelector.class)` 加载 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 中声明的自动配置类。每个自动配置类使用 `@Conditional` 条件注解判断是否生效（如 `@ConditionalOnClass` 检查类是否存在）。这种方式实现了"依赖即配置"的约定优于配置思想。

### Q6：Spring 中 Bean 的作用域有哪些？

**答**：
- **singleton**（默认）：整个 IoC 容器一个实例，适合无状态的 Service、DAO
- **prototype**：每次获取创建新实例，适合有状态的 Bean
- **request**：一次 HTTP 请求一个实例（仅 Web 容器）
- **session**：一次 HTTP Session 一个实例（仅 Web 容器）
- **application**：整个 ServletContext 一个实例

注意：原型 Bean 注入单例 Bean 时，需要 `ObjectFactory` 或 `@Lookup` 保证每次获取新实例。

### Q7：Spring 中 BeanFactory 和 FactoryBean 的区别？

**答**：
- **BeanFactory**：IoC 容器的顶层接口，管理 Bean 的生命周期
- **FactoryBean**：工厂 Bean 接口，用于创建**复杂对象**（如 `SqlSessionFactoryBean`）
- 通过 `&beanName` 获取 FactoryBean 本身，`beanName` 获取其生产的对象

```java
// FactoryBean 示例：创建复杂对象
@Component
public class MyFactoryBean implements FactoryBean<ComplexObject> {
    @Override
    public ComplexObject getObject() {
        return new ComplexObject(/* 复杂的创建逻辑 */);
    }
    @Override
    public Class<?> getObjectType() {
        return ComplexObject.class;
    }
}
// 获取：context.getBean("myFactoryBean") → ComplexObject
//      context.getBean("&myFactoryBean") → MyFactoryBean
```

### Q8：如何优化 Spring Boot 启动速度？

**答**：
1. **延迟初始化**：`spring.main.lazy-initialization=true`（减少启动时 Bean 创建，适合开发环境）
2. **排除不需要的自动配置**：`@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})`
3. **使用 Spring 的组件索引**：`spring-context-indexer` 依赖，避免类路径扫描
4. **减少 `@ComponentScan` 范围**：指定具体的包路径
5. **JVM 调优**：使用 CDS（Class Data Sharing）、AOT 编译（Spring Boot 3.x + GraalVM）

---

## 参考文章与推荐阅读

- [Spring Framework 官方文档](https://docs.spring.io/spring-framework/reference/)
- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring 源码分析 — 江南一点雨](https://github.com/lenve/spring-source)
- [《Spring 核心》— 芋道源码](https://www.iocoder.cn/Spring/Good-collection/)
- [Spring Boot 自动配置原理](https://www.baeldung.com/spring-boot-custom-auto-configuration)
- [美团技术 — Spring 循环依赖源码分析](https://tech.meituan.com/2018/09/27/spring-cycle-dependency.html)
- [阿里巴巴 Java 开发手册](https://github.com/alibaba/p3c) — 事务与 AOP 规范
- [Spring Boot 参考指南 — 配置优先级](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)
- [Baeldung — Spring Transaction Management](https://www.baeldung.com/transaction-configuration-with-jpa-and-spring)
- [Spring AOP 源码分析 — 知乎](https://zhuanlan.zhihu.com/p/83878532)

---

## 相关文章

- [JVM 原理](/java/jvm)
- [并发编程](/java/concurrent)
- [JDK 版本特性 (8~21)](/java/jdk-versions)
