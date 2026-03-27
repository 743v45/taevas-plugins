---
name: blackbox
description: 记录理念设计指南。帮助理解"记什么、怎么记"，指导埋点方案设计，可通过 OpenTelemetry/日志/自定义等多种方式实现。
argument-hint: "[场景/组件]"
---

# 黑匣子 (BlackBox)

**记录理念设计指南**——帮助你理解"记什么、怎么记"，让代码运行时的一切都可被观测、可被追溯、可被分析。

---

## 产品定位

### 黑匣子是什么？

**黑匣子是一种记录理念**，不是具体的工具或框架。

| 维度 | 说明 |
|-----|------|
| **定位** | 理念层 - 提供设计思维和方法论 |
| **核心理念** | 让代码的"经历"可以被看见 |
| **适用范围** | 任何需要记录运行时信息的场景 |
| **实现方式** | OpenTelemetry、日志框架、APM 工具、自定义方案 |

### 黑匣子理念的实现

**同一个理念，多种实现方式：**

```
┌─────────────────────────────────────────────────────────────┐
│                    黑匣子理念层                               │
│                  "让代码经历可以被看见"                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【实现 1】OpenTelemetry - 工业标准                           │
│  【实现 2】日志框架 - 传统方式                                │
│  【实现 3】APM 工具 - 商业方案                                │
│  【实现 4】自定义方案 - 完全定制                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心理解

> **黑匣子是"记什么、怎么记"的设计理念，OTEL/日志/APM 都是"如何采集"的实现方式。**

| 理念层（黑匣子） | 实现层（可选） |
|----------------|--------------|
| 记录什么状态 | Trace / Log / Custom |
| 在哪些地方记录 | API 埋点 / 中间件 / 自动化 |
| 何时记录 | 同步 / 异步 / 批量 |
| 记录多详细 | 标准 schema / 自定义结构 |

### 如何选择实现方式？

| 场景 | 推荐实现 | 理由 |
|-----|---------|------|
| **企业级应用、微服务架构** | OpenTelemetry | 标准化、生态完善、跨服务追踪 |
| **简单项目、快速原型** | 日志框架 | 简单直接、无需额外依赖 |
| **需要深度定制** | 自定义方案 | 完全控制、适应特殊需求 |
| **不想投入开发资源** | APM 工具 | 开箱即用、功能丰富 |

### 实现示例

#### 用 OpenTelemetry 实现黑匣子理念

```typescript
// 黑匣子理念：记录登录操作的状态变化
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('auth');

