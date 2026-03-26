# 通用记录原则

## 定义

**通用记录原则 = 黑匣子类系统的核心设计原则**

这些原则是黑匣子、日志系统、监控系统、审计系统等所有记录类系统的共同基础。

---

## 十大原则

### 1. 完整性原则

**关键过程不遗漏、不中断，全程连续记录。**

| 要求 | 说明 |
|-----|------|
| 不遗漏 | 记录所有关键事件和数据 |
| 不中断 | 记录过程不被意外终止 |
| 连续 | 时间线上没有空白片段 |

```typescript
// ✅ 正确：使用 finally 确保记录完成
try {
  operation();
} finally {
  // 无论成功失败，都记录结束
  blackbox.record('operation-end', { timestamp: Date.now() });
}

// ❌ 错误：异常时记录中断
try {
  operation();
  blackbox.record('operation-end', { timestamp: Date.now() });
} catch (error) {
  // 记录中断
}
```

---

### 2. 不可篡改性原则

**记录一旦写入，禁止删除、修改、覆盖关键数据。**

| 操作 | 规则 |
|-----|------|
| 写入 | 只追加，不覆盖 |
| 修改 | 禁止修改已存在的记录 |
| 删除 | 只能按策略循环覆盖旧数据，禁止针对性删除 |

```typescript
// ✅ 正确：追加模式
class Blackbox {
  private records: Record[] = [];

  record(data: Record) {
    // 追加新记录
    this.records.push({ ...data, id: this.nextId() });
  }
}

// ❌ 错误：允许修改
class Blackbox {
  updateRecord(id: string, data: Partial<Record>) {
    // 禁止修改
    Object.assign(this.records.find(r => r.id === id), data);
  }
}
```

---

### 3. 可靠性原则

**极端环境下仍能保存（抗冲击、耐高温、抗电磁干扰）。**

在软件系统中对应：

| 场景 | 要求 |
|-----|------|
| 崩溃 | 记录已缓存的数据 |
| 磁盘满 | 保护关键记录，优先保留 |
| 网络断开 | 本地缓存，恢复后上传 |
| 内存不足 | 优先保留最新记录 |

```typescript
// ✅ 正确：异常时持久化
process.on('uncaughtException', (error) => {
  blackbox.flush();  // 持久化缓存数据
  throw error;
});

process.on('exit', () => {
  blackbox.flush();  // 退出前持久化
});

// ❌ 错误：不处理异常
process.on('uncaughtException', (error) => {
  throw error;  // 缓存数据丢失
});
```

---

### 4. 实时性原则

**数据同步记录，不延迟、不后补、不事后编造。**

| 要求 | 说明 |
|-----|------|
| 同步 | 事件发生时立即记录 |
| 不延迟 | 避免批量写入造成的延迟 |
| 不后补 | 禁止事后补录历史数据 |
| 不编造 | 记录真实发生的数据 |

```typescript
// ✅ 正确：实时记录
blackbox.record('api-call', {
  url: request.url,
  timestamp: Date.now(),  // 当前时间
});

// ❌ 错误：延迟记录
setTimeout(() => {
  blackbox.record('api-call', {
    url: request.url,
    timestamp: Date.now(),  // 时间不真实
  });
}, 1000);

// ❌ 错误：后补记录
blackbox.record('api-call', {
  url: request.url,
  timestamp: Date.now() - 5000,  // 编造时间
});
```

---

### 5. 可溯源性原则

**每条记录带时间戳、来源、操作人/设备、事件上下文。**

| 追溯要素 | 说明 |
|---------|------|
| 时间戳 | 精确到毫秒 |
| 来源 | 事件的发起者 |
| 操作人/设备 | 用户 ID、设备 ID |
| 上下文 | 环境信息、请求 ID、Trace ID |

```typescript
// ✅ 正确：完整追溯信息
blackbox.record('user-action', {
  action: 'click',
  timestamp: Date.now(),
  source: 'web-client',
  userId: 'user-123',
  deviceId: 'device-456',
  context: {
    requestId: 'req-789',
    traceId: 'trace-abc',
    userAgent: 'Mozilla/5.0...',
    ip: '192.168.1.1',
  },
});

// ❌ 错误：信息不完整
blackbox.record('user-action', {
  action: 'click',
  timestamp: Date.now(),
});
```

---

### 6. 最小必要原则

**只记录关键参数与行为，不冗余、不无效存储。**

| 原则 | 说明 |
|-----|------|
| 关键参数 | 记录对问题分析有用的数据 |
| 不冗余 | 避免重复记录相同数据 |
| 不无效 | 不记录无用的信息 |

