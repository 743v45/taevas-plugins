# 黑匣子运行模式

## 定义

运行模式 = 黑匣子在不同环境、不同场景下的行为配置。

---

## 核心概念

黑匣子的运行模式由两个维度决定：

| 维度 | 说明 | 控制方式 |
|-----|------|---------|
| **是否启用** | 黑匣子是否开启 | Feature Flag 模式 |
| **记录级别** | 记录多少数据 | 配置参数 |

```
启用 → 记录级别 → 运行模式
  ↓        ↓          ↓
 Feature  FULL      生产模式
   Flag   MINIMAL   调试模式
          OFF       关闭模式
```

---

## 运行模式分类

### 1. 关闭模式 (OFF)

黑匣子完全关闭，不记录任何数据。

| 特性 | 说明 |
|-----|------|
| 记录 | 无 |
| 性能影响 | 无 |
| 存储占用 | 无 |
| 适用场景 | 生产环境默认状态 |

```bash
# 配置
BLACKBOX_ENABLED=false
```

```typescript
// 行为
if (blackboxEnabled) {
  // 不会执行
  blackbox.record(...);
}
```

---

### 2. 最小模式 (MINIMAL)

只记录关键事件，用于生产环境的故障追踪。

| 特性 | 说明 |
|-----|------|
| 记录 | 仅错误、关键失败 |
| 性能影响 | 极小 |
| 存储占用 | 极小 |
| 适用场景 | 生产环境故障追踪 |

```bash
# 配置
BLACKBOX_ENABLED=true
BLACKBOX_LEVEL=minimal
```

```typescript
// 行为
if (blackboxEnabled && blackboxLevel === 'minimal') {
  // 只记录错误
  if (error) {
    blackbox.record('error', { message: error.message });
  }
}
```

---

### 3. 标准模式 (STANDARD)

记录常用事件，用于日常开发和测试。

| 特性 | 说明 |
|-----|------|
| 记录 | 错误、警告、关键操作 |
| 性能影响 | 小 |
| 存储占用 | 小 |
| 适用场景 | 测试环境、开发调试 |

```bash
# 配置
BLACKBOX_ENABLED=true
BLACKBOX_LEVEL=standard
```

```typescript
// 行为
if (blackboxEnabled && blackboxLevel === 'standard') {
  // 记录错误和警告
  if (error) {
    blackbox.record('error', { message: error.message });
  }
  // 记录关键操作
  blackbox.record('operation', { name: 'login' });
}
```

---

### 4. 完整模式 (FULL)

记录所有事件，用于深度问题分析。

| 特性 | 说明 |
|-----|------|
| 记录 | 所有事件、状态、性能数据 |
| 性能影响 | 中等 |
| 存储占用 | 中等 |
| 适用场景 | 生产环境事故分析、问题复现 |

```bash
# 配置
BLACKBOX_ENABLED=true
BLACKBOX_LEVEL=full
```

```typescript
// 行为
if (blackboxEnabled && blackboxLevel === 'full') {
  // 记录所有事件
  blackbox.record('event', { type: 'any-event' });
  // 记录性能
  blackbox.record('performance', { duration: 123 });
  // 记录网络
  blackbox.record('network', { url, method });
}
```

---

### 5. 调试模式 (DEBUG)

记录所有事件和详细上下文，用于开发时的问题定位。

| 特性 | 说明 |
|-----|------|
| 记录 | 所有事件 + 详细上下文 + 调用堆栈 |
| 性能影响 | 较大 |
| 存储占用 | 较大 |
| 适用场景 | 开发环境、本地调试 |

```bash
# 配置
BLACKBOX_ENABLED=true
BLACKBOX_LEVEL=debug
```

```typescript
// 行为
if (blackboxEnabled && blackboxLevel === 'debug') {
  // 记录所有事件
  blackbox.record('event', {
    type: 'any-event',
    context: { ...fullContext },
    stack: new Error().stack,
  });
  // 记录详细性能
  blackbox.record('performance', {
    duration: 123,
    memory: process.memoryUsage(),
    cpu: getCpuUsage(),
  });
}
```

