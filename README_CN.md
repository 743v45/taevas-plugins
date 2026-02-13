# Taevas 插件市场

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple.svg)](https://claude.ai/code)

Claude Code 插件集合，包含声音通知与工作流增强工具。

## 可用插件

| 插件 | 描述 | 分类 |
|------|------|------|
| **sound-hooks** | 任务事件声音通知 | 通知 |
| **workflow-helper** | Git 信息与工作流工具 | 效率 |

## 快速开始

```bash
# 添加市场
claude plugin marketplace add 743v45/taevas-plugins

# 安装插件
claude plugin install sound-hooks@taevas-plugins
claude plugin install workflow-helper@taevas-plugins
```

## 声音通知

任务和命令事件的声音反馈。

### 配置

编辑 `.claude/plugins/sound-hooks/config.json`：

```json
{
  "enabled": true,
  "notifications": {
    "enabled": true,
    "sound": "Glass",
    "sounds": {
      "task_start": "Ping",
      "task_complete": "Hero",
      "task_error": "Basso",
      "command_start": "Tink"
    },
    "log": true
  }
}
```

### 可用声音 (macOS)

| 声音 | 描述 |
|------|------|
| Basso | 低音 |
| Blow | 吹气声 |
| Bottle | 瓶子碰撞 |
| Frog | 青蛙叫 |
| Funk | 放克音乐 |
| Glass | 玻璃声 (默认) |
| Hero | 英雄效 |
| Morse | 摩斯电码 |
| Ping | 铃声 |
| Pop | 爆音 |
| Purr | 猫呼噜 |
| Sosumi | 系统提示 |
| Submarine | 潜水声 |
| Tink | 叮铃声 |

## 许可证

MIT License - 见 [LICENSE](LICENSE)
