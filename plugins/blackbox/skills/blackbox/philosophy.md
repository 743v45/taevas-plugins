# 黑匣子设计哲学

## 核心定义

```
黑匣子 = 记录理念
```

**黑匣子是一种设计理念**：让代码运行时的一切都可被记录、可被追溯、可被分析。

出事后可完整回放分析，让问题从"难以复现"变成"有迹可循"。

---

## 理念层的定位

### 黑匣子是什么？

**黑匣子是一种记录理念**，不是具体的工具或框架。

| 维度 | 说明 |
|-----|------|
| **定位** | 理念层 - 提供设计思维和方法论 |
| **核心理念** | 让代码的"经历"可以被看见 |
| **适用范围** | 任何需要记录运行时信息的场景 |

### 黑匣子的实现方式

**黑匣子理念可以通过多种方式实现：**

```
┌─────────────────────────────────────────────────────────────┐
│                    黑匣子理念层                               │
│                  "让代码经历可以被看见"                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【实现方式 1】OpenTelemetry                                  │
│  - 工业标准：Trace/Metric/Log                                │
│  - 优点：跨语言、跨平台、生态完善                             │
│                                                             │
│  【实现方式 2】日志框架                                        │
│  - 传统方式：console.log / winston / log4j                  │
│  - 优点：简单直接、易于上手                                   │
│                                                             │
│  【实现方式 3】APM 工具                                       │
│  - 商业方案：New Relic / Datadog / Sentry                  │
│  - 优点：开箱即用、功能丰富                                   │
│                                                             │
│  【实现方式 4】自定义方案                                      │
│  - 项目特有：黑匣子 record() / 事件追踪                        │
│  - 优点：完全定制、适应项目需求                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 关键理解

> **黑匣子是"记什么、怎么记"的设计理念，OTEL 是"如何采集"的工具实现。**

| 理念层 | 实现层 |
|-------|-------|
| 记录什么状态 | Trace/Metric/Log |
| 在哪些地方记录 | API 埋点 / 中间件 / 自动化 |
| 何时记录 | 同步 / 异步 / 批量 |
| 记录多详细 | 标准 schema / 自定义结构 |

### 理念与实现的关系

```
黑匣子理念（道）：
  "记录关键操作的状态变化"
  "保证数据完整、可靠、可追溯"
         ↓
        实现（术）：
  OpenTelemetry 标准采集
  日志框架直接输出
  APM 工具自动追踪
  自定义 record() 函数
```

**同一个理念，多种实现方式。**

---

## 六大核心哲学

### 1. 事后可见性哲学

**让不可见的过程，在事后完整可见、可复现、可解释。**

```
代码一直在运行 → 我们不知道它在经历什么
                 ↓
               黑匣子
                 ↓
事后完整可见 → 我们可以复现和分析
```

| 状态 | 黑匣子前 | 黑匣子后 |
|-----|---------|---------|
| 运行时 | 不可见 | 可记录 |
| 事后 | 无法复现 | 完整回放 |
| 问题 | 难以定位 | 有迹可循 |

---

### 2. 客观中立性哲学

**只记录事实，不干预运行，不参与决策，不主观评判。**

| 原则 | 说明 |
|-----|------|
| **只记录** | 记录数据、状态、事件，不解释 |
| **不干预** | 记录不影响主流程运行 |
| **不决策** | 不根据记录内容做出任何业务决策 |
| **不评判** | 不对记录的数据进行好坏判断 |

```
错误示例：
blackbox.record('error', {
  message: error.message,
  severity: 'high',        // ❌ 主观评判
  action: 'retry'          // ❌ 参与决策
});

正确示例：
blackbox.record('error', {
  message: error.message,
  stack: error.stack,      // ✅ 只记录事实
  timestamp: Date.now()    // ✅ 客观数据
});
```

---

### 3. 生存优先性哲学

**记录系统的可靠性高于被记录系统，主体可毁，记录不可毁。**

```
飞机坠毁时，黑匣子必须能保存数据。
系统崩溃时，黑匣子必须能记录崩溃现场。
```

| 场景 | 黑匣子要求 |
|-----|-----------|
| 主系统崩溃 | 记录崩溃前的最后一刻数据 |
| 进程异常退出 | 持久化已记录的数据 |
| 磁盘满 | 保护关键记录，优先保留 |
| 网络断开 | 本地缓存，恢复后上传 |

```typescript
// ✅ 正确：确保数据持久化
process.on('uncaughtException', (error) => {
  // 先保存黑匣子数据
  blackbox.flush();
  // 再处理异常
  console.error(error);
});

// ❌ 错误：直接退出，数据丢失
process.on('uncaughtException', (error) => {
  process.exit(1);  // 黑匣子数据未保存
});
```

---

### 4. 证据唯一性哲学

**记录不可篡改、不可删除，成为唯一可信的事实依据。**

| 原则 | 说明 |
|-----|------|
| **不可篡改** | 记录后禁止修改任何数据 |
| **不可删除** | 记录后禁止删除（除非按策略循环覆盖） |
| **唯一可信** | 作为事故调查、责任界定的唯一依据 |

```typescript
// ✅ 正确：只追加，不修改
class Blackbox {
  private records: Record[] = [];

  record(data: Record) {
    // 只追加新记录，不修改旧记录
    this.records.push({ ...data, id: this.nextId() });
  }
}