async function login(credentials) {
  const span = tracer.startSpan('login', {
    attributes: { phase: 'before', username: credentials.username }
  });

  try {
    const user = await api.login(credentials);
    span.setAttribute('phase', 'after');
    span.setAttribute('userId', user.id);
    span.setStatus({ code: 1 });
    span.end();
    return user;
  } catch (error) {
    span.recordException(error);
    span.end();
    throw error;
  }
}
```

#### 用日志框架实现黑匣子理念

```typescript
import winston from 'winston';
const logger = winston.createLogger({ format: winston.format.json() });

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
class Blackbox {
  record(type: string, data: any) { /* ... */ }
}

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

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│  埋点生命周期 = 思考 → 添加 → 审查 → 验证 → 改进     │
├─────────────────────────────────────────────────────┤
│  道（哲学层）：黑匣子的核心设计思想                    │
│  目的：理解为什么需要状态观测                          │
├─────────────────────────────────────────────────────┤
│  法（原则层）：埋点必须遵守的铁律                      │
│  目的：保证记录完整、可靠、可追溯、可访问              │
├─────────────────────────────────────────────────────┤
│  术（模式层）：状态观测/埋点审查/埋点验证              │
│  目的：引导思考、审查已有、验证有效                    │
├─────────────────────────────────────────────────────┤
│  行（操作层）：模板 + 检查清单                         │
│  目的：拿来就用，快速实施                              │
└─────────────────────────────────────────────────────┘
```

---

## 交互式使用流程

### 第一步：确认你的需求

**你可以通过黑匣子理念解决：**

| 阶段 | 需求 | SKILL 帮你 |
|-----|------|----------|
| 思考 | 我该在哪些地方加埋点？ | 状态观测模式 - 引导你选择观测时机和状态 |
| 审查 | 已有的埋点够用吗？ | 埋点审查模式 - 检查可访问性、覆盖度、有效性 |
| 验证 | 埋下去的数据能定位问题吗？ | 埋点验证模式 - 开发/测试/生产三阶段验证 |
| 选择 | 我该用什么实现？ | 实现方式对比 - OTEL/日志/APM/自定义 |

---

### 第二步：选择深入层级

使用 `AskUserQuestion` 工具询问（支持多选）：

```
问题：您想深入了解哪几层内容？（可多选）
选项：
- 行（操作层）：模板 + 检查清单，拿来就用
- 术（模式层）：状态观测/埋点审查/埋点验证模式
- 法（原则层）：通用原则 + 埋点审查原则
- 道（哲学层）：黑匣子核心设计思想
```

---

### 第三步：按需加载并实施

| 用户需求 | 加载内容 | 实施方式 |
|---------|----------|----------|
| 思考加什么埋点 | 术：模式1 - 状态观测 | 确定时机 → 选择状态 |
| 审查已有埋点 | 术：模式2 - 埋点审查 | 检查可访问性、覆盖度、有效性 |
| 验证埋点有效 | 术：模式3 - 埋点验证 | 开发/测试/生产三阶段验证 |
| 直接用模板 | 行：模板 + 检查清单 | 复制模板，按清单检查 |

---

## 四层速查

### 道（哲学层）

**六大核心哲学：**

1. **事后可见性** - 让不可见的过程在事后完整可见
2. **客观中立性** - 只记录事实，不干预运行
3. **生存优先性** - 主体可毁，记录不可毁
4. **证据唯一性** - 记录不可篡改、不可删除
5. **全局追溯性** - 所有关键行为可溯源
6. **迭代预防性** - 从事后追溯走向事前预防

→ [完整内容：philosophy.md](philosophy.md)

---

### 法（原则层）

**十大通用原则：**

| 原则 | 核心要求 |
|-----|---------|
| 完整性 | 关键过程不遗漏、不中断 |
| 不可篡改性 | 只追加，不修改已存在的记录 |
| 可靠性 | 极端环境下仍能保存数据 |
| 实时性 | 同步记录，不延迟、不后补 |
| 可溯源性 | 每条记录带时间戳、来源、上下文 |
| 最小必要 | 只记录关键参数，不冗余 |
| 可读可解析 | 使用标准格式（JSON） |
| 防丢失 | 多副本、循环覆盖策略 |
| 独立性 | 记录模块独立运行 |
| 合规审计 | 可作为证据，满足监管要求 |

**埋点审查原则：**

| 原则 | 检查要点 |
|-----|---------|
| 可访问性 | harness 能否读取到已有埋点数据？ |
| 可检索性 | 出事后能否快速定位相关记录？ |
| 可解释性 | 记录的数据能否理解问题根因？ |
| 必要性 | 每条记录对问题分析是否有用？ |

→ [完整内容：principles.md](principles.md)

---

### 术（模式层）

#### 步骤0：分析用户已有的状态类型

```
用户："帮我检查埋点是否完整"
       ↓
   扫描代码中的现有埋点
       ↓
   分析覆盖度和遗漏
       ↓
   发现同类可补充的状态
       ↓
   推荐补充方案
```

---

**自动识别代码中的埋点模式：**

| 代码模式 | 对应状态类型 | 典型位置 | 是否已记录 |
|---------|-------------|---------|----------|
| `function(a, b)` | 输入状态 | 函数入口 | ❓ |
| `return result` | 输出状态 | 函数返回 | ❓ |
| `for (let i=0; i<n; i++)` | 中间状态 | 循环中 | ❓ |
| `await fetch(...)` | 外部响应状态 | API 调用后 | ❓ |
| `catch (error)` | 错误状态 | 异常处理 | ❓ |
| `page.url()` | 上下文状态 | 任意位置 | ❓ |
| `config.xxx` | 配置状态 | 操作前 | ❓ |
| `Date.now()` | 时序状态 | 操作前/后 | ❓ |
| `db.query(...)` | 依赖状态 | DB 操作前后 | ❓ |
| `process.memoryUsage()` | 资源状态 | 任意位置 | ❓ |
| `performance.now()` | 性能状态 | 操作前后 | ❓ |
| `await page.screenshot()` | 快照状态 | 异常时 | ❓ |

---

**分析命令：**

```bash
# 扫描项目中的黑匣子埋点
python plugins/blackbox/bin/analyze.py src/

