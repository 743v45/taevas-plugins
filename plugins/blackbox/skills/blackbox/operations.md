# 黑匣子操作方法

## 定义

操作方法 = 如何使用黑匣子记录数据、查询数据、导出数据。

---

## 核心操作

```
记录 → 查询 → 导出 → 分析
```

---

## 1. 记录操作

### 基础记录

```typescript
// 基础接口
blackbox.record(type: string, data: Record): void;

// 使用
blackbox.record('event', {
  name: 'user-click',
  target: 'submit-button',
  timestamp: Date.now(),
});
```

### 类型化记录

```typescript
// 性能记录
blackbox.record('performance', {
  operation: 'login',
  duration: 234,
  timestamp: Date.now(),
});

// 错误记录
blackbox.record('error', {
  message: error.message,
  stack: error.stack,
  timestamp: Date.now(),
});

// 网络记录
blackbox.record('network', {
  url: request.url,
  method: request.method,
  status: response.status,
  timestamp: Date.now(),
});
```

### 带上下文记录

```typescript
// 设置全局上下文
blackbox.setContext({
  userId: 'user-123',
  sessionId: 'session-456',
  requestId: 'request-789',
});

// 记录时自动带上上下文
blackbox.record('event', {
  name: 'user-action',
  // 自动包含：userId, sessionId, requestId
});
```

---

## 2. 查询操作

### 按类型查询

```typescript
// 查询所有错误
const errors = blackbox.query({
  type: 'error',
});

// 查询所有网络请求
const requests = blackbox.query({
  type: 'network',
});
```

### 按时间范围查询

```typescript
// 查询最近 1 小时的记录
const recent = blackbox.query({
  startTime: Date.now() - 60 * 60 * 1000,
  endTime: Date.now(),
});

// 查询特定时间段
const specific = blackbox.query({
  startTime: new Date('2024-01-01').getTime(),
  endTime: new Date('2024-01-02').getTime(),
});
```

### 按条件查询

```typescript
// 查询特定状态码的请求
const failedRequests = blackbox.query({
  type: 'network',
  filter: (record) => record.status >= 400,
});

// 查询超过阈值的性能记录
const slowOperations = blackbox.query({
  type: 'performance',
  filter: (record) => record.duration > 1000,
});
```

### 组合查询

```typescript
// 查询最近 1 小时的所有错误
const recentErrors = blackbox.query({
  type: 'error',
  startTime: Date.now() - 60 * 60 * 1000,
});

// 查询特定操作的慢请求
const slowLogins = blackbox.query({
  type: 'performance',
  filter: (record) =>
    record.operation === 'login' &&
    record.duration > 2000,
});
```

---

## 3. 导出操作

### 导出为 JSON

```typescript
// 导出所有记录
const json = blackbox.export('json');
fs.writeFileSync('blackbox.json', json);

// 导出查询结果
const errors = blackbox.query({ type: 'error' });
const json = blackbox.export('json', errors);
fs.writeFileSync('errors.json', json);
```

### 导出为 CSV

```typescript
// 导出为 CSV
const csv = blackbox.export('csv', records);
fs.writeFileSync('blackbox.csv', csv);
```

### 导出为文本报告

```typescript
// 生成可读报告
const report = blackbox.generateReport();
fs.writeFileSync('blackbox-report.txt', report);
```

### 报告示例

```
============================================================
黑匣子报告
============================================================

时间范围: 2024-01-01 00:00:00 - 2024-01-01 23:59:59
总记录数: 1,234

错误统计:
  总数: 12
  最常见: "Network timeout" (5次)

性能统计:
  平均耗时: 234ms
  最慢操作: login (8,234ms)

网络统计:
  总请求数: 234
  失败数: 15
  失败率: 6.4%

============================================================
```

---

## 4. 分析操作

### 统计分析

```typescript
// 性能统计
const stats = blackbox.analyze('performance', {
  operation: 'login',
});

console.log(stats);
// {
//   count: 245,
//   avg: 2300,
//   min: 1200,
//   max: 8500,
//   p50: 1800,
//   p95: 4100,
//   p99: 8200,
// }
```

### 趋势分析

```typescript
// 按时间分组统计
const trend = blackbox.trend('error', {
  interval: '1h',
  startTime: Date.now() - 24 * 60 * 60 * 1000,
});

console.log(trend);
// [
//   { time: '00:00', count: 2 },
//   { time: '01:00', count: 1 },
//   { time: '02:00', count: 3 },
//   ...
// ]
```