// ❌ 错误：修改已存在的记录
class Blackbox {
  updateRecord(id: string, data: Partial<Record>) {
    // 禁止修改已存在的记录
    const record = this.records.find(r => r.id === id);
    Object.assign(record, data);  // ❌ 篡改记录
  }
}
```

---

### 5. 全局追溯性哲学

**所有关键行为、状态、时序可溯源，责任可定、问题可查。**

| 追溯维度 | 记录内容 |
|---------|---------|
| **行为** | 谁做了什么操作 |
| **状态** | 操作前后的系统状态 |
| **时序** | 操作发生的精确时间 |
| **来源** | 操作的发起者（用户、系统、定时器等） |
| **上下文** | 操作发生时的环境信息 |

```typescript
// ✅ 正确：记录完整的追溯信息
blackbox.record('api-call', {
  action: 'createUser',
  caller: 'user-service',
  userId: '12345',
  timestamp: Date.now(),
  requestId: 'req-123',
  traceId: 'trace-456',
  context: {
    userAgent: 'Mozilla/5.0...',
    ip: '192.168.1.1',
  },
});

// ❌ 错误：信息不完整
blackbox.record('api-call', {
  action: 'createUser',
  timestamp: Date.now(),
});
```

---

### 6. 迭代预防性哲学

**用历史记录反推问题根源，实现从"事后追溯"走向"事前预防"。**

```
循环：
  记录数据 → 分析问题 → 发现模式 → 改进系统 → 预防复发
```

| 阶段 | 行动 | 目标 |
|-----|------|-----|
| 事后 | 收集数据 | 完整记录事故 |
| 分析 | 发现模式 | 找到根本原因 |
| 改进 | 修复系统 | 消除隐患 |
| 事前 | 预防复发 | 避免同类问题 |

```typescript
// 示例：从历史记录中发现模式
function analyzeHistory() {
  const errors = blackbox.query('error', {
    timeRange: 'last-30-days',
  });

  // 发现：每周五下午 3-5 点错误率最高
  const pattern = findPattern(errors);
  // {
  //   time: 'Friday 15:00-17:00',
  //   errorRate: '12%',
  //   cause: 'database-backup-load'
  // }

  // 改进：调整备份时间或增加负载均衡
}
```

---

## 一句话总结

> **黑匣子：让不可见的运行过程在事后完整可见、可复现、可解释，成为唯一可信的事实依据。**

> **产品定位：可观测性设计指南，与 OpenTelemetry 等工具互补。**

---

## 如何选择实现方式？

### 决策矩阵

| 场景 | 推荐实现 | 理由 |
|-----|---------|------|
| **企业级应用、微服务架构** | OpenTelemetry | 标准化、生态完善、跨服务追踪 |
| **简单项目、快速原型** | 日志框架 | 简单直接、无需额外依赖 |
| **需要深度定制** | 自定义方案 | 完全控制、适应特殊需求 |
| **不想投入开发资源** | APM 工具 | 开箱即用、功能丰富 |

### 使用流程

```
第一步：用黑匣子理念设计埋点方案
  → 确定观测时机（前/中/后/异常）
  → 选择观测状态（输入/输出/资源/错误）
  → 设计记录格式

第二步：选择实现方式
  → 企业级：OpenTelemetry
  → 简单项目：日志框架
  → 深度定制：自定义方案
  → 快速上线：APM 工具

第三步：实现数据采集
  → OTEL：使用 Trace/Metric/Log API
  → 日志：console.log / winston / log4j
  → 自定义：blackbox.record()
  → APM：集成 SDK

第四步：选择存储和展示
  → Prometheus/Grafana
  → Jaeger
  → ELK/Loki
  → APM 平台
```

### 实现示例

#### 用 OpenTelemetry 实现黑匣子理念

```typescript
// 黑匣子理念：记录登录操作的状态变化
import { trace } from '@opentelemetry/api';

// 用 OTEL 实现黑匣子理念
const tracer = trace.getTracer('auth');

async function login(credentials) {
  // 记录操作前状态
  const span = tracer.startSpan('login', {
    attributes: { phase: 'before', username: credentials.username }
  });

  try {
    const user = await api.login(credentials);

    // 记录操作后状态
    span.setAttribute('phase', 'after');
    span.setAttribute('userId', user.id);
    span.setStatus({ code: 1 }); // OK
    span.end();
    return user;
  } catch (error) {
    // 记录错误状态
    span.recordException(error);
    span.setStatus({ code: 2, message: error.message });
    span.end();
    throw error;
  }
}
```

#### 用日志框架实现黑匣子理念

```typescript
import winston from 'winston';

// 黑匣子理念：记录关键状态
const logger = winston.createLogger({
  format: winston.format.json()
});

async function login(credentials) {
  logger.info('login:before', { username: credentials.username });

  try {
    const user = await api.login(credentials);
    logger.info('login:after', { userId: user.id });
    return user;
  } catch (error) {
    logger.error('login:error', { message: error.message });
    throw error;
  }
}
```

#### 用自定义方式实现黑匣子理念

```typescript
// 黑匣子理念：自定义实现
class Blackbox {
  record(type: string, data: any) {
    // 你的记录逻辑
  }
}

const blackbox = new Blackbox();

async function login(credentials) {
  blackbox.record('login:before', { username: credentials.username });

  try {
    const user = await api.login(credentials);
    blackbox.record('login:after', { userId: user.id });
    return user;
  } catch (error) {
    blackbox.record('login:error', { message: error.message });
    throw error;
  }
}
```

**三种方式，同一个黑匣子理念。**

---

## 相关文档

- **[principles.md](principles.md)** - 通用记录原则（10条）
- **[runtime.md](runtime.md)** - 运行模式
- **[operations.md](operations.md)** - 操作方法
- **[SKILL.md](SKILL.md)** - 使用指南
- **[../feature-flag/SKILL.md](../feature-flag/SKILL.md)** - Feature Flag 模式（环境开关控制）