# 输出示例：
# ✅ 已发现: 23 个埋点
# 📊 状态类型分布:
#   - 输入状态: 3
#   - 输出状态: 2
#   - 错误状态: 8
#   - 外部响应: 6
#   - 其他: 4
# ⚠️  发现遗漏:
#   - 时序状态: 有外部响应，但无请求间隔记录
#   - 上下文状态: 有 URL 记录，但缺少 userId/requestId
#   - 资源状态: 建议在长操作中添加资源监控
```

---

**自动发现的同类补充建议：**

| 已有状态 | 建议补充同类 | 理由 |
|---------|-------------|------|
| API 响应记录 | 时序状态（请求间隔） | 分析是否因请求过快导致限流 |
| 错误记录 | 失败前状态 | 知道失败前最后成功的状态是什么 |
| URL 记录 | 完整上下文（userId, requestId） | 追溯是哪个用户、哪个请求出错 |
| 函数返回值 | 函数输入参数 | 对比输入输出，发现异常转换 |
| 单次操作 | 性能状态（耗时、进度） | 量化操作快慢 |

---

#### 步骤0.5：询问用户是否需要补充

**使用 `AskUserQuestion` 工具：**

```
问题：扫描发现您有以下埋点，是否需要补充相关状态？

选项（多选）：
- 时序状态（已有 API 调用，补充请求间隔记录）
- 上下文状态（已有 URL，补充 userId/requestId）
- 失败前状态（已有错误处理，补充最后成功状态）
- 输入状态（已有返回值，补充函数参数）
- 资源状态（长操作中补充内存监控）
- 暂不需要补充
```

```
问题：是否需要添加新的状态类型？

选项（多选）：
- 依赖状态（记录数据库、缓存等依赖健康）
- 快照状态（异常时截图、内存 dump）
- 性能状态（记录耗时、进度、ETA）
- 配置状态（记录使用的配置值）
- 都不需要
```

---

#### 模式1：状态观测模式（引导加什么埋点）

```
用户："我想在XX地方加埋点"
       ↓
   确定观测时机（前/中/后/异常）
       ↓
   选择该时机下可观测的状态
