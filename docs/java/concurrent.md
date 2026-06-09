# Java 并发编程

## 一、核心概念

- 线程（Thread）
- 线程池（ThreadPool）
- 锁（Lock）
- CAS

---

## 二、线程池核心参数

- corePoolSize
- maximumPoolSize
- keepAliveTime
- BlockingQueue

---

## 三、线程池工作流程

1. 任务提交
2. 核心线程执行
3. 队列缓存
4. 扩容线程
5. 拒绝策略

---

## 四、高并发问题

- 线程安全
- 死锁
- 资源竞争
- 上下文切换开销