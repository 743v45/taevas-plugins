# 网络拦截模式

## 概述

拦截并记录 HTTP 请求/响应的完整数据，包括 URL、方法、Headers、Body、状态码、Timing，用于快速定位 API 问题。

---

## 适用场景

- API 失败时看不到请求体/响应体
- 无法判断是客户端问题还是服务端问题
- 请求时序异常导致的问题
- 需要分析网络性能

---

## 核心结构

```typescript
class NetworkInterceptor {
  private records: NetworkRecord[] = [];

  intercept(page: Page) {
    // 请求拦截
    page.on('request', (request) => {
      this.recordRequest(request);
    });

    // 响应拦截
    page.on('response', async (response) => {
      await this.recordResponse(response);
    });
  }

  private recordRequest(request: Request) {
    // blackboxEnabled 由 Feature Flag 模式提供
    if (blackboxEnabled) {
      // 📦 [黑匣子] 网络 - 记录请求
      blackbox.record('network-request', {
        id: request.id(),
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        body: request.postData(),
        resourceType: request.resourceType(),
        timestamp: Date.now(),
      });
    }
  }

  private async recordResponse(response: Response) {
    // blackboxEnabled 由 Feature Flag 模式提供
    if (blackboxEnabled) {
      const body = await this.safeGetBody(response);

      // 📦 [黑匣子] 网络 - 记录响应
      blackbox.record('network-response', {
        id: response.request().id(),
        url: response.url(),
        status: response.status(),
        headers: response.headers(),
        body: body,
        timing: response.timing(),
        timestamp: Date.now(),
      });
    }
  }

  private async safeGetBody(response: Response): Promise<string | null> {
    try {
      const contentType = response.headers()['content-type'] || '';
      if (contentType.includes('application/json')) {
        return await response.text();
      }
      return null;
    } catch {
      return null;
    }
  }
}
```

---

## 实现要点

### 1. 遵循沉默原则

```typescript
// ✅ 默认不执行（由 Feature Flag 模式控制）
if (blackboxEnabled) {
  blackbox.record('network-request', { ... });
}
```

### 2. 遵循隔离原则

```typescript
// 📦 [黑匣子] 网络 - 记录请求
if (process.env.BLACKBOX_ENABLED) {
  blackbox.record('network-request', { ... });
}
```

### 3. 遵循完整原则

```typescript
// ✅ 记录完整信息
{
  id: '123',
  url: 'https://api.example.com/login',
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: '{"username":"test"}',
  status: 200,
  responseHeaders: { ... },
  responseBody: '{"token":"xxx"}',
  timing: { requestTime: 100, responseTime: 200, ... },
  timestamp: 1234567890,
}
```

### 4. 错误处理

```typescript
// ✅ 响应体获取失败不影响记录
private async safeGetBody(response: Response): Promise<string | null> {
  try {
    return await response.text();
  } catch {
    return null; // 不抛出异常，静默处理
  }
}
```

---

## 代码模板

### Playwright 拦截模板

```typescript
async setupNetworkMonitoring(page: Page) {
  // 📦 [黑匣子] 网络 - 设置请求拦截
  page.on('request', (request) => {
    if (process.env.BLACKBOX_ENABLED) {
      blackbox.record('network-request', {
        id: request.id(),
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        body: request.postData(),
        resourceType: request.resourceType(),
        timestamp: Date.now(),
      });
    }
  });

  // 📦 [黑匣子] 网络 - 设置响应拦截
  page.on('response', async (response) => {
    if (process.env.BLACKBOX_ENABLED) {
      const body = await response.text().catch(() => null);
      blackbox.record('network-response', {
        id: response.request().id(),
        url: response.url(),
        status: response.status(),
        headers: response.headers(),
        body: body,
        timing: response.timing(),
        timestamp: Date.now(),
      });
    }
  });
}
```

### Fetch 拦截模板

```typescript
function setupFetchInterceptor() {
  const originalFetch = window.fetch;

  window.fetch = async function (...args) {
    const url = args[0]?.toString() || '';
    const options = args[1] || {};

    // 📦 [黑匣子] 网络 - 记录 fetch 请求
    if (process.env.BLACKBOX_ENABLED) {
      blackbox.record('fetch-request', {
        url,
        method: options.method || 'GET',
        headers: options.headers,
        body: options.body,
        timestamp: Date.now(),
      });
    }

    const response = await originalFetch.apply(this, args);

    // 📦 [黑匣子] 网络 - 记录 fetch 响应
    if (process.env.BLACKBOX_ENABLED) {
      const body = await response.clone().text().catch(() => null);
      blackbox.record('fetch-response', {
        url,
        status: response.status,
        headers: Object.fromEntries(response.headers.entries()),
        body: body,
        timestamp: Date.now(),
      });
    }

    return response;
  };
}
```

### Axios 拦截模板