```

---

**1.1 操作前观测**

**场景：** 需要知道"进入操作时的状态是什么"
**适用：** 函数入口、循环开始、异步任务启动

```typescript
// 📦 [BB] STATE - 记录输入状态
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'login',
    phase: 'before',
    inputs: { username, passwordType },
    timestamp: Date.now(),
  });
}
```

```typescript
// 📦 [BB] STATE - 记录资源状态
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'process-large-data',
    phase: 'before',
    resources: {
      memory: process.memoryUsage(),
      connections: connectionPool.count,
    },
  });
}
```

---

**1.2 操作中观测**

**场景：** 需要知道"进行中的状态变化"
**适用：** 循环迭代、异步进度、长任务

```typescript
// 📦 [BB] STATE - 记录循环进度
if (process.env.BLACKBOX_ENABLED && index % 100 === 0) {
  blackbox.record('state', {
    location: 'process-items',
    phase: 'during',
    progress: `${index}/${total}`,
    currentItem: items[index],
  });
}
```

```typescript
// 📦 [BB] STATE - 记录内存增长
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'parse-large-json',
    phase: 'during',
    resources: {
      memory: process.memoryUsage(),
    },
    parsedCount: objects.length,
  });
}
```

---

**1.3 操作后观测**

**场景：** 需要知道"操作完成时的结果"
**适用：** 函数返回、API 响应、DB 查询结果

```typescript
// 📦 [BB] STATE - 记录输出状态
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'login',
    phase: 'after',
    output: { userId, token },
    result: 'success',
  });
}
```

```typescript
// 📦 [BB] STATE - 记录外部响应
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'fetch-user',
    phase: 'after',
    external: {
      type: 'api',
      url: response.url,
      status: response.status,
      timing: response.timing,
    },
  });
}
```

---

**1.4 异常时观测**

**场景：** 需要知道"出问题时是什么状态"
**适用：** catch 块、错误处理器

```typescript
catch (error) {
  // 📦 [BB] STATE - 记录错误现场
  if (process.env.BLACKBOX_ENABLED) {
    blackbox.record('state', {
      location: 'login',
      phase: 'error',
      error: {
        message: error.message,
        stack: error.stack,
      },
      context: {
        url: page.url(),
        memory: process.memoryUsage(),
      },
    });
  }
}
```

```typescript
catch (error) {
  // 📦 [BB] STATE - 记录失败前状态
  if (process.env.BLACKBOX_ENABLED) {
    blackbox.record('state', {
      location: 'process-payment',
      phase: 'error',
      lastSuccessState: {
        step: 'validated',
        amount: payment.amount,
      },
      error: error.message,
    });
  }
}
```

---

#### 模式2：埋点审查模式（已有埋点是否合理）

```
用户："我们已经有 OpenTelemetry，够用吗？"
       ↓
   审查已有观测系统的可访问性
       ↓
   审查埋点覆盖度
       ↓
   审查记录的有效性
```

---

**2.1 审查观测系统可访问性**

**问题：** harness 能否读取到已有埋点数据？

```typescript
// 📦 [BB] AUDIT - 检查观测系统可访问性
// [示例代码] 需要根据实际项目适配 - 以下函数需要根据你的观测系统实现
if (process.env.BLACKBOX_ENABLED) {
  // TODO: 实现读取观测系统数据的函数，例如：
  // const otlpRecords = await readOtelTraces();
  // const otlpRecords = await readFromJaeger();
  // const otlpRecords = await readFromPrometheus();

  // 示例：假设你已经获取了观测数据
  const otlpRecords = []; // 替换为实际的数据获取逻辑

  blackbox.record('audit', {
    system: 'opentelemetry', // 或 'jaeger', 'prometheus' 等
    check: 'accessibility',
    result: otlpRecords.length > 0 ? 'accessible' : 'not-accessible',
    recordCount: otlpRecords.length,
    // harness: currentHarness, // TODO: 根据实际环境配置
  });
}
```

---

**2.2 审查埋点覆盖度**

**问题：** 关键路径是否有埋点覆盖？

```typescript
// 📦 [BB] AUDIT - 检查埋点覆盖度
// [示例代码] 需要根据实际项目适配 - 以下函数需要实现
if (process.env.BLACKBOX_ENABLED) {
  const criticalPaths = [
    'user-login',
    'payment-process',
    'order-create',
  ];

  // TODO: 实现埋点覆盖度检查函数，例如：
  // - 静态分析代码中的埋点标记
  // - 运行时测试验证关键路径是否有数据
  // const coverage = checkInstrumentationCoverage(criticalPaths);

  // 示例：手动定义覆盖情况
  const coverage = {
    percentage: 66, // 示例值
    covered: ['user-login', 'payment-process'],
    missing: ['order-create'],
  };

  blackbox.record('audit', {
    type: 'coverage',
    criticalPaths,
    coverage: coverage.percentage,
    covered: coverage.covered,
    missing: coverage.missing,
  });
}
```

---

**2.3 审查记录有效性**

**问题：** 记录是否满足追溯性和可解释性？

```typescript
// 📦 [BB] AUDIT - 检查记录追溯性
if (process.env.BLACKBOX_ENABLED) {
  const incomplete = records.filter(r =>
    !r.timestamp || !r.location || !r.phase
  );

  if (incomplete.length > 0) {
    blackbox.record('audit', {
      type: 'traceability',
      result: 'incomplete',
      issues: incomplete.map(r => r.id),
      totalRecords: records.length,
      incompleteRecords: incomplete.length,
    });
  }
}
```

---

#### 模式3：埋点验证模式（埋点是否起作用）

```
开发时：埋点能否产生预期数据？
       ↓