---

## 运行模式对比

| 模式 | 记录范围 | 性能影响 | 存储 | 适用环境 |
|-----|---------|---------|------|---------|
| OFF | 无 | 无 | 无 | 生产（默认） |
| MINIMAL | 仅错误 | 极小 | 极小 | 生产（故障追踪） |
| STANDARD | 错误 + 关键操作 | 小 | 小 | 测试、开发 |
| FULL | 所有事件 | 中等 | 中等 | 生产（事故分析） |
| DEBUG | 所有 + 详细上下文 | 较大 | 较大 | 开发（本地调试） |

---

## 动态切换

### 运行时切换

```typescript
// 初始模式
let blackboxLevel = 'standard';

// 运行时切换
function switchBlackboxLevel(level: BlackboxLevel) {
  blackboxLevel = level;
  blackbox.record('level-change', {
    from: blackboxLevel,
    to: level,
    timestamp: Date.now(),
  });
}

// 检测到异常时自动切换
function onCriticalError(error: Error) {
  switchBlackboxLevel('full');  // 切换到完整模式
}
```

### 信号触发

```bash
# 发送信号切换模式
kill -USR1 <pid>  # 切换到 FULL 模式
kill -USR2 <pid>  # 切换回 STANDARD 模式
```

```typescript
process.on('SIGUSR1', () => {
  switchBlackboxLevel('full');
});

process.on('SIGUSR2', () => {
  switchBlackboxLevel('standard');
});
```

---

## 存储策略

### 内存存储

```typescript
class MemoryBlackbox {
  private records: Record[] = [];

  record(data: Record) {
    this.records.push(data);
    // 超过容量时移除最旧记录
    if (this.records.length > MAX_SIZE) {
      this.records.shift();
    }
  }
}
```

### 文件存储

```typescript
class FileBlackbox {
  private file: fs.WriteStream;

  constructor(path: string) {
    this.file = fs.createWriteStream(path, { flags: 'a' });
  }

  record(data: Record) {
    this.file.write(JSON.stringify(data) + '\n');
  }
}
```

### 混合存储

```typescript
class HybridBlackbox {
  private memory: MemoryBlackbox;
  private file: FileBlackbox;

  record(data: Record) {
    // 内存记录（快速访问）
    this.memory.record(data);

    // 文件记录（持久化）
    this.file.record(data);
  }
}
```

---

## 数据保留策略

### 循环覆盖

```typescript
class RotatingBlackbox {
  private files: string[] = [];
  private readonly MAX_FILES = 10;

  rotate() {
    // 创建新文件
    const newFile = `blackbox-${Date.now()}.log`;
    this.files.push(newFile);

    // 超过数量时删除最旧文件
    if (this.files.length > this.MAX_FILES) {
      const oldFile = this.files.shift();
      fs.unlinkSync(oldFile);
    }
  }
}
```

### 时间保留

```typescript
class TimeBasedBlackbox {
  private readonly RETENTION_DAYS = 7;

  cleanup() {
    const cutoff = Date.now() - this.RETENTION_DAYS * 24 * 60 * 60 * 1000;

    const files = fs.readdirSync('./blackbox');
    for (const file of files) {
      const stat = fs.statSync(`./blackbox/${file}`);
      if (stat.mtimeMs < cutoff) {
        fs.unlinkSync(`./blackbox/${file}`);
      }
    }
  }
}
```

---

## 相关文档

- **[philosophy.md](philosophy.md)** - 黑匣子设计哲学
- **[principles.md](principles.md)** - 通用记录原则
- **[operations.md](operations.md)** - 操作方法
- **[SKILL.md](SKILL.md)** - 使用指南
- **[../feature-flag/SKILL.md](../feature-flag/SKILL.md)** - Feature Flag 模式