```typescript
function setupAxiosInterceptors(axiosInstance) {
  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config) => {
      if (process.env.BLACKBOX_ENABLED) {
        // 📦 [黑匣子] 网络 - 记录 axios 请求
        blackbox.record('axios-request', {
          url: config.url,
          method: config.method,
          headers: config.headers,
          data: config.data,
          timestamp: Date.now(),
        });
      }
      return config;
    },
    (error) => {
      if (process.env.BLACKBOX_ENABLED) {
        // 📦 [黑匣子] 错误 - 记录请求失败
        blackbox.record('axios-request-error', {
          message: error.message,
          config: error.config,
          timestamp: Date.now(),
        });
      }
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response) => {
      if (process.env.BLACKBOX_ENABLED) {
        // 📦 [黑匣子] 网络 - 记录 axios 响应
        blackbox.record('axios-response', {
          url: response.config.url,
          status: response.status,
          headers: response.headers,
          data: response.data,
          timestamp: Date.now(),
        });
      }
      return response;
    },
    (error) => {
      if (process.env.BLACKBOX_ENABLED) {
        // 📦 [黑匣子] 错误 - 记录响应失败
        blackbox.record('axios-response-error', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
          timestamp: Date.now(),
        });
      }
      return Promise.reject(error);
    }
  );
}
```

---

## 输出报告

```
============================================================
网络监控报告
============================================================

请求统计:
  总计: 234
  成功: 219
  失败: 15
  失败率: 6.4%

失败请求:
  [POST] https://api.example.com/login
    状态: 401
    响应: {"error": "invalid credentials"}

  [GET] https://api.example.com/user
    状态: 403
    响应: {"error": "forbidden"}

性能:
  平均耗时: 234ms
  p95: 450ms
  p99: 890ms
  最慢: 2340ms

============================================================
```

---

## 关键信号

### 状态码分析

| 状态码 | 类型 | 含义 | 可能原因 |
|-------|------|------|---------|
| 2xx | 成功 | 请求成功 | 正常 |
| 3xx | 重定向 | 需要进一步操作 | 循环重定向、配置问题 |
| 4xx | 客户端错误 | 请求有问题 | 参数错误、权限不足 |
| 5xx | 服务端错误 | 服务器有问题 | 服务异常、超时 |

### 时序分析

```typescript
interface Timing {
  requestStart: number;    // 请求开始时间
  domainLookupStart: number; // DNS 查询开始
  domainLookupEnd: number;   // DNS 查询结束
  connectStart: number;      // TCP 连接开始
  connectEnd: number;        // TCP 连接结束
  requestStart: number;      // 请求发送开始
  responseStart: number;     // 响应开始
  responseEnd: number;       // 响应结束
}
```

| 指标 | 计算方式 | 含义 |
|-----|---------|------|
| DNS 时间 | domainLookupEnd - domainLookupStart | DNS 解析耗时 |
| TCP 连接时间 | connectEnd - connectStart | 建立连接耗时 |
| 请求时间 | responseStart - requestStart | 发送请求耗时 |
| 响应时间 | responseEnd - responseStart | 接收响应耗时 |
| 总耗时 | responseEnd - requestStart | 完整请求耗时 |

---

## 扩展：请求链追踪

```typescript
class NetworkInterceptor {
  private records: Map<string, NetworkRecord> = new Map();

  private recordRequest(request: Request) {
    const record = {
      id: this.generateId(),
      parentId: this.getParentId(request),
      url: request.url(),
      method: request.method(),
      timestamp: Date.now(),
      type: 'request',
    };
    this.records.set(record.id, record);
  }

  private recordResponse(response: Response) {
    const request = response.request();
    const record = this.records.get(request.id());
    if (record) {
      record.response = {
        status: response.status(),
        headers: response.headers(),
        timing: response.timing(),
        timestamp: Date.now(),
      };
    }
  }

  private getParentId(request: Request): string | null {
    // 通过 referer 或其他方式找到父请求
    const referer = request.headers()['referer'];
    const parent = Array.from(this.records.values()).find(
      r => r.url === referer && r.type === 'request'
    );
    return parent?.id || null;
  }

  // 生成请求树
  getRequestTree(): TreeNode[] {
    // 按 parentId 组织成树形结构
    const roots: TreeNode[] = [];
    const map = new Map<string, TreeNode>();

    for (const record of this.records.values()) {
      const node = this.recordToNode(record);
      map.set(record.id, node);

      if (!record.parentId) {
        roots.push(node);
      } else {
        const parent = map.get(record.parentId);
        if (parent) {
          parent.children.push(node);
        }
      }
    }

    return roots;
  }
}
```

---

## 扩展：敏感数据过滤

```typescript
class NetworkInterceptor {
  private sensitiveKeys = ['password', 'token', 'creditCard', 'ssn'];
  private sensitivePatterns = [/\d{16}/, /\d{4}-\d{4}-\d{4}-\d{4}/]; // 信用卡号

  private sanitizeBody(body: string | null): string | null {
    if (!body) return null;

    try {
      const parsed = JSON.parse(body);
      this.sanitizeObject(parsed);
      return JSON.stringify(parsed);
    } catch {
      return this.sanitizeString(body);
    }
  }

  private sanitizeObject(obj: any): void {
    for (const key in obj) {
      if (this.sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
        obj[key] = '***REDACTED***';
      } else if (typeof obj[key] === 'object') {
        this.sanitizeObject(obj[key]);
      }
    }
  }

  private sanitizeString(str: string): string {
    for (const pattern of this.sensitivePatterns) {
      str = str.replace(pattern, '***REDACTED***');
    }
    return str;
  }
}
```