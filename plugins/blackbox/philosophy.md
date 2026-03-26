# 黑匣子设计哲学

## 核心定义

```
黑匣子 = 飞行记录仪
```

一个运行时观测系统，默默记录代码运行时的一切。出事后可完整回放分析，让问题从"难以复现"变成"有迹可循"。

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

---

## 相关文档

- **[principles.md](principles.md)** - 通用记录原则（10条）
- **[runtime.md](runtime.md)** - 运行模式
- **[operations.md](operations.md)** - 操作方法
- **[SKILL.md](SKILL.md)** - 使用指南
- **[../feature-flag/SKILL.md](../feature-flag/SKILL.md)** - Feature Flag 模式（环境开关控制）