```typescript
// ✅ 正确：只记录关键信息
blackbox.record('api-call', {
  url: request.url,
  method: request.method,
  status: response.status,
  timestamp: Date.now(),
});

// ❌ 错误：记录过多信息
blackbox.record('api-call', {
  url: request.url,
  method: request.method,
  status: response.status,
  timestamp: Date.now(),
  headers: request.headers,  // 冗余
  fullBody: request.body,    // 可能很大
  stackTrace: new Error().stack,  // 无关信息
});
```

---

### 7. 可读性/可解析原则

**标准格式，事后能被第三方读取、解析、复现场景。**

| 要求 | 说明 |
|-----|------|
| 标准格式 | 使用 JSON、CSV 等标准格式 |
| 结构化 | 字段命名清晰、类型明确 |
| 可解析 | 第三方工具能读取和分析 |

```typescript
// ✅ 正确：标准 JSON 格式
blackbox.record('api-call', {
  type: 'api-call',
  url: 'https://api.example.com/users',
  method: 'POST',
  status: 200,
  duration: 234,
  timestamp: 1640995200000,
});

// ❌ 错误：非标准格式
blackbox.record('POST https://api.example.com/users 200 234ms');
```

---

### 8. 防丢失原则

**多副本、循环覆盖旧数据但保留最近完整周期。**

| 策略 | 说明 |
|-----|------|
| 多副本 | 数据写入多个位置 |
| 循环覆盖 | 旧数据被新数据覆盖 |
| 完整周期 | 保留最近一个完整周期的数据 |

```typescript
// ✅ 正确：循环覆盖策略
class Blackbox {
  private records: Record[] = [];
  private readonly MAX_SIZE = 1000;

  record(data: Record) {
    this.records.push(data);

    // 超过容量时，移除最旧的记录
    if (this.records.length > this.MAX_SIZE) {
      this.records.shift();  // 移除最旧记录
    }
  }
}

// ❌ 错误：无限增长
class Blackbox {
  private records: Record[] = [];

  record(data: Record) {
    this.records.push(data);  // 永不删除，内存溢出
  }
}
```

---

### 9. 独立性原则

**记录模块独立运行，不依赖主系统，主系统故障仍能记录。**

| 要求 | 说明 |
|-----|------|
| 独立进程 | 黑匣子作为独立进程运行 |
| 不依赖主系统 | 黑匣子有自己的存储和通信 |
| 容错 | 主系统故障不影响黑匣子 |

```typescript
// ✅ 正确：黑匣子独立运行
// 进程 A: 主应用
const blackboxClient = new BlackboxClient();
blackboxClient.record('event', { data });

// 进程 B: 黑匣子服务
class BlackboxService {
  start() {
    // 独立运行，不依赖主应用
    this.listenForRecords();
    this.persistRecords();
  }
}

// ❌ 错误：黑匣子依赖主系统
class Blackbox {
  private db: Database;  // 依赖主系统的数据库

  record(data: Record) {
    this.db.save(data);  // 主系统故障时无法记录
  }
}
```

---

### 10. 合规审计原则

**记录可作为证据，满足监管、事故调查、责任界定要求。**

| 要求 | 说明 |
|-----|------|
| 完整性 | 记录完整，无遗漏 |
| 不可篡改 | 记录可验证真伪 |
| 可追溯 | 责任可追溯到具体操作 |
| 长期保存 | 按法规要求保存一定时间 |

```typescript
// ✅ 正确：记录包含审计信息
blackbox.record('user-login', {
  userId: 'user-123',
  action: 'login',
  result: 'success',
  timestamp: Date.now(),
  ip: '192.168.1.1',
  deviceId: 'device-456',
  sessionId: 'session-789',
  // 数字签名，防止篡改
  signature: sign({ userId, action, timestamp }),
});

// ❌ 错误：缺少审计信息
blackbox.record('user-login', {
  userId: 'user-123',
  timestamp: Date.now(),
});
```

---

## 原则检查清单

添加记录时，检查：

- [ ] 是否完整记录关键过程？
- [ ] 是否保证记录不可篡改？
- [ ] 是否在极端环境下仍能保存？
- [ ] 是否实时记录，不延迟？
- [ ] 是否包含完整的追溯信息？
- [ ] 是否只记录必要信息，不冗余？
- [ ] 是否使用标准格式，可解析？
- [ ] 是否有防丢失策略？
- [ ] 是否独立运行，不依赖主系统？
- [ ] 是否满足合规审计要求？

---

## 相关文档

- **[philosophy.md](philosophy.md)** - 黑匣子设计哲学
- **[runtime.md](runtime.md)** - 运行模式
- **[operations.md](operations.md)** - 操作方法
- **[SKILL.md](SKILL.md)** - 使用指南