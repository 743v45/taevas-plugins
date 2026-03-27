# 重试模式

## 概述

对临时性错误进行智能重试，通过指数退避策略提高操作稳定性。

---

## 适用场景

- 网络抖动导致的偶发失败
- 页面元素加载慢导致的查找失败
- 竞态条件（element detached）
- 服务端限流（429）

---

## 核心结构

```typescript
interface RetryOptions {
  maxRetries?: number;
  delayMs?: number;
  maxDelayMs?: number;
  retryable?: (error: Error) => boolean;
  onRetry?: (attempt: number, error: Error) => void;
}

async function retryOperation<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    delayMs = 1000,
    maxDelayMs = 10000,
    retryable = () => true,
    onRetry = () => {},
  } = options;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // 最后一次失败或不可重试，抛出异常
      if (attempt === maxRetries || !retryable(lastError)) {
        throw lastError;
      }

      // 计算退避时间
      const backoff = Math.min(delayMs * Math.pow(2, attempt), maxDelayMs);

      // 📦 [BB] 错误 - 记录重试
      // blackboxEnabled 由 Feature Flag 模式提供
      if (blackboxEnabled) {
        blackbox.record('retry', {
          attempt: attempt + 1,
          maxRetries: maxRetries + 1,
          backoff,
          error: lastError.message,
          stack: lastError.stack,
          timestamp: Date.now(),
        });
      }

      onRetry(attempt + 1, lastError);
      await new Promise(resolve => setTimeout(resolve, backoff));
    }
  }

  throw lastError;
}
```

---

## 实现要点

### 1. 遵循沉默原则

```typescript
// ✅ 默认不执行（由 Feature Flag 模式控制）
if (blackboxEnabled) {
  blackbox.record('retry', { ... });
}
```

### 2. 遵循隔离原则

```typescript
// 📦 [BB] 错误 - 记录重试
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('retry', { ... });
}
```

### 3. 遵循完整原则

```typescript
// ✅ 记录完整重试信息
{
  attempt: 2,
  maxRetries: 4,
  backoff: 2000,
  error: 'Element detached',
  stack: '...',
  timestamp: 1234567890,
}
```

---

## 代码模板

### 基础模板

```typescript
// ✅ 基础使用
await retryOperation(
  () => page.click('[data-testid="submit"]'),
  {
    maxRetries: 3,
    delayMs: 500,
  }
);

// 📦 [BB] 错误 - 记录重试（在 retryOperation 内部）
```

### 带重试条件模板

```typescript
await retryOperation(
  () => this.api.login(credentials),
  {
    maxRetries: 3,
    delayMs: 1000,
    retryable: (error) => {
      // 只重试网络错误和超时
      return error.message.includes('network') ||
             error.message.includes('timeout');
    },
  }
);
```

### 带回调模板

```typescript
await retryOperation(
  () => page.click(selector),
  {
    maxRetries: 3,
    onRetry: (attempt, error) => {
      // 📦 [BB] 错误 - 记录重试（也可以在回调中记录）
      if (process.env.BLACKBOX_ENABLED) {
        blackbox.record('retry', {
          attempt,
          error: error.message,
          timestamp: Date.now(),
        });
      }
    },
  }
);
```

---

## 指数退避策略

```
延迟 = min(delay * 2^attempt, maxDelay)

attempt 0: 失败，等待 delay * 2^0 = 1000ms
attempt 1: 失败，等待 delay * 2^1 = 2000ms
attempt 2: 失败，等待 delay * 2^2 = 4000ms
attempt 3: 最后一次失败，抛出异常
```

| 尝试次数 | 延迟 | 累计延迟 |
|---------|------|---------|
| 1 | 1000ms | 1000ms |
| 2 | 2000ms | 3000ms |
| 3 | 4000ms | 7000ms |
| 4 | 8000ms | 15000ms |

---

## 可重试错误判断

### 常见可重试错误

