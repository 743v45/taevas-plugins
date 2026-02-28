# 声音通知 (Sound Hooks)

为 Claude Code 任务事件提供声音通知。在会话事件、任务完成或命令执行时获得音频反馈。

## 功能特性

- **会话通知**：会话开始/结束、代理启动/停止时播放提示音
- **任务通知**：任务完成时播放提示音
- **自定义声音**：为不同事件类型选择不同声音
- **跨平台**：支持 macOS、Linux 和 Windows
- **日志记录**：可选的通知日志

## 安装

```bash
# 从 marketplace 安装
claude plugin marketplace add 743v45/taevas-plugins
claude plugin install sound-hooks@taevas-plugins

# 更新命令
claude plugin marketplace update taevas-plugins && claude plugin update sound-hooks@taevas-plugins
```

## 配置

编辑 `.claude/plugins/sound-hooks/config.json`：

```json
{
  "enabled": true,
  "events": {
    "SessionStart": {
      "enabled": true,
      "notification": true,
      "sound": "Submarine",
      "message": "会话开始"
    },
    "TaskCompleted": {
      "enabled": true,
      "notification": true,
      "sound": "1up",
      "message": "任务完成"
    },
    "SubagentStop": {
      "enabled": false,
      "notification": true,
      "sound": "Purr",
      "message": "子代理停止"
    }
  },
  "log": true,
  "log_file": "${CLAUDE_PLUGIN_ROOT}/notifications.log"
}
```

### 配置说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 总开关 |
| `events.{event}.enabled` | boolean | 该事件是否启用 |
| `events.{event}.notification` | boolean | 是否显示桌面通知 |
| `events.{event}.sound` | string | 声音名称（空字符串则不播放声音） |
| `events.{event}.message` | string | 通知消息内容 |
| `log` | boolean | 是否记录日志 |
| `log_file` | string | 日志文件路径 |

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

自定义音效：将 mp3 文件放入 `src/sounds/` 目录，配置时使用文件名（不含扩展名）。

## 可用事件

| 事件 | 说明 |
|------|------|
| `SessionStart` | 会话开始 |
| `SessionEnd` | 会话结束 |
| `UserPromptSubmit` | 提交用户提示 |
| `PreToolUse` | 工具执行前 |
| `PostToolUse` | 工具执行成功 |
| `PostToolUseFailure` | 工具执行失败 |
| `PermissionRequest` | 请求权限 |
| `Notification` | 收到通知 |
| `SubagentStart` | 子代理启动 |
| `SubagentStop` | 子代理停止 |
| `Stop` | 响应完成 |
| `TeammateIdle` | 队友空闲 |
| `TaskCompleted` | 任务完成 |
| `PreCompact` | 上下文压缩前 |

## 快速禁用/启用

### 禁用某个事件的通知但保留声音
```json
{
  "events": {
    "SessionStart": {
      "notification": false,
      "sound": "Submarine"
    }
  }
}
```

### 禁用某个事件的声音但保留通知
```json
{
  "events": {
    "SessionStart": {
      "notification": true,
      "sound": ""
    }
  }
}
```

### 完全禁用某个事件
```json
{
  "events": {
    "SessionStart": {
      "enabled": false
    }
  }
}
```

## 手动安装

如果需要手动安装：

1. 复制插件文件：
```bash
mkdir -p .claude/plugins/sound-hooks/scripts
cp scripts/notify.sh .claude/plugins/sound-hooks/scripts/
cp config.json .claude/plugins/sound-hooks/
cp -r src/sounds .claude/plugins/sound-hooks/src/
```

2. 将 `hooks/hooks.json` 复制到 `.claude/hooks.json`：
```bash
cp hooks/hooks.json .claude/hooks.json
```

或手动编辑 `.claude/hooks.json`：
```json
{
  "description": "Sound notification hooks for Claude Code task events",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify.sh SessionStart"
          }
        ]
      }
    ]
  }
}
```
