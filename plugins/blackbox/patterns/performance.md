# 性能监控模式

## 概述

记录关键操作的耗时，生成延迟分布报告，用于定位性能瓶颈。

---

## 适用场景

- 登录/响应变慢，无法量化哪里慢
- 需要知道操作的 p50/p95/p99 延迟
- 检测性能退化

---

## 核心结构

```typescript
class PerformanceTracker {
  private timers = new Map<string, number>();
  private samples = new Map<string, number[]>();

  start(name: string): void {
    this.timers.set(name, performance.now());
  }

  end(name: string): void {
    const start = this.timers.get(name);
    if (!start) return;

    const duration = performance.now() - start;
    const samples = this.samples.get(name) || [];
    samples.push(duration);
    this.samples.set(name, samples.slice(-1000)); // 保留最近1000次
    this.timers.delete(name);
  }

  getStats(name: string): Stats | null {
    const samples = this.samples.get(name);
    if (!samples || samples.length === 0) return null;

    samples.sort((a, b) => a - b);
    return {
      count: samples.length,
      avg: samples.reduce((a, b) => a + b, 0) / samples.length,
      min: samples[0],
      max: samples[samples.length - 1],
      p50: samples[Math.floor(samples.length * 0.5)],
      p95: samples[Math.floor(samples.length * 0.95)],
      p99: samples[Math.floor(samples.length * 0.99)],
    };
  }
}
```

---

## 实现要点

### 1. 遵循沉默原则

```typescript
// ✅ 默认不执行（由 Feature Flag 模式控制）
if (blackboxEnabled) {
  perfTracker.start('login');
  try {
    // 业务逻辑
  } finally {
    perfTracker.end('login');
  }
}
```

### 2. 遵循隔离原则

```typescript
// 📦 [黑匣子] 性能 - 记录登录操作耗时
if (process.env.BLACKBOX_ENABLED) {
  perfTracker.start('login');
}
```

### 3. 遵循完整原则

```typescript
// ✅ 记录完整统计信息
{
  name: 'login',
  count: 245,
  avg: 2300,
  min: 1200,
  max: 8500,
  p50: 1800,
  p95: 4100,
  p99: 8200,
}
```

---

## 代码模板

### 基础模板

```typescript
async login() {
  // 📦 [黑匣子] 性能 - 记录登录操作耗时
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.start('login');
  }

  try {
    const user = await this.api.login(credentials);
    return user;
  } finally {
    if (process.env.BLACKBOX_ENABLED) {
      perfTracker.end('login');
    }
  }
}
```

### 带上下文模板

```typescript
async chat(prompt: string) {
  // 📦 [黑匣子] 性能 - 记录聊天操作耗时
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.start('chat', { promptLength: prompt.length });
  }

  try {
    const response = await this.api.chat(prompt);
    return response;
  } finally {
    if (process.env.BLACKBOX_ENABLED) {
      perfTracker.end('chat');
    }
  }
}
```

### 多阶段模板

```typescript
async processOrder(order: Order) {
  // 阶段1：验证
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.start('order-validate');
  }
  await this.validateOrder(order);
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.end('order-validate');
  }

  // 阶段2：处理
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.start('order-process');
  }
  const result = await this.process(order);
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.end('order-process');
  }

  // 阶段3：保存
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.start('order-save');
  }
  await this.save(result);
  if (process.env.BLACKBOX_ENABLED) {
    perfTracker.end('order-save');
  }

  return result;
}
```

---

## 输出报告

```
============================================================
性能监控报告
============================================================

login:
  样本数: 245
  平均: 2300ms
  范围: 1200ms - 8500ms
  p50: 1800ms
  p95: 4100ms
  p99: 8200ms

chat:
  样本数: 89
  平均: 5100ms
  范围: 2300ms - 18700ms
  p50: 3200ms
  p95: 12300ms
  p99: 18700ms

============================================================
```

---

## 性能分析

### 判断指标

| 指标 | 正常 | 警告 | 异常 |
|-----|------|------|------|
| p95 | < p50 × 2 | p50 × 2 ~ 3 | > p50 × 3 |
| p99 | < p50 × 3 | p50 × 3 ~ 5 | > p50 × 5 |
| max | < p95 × 2 | p95 × 2 ~ 3 | > p95 × 3 |

### 常见问题

- **p95 过高**：偶发慢操作，需要重试或优化
- **p99 过高**：极端情况，可能需要限流或降级
- **max 过高**：可能有异常分支，需要检查逻辑

---

## 扩展：带标签的性能追踪

```typescript
class PerformanceTracker {
  start(name: string, tags?: Record<string, any>): void {
    this.timers.set(name, {
      start: performance.now(),
      tags,
    });
  }

  end(name: string): void {
    const timer = this.timers.get(name);
    if (!timer) return;

    const duration = performance.now() - timer.start;
    const samples = this.samples.get(name) || [];
    samples.push({
      duration,
      tags: timer.tags || {},
      timestamp: Date.now(),
    });
    this.samples.set(name, samples.slice(-1000));
    this.timers.delete(name);
  }

  // 按标签分组统计
  getStatsByTag(name: string, tagKey: string): Record<string, Stats> {
    const samples = this.samples.get(name);
    if (!samples) return {};

    const groups = new Map<string, number[]>();
    samples.forEach(s => {
      const tagValue = s.tags[tagKey] || 'unknown';
      const group = groups.get(tagValue) || [];
      group.push(s.duration);
      groups.set(tagValue, group);
    });

    const result: Record<string, Stats> = {};
    groups.forEach((values, tagValue) => {
      result[tagValue] = this.calculateStats(values);
    });

    return result;
  }
}

// 使用
if (process.env.BLACKBOX_ENABLED) {
  perfTracker.start('api-call', { endpoint: '/login', method: 'POST' });
}
// ...
perfTracker.end('api-call');

// 分组统计
const stats = perfTracker.getStatsByTag('api-call', 'endpoint');
// {
//   '/login': { count: 100, avg: 2300, ... },
//   '/chat': { count: 89, avg: 5100, ... },
// }
```