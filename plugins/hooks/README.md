# Sound Hooks

Sound notification hooks for Claude Code task events. Get audio feedback when tasks are created, completed, or when commands execute.

## Features

- **Task Notifications**: Sound alerts when tasks start, complete, or are in progress
- **Command Notifications**: Sound alerts when bash commands execute
- **Customizable Sounds**: Choose different sounds for different event types
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Logging**: Optional notification logging

## Installation

```bash
# 从 marketplace 安装
claude plugin marketplace add taevas-org/taevas-plugins
claude plugin install sound-hooks@taevas-plugins
```

## Configuration

Edit `.claude/plugins/sound-hooks/config.json`:

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

## Available Sounds (macOS)

| Sound | Description |
|-------|-------------|
| Basso | Deep bass |
| Blow | Blowing sound |
| Bottle | Bottle sound |
| Frog | Frog croak |
| Funk | Funk groove |
| Glass | Glass ping (default) |
| Hero | Hero effect |
| Morse | Morse code |
| Ping | Bell ping |
| Pop | Pop sound |
| Purr | Purring |
| Sosumi | System alert |
| Submarine | Underwater |
| Tink | Tinkling bell |

## Events

| Event | Description |
|-------|-------------|
| `task_start` | When a new task is created |
| `task_complete` | When a task is marked completed |
| `task_in_progress` | When a task starts being worked on |
| `task_error` | When a task encounters an error |
| `command_start` | When a bash command is executed |
| `command_complete` | When a bash command finishes |

## Manual Installation

If you want to install manually:

1. Copy the plugin files:
```bash
mkdir -p .claude/plugins/sound-hooks/scripts
cp scripts/notify.sh .claude/plugins/sound-hooks/scripts/
cp config.json .claude/plugins/sound-hooks/
```

2. Add hooks to your `.claude/hooks.json`:
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
