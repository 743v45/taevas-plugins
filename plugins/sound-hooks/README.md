# 声音通知 (Sound Hooks)

为 Claude Code 任务事件提供声音通知。在任务创建、完成或命令执行时获得音频反馈。

## 功能特性

- **任务通知**：任务开始、进行中、完成时播放声音提示
- **命令通知**：执行 bash 命令时播放声音提示
- **自定义声音**：为不同事件类型选择不同声音
- **跨平台**：支持 macOS、Linux 和 Windows
- **日志记录**：可选的通知日志

## 安装

```bash
# 从 marketplace 安装
claude plugin marketplace add 743v45/taevas-plugins
claude plugin install sound-hooks@taevas-plugins
```

## 配置

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
      "task_in_progress": "Pop",
      "task_error": "Basso",
      "command_start": "Tink",
      "command_complete": "Glass"
    },
    "log": true
  },
  "stages": {
    "task_start": true,
    "task_complete": true,
    "task_in_progress": true,
    "command_start": true,
    "command_complete": false
  }
}
```

### 配置说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 总开关 |
| `notifications.enabled` | boolean | 通知开关 |
| `notifications.sound` | string | 默认声音名称 |
| `notifications.sounds` | object | 各事件的声音映射 |
| `notifications.log` | boolean | 是否记录日志 |
| `stages` | object | 各事件是否启用 |

## 可用声音 (macOS)

| 声音 | 描述 |
|------|------|
| Basso | 低音 |
| Blow | 吹气声 |
| Bottle | 瓶子碰撞 |
| Frog | 青蛙叫 |
| Funk | 放克音乐 |
| Glass | 玻璃声 (默认) |
| Hero | 英雄效果 |
| Morse | 摩斯电码 |
| Ping | 铃声 |
| Pop | 爆音 |
| Purr | 猫呼噜 |
| Sosumi | 系统提示 |
| Submarine | 潜水声 |
| Tink | 叮铃声 |

## 事件

| 事件 | 说明 |
|------|------|
| `task_start` | 创建新任务时 |
| `task_complete` | 任务标记完成时 |
| `task_in_progress` | 开始执行任务时 |
| `task_error` | 任务遇到错误时 |
| `command_start` | 执行 bash 命令时 |
| `command_complete` | bash 命令完成时 |

## 手动安装

如果需要手动安装：

1. 复制插件文件：
```bash
mkdir -p .claude/plugins/sound-hooks/scripts
cp scripts/notify.sh .claude/plugins/sound-hooks/scripts/
cp config.json .claude/plugins/sound-hooks/
```

2. 在 `.claude/hooks.json` 中添加 hooks：
```json
{
  "hooks": [
    {
      "name": "task-start-notification",
      "match": [{ "event_type": "tool_use", "tool_name": "TaskCreate" }],
      "prompt": "执行通知脚本: {{.rootDir}}/.claude/plugins/sound-hooks/scripts/notify.sh '任务开始: {{.subject}}' 'task_start' '{{.rootDir}}/.claude/plugins/sound-hooks/config.json'"
    }
  ]
}
```