测试时：能否从记录中定位问题？
       ↓
生产时：事故分析时能否快速找到？
```

---

**3.1 开发时验证数据产生**

**问题：** 添加埋点后，真的能产生数据吗？

```typescript
// 📦 [BB] VALIDATE - 验证埋点产生数据
if (process.env.BLACKBOX_ENABLED) {
  const before = blackbox.query({ location: 'login' }).length;

  // 触发操作
  await login(credentials);

  const after = blackbox.query({ location: 'login' }).length;

  blackbox.record('validate', {
    type: 'data-production',
    location: 'login',
    expected: 'at-least-1',
    actual: after - before,
    result: after > before ? 'pass' : 'fail',
  });
}
```

---

**3.2 测试时验证问题定位**

**问题：** 记录的数据能否帮助定位问题？

```typescript
// 📦 [BB] VALIDATE - 验证问题定位能力
// [示例代码] 需要根据实际项目适配 - 测试埋点数据是否能帮助定位问题
if (process.env.BLACKBOX_ENABLED) {
  // TODO: 实现测试问题场景的函数，或手动触发测试
  // 示例测试场景：
  // 1. 使用无效凭证触发登录失败
  // 2. 模拟网络超时
  // 3. 触发业务逻辑错误

  // 示例：手动测试场景（需要你根据实际情况实现）
  // const error = await forceLoginError();

  // 模拟一个错误对象用于演示
  const error = {
    time: Date.now(),
    message: 'Invalid credentials',
  };

  // 尝试用埋点定位
  const relevant = blackbox.query({
    location: 'login',
    startTime: error.time - 5000,
    endTime: error.time,
  });

  blackbox.record('validate', {
    type: 'issue-locating',
    issue: 'login-fail',
    recordsFound: relevant.length,
    canLocate: relevant.length > 0,
    reason: relevant.length === 0 ? 'insufficient-data' : 'ok',
  });
}
```

---

**3.3 生产时验证快速检索**

**问题：** 事故发生时能否快速找到记录？

```typescript
// 📦 [BB] VALIDATE - 验证检索性能
if (process.env.BLACKBOX_ENABLED) {
  const startTime = Date.now() - 3600000; // 1小时前

  const queryStart = performance.now();
  const records = blackbox.query({
    startTime,
    types: ['error', 'state'],
  });
  const queryTime = performance.now() - queryStart;

  blackbox.record('validate', {
    type: 'query-performance',
    timeRange: '1-hour',
    recordCount: records.length,
    queryTime,
    acceptable: queryTime < 1000,
  });
}
```

---

### 行（操作层）

#### 0. 分析现有埋点

```bash
# 扫描项目中的黑匣子埋点
python plugins/blackbox/bin/analyze.py src/