```typescript
function isRetryable(error: Error): boolean {
  const message = error.message.toLowerCase();

  // 网络相关
  if (message.includes('network') ||
      message.includes('timeout') ||
      message.includes('connection')) {
    return true;
  }

  // DOM 元素相关
  if (message.includes('detached') ||
      message.includes('not found') ||
      message.includes('stale')) {
    return true;
  }

  // HTTP 状态码
  const match = error.message.match(/\[(\d{3})\]/);
  if (match) {
    const status = parseInt(match[1]);
    // 5xx 和 429 可重试
    return status >= 500 || status === 429;
  }

  return false;
}
```

### 不可重试错误

```typescript
function isNonRetryable(error: Error): boolean {
  const message = error.message.toLowerCase();

  // 认证错误
  if (message.includes('unauthorized') ||
      message.includes('invalid credentials') ||
      message.includes('forbidden')) {
    return true;
  }

  // 验证错误
  if (message.includes('validation') ||
      message.includes('invalid')) {
    return true;
  }

  // 4xx 错误（除了 429）
  const match = error.message.match(/\[(\d{3})\]/);
  if (match) {
    const status = parseInt(match[1]);
    return status >= 400 && status < 500 && status !== 429;
  }

  return false;
}
```

---

## 输出报告

```
============================================================
重试统计报告
============================================================

总操作数: 150
成功数: 138
重试成功数: 8
最终失败数: 4

重试操作:
  login
    重试次数: 2/3
    最终状态: 成功
    错误: "timeout", "network"

  click-submit
    重试次数: 3/3
    最终状态: 失败
    错误: "detached", "detached", "detached"

重试耗时:
    等待 1.0s (第1次)
    等待 2.0s (第2次)
    等待 4.0s (第3次)
    总计: 7.0s

============================================================
```

---

## 扩展：带熔断的重试

```typescript
class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private readonly threshold: number;
  private readonly timeout: number;

  constructor(threshold: number = 5, timeout: number = 60000) {
    this.threshold = threshold;
    this.timeout = timeout;
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // 检查熔断状态
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    if (this.state === 'half-open') {
      this.state = 'closed';
    }
  }

  private onFailure() {
    this.failures++;
    this.lastFailureTime = Date.now();

    if (this.failures >= this.threshold) {
      this.state = 'open';

      // 📦 [BB] 错误 - 记录熔断
      if (process.env.BLACKBOX_ENABLED) {
        blackbox.record('circuit-breaker', {
          state: this.state,
          failures: this.failures,
          threshold: this.threshold,
          timestamp: Date.now(),
        });
      }
    }
  }
}

// 使用
const circuitBreaker = new CircuitBreaker(5, 60000);

await circuitBreaker.execute(async () => {
  return await api.call();
});
```

---

## 扩展：带重试统计的重试

```typescript
class RetryTracker {
  private operations = new Map<string, RetryStats>();

  record(operation: string, attempt: number, maxRetries: number, error: Error) {
    let stats = this.operations.get(operation);
    if (!stats) {
      stats = {
        operation,
        attempts: 0,
        successes: 0,
        failures: 0,
        errors: [],
      };
      this.operations.set(operation, stats);
    }

    stats.attempts++;

    // 📦 [BB] 错误 - 记录重试统计
    if (process.env.BLACKBOX_ENABLED) {
      blackbox.record('retry-stats', {
        operation,
        attempt,
        maxRetries,
        error: error.message,
        totalAttempts: stats.attempts,
        timestamp: Date.now(),
      });
    }
  }

  recordSuccess(operation: string) {
    const stats = this.operations.get(operation);
    if (stats) {
      stats.successes++;
    }
  }

  recordFailure(operation: string, error: Error) {
    const stats = this.operations.get(operation);
    if (stats) {
      stats.failures++;
      stats.errors.push({
        error: error.message,
        timestamp: Date.now(),
      });
    }
  }

  getStats(operation: string): RetryStats | undefined {
    return this.operations.get(operation);
  }

  getAllStats(): RetryStats[] {
    return Array.from(this.operations.values());
  }
}
```