### 关联分析

```typescript
// 查找错误前的网络请求
const errors = blackbox.query({ type: 'error' });
for (const error of errors) {
  const beforeError = blackbox.query({
    type: 'network',
    endTime: error.timestamp,
    startTime: error.timestamp - 5000,
  });
  console.log('Error:', error.message, 'Before:', beforeError);
}
```

---

## 5. 管理操作

### 清空记录

```typescript
// 清空所有记录
blackbox.clear();

// 清空特定类型记录
blackbox.clear({ type: 'error' });
```

### 设置容量限制

```typescript
// 设置最大记录数
blackbox.setMaxSize(1000);

// 设置最大存储大小（字节）
blackbox.setMaxSize(10 * 1024 * 1024);  // 10MB
```

### 设置保留时间

```typescript
// 设置记录保留时间
blackbox.setRetention(7 * 24 * 60 * 60 * 1000);  // 7天
```

---

## 6. 埋点注释规范

### 标记格式

```typescript
// 📦 [BB] <类型> <说明>
```

### 类型分类

| 标记 | 类型 | 说明 |
|-----|------|------|
| `📦 [BB] 性能` | 性能埋点 | 记录操作耗时 |
| `📦 [BB] 网络` | 网络埋点 | 记录请求/响应 |
| `📦 [BB] 资源` | 资源埋点 | 记录内存/CPU |
| `📦 [BB] 错误` | 错误埋点 | 记录异常信息 |
| `📦 [BB] 状态` | 状态埋点 | 记录页面状态 |
| `📦 [BB] 快照` | 快照埋点 | 保存现场数据 |

### 搜索命令

```bash
# 搜索所有黑匣子埋点
grep -r "📦 \[黑匣子\]" src/

# 搜索特定类型
grep -r "📦 \[黑匣子\] 性能" src/
grep -r "📦 \[黑匣子\] 网络" src/

# 排除黑匣子查看正常代码
grep -v "📦 \[黑匣子\]" src/file.ts
```

---

## 7. 代码模板

### 基础模板

```typescript
// ✅ 正确：使用 Feature Flag 控制
// blackboxEnabled 由 Feature Flag 模式提供
if (blackboxEnabled) {
  // 📦 [BB] 性能 - 记录登录操作耗时
  blackbox.record('performance', {
    operation: 'login',
    start: startTime,
    end: Date.now(),
    duration: Date.now() - startTime,
  });
}
```

### 带上下文模板

```typescript
// ✅ 正确：设置全局上下文
if (blackboxEnabled) {
  blackbox.setContext({
    userId: user.id,
    sessionId: session.id,
  });
}

// 所有后续记录自动带上上下文
if (blackboxEnabled) {
  // 📦 [BB] 网络 - 记录请求
  blackbox.record('network', {
    url: request.url,
    method: request.method,
    // 自动包含：userId, sessionId
  });
}
```

### 错误处理模板

```typescript
// ✅ 正确：记录错误上下文
try {
  await operation();
} catch (error) {
  if (blackboxEnabled) {
    // 📦 [BB] 错误 - 记录错误上下文
    blackbox.record('error', {
      message: error.message,
      stack: error.stack,
      context: {
        url: page.url(),
        title: await page.title(),
        screenshot: await page.screenshot(),
      },
    });
  }
  throw error;
}
```

---

## 操作检查清单

添加记录时，检查：

- [ ] 是否有 `// 📦 [BB]` 标记？
- [ ] 标记类型是否正确（性能/网络/资源/错误/状态/快照）？
- [ ] 是否有 Feature Flag 控制（如 `if (blackboxEnabled)`）？
- [ ] 是否包含时间戳？
- [ ] 是否包含必要的追溯信息？
- [ ] 记录的信息是否结构化（JSON）？
- [ ] 是否遵循最小必要原则？

---

## 相关文档

- **[philosophy.md](philosophy.md)** - 黑匣子设计哲学
- **[principles.md](principles.md)** - 通用记录原则
- **[runtime.md](runtime.md)** - 运行模式
- **[SKILL.md](SKILL.md)** - 使用指南
- **[../feature-flag/SKILL.md](../feature-flag/SKILL.md)** - Feature Flag 模式