# 输出示例：
# ✅ 已发现: 23 个埋点
# 📊 状态类型分布:
#   - STATE: 15
#   - AUDIT: 5
#   - VALIDATE: 3
# ⏱️ 观测阶段分布:
#   - before: 6
#   - after: 5
#   - error: 4
# ⚠️ 发现遗漏:
#   - 时序状态（请求间隔）
#   - 失败前状态（最后成功状态）
#   - 完整上下文（userId/requestId）
# 💡 建议:
#   1. 发现外部 API 调用，建议添加时序状态记录请求间隔
#   2. 发现错误处理，建议添加失败前的最后成功状态
#   3. 建议在上下文中添加 userId 和 requestId 以增强追溯能力
```

**分析工具功能：**
- 自动扫描代码中的 `📦 [BB]` 标记
- 统计状态类型分布
- 检测常见遗漏（如：有外部响应但无时序记录）
- 生成补充建议

---

#### 1. 埋点添加模板

**操作前观测**
```typescript
// 📦 [BB] STATE - 记录输入/资源状态
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'function-name',
    phase: 'before',
    inputs: { /* 输入参数 */ },
    resources: { /* 内存、连接数等 */ },
  });
}
```

**操作中观测**
```typescript
// 📦 [BB] STATE - 记录中间状态/资源消耗
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'function-name',
    phase: 'during',
    progress: { /* 进度信息 */ },
    resources: { /* 内存增长等 */ },
  });
}
```

**操作后观测**
```typescript
// 📦 [BB] STATE - 记录输出/外部响应
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'function-name',
    phase: 'after',
    output: { /* 返回值 */ },
    external: { /* API/DB 响应 */ },
  });
}
```

**异常时观测**
```typescript
// 📦 [BB] STATE - 记录错误现场
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('state', {
    location: 'function-name',
    phase: 'error',
    error: { message, stack },
    context: { /* 出错时的上下文 */ },
    lastSuccessState: { /* 最后一次成功状态 */ },
  });
}
```

---

#### 2. 埋点审查检查清单

**审查观测系统：**
- [ ] harness 能否读取到已有观测系统的数据？
- [ ] 不同观测系统的数据能否统一查询？
- [ ] 关键路径是否有埋点覆盖？
- [ ] 每条记录是否包含追溯信息（timestamp/location/phase）？
- [ ] 记录的数据能否解释问题根因？
- [ ] 是否有冗余或无用的记录？

---

#### 3. 埋点验证检查清单

**开发时验证：**
- [ ] 添加埋点后立即验证数据产生
- [ ] 故意制造问题测试定位能力

**测试时验证：**
- [ ] 记录能否复现问题？
- [ ] 记录能否解释问题根因？

**生产时验证：**
- [ ] 事故发生时能否快速检索？
- [ ] 检索性能是否可接受？
- [ ] 历史数据能否追溯？

---

## 快速开始

### 1. 启用黑匣子

```bash
# 通过环境变量启用
export BLACKBOX_ENABLED=true
export BLACKBOX_LEVEL=standard  # standard | full

# 运行测试
pnpm test
```

### 2. 添加第一个埋点

```typescript
async login(credentials: Credentials) {
  // 📦 [BB] STATE - 记录操作前状态
  if (process.env.BLACKBOX_ENABLED) {
    blackbox.record('state', {
      location: 'login',
      phase: 'before',
      inputs: { username: credentials.username },
    });
  }

  try {
    const user = await this.api.login(credentials);

    // 📦 [BB] STATE - 记录操作后状态
    if (process.env.BLACKBOX_ENABLED) {
      blackbox.record('state', {
        location: 'login',
        phase: 'after',
        output: { userId: user.id },
        result: 'success',
      });
    }

    return user;
  } catch (error) {
    // 📦 [BB] STATE - 记录错误现场
    if (process.env.BLACKBOX_ENABLED) {
      blackbox.record('state', {
        location: 'login',
        phase: 'error',
        error: { message: error.message },
      });
    }
    throw error;
  }
}
```

### 3. 验证埋点有效

```typescript
// 添加埋点后立即验证
const before = blackbox.query({ location: 'login' }).length;
await login(credentials);
const after = blackbox.query({ location: 'login' }).length;

console.log(`埋点产生数据: ${after > before ? '是' : '否'}`);
```

---

## 搜索命令

```bash
# 搜索所有黑匣子埋点
grep -r "📦 \[BB\]" src/

# 搜索状态观测
grep -r "📦 \[BB\] STATE" src/

# 排除黑匣子查看正常代码
grep -v "📦 \[BB\]" src/file.ts
```

---

## 相关文档

| 文档 | 说明 |
|-----|------|
| [philosophy.md](philosophy.md) | 黑匣子设计哲学（六大核心哲学） |
| [principles.md](principles.md) | 通用记录原则（十大原则） |
| [runtime.md](runtime.md) | 运行模式详解 |
| [operations.md](operations.md) | 操作方法详解 |
| [bin/analyze.py](bin/analyze.py) | 埋点分析工具 |
| [patterns/performance.md](patterns/performance.md) | 性能监控模式 |
| [patterns/network.md](patterns/network.md) | 网络拦截模式 |
| [patterns/retry.md](patterns/retry.md) | 重